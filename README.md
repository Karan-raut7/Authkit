# AuthKit

A production-oriented authentication API built with FastAPI, PostgreSQL, and SQLAlchemy. AuthKit implements user authentication, JWT access tokens, rotating refresh tokens, token reuse detection, and authentication rate limiting.


## Features

- **User Registration** — Register accounts using email and password.
- **Password Hashing** — Secure password hashing using Argon2.
- **JWT Authentication** — Short-lived access tokens.
- **Refresh Token Rotation** — Issue new access and refresh tokens during token renewal.
- **Refresh Token Reuse Detection** — Track refresh-token rotation and detect reuse of revoked tokens.
- **Token Revocation** — Revoke refresh tokens during logout.
- **Protected Endpoints** — Authenticate users using bearer tokens.
- **Password Change** — Change account passwords through an authenticated endpoint.
- **Rate Limiting** — Limit authentication-related requests.
- **Database Migrations** — Manage schema changes using Alembic.
- **Frontend** — A lightweight HTML, CSS and JavaScript interface.
- **Health Checks** — Health and readiness endpoints.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| JWT | Access-token authentication |
| Argon2 | Password hashing |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend logic |

## Architecture

```text
AuthKit
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── alembic/
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── change-password.html
├── tests/
├── alembic.ini
├── requirements.txt
└── README.md
```

## Authentication Flow

### Login

1. The user submits their email and password.
2. The backend validates the credentials.
3. The backend issues an access token and refresh token.
4. The frontend stores the tokens in session storage.
5. The user is redirected to the dashboard.

### Access Token Refresh

When an authenticated request fails because the access token is invalid or expired:

1. The frontend detects a `401 Unauthorized` response.
2. The frontend sends the refresh token to the refresh endpoint.
3. The backend validates the refresh token.
4. The backend revokes the old refresh token.
5. The backend generates a new access token and refresh token.
6. The newly generated refresh token is stored in the database.
7. The frontend updates its stored tokens.
8. The original request is retried.

### Logout

1. The client sends its refresh token to the logout endpoint.
2. The backend revokes the refresh token.
3. The frontend removes its stored tokens.
4. The user is redirected to the login page.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/v1/auth/register` | Register a new user |
| POST | `/v1/auth/login` | Authenticate a user |
| POST | `/v1/auth/refresh` | Refresh access and refresh tokens |
| POST | `/v1/auth/logout` | Revoke a refresh token |
| PATCH | `/v1/auth/change-password` | Change account password |
| GET | `/me` | Retrieve authenticated user information |
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness check |

## Token Configuration

| Token | Expiration |
|---|---|
| Access Token | 30 minutes |
| Refresh Token | 7 days |

Refresh tokens are stored in the database as hashes rather than plaintext tokens.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Karan-raut7/Authkit.git
cd Authkit
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure your environment.

**Windows:**

```powershell
Copy-Item .env.example .env
```

Configure your database connection, secret key and other required settings inside `.env`.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
python -m uvicorn app.main:app --reload
```

### 7. Access AuthKit

| Page | URL |
|---|---|
| Homepage | http://127.0.0.1:8000/ |
| Register | http://127.0.0.1:8000/register |
| Login | http://127.0.0.1:8000/login |
| Dashboard | http://127.0.0.1:8000/dashboard |
| API Documentation | http://127.0.0.1:8000/docs |

## Testing

Run the test suite with:

```bash
pytest
```

## Security Considerations

- Passwords are hashed rather than stored in plaintext.
- Access tokens are short-lived.
- Refresh tokens are stored as hashes.
- Refresh-token rotation is implemented.
- Authentication endpoints are rate-limited.
- Refresh-token revocation is supported.

This project is intended as a learning and portfolio project demonstrating authentication architecture and implementation. Further security hardening and testing are necessary before production deployment.