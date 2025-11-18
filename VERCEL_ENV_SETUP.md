# Vercel Environment Variables Setup

## Required Environment Variables

To deploy this application to Vercel, you need to set the following environment variables in your Vercel project dashboard.

### Generated Secrets (Use These)

```
SECRET_KEY=2992a9f9fa61e7995318be53b654e7cc0619fd2698d6d73c7a4fc68f1fb18c5f
ENCRYPTION_KEY=24c11cd8bf76608e64a6fae81c6ccd45a89919a7a399f1c3b9209149041603e4
```

### Supabase Configuration

You need to get your DATABASE_URL from Supabase:

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Select your project (gunwutdhoepjsfdmjmkv)
3. Go to **Settings** → **Database**
4. Under **Connection string** select **Transaction pooler** or **Session pooler**
5. Copy the connection string and set it as `DATABASE_URL`

The format should be:
```
DATABASE_URL=postgresql://postgres.gunwutdhoepjsfdmjmkv:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### All Environment Variables to Set in Vercel

Go to your Vercel project → Settings → Environment Variables and add these:

```env
# Environment
ENVIRONMENT=production

# Supabase
SUPABASE_URL=https://gunwutdhoepjsfdmjmkv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1bnd1dGRob2VwanNmZG1qbWt2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNzg0MzYsImV4cCI6MjA3Nzg1NDQzNn0.NZgG-54WNU3bZiJiptjbodp2WxbbHVmGOaG1q74z_nI

# Database (Get this from Supabase Dashboard → Settings → Database → Connection pooler)
DATABASE_URL=postgresql://postgres.gunwutdhoepjsfdmjmkv:[YOUR-DB-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Redis (Optional - can use free tier from Upstash)
REDIS_URL=redis://localhost:6379/0

# Authentication
SECRET_KEY=2992a9f9fa61e7995318be53b654e7cc0619fd2698d6d73c7a4fc68f1fb18c5f
ENCRYPTION_KEY=24c11cd8bf76608e64a6fae81c6ccd45a89919a7a399f1c3b9209149041603e4
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200

# DataForSEO API
DATAFORSEO_LOGIN=connor@provinesconsulting.com
DATAFORSEO_PASSWORD=ca4cc25b9f8a16e6

# Frontend URL (Update after first deployment)
FRONTEND_URL=https://your-app-name.vercel.app
CORS_ORIGINS=https://your-app-name.vercel.app

# Backend URL (Update after deployment)
BACKEND_URL=https://your-app-name.vercel.app
```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Import your GitHub repository: `connorprovines-code/seo-dashboard-build`
3. Configure the project:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Build Command: Leave default
   - Output Directory: Leave default
4. Add all environment variables listed above
5. Click **Deploy**
6. After deployment, update `FRONTEND_URL` and `CORS_ORIGINS` with your actual Vercel URL

### Option 2: Deploy via CLI

```bash
# Make sure you're in the project directory
cd seo-dashboard-build

# Deploy to production
vercel --prod

# Set environment variables (run these one by one)
vercel env add ENVIRONMENT production production
vercel env add SUPABASE_URL production
# ... add all other env vars
```

## Post-Deployment

1. Get your Vercel deployment URL (e.g., `https://seo-dashboard-build.vercel.app`)
2. Update these environment variables in Vercel dashboard:
   - `FRONTEND_URL` → Your Vercel URL
   - `CORS_ORIGINS` → Your Vercel URL
   - `BACKEND_URL` → Your Vercel URL
3. Redeploy the application

## Troubleshooting

### Database Connection Issues

If you get database connection errors:
1. Verify your DATABASE_URL is correct
2. Make sure you're using the **pooler** connection string (port 6543), not the direct connection (port 5432)
3. Ensure your database password is correct

### CORS Errors

If you get CORS errors:
1. Make sure `CORS_ORIGINS` includes your Vercel deployment URL
2. Redeploy after updating environment variables
