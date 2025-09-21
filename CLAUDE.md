# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI backend for IELTS writing assessment with PostgreSQL integration. The API provides endpoints for user management and writing evaluation services.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Database migrations (when enabled)
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture

### Project Structure
- **Routes**: `src/routes/` - API endpoints organized by feature (users, write)
- **Models**: `src/models/` - SQLAlchemy database models  
- **Schemas**: `src/schemas/` - Pydantic validation schemas for request/response
- **Core**: `src/core/` - Database configuration, utilities, logging

### API Design
- **FastAPI** with automatic OpenAPI documentation
- **Pydantic schemas** for strict validation and serialization
- **Async/await** patterns throughout for database operations
- **CORS** configured for `http://localhost:8080` and `https://essay-buddy-ielts.lovable.app`

### Database Architecture
- **PostgreSQL** with SQLAlchemy async ORM (currently commented out)
- Models use declarative base pattern
- Database session management through AsyncSession
- Alembic for schema migrations (configured but not active)

### IELTS Writing Assessment
The core feature is the `/write/review` endpoint which:
- Accepts `WritingInput` with essay content, question details, timing data
- Returns structured `AIReview` with IELTS band scores (0-9 in 0.5 increments)
- Validates scores for four IELTS criteria: Task Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy
- Currently returns static mock data - AI integration pending

### Key Dependencies
- **FastAPI** + **uvicorn** for async web framework
- **SQLAlchemy** + **asyncpg** for PostgreSQL async operations  
- **Pydantic** for data validation and serialization
- **Alembic** for database migrations
- **python-dotenv** for environment configuration

## Development Notes

### Current State
- Database connection is commented out in `main.py` and `src/core/db.py`
- User routes reference undefined `db` variable (needs MongoDB or PostgreSQL implementation)
- Write review endpoint returns hardcoded response
- Models are defined but not connected to active database

### CORS Configuration  
CORS middleware in `main.py:10-21` allows requests from frontend applications with credentials enabled.