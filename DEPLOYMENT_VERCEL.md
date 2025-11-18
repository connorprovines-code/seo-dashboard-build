# Deploying SEO Dashboard to Vercel + Supabase

This guide walks through deploying the SEO Dashboard to Vercel (frontend + backend) with Supabase PostgreSQL database.

---

## Prerequisites

- Vercel account (free tier works)
- Supabase account (free tier works)
- Git repository (GitHub, GitLab, or Bitbucket)

---

## Step 1: Set Up Supabase Database

### 1.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Choose organization or create one
4. Project settings:
   - **Name:** `seo-dashboard`
   - **Database Password:** (generate strong password - SAVE THIS!)
   - **Region:** Choose closest to your users
   - **Pricing Plan:** Free tier is sufficient to start

5. Wait ~2 minutes for project to provision

### 1.2 Get Database Connection String

1. In Supabase dashboard, go to **Project Settings** → **Database**
2. Scroll to **Connection String** section
3. Select **URI** tab
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password
6. **SAVE THIS** - you'll need it for Vercel

### 1.3 Run Database Migrations

You have two options:

**Option A: Using Supabase SQL Editor (Recommended)**

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the schema from `backend/app/models/` and create tables manually, OR
4. Use the migration SQL below

**Option B: Using Alembic Locally**

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres"

# Run migrations
cd backend
alembic upgrade head
```

### 1.4 Database Schema SQL

Run this SQL in Supabase SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    api_credits_remaining NUMERIC(10, 2) DEFAULT 0.00
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    gsc_connected BOOLEAN DEFAULT FALSE,
    gsc_refresh_token TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Keywords table
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    keyword_text VARCHAR(500) NOT NULL,
    search_volume INTEGER,
    keyword_difficulty INTEGER,
    cpc NUMERIC(10, 2),
    competition NUMERIC(5, 2),
    last_refreshed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_project_keyword ON keywords(project_id, keyword_text);

-- Rank tracking table
CREATE TABLE rank_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tracked_url VARCHAR(2048) NOT NULL,
    rank_position INTEGER,
    search_engine VARCHAR(20) DEFAULT 'google',
    location_code INTEGER NOT NULL,
    language_code VARCHAR(10) DEFAULT 'en',
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_keyword_checked ON rank_tracking(keyword_id, checked_at);

-- Competitor domains table
CREATE TABLE competitor_domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SERP snapshots table
CREATE TABLE serp_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    rank_position INTEGER NOT NULL,
    url TEXT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    title TEXT,
    description TEXT,
    serp_features JSONB,
    snapshot_date DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_keyword_snapshot ON serp_snapshots(keyword_id, snapshot_date);

-- API credentials table
CREATE TABLE api_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    credentials_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_verified_at TIMESTAMP
);

CREATE UNIQUE INDEX idx_user_provider ON api_credentials(user_id, provider);

-- API usage logs table
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_provider VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    cost NUMERIC(10, 4) NOT NULL,
    request_payload JSONB,
    response_status INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_created ON api_usage_logs(user_id, created_at);
```

---

## Step 2: Set Up Vercel Project

### 2.1 Connect Git Repository

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/dashboard
3. Click **"Add New..."** → **"Project"**
4. Import your Git repository
5. Vercel will auto-detect the framework

### 2.2 Configure Build Settings

**Framework Preset:** Other

**Root Directory:** Leave as `./` (root)

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Output Directory:**
```
frontend/dist
```

**Install Command:**
```bash
npm install
```

### 2.3 Set Environment Variables

In Vercel project settings, add these environment variables:

#### Required Environment Variables

```bash
# Database (from Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres

# Redis (Upstash free tier recommended for Vercel)
REDIS_URL=redis://default:[PASSWORD]@[HOST]:6379

# Security (generate strong random strings)
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
ENCRYPTION_KEY=your-encryption-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200

# App Config
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
DEBUG=False

# CORS
ALLOWED_ORIGINS=https://your-app.vercel.app
```

#### How to Generate Secure Keys

**On macOS/Linux:**
```bash
# SECRET_KEY
openssl rand -base64 32

# ENCRYPTION_KEY
openssl rand -base64 32
```

