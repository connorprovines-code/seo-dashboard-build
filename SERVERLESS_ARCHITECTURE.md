# Serverless Architecture Changes for Vercel

This document explains how the original architecture was adapted for serverless deployment on Vercel.

## Key Architectural Changes

### 1. Background Tasks: Celery → Vercel Cron Jobs

**Original Architecture:**
```
Celery Workers + Redis Queue
- Long-running background processes
- Persistent workers
- Complex task scheduling
```

**Serverless Architecture:**
```
Vercel Cron Jobs + Upstash QStash
- Scheduled HTTP endpoints
- Stateless function invocations
- Simple cron expressions
```

#### Migration Strategy

**Before (Celery):**
```python
@celery.task
def check_keyword_rank(keyword_id):
    # Check rank for keyword
    pass

@celery.task
def daily_rank_check_job():
    # Runs daily at 2 AM
    keywords = get_all_tracked_keywords()
    for keyword in keywords:
        check_keyword_rank.delay(keyword.id)
```

**After (Vercel Cron):**
```python
# In vercel.json
{
  "crons": [
    {
      "path": "/api/cron/daily-rank-check",
      "schedule": "0 2 * * *"
    }
  ]
}

# In app/routers/cron.py
@router.post("/cron/daily-rank-check")
async def daily_rank_check(authorization: str = Header(None)):
    # Verify cron secret
    verify_cron_authorization(authorization)

    # Get all tracked keywords
    keywords = await get_all_tracked_keywords()

    # For large batches, use Upstash QStash
    for keyword in keywords:
        await qstash.publish_json({
            "url": f"{os.getenv('FRONTEND_URL')}/api/jobs/rank-check",
            "body": {"keyword_id": str(keyword.id)},
        })

    return {"status": "success", "queued": len(keywords)}
```

### 2. Database Connections: Connection Pool → NullPool

**Original Architecture:**
```python
# Traditional connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
)
```

**Serverless Architecture:**
```python
# No connection pooling for serverless
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Each function gets fresh connection
    pool_pre_ping=True,  # Verify connection before use
)
```

**Why?** Serverless functions are stateless. Connection pools can't persist between invocations.

### 3. Caching: In-Memory → Redis

**Original Architecture:**
```python
# In-memory caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_data(key):
    return expensive_operation(key)
```

**Serverless Architecture:**
```python
# Redis caching (Upstash)
import redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def get_cached_data(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    result = expensive_operation(key)
    redis_client.setex(key, 3600, json.dumps(result))
    return result
```

**Why?** In-memory caches are lost between function invocations.

### 4. Long-Running Tasks: Split into Smaller Functions

**Challenge:** Vercel has a 60-second timeout (10s on Hobby plan).

**Solution:** Break long tasks into smaller chunks.

**Before:**
```python
async def analyze_all_competitors():
    # This might take 5 minutes
    for competitor in all_competitors:
        analyze_backlinks(competitor)  # 30 seconds each
        analyze_keywords(competitor)   # 30 seconds each
```

**After:**
```python
async def queue_competitor_analysis():
    # Queue individual tasks
    for competitor in all_competitors:
        await qstash.publish_json({
            "url": f"{base_url}/api/jobs/analyze-competitor",
            "body": {"competitor_id": str(competitor.id)}
        })

async def analyze_single_competitor(competitor_id):
    # Each function handles one competitor (< 60s)
    competitor = get_competitor(competitor_id)
    analyze_backlinks(competitor)
    analyze_keywords(competitor)
```

### 5. File Storage: Local Files → Object Storage

**Original Architecture:**
```python
# Store CSV exports locally
export_path = f"/tmp/exports/{user_id}_{timestamp}.csv"
df.to_csv(export_path)
return FileResponse(export_path)
```

**Serverless Architecture:**
```python
# Use Vercel Blob or S3
from vercel_blob import put

csv_data = df.to_csv(index=False)
blob = await put(
    f"exports/{user_id}_{timestamp}.csv",
    csv_data,
    content_type="text/csv"
)

return {"download_url": blob.url}
```

**Why?** Serverless functions have ephemeral filesystems.

### 6. Environment Variables: .env → Vercel Dashboard

**Original:**
```bash
# .env file
DATABASE_URL=postgresql://localhost/seo_dashboard
```

**Serverless:**
- Set in Vercel Dashboard → Settings → Environment Variables
- Available as `os.getenv("DATABASE_URL")`
- Separate values for Production/Preview/Development

## Performance Optimizations

### 1. Cold Starts

**Problem:** First request after idle period is slow (1-3 seconds).

**Solutions:**
1. **Keep functions warm:**
   ```python
   # Add a warmup cron
   {
     "crons": [
       {
         "path": "/api/warmup",
         "schedule": "*/5 * * * *"  # Every 5 minutes
       }
     ]
   }
   ```

2. **Edge Functions for critical paths:**
   ```javascript
   // Use Vercel Edge Runtime for instant responses
   export const config = { runtime: 'edge' }

   export default async function handler(req) {
     return new Response('Fast!', { status: 200 })
   }
   ```

