# SEO Dashboard - Setup Guide

This guide will help you get the SEO Dashboard up and running on your local machine or server.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.10+, Node.js 18+, PostgreSQL 15+, Redis 7+

## Quick Start with Docker (Recommended)

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd seo-dashboard-build
   ```

2. **Create environment files**:
   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

5. **Create your first user**:
   - Go to http://localhost:3000/register
   - Create an account
   - Log in and start creating projects!

## Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secret keys
   ```

5. **Set up PostgreSQL database**:
   ```bash
   createdb seo_dashboard
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit if needed
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

### Celery Workers (Optional - for background tasks)

In a new terminal:

```bash
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

For scheduled tasks (Celery Beat):

```bash
celery -A app.celery_app beat --loglevel=info
```

## Configuration

### Backend Environment Variables

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/seo_dashboard

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-here  # Generate a strong random key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200

# Encryption for API credentials
ENCRYPTION_KEY=your-encryption-key-here  # Generate a strong random key

# App Config
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
DEBUG=True
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SEO Dashboard
```

## API Keys (Per-User Configuration)

Users will configure their own API keys through the application UI:

- **DataForSEO**: For keyword research and rank tracking
  - Sign up at: https://dataforseo.com/apis
  - Get $1 free trial
  - Users add their API keys in Settings

- **Google Search Console**: For free ranking data
  - Users connect via OAuth in the app

- **Anthropic Claude** (Phase 3): For AI assistant features
  - Sign up at: https://console.anthropic.com/

## Verify Installation

1. **Check backend health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check frontend**:
   Open http://localhost:3000 in your browser

3. **Create a test user**:
   - Go to Register page
   - Create account
   - Log in
   - Create a test project

## Troubleshooting

### Database Connection Error
- Make sure PostgreSQL is running
- Verify DATABASE_URL in .env
- Check database exists: `psql -l`

### Port Already in Use
- Backend (8000): Change in docker-compose.yml or when running uvicorn
- Frontend (3000): Change in vite.config.ts and docker-compose.yml

### Frontend Can't Connect to Backend
- Check VITE_API_URL in frontend/.env
- Verify backend is running on port 8000
- Check CORS settings in backend/app/main.py

## Next Steps

1. **Create your first project**: Click "Create New Project" in the Projects page
2. **Add API credentials**: Go to project settings and add DataForSEO credentials
3. **Add keywords**: Start tracking keywords for your project
4. **Connect Google Search Console**: Get free ranking data
5. **Set up rank tracking**: Enable automated daily rank checks

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm run test
```

### Database Migrations

Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Production Deployment

For production deployment:

1. Change DEBUG=False in backend/.env
2. Generate strong SECRET_KEY and ENCRYPTION_KEY
3. Set up proper PostgreSQL database (not SQLite)
4. Use environment-specific docker-compose files
5. Set up SSL/TLS certificates
6. Configure proper CORS origins
7. Set up monitoring and logging

See README.md for detailed production deployment instructions.

## Support

For issues and questions:
- Check the main README.md
- Review the API documentation at /api/docs
- Check logs: `docker-compose logs -f`

## License

MIT License - See LICENSE file for details
