# Quick Start Guide - Vercel Deployment

Get your SEO Dashboard deployed to Vercel in under 30 minutes!

## Prerequisites Checklist

- [ ] GitHub account
- [ ] Vercel account (free at https://vercel.com)
- [ ] Credit card (for database, but free tiers available)

## 5-Step Deployment

### Step 1: Set Up Database (5 minutes)

**Option A: Neon.tech (Free Tier)**

1. Go to https://neon.tech
2. Sign up with GitHub
3. Click "Create Project"
4. Name it: `seo-dashboard`
5. Copy the connection string (looks like: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/...`)
6. Save it for Step 3

**Option B: Vercel Postgres ($20/month)**

1. Go to https://vercel.com/dashboard
2. Click "Storage" → "Create Database"
3. Select "Postgres"
4. Name it: `seo-dashboard`
5. Vercel will auto-set `DATABASE_URL` for you

### Step 2: Set Up Redis Cache (3 minutes)

1. Go to https://console.upstash.com
2. Sign up (free)
3. Click "Create Database"
4. Name it: `seo-cache`
5. Select a region close to your database
6. Copy the `UPSTASH_REDIS_REST_URL`
7. Save it for Step 3

### Step 3: Initialize Database (2 minutes)

Run this command with your database URL:

```bash
# Install PostgreSQL client (if not installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql-client

# Run the schema
psql "YOUR_DATABASE_URL_FROM_STEP_1" < backend/database/schema.sql
```

Or use the web SQL editor provided by Neon/Vercel Postgres.

### Step 4: Get API Keys (10 minutes)

#### DataForSEO (Required - for SEO data)

1. Go to https://app.dataforseo.com/register
2. Sign up (you get $1 free credit)
3. Go to Dashboard → API Access
4. Copy your **Login** and **Password**
5. Save them for Step 5

#### Google Search Console (Optional but recommended)

1. Go to https://console.cloud.google.com/
2. Create a new project: `seo-dashboard`
3. Enable "Google Search Console API"
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URI: `https://YOUR-APP.vercel.app/api/auth/google/callback`
5. Copy **Client ID** and **Client Secret**
6. Save them for Step 5

### Step 5: Deploy to Vercel (10 minutes)

#### 5.1: Push to GitHub

```bash
# Initialize git if not done
git init
git add .
git commit -m "Initial commit: SEO Dashboard for Vercel"

# Create GitHub repo and push
gh repo create seo-dashboard --public --source=. --remote=origin --push
# Or manually create on GitHub and push
```

#### 5.2: Import to Vercel

1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repository
4. Vercel will auto-detect settings from `vercel.json`
5. **Don't deploy yet!** Click "Environment Variables"

#### 5.3: Add Environment Variables

Add these variables in Vercel:

```
DATABASE_URL=postgresql://... (from Step 1)
REDIS_URL=rediss://... (from Step 2)
SECRET_KEY=[generate: openssl rand -hex 32]
DATAFORSEO_LOGIN=your_login (from Step 4)
DATAFORSEO_PASSWORD=your_password (from Step 4)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com (from Step 4)
GOOGLE_CLIENT_SECRET=xxx (from Step 4)
FRONTEND_URL=https://your-app-name.vercel.app
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200
ENVIRONMENT=production
```

Generate SECRET_KEY:
```bash
openssl rand -hex 32
```

#### 5.4: Deploy!

1. Click "Deploy"
2. Wait 2-3 minutes
3. Your app will be live at `https://your-app-name.vercel.app`

## Post-Deployment

### Test Your Deployment

1. Visit `https://your-app-name.vercel.app/api/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "timestamp": "2025-01-18T..."
   }
   ```

3. Visit `https://your-app-name.vercel.app/docs` to see the API documentation

### Set Up Background Jobs (Optional)

Create a cron job for daily rank tracking:

1. Add to `vercel.json`:
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

2. Generate a CRON_SECRET:
   ```bash
   openssl rand -hex 32
   ```

3. Add `CRON_SECRET` to Vercel environment variables

4. Redeploy

### Add Custom Domain (Optional)

1. Go to Vercel Project Settings → Domains
2. Add your domain: `dashboard.yourdomain.com`
3. Update DNS records as instructed
4. SSL certificate is automatic!

## Troubleshooting

### Database connection failed

```bash
# Test your connection string
psql "YOUR_DATABASE_URL" -c "SELECT 1"
```

If it fails:
- Check your IP is whitelisted (Neon/Vercel Postgres)
- Verify the connection string format
- Try adding `?sslmode=require` to the URL

### Deployment timeout

- Increase timeout in `vercel.json`:
  ```json
  {
    "functions": {
      "backend/app/main.py": {
        "maxDuration": 60
      }
    }
  }
  ```

### API keys not working

- Go to Vercel Dashboard → Settings → Environment Variables
- Click "Redeploy" after changing variables

## Next Steps

1. **Create a user account**: Use the `/api/auth/register` endpoint
2. **Create your first project**: Track your first website
3. **Add keywords**: Start tracking keyword rankings
4. **Connect Google Search Console**: Get free ranking data
5. **Set up monitoring**: Add Sentry for error tracking

## Cost Breakdown

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Vercel | Hobby | $0 |
| Neon Database | Free Tier | $0 |
| Upstash Redis | Free Tier | $0 |
| DataForSEO | Pay-per-use | ~$5-20 |
| **Total** | | **$5-20/month** |

**vs. Ahrefs**: $129/month → **Save $109-124/month!**

## Support

- Documentation: See `VERCEL_DEPLOYMENT.md`
- Issues: Create a GitHub issue
- Community: Join our Discord (link in README)

---

**Congratulations! Your SEO Dashboard is now live on Vercel! 🎉**

Visit your app and start tracking your SEO performance!
