from fastapi import FastAPI
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import FileResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.db.session import engine
from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.api.router import router as api_router
from fastapi.middleware.cors import CORSMiddleware
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


settings = get_settings()

is_development = settings.environment.lower() == "development"

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if is_development else None,
    redoc_url="/redoc" if is_development else None,
    openapi_url="/openapi.json" if is_development else None,
)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Register rate limiting with FastAPI.
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(api_router)




@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/register", include_in_schema=False)
def register_page():
    return FileResponse(FRONTEND_DIR / "register.html")


@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/change-password", include_in_schema=False)
def change_password_page():
    return FileResponse(FRONTEND_DIR / "change-password.html")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
    }


@app.get("/health/ready", tags=["Health"])
def readiness_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "database": "connected",
    }
