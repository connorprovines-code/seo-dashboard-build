# SEO Dashboard Backend

FastAPI-based backend optimized for Vercel serverless deployment.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py      # Database configuration (serverless-optimized)
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── keyword.py
│   │   ├── rank_tracking.py
│   │   ├── competitor.py
│   │   ├── serp.py
│   │   ├── backlink.py
│   │   ├── outreach.py
│   │   ├── api.py
│   │   ├── ai.py
│   │   └── email.py
│   ├── routers/            # API route handlers (to be created)
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── keywords.py
│   │   ├── rank_tracking.py
│   │   ├── competitors.py
│   │   ├── api_credentials.py
│   │   ├── ai.py
│   │   └── cron.py        # Vercel cron job handlers
│   ├── services/          # Business logic (to be created)
│   │   ├── dataforseo.py
│   │   ├── google_search_console.py
│   │   ├── anthropic_client.py
│   │   └── encryption.py
│   └── schemas/           # Pydantic models (to be created)
│       ├── user.py
│       ├── project.py
│       └── keyword.py
├── database/
│   └── schema.sql         # PostgreSQL schema for initialization
├── alembic/               # Database migrations
├── tests/                 # Unit and integration tests
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Local Development

### Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your database URL and API keys
```

### Initialize Database

```bash
# Option 1: Using the SQL schema (recommended for first setup)
psql $DATABASE_URL < database/schema.sql

# Option 2: Using Alembic migrations
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Run Development Server

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py script
python -m app.main
```

Visit:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Database Models

All models use SQLAlchemy ORM with UUID primary keys and proper relationships.

### Core Models
- **User**: User accounts with authentication
- **Project**: Website projects tracked by users
- **Keyword**: Keywords tracked within projects
- **RankTracking**: Historical rank position data
- **SerpSnapshot**: Full SERP result snapshots

### Phase 2 Models
- **Backlink**: Backlink profile data
- **OutreachProspect**: Link building prospects
- **CompetitorDomain**: Competitor tracking

### Phase 3 Models (AI Assistant)
- **AiConversation**: Chat conversation threads
- **AiMessage**: Individual messages
- **AiPermission**: User permissions for AI
- **EmailConnection**: Connected email accounts

### Supporting Models
- **ApiUsageLog**: API call tracking
- **ApiCredential**: Encrypted API credentials

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (Upstash)
- `SECRET_KEY` - JWT secret key
- `DATAFORSEO_LOGIN` - DataForSEO API login
- `DATAFORSEO_PASSWORD` - DataForSEO API password

Optional:
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `ANTHROPIC_API_KEY` - Claude API key
- `SENDGRID_API_KEY` - SendGrid for emails
- `SENTRY_DSN` - Error tracking

See `.env.example` for full list.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_keywords.py

# Run integration tests
pytest tests/integration/
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## API Documentation

Once the server is running, visit `/docs` for interactive API documentation powered by Swagger UI.

## Deployment

See the root [VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) for deployment instructions.

## Key Features

### Serverless Optimizations

1. **NullPool Database Connections**: No connection pooling, fresh connections per request
2. **Stateless Design**: All state stored in PostgreSQL or Redis
3. **Fast Cold Starts**: Minimal imports, lazy loading
4. **Timeout Handling**: All operations complete within 60 seconds

### Security

- JWT authentication
- Bcrypt password hashing
- Encrypted API credentials at rest
- CORS configuration
- SQL injection prevention via ORM
- Rate limiting (to be implemented)

### Performance

- Redis caching for expensive queries
- Database query optimization with indexes
- Batch API requests to DataForSEO
- Edge caching headers
- Materialized views for analytics

## Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Submit a pull request

## License

MIT License
