from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.security.jwt_utils import create_access_token
from app.security.password import hash_password,verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse, UserLogin,TokenResponse,RefreshRequest,ChangePasswordRequest
from app.security.refresh_tokens import (
    generate_refresh_token,
    hash_refresh_token,
    store_refresh_token,
)
from app.security.dependencies import get_current_user
from app.core.rate_limiter import limiter
from datetime import datetime, timezone
from app.models.refresh_token import RefreshToken
import uuid



router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def register_user(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=str(data.email),
        hashed_password=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def user_login(
    request: Request,
    usersignin: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == usersignin.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        usersignin.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(existing_user.id)

    refresh_token = generate_refresh_token()
    family_id = uuid.uuid4()
    
    store_refresh_token(
        db=db,
        user_id=existing_user.id,
        token=refresh_token,
        family_id=family_id,
        )

    db.commit()

    return {
"access_token": access_token,
"refresh_token": refresh_token,
"token_type": "bearer",
}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
def refresh_access_token(
    request: Request,
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    token_hash = hash_refresh_token(data.refresh_token)

    stored_token = (
    db.query(RefreshToken)
    .filter(RefreshToken.token_hash == token_hash)
    .with_for_update()
    .first()
)

    if not stored_token:
        raise HTTPException(
        status_code=401,
        detail="Invalid refresh token",
    )

    now = datetime.now(timezone.utc)

# Detect reuse of a revoked refresh token.
    if stored_token.revoked_at is not None:
        db.query(RefreshToken).filter(
            RefreshToken.family_id == stored_token.family_id,
            RefreshToken.revoked_at.is_(None),
            ).update(
                {RefreshToken.revoked_at: now},
                synchronize_session=False,
                )

        db.commit()

        raise HTTPException(
        status_code=401,
        detail="Refresh token reuse detected. Token family revoked.",
        )

# Check expiration.
    expires_at = stored_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        db.rollback()
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
    )

# Validate the user.
    user = db.get(User, stored_token.user_id)

    if not user or not user.is_active:
        raise HTTPException(
        status_code=401,
        detail="User account is unavailable",
    )

    try:
        # Revoke the old token.
        stored_token.revoked_at = now

        # Generate a replacement in the same token family.
        new_refresh_token = generate_refresh_token()

        store_refresh_token(
            db=db,
            user_id=user.id,
            token=new_refresh_token,
            family_id=stored_token.family_id,
        )

        new_access_token = create_access_token(user.id)

        # Save both changes in one transaction.
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
        

    except Exception:
        db.rollback()
        raise

    
@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    # 1. Hash the supplied refresh token
    token_hash = hash_refresh_token(data.refresh_token)

    # 2. Find the corresponding database record
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )

    # 3. Reject unknown tokens
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # 4. Revoke the token if it hasn't already been revoked
    if stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(timezone.utc)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    # 5. Confirm logout
    return {"message": "Logged out successfully"}





@router.patch("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Verify the current password
    if not verify_password(
        data.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # 2. Prevent reusing the current password
    if verify_password(
        data.new_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from the current password",
        )

    try:
        # 3. Hash and update the new password
        current_user.hashed_password = hash_password(data.new_password)

        # 4. Revoke all existing refresh tokens for this user
        db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
        ).update(
            {
                RefreshToken.revoked_at: datetime.now(timezone.utc)
            },
            synchronize_session=False,
        )

        # 5. Save both changes in one transaction
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {"message": "Password changed successfully"}