**On Windows (PowerShell):**
```powershell
# Generate random string
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

---

## Step 3: Set Up Redis (for Celery Background Jobs)

### Option A: Upstash Redis (Free Tier - Recommended for Vercel)

1. Go to https://console.upstash.com/
2. Create account
3. Click **Create Database**
4. Choose **Global** (free tier)
5. Copy **Redis URL** from dashboard
6. Add to Vercel environment variables as `REDIS_URL`

### Option B: Redis Labs

1. Go to https://redis.com/try-free/
2. Create free account
3. Create database
4. Get connection string
5. Add to Vercel

---

## Step 4: Deploy Backend API

### 4.1 Create `api/index.py` for Vercel

Vercel needs the FastAPI app in a specific location:

```bash
mkdir -p api
```

Create `api/index.py`:

```python
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from app.main import app

# Vercel serverless function handler
def handler(request):
    return app(request)
```

### 4.2 Create `requirements.txt` in Root

```bash
cp backend/requirements.txt ./requirements.txt
```

---

## Step 5: Configure Celery for Vercel

**Important:** Vercel doesn't support long-running processes like Celery workers.

### Options:

**Option A: Use Vercel Cron Jobs (Recommended)**

Create `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-rank-check",
      "schedule": "0 2 * * *"
    }
  ]
}
```

Then create endpoint in `backend/app/routers/cron.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/cron", tags=["cron"])

@router.get("/daily-rank-check")
async def daily_rank_check():
    # Trigger rank checks
    # This runs as HTTP request, not background job
    pass
```

**Option B: Use External Service**

- Deploy Celery worker to Railway.app or Heroku (free tier)
- Point to same Supabase database
- Use Upstash Redis

---

## Step 6: Deploy

1. Push code to Git repository:
   ```bash
   git add -A
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. Vercel will auto-deploy on push

3. Check deployment logs in Vercel dashboard

4. Visit your deployed URL!

---

## Step 7: Post-Deployment Checks

### Test the API

```bash
# Health check
curl https://your-app.vercel.app/health

# API docs
open https://your-app.vercel.app/api/docs
```

### Test the Frontend

1. Open https://your-app.vercel.app
2. Register account
3. Create project
4. Add keyword
5. Set up DataForSEO API credentials

---

## Troubleshooting

### Database Connection Errors

- Verify DATABASE_URL is correct
- Check Supabase database is running
- Ensure password has no special URL characters (or URL-encode them)

### Import Errors

- Make sure all dependencies are in `requirements.txt`
- Check Python version (Vercel uses 3.9 by default)

### Build Failures

- Check Vercel build logs
- Ensure `frontend/dist` is created during build
- Verify all environment variables are set

### CORS Issues

- Add your Vercel URL to `ALLOWED_ORIGINS`
- Check CORS middleware in `backend/app/main.py`

---

## Cost Breakdown

### Free Tier Limits

**Vercel (Free):**
- 100 GB bandwidth/month
- Unlimited deployments
- Serverless functions (100 GB-hours/month)

**Supabase (Free):**
- 500 MB database
- Unlimited API requests
- 1 GB file storage
- 50,000 monthly active users

**Upstash Redis (Free):**
- 10,000 commands/day
- 256 MB storage

**Total:** $0/month for free tiers!

### Paid Tiers (if you scale)

**Vercel Pro:** $20/month
**Supabase Pro:** $25/month
**Upstash Pay-as-you-go:** ~$0.20 per 100K commands

---

## Production Best Practices

1. **Environment Variables:** Never commit secrets to Git
2. **Database Backups:** Enable Supabase automated backups
3. **Monitoring:** Use Vercel Analytics + Sentry for error tracking
4. **Rate Limiting:** Implement rate limiting on API endpoints
5. **HTTPS Only:** Vercel provides this automatically
6. **CDN:** Vercel's Edge Network handles this

---

## Alternative: Railway Deployment

If you need Celery workers, consider Railway.app:

1. Railway supports background workers
2. Connect to same Supabase database
3. Deploy FastAPI + Celery worker + Beat scheduler
4. Point Vercel frontend to Railway backend

---

## Need Help?

- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Upstash Docs: https://docs.upstash.com/

---

**You're Ready!** Your SEO Dashboard is now live on Vercel with Supabase! 🚀
