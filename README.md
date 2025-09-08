# IELTS Writing Assessment Backend

A FastAPI-based backend service for IELTS writing assessment and evaluation.

## Features

- 🔍 **Writing Assessment**: Automated IELTS writing evaluation with detailed scoring
- 👤 **User Management**: User registration and profile management
- 📊 **IELTS Scoring**: Comprehensive band scoring across four criteria
- 🌐 **CORS Support**: Configured for frontend integration
- ⚡ **Async Operations**: High-performance async database operations

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, currently disabled)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ielts-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Users
- `POST /users/` - Create a new user
- `GET /users/{email}` - Get user by email

### Writing Assessment
- `POST /write/review` - Submit writing for AI review and scoring

## IELTS Scoring Criteria

The writing assessment evaluates four key areas:

1. **Task Response** (0-9): How well the writing addresses the task
2. **Coherence & Cohesion** (0-9): Organization and logical flow
3. **Lexical Resource** (0-9): Vocabulary range and accuracy
4. **Grammatical Range & Accuracy** (0-9): Grammar complexity and correctness

Scores are given in 0.5 increments (e.g., 6.0, 6.5, 7.0).

## Project Structure

```
src/
├── core/           # Core utilities and configuration
│   ├── config.py   # Configuration settings
│   ├── db.py       # Database connection
│   └── utils.py    # Utility functions
├── models/         # SQLAlchemy models
│   └── users.py    # User model
├── routes/         # API route handlers
│   ├── users.py    # User endpoints
│   └── write.py    # Writing assessment endpoints
└── schemas/        # Pydantic schemas
    ├── user.py     # User validation schemas
    └── write.py    # Writing assessment schemas
```

## Development

### Database Migrations (when enabled)

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Running Tests

```bash
# Run tests (when test suite is added)
pytest
```

## Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/ielts_db
SECRET_KEY=your-secret-key
DEBUG=True
```

## Technology Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database (asyncpg driver)
- **Pydantic** - Data validation using Python type hints
- **Alembic** - Database migration tool
- **Uvicorn** - ASGI server implementation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]