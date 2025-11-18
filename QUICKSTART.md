# Quick Start Guide - Vercel Deployment

Get your SEO Dashboard deployed to Vercel in under 20 minutes!

## Prerequisites Checklist

- [ ] GitHub account
- [ ] Vercel account (free at https://vercel.com)
- [ ] Supabase account (free at https://supabase.com)

## 4-Step Deployment

### Step 1: Set Up Supabase Database (5 minutes)

1. Go to https://supabase.com
2. Click "Start your project"
3. Create a new project:
   - Name: `seo-dashboard`
   - Database Password: (choose a strong password)
   - Region: Choose closest to your users
4. Wait ~2 minutes for database to provision
5. Go to **SQL Editor** in left sidebar
6. Copy the SQL from `backend/database/schema.sql` in your repo
7. Paste it into the SQL editor and click **Run**
8. Go to **Project Settings** → **API**
9. Copy these values:
   - **Project URL** (looks like: `https://xxx.supabase.co`)
   - **Anon/Public Key** (long JWT token)

**That's it!** No connection strings, no passwords needed for deployment.

### Step 2: Get DataForSEO API Keys (5 minutes)

1. Go to https://app.dataforseo.com/register
2. Sign up (you get $1 free credit)
3. Go to Dashboard → API Access
4. Copy your **Login** (email) and **Password**

### Step 3: Deploy to Vercel (8 minutes)

#### 3.1: Push to GitHub

```bash
# If not already pushed
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

#### 3.2: Import to Vercel

1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repository
4. Vercel will auto-detect settings from `vercel.json`
5. **Don't deploy yet!** Click "Environment Variables"

#### 3.3: Add Environment Variables

Add these variables in Vercel:

```bash
# Supabase (from Step 1)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUz... (your anon key)

# DataForSEO (from Step 2)
DATAFORSEO_LOGIN=your-email@example.com
DATAFORSEO_PASSWORD=your_password

# Security (generate this)
SECRET_KEY=[run: openssl rand -hex 32]

# App Config
ENVIRONMENT=production
FRONTEND_URL=https://your-app-name.vercel.app
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200
CORS_ORIGINS=https://your-app-name.vercel.app
```

**To generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

#### 3.4: Deploy!

1. Click **Deploy**
2. Wait 2-3 minutes
3. Your app will be live at `https://your-app-name.vercel.app`

### Step 4: Test Your Deployment (2 minutes)

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

## Optional: Add Redis Cache

For better performance (optional, recommended for production):

1. Go to https://console.upstash.com
2. Sign up (free)
3. Create a Redis database: `seo-cache`
4. Copy the Redis URL
5. Add to Vercel environment variables:
   ```
   REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379
   ```
6. Redeploy

## Optional: Google Search Console

For free ranking data from your own sites:

1. Go to https://console.cloud.google.com/
2. Create a new project: `seo-dashboard`
3. Enable "Google Search Console API"
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URI: `https://your-app.vercel.app/api/auth/google/callback`
5. Add to Vercel environment variables:
   ```
   GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=xxx
   GOOGLE_REDIRECT_URI=https://your-app.vercel.app/api/auth/google/callback
   ```
6. Redeploy

## Custom Domain (Optional)

1. Go to Vercel Project Settings → Domains
2. Add your domain: `dashboard.yourdomain.com`
3. Update DNS records as instructed
4. SSL certificate is automatic!

## Troubleshooting

### Database connection failed

- Go to Supabase dashboard → SQL Editor
- Run: `SELECT * FROM users LIMIT 1;`
- If it works, your database is fine
- Check your `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Vercel

### API endpoint returns 500

- Check Vercel logs: `vercel logs --follow`
- Make sure all environment variables are set
- Redeploy after changing environment variables

### DataForSEO not working

- Verify your credentials at https://app.dataforseo.com/
- Make sure you have credits remaining
- Check `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` are correct

## Cost Breakdown

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Vercel | Hobby | $0 |
| Supabase | Free Tier | $0 |
| DataForSEO | Pay-per-use | ~$5-20 |
| **Total** | | **$5-20/month** |

**vs. Ahrefs**: $129/month → **Save $109-124/month!**

## What's Next?

1. **Build the frontend** - React app to interact with the API
2. **Create user accounts** - Use `/api/auth/register`
3. **Add your first project** - Track a website
4. **Import keywords** - Start tracking rankings
5. **Set up cron jobs** - Automated daily rank checks

## Support

- Full docs: See `VERCEL_DEPLOYMENT.md`
- Supabase help: https://supabase.com/docs
- DataForSEO docs: https://docs.dataforseo.com/
- Issues: Create a GitHub issue

---

**Congratulations! Your SEO Dashboard is now live! 🎉**

Total setup time: ~20 minutes
Monthly cost: $5-20 (vs Ahrefs $129/month)
