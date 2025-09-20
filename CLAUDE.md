# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IELTS backend API built with FastAPI and PostgreSQL, featuring Firebase authentication integration. The application follows an async/await pattern throughout and uses SQLAlchemy for database operations.

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload

# Run the development server with custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Database
```bash
# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade database
alembic downgrade -1
```

## Architecture

### Core Structure
```
src/
├── core/               # Core configuration and setup
│   ├── config.py      # Environment configuration (DB, Firebase)
│   ├── db.py          # SQLAlchemy async engine and session setup
│   ├── firebase.py    # Firebase Admin SDK initialization and token verification
│   └── logging_config.py
├── middleware/         # Custom middleware
│   └── auth.py        # Firebase token verification middleware
├── models/            # SQLAlchemy ORM models
│   └── users.py       # User database model
├── schemas/           # Pydantic models for request/response validation
│   └── user.py        # User schema definitions
└── routes/            # API route handlers
    └── users.py       # User-related endpoints
```

### Key Patterns

**Database Setup**: The application uses async SQLAlchemy with PostgreSQL. Database connection is configured in `src/core/db.py` with async engine and session management.

**Firebase Authentication**: Firebase token verification is handled through a dependency injection pattern:
- `src/core/firebase.py` contains Firebase initialization and token verification
- `src/middleware/auth.py` provides FastAPI dependencies for authentication
- Protected endpoints use `Depends(get_current_user)` to require authentication

**Route Organization**: Routes are organized by feature in the `src/routes/` directory and included in `main.py` using `app.include_router()`.

**Configuration Management**: Environment variables are managed through `src/core/config.py` using pydantic Settings with automatic `.env` file loading.

### Authentication Flow
1. Frontend sends Firebase ID token in `Authorization: Bearer <token>` header
2. `verify_token()` middleware extracts and validates the token with Firebase Admin SDK
3. `get_current_user()` dependency provides decoded user information to protected endpoints
4. User data includes `uid`, `email`, `name`, and `picture` from Firebase token

### Database Models vs Schemas
- **Models** (`src/models/`): SQLAlchemy ORM classes defining database tables
- **Schemas** (`src/schemas/`): Pydantic models for API request/response validation and serialization

### Environment Variables Required
```
DATABASE_URL=postgresql://username:password@localhost:5432/ielts_db
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
```

## Common Development Tasks

### Adding New Protected Endpoints
1. Import authentication dependency: `from src.middleware.auth import get_current_user`
2. Add dependency to route: `current_user: dict = Depends(get_current_user)`
3. Access user data via `current_user["uid"]`, `current_user["email"]`, etc.

### Database Changes
1. Modify SQLAlchemy models in `src/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Apply migration: `alembic upgrade head`

### Adding New Route Modules
1. Create route file in `src/routes/`
2. Define router with appropriate prefix and tags
3. Include router in `main.py`: `app.include_router(new_router.router)`