### 2. Database Query Optimization

**Use connection pooling proxy:**
```python
# Use Neon's serverless driver
from neon_serverless import connect

conn = await connect(os.getenv("DATABASE_URL"))
```

**Or use PgBouncer:**
```
DATABASE_URL=postgresql://user:pass@pooler.neon.tech/db?sslmode=require
```

### 3. Batch API Requests

**Before:**
```python
# 100 separate API calls
for keyword in keywords:
    data = await dataforseo_client.get_keyword_data(keyword)
```

**After:**
```python
# 1 batch API call
keywords_batch = [k.text for k in keywords]
data = await dataforseo_client.get_bulk_keyword_data(keywords_batch)
```

## Monitoring & Debugging

### 1. Vercel Analytics

Enable in Vercel Dashboard:
- Request count
- Response times
- Error rates
- Cold start frequency

### 2. Structured Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "rank_check_completed",
    keyword_id=keyword_id,
    position=5,
    duration_ms=234,
    cold_start=is_cold_start
)
```

Logs are automatically collected by Vercel.

### 3. Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    traces_sample_rate=0.1,  # 10% of requests
)
```

## Migration Checklist

If migrating from traditional deployment:

- [ ] Replace Celery tasks with Vercel Cron or Upstash QStash
- [ ] Change database connection pooling to NullPool
- [ ] Move in-memory caches to Redis (Upstash)
- [ ] Split long-running tasks into smaller functions
- [ ] Move file storage to Vercel Blob or S3
- [ ] Set environment variables in Vercel Dashboard
- [ ] Update OAuth redirect URIs to Vercel domain
- [ ] Test cold start performance
- [ ] Set up monitoring (Sentry, Vercel Analytics)
- [ ] Configure cron jobs for background tasks
- [ ] Test function timeouts (60s limit)

## Cost Comparison

### Traditional VPS Deployment

| Component | Cost/month |
|-----------|------------|
| VPS (2GB RAM) | $12 |
| PostgreSQL | Included |
| Redis | Included |
| Celery Workers | Included |
| **Total** | **$12** |

### Serverless Vercel Deployment

| Component | Cost/month |
|-----------|------------|
| Vercel Pro | $20 |
| Neon Database (Free) | $0 |
| Upstash Redis (Free) | $0 |
| Upstash QStash (Free) | $0 |
| **Total** | **$20** |

**OR with free tiers:**

| Component | Cost/month |
|-----------|------------|
| Vercel Hobby | $0 |
| Neon Database (Free) | $0 |
| Upstash Redis (Free) | $0 |
| **Total** | **$0** |

## Limitations of Serverless

### What You Can't Do

1. **WebSockets**: Not supported on Vercel (use Pusher or Ably instead)
2. **Long-running tasks > 60s**: Must be split into smaller tasks
3. **Stateful services**: Use external state (Redis, Database)
4. **Large uploads**: Use Vercel Blob with client-side uploads
5. **Cron jobs < 1 minute**: Minimum is 1 minute intervals

### Workarounds

1. **Real-time features**: Use Vercel Edge Functions + SSE (Server-Sent Events)
2. **Large data processing**: Use Upstash QStash to chain smaller tasks
3. **File processing**: Upload to Vercel Blob, process asynchronously
4. **High-frequency cron**: Use external service (e.g., Pipedream)

## Best Practices

### 1. Optimize for Cold Starts

```python
# Import only what you need
# BAD
import pandas as pd  # Heavy import

# GOOD
from pandas import DataFrame  # Lighter
```

### 2. Use Edge Caching

```python
@app.get("/api/projects/{id}/stats")
async def get_stats(id: str, response: Response):
    # Cache at CDN edge for 5 minutes
    response.headers["Cache-Control"] = "public, s-maxage=300"
    return stats
```

### 3. Batch Operations

```python
# Process multiple items in one function call
async def process_batch(items: List[Item]):
    # Process up to 100 items in one go
    results = await asyncio.gather(*[
        process_item(item) for item in items[:100]
    ])
    return results
```

### 4. Use Database Transactions Wisely

```python
# Keep transactions short
async with db.begin():
    # Fast operations only
    db.add(record)
    # Don't call external APIs inside transactions
```

## Conclusion

The serverless architecture requires some adjustments but offers:

✅ **Zero infrastructure management**
✅ **Automatic scaling**
✅ **Pay-per-use pricing**
✅ **Global edge network**
✅ **Built-in SSL/CDN**
✅ **Preview deployments**

Perfect for:
- Side projects
- MVPs
- Low-to-medium traffic applications
- Teams without DevOps resources

Not ideal for:
- High-traffic applications (> 1M requests/month)
- Real-time applications (WebSockets)
- Heavy data processing
- Applications requiring state between requests

For the SEO Dashboard use case, serverless is **excellent** because:
- Most operations are async (rank checks, API calls)
- Traffic is moderate and predictable
- Background tasks can be scheduled
- No need for real-time features
