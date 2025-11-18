# Vercel Deployment Guide for SEO Dashboard

This guide will walk you through deploying the SEO Dashboard to Vercel with a serverless architecture.

## Architecture Overview

### Vercel Serverless Setup

```
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Edge Network                       │
│  (Global CDN for static files and serverless functions)     │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   React     │ │   FastAPI   │ │Vercel Cron  │
    │  Frontend   │ │  Serverless │ │   Jobs      │
    │   (Static)  │ │  Functions  │ │(Background) │
    └─────────────┘ └─────────────┘ └─────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Vercel    │ │   Upstash   │ │  External   │
    │  Postgres   │ │    Redis    │ │   APIs      │
    │  (or Neon)  │ │  (caching)  │ │ (DataForSEO)│
    └─────────────┘ └─────────────┘ └─────────────┘
```

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **GitHub Repository** - Push your code to GitHub
3. **Database** - Choose one:
   - Vercel Postgres (recommended, $20/month)
   - Neon.tech (Free tier available)
   - Supabase (Free tier available)
   - Railway.app PostgreSQL (Free tier available)
4. **Redis** - Upstash Redis (Free tier: 10K commands/day)
5. **DataForSEO Account** - For SEO APIs (Pay-per-use)

## Step-by-Step Deployment

### 1. Set Up Database (Vercel Postgres)

#### Option A: Vercel Postgres (Recommended)

1. Go to your Vercel dashboard
2. Navigate to **Storage** → **Create Database**
3. Select **Postgres**
4. Choose a name: `seo-dashboard-db`
5. Select a region close to your users
6. Click **Create**

Vercel will automatically add `DATABASE_URL` to your environment variables.

#### Initialize Database Schema

After creating the database, run the schema initialization:

```bash
# Install Vercel CLI
npm i -g vercel

# Pull environment variables
vercel env pull

# Connect to your database and run schema
psql $DATABASE_URL < backend/database/schema.sql
```

Or use the Vercel Postgres web interface to paste the schema from `backend/database/schema.sql`.

#### Option B: Neon.tech (Free Alternative)

1. Go to https://neon.tech
2. Sign up and create a project
3. Create a database called `seo_dashboard`
4. Copy the connection string
5. Run the schema:
   ```bash
   psql postgresql://user:pass@ep-xxx.region.aws.neon.tech/seo_dashboard?sslmode=require < backend/database/schema.sql
   ```

### 2. Set Up Redis (Upstash)

1. Go to https://console.upstash.com/
2. Create a new Redis database
3. Choose a name: `seo-dashboard-cache`
4. Select a region close to your database
5. Copy the REST URL or Redis URL

### 3. Configure Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables for all environments (Production, Preview, Development):

```
# Database (auto-set if using Vercel Postgres)
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379

# Authentication
SECRET_KEY=<generate with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200

# App Config
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app

# DataForSEO
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password

# Google Search Console
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=https://your-app.vercel.app/api/auth/google/callback

# Optional: Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Optional: SendGrid
SENDGRID_API_KEY=SG.xxx

# Optional: Sentry
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 4. Deploy to Vercel

#### Option A: Deploy via GitHub (Recommended)

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. Go to https://vercel.com/new
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click **Deploy**

#### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### 5. Set Up Background Jobs (Vercel Cron)

Since Vercel is serverless, we can't use Celery. Instead, use **Vercel Cron Jobs**.

Create `vercel.json` with cron configuration:

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-rank-check",
      "schedule": "0 2 * * *"
    },
    {
      "path": "/api/cron/sync-gsc-data",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

Create cron endpoints in your FastAPI app:

```python
# backend/app/routers/cron.py
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/api/cron", tags=["cron"])

@router.post("/daily-rank-check")
async def daily_rank_check(authorization: str = Header(None)):
    # Verify cron secret
    if authorization != f"Bearer {os.getenv('CRON_SECRET')}":
        raise HTTPException(401, "Unauthorized")

    # Trigger rank checks for all tracked keywords
    # Implementation here...
    return {"status": "success"}
```

Add `CRON_SECRET` to environment variables for security.

### 6. Alternative: Use Upstash QStash for Background Tasks

For more complex background jobs, use Upstash QStash:

```python
from upstash_qstash import QStash

qstash = QStash(os.getenv("QSTASH_TOKEN"))

# Schedule a job
qstash.publish_json({
    "url": "https://your-app.vercel.app/api/jobs/rank-check",
    "body": {"keyword_id": "123"},
    "delay": 3600  # 1 hour delay
})
```

## Database Migrations with Alembic

### Initial Setup

```bash
cd backend

# Initialize Alembic (if not done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### For Vercel Deployment

Add a post-deployment script:

```json
// package.json
{
  "scripts": {
    "vercel-build": "npm run build && npm run migrate",
    "migrate": "cd backend && alembic upgrade head"
  }
}
```

## Monitoring & Debugging

### 1. View Logs

```bash
# Real-time logs
vercel logs --follow

# Production logs
vercel logs --prod
```

### 2. Health Check Endpoint

Add to your FastAPI app:

```python
@app.get("/api/health")
async def health_check():
    db_status = check_db_connection()
    redis_status = check_redis_connection()

    return {
        "status": "healthy" if db_status and redis_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "redis": "connected" if redis_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }
```

### 3. Sentry Error Tracking

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "production"),
)
```

## Performance Optimization

### 1. Database Connection Pooling

Already configured in `backend/app/core/database.py` with `NullPool` for serverless.

### 2. Redis Caching

```python
import redis
from functools import wraps
import json

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(ttl=3600)
async def get_keyword_data(keyword_id):
    # Expensive database query...
    pass
```

### 3. Edge Caching

Add cache headers to static responses:

```python
@app.get("/api/projects/{project_id}/stats")
async def get_project_stats(project_id: str, response: Response):
    stats = get_stats(project_id)

    # Cache for 5 minutes
    response.headers["Cache-Control"] = "public, max-age=300"

    return stats
```

## Cost Optimization

### Vercel Costs

- **Hobby Plan**: $0/month (Personal projects)
  - 100GB bandwidth
  - 100GB-hrs serverless function execution
  - Unlimited deployments

- **Pro Plan**: $20/month
  - 1TB bandwidth
  - 1000GB-hrs serverless function execution
  - Team collaboration features

### Database Costs

- **Vercel Postgres**: ~$20/month for production
- **Neon.tech**: Free tier (0.5GB storage, 3 compute hours/day)
- **Supabase**: Free tier (500MB database, 2GB bandwidth)

### Redis Costs

- **Upstash**: Free tier (10K commands/day)
- **Upstash Pro**: $0.20 per 100K commands

### Total Monthly Cost Estimate

| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| Neon Database (Free) | $0 |
| Upstash Redis (Free) | $0 |
| DataForSEO APIs | ~$10-50 (usage-based) |
| **Total** | **$30-60/month** |

Still **70% cheaper** than Ahrefs ($129/month)!

## Troubleshooting

### Issue: Database connection timeout

**Solution**: Increase `connect_timeout` in database URL:
```
postgresql://user:pass@host:5432/db?connect_timeout=30
```

### Issue: Serverless function timeout

**Solution**: Increase timeout in `vercel.json`:
```json
{
  "functions": {
    "backend/app/main.py": {
      "maxDuration": 60
    }
  }
}
```

Note: Max duration is 60s on Pro plan, 10s on Hobby plan.

### Issue: Cold starts causing slow responses

**Solutions**:
1. Use Vercel Edge Functions for critical endpoints
2. Implement Redis caching aggressively
3. Use database connection pooling (already configured)
4. Consider upgrading to Vercel Pro for better performance

## Security Checklist

- [ ] All environment variables are set in Vercel dashboard
- [ ] `SECRET_KEY` is strong and unique (use `openssl rand -hex 32`)
- [ ] Database credentials are encrypted
- [ ] API keys are never committed to git
- [ ] CORS is properly configured
- [ ] HTTPS is enforced (automatic with Vercel)
- [ ] Rate limiting is implemented for sensitive endpoints
- [ ] SQL injection prevention (using SQLAlchemy ORM)
- [ ] XSS protection in frontend

## Next Steps

1. **Custom Domain**: Add your domain in Vercel settings
2. **SSL Certificate**: Automatic with Vercel (free)
3. **Analytics**: Add Vercel Analytics for insights
4. **Monitoring**: Set up Sentry for error tracking
5. **Backups**: Schedule automated database backups
6. **Testing**: Set up preview deployments for testing

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
- [Upstash Redis Docs](https://docs.upstash.com/redis)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/vercel/)
- [Neon.tech Docs](https://neon.tech/docs/introduction)

## Support

For issues or questions:
- Vercel Support: support@vercel.com
- Community Discord: discord.gg/vercel
- GitHub Issues: Create an issue in your repository
