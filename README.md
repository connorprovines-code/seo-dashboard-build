# DIY SEO Dashboard - Complete Build Profile

## 🚀 Quick Deploy to Vercel

This project is now fully configured for **serverless deployment on Vercel**!

**Get started in 30 minutes:**
1. Read the [Quick Start Guide](QUICKSTART.md)
2. Follow the [Vercel Deployment Guide](VERCEL_DEPLOYMENT.md)
3. Learn about [Serverless Architecture](SERVERLESS_ARCHITECTURE.md)

**Total Cost:** $0-20/month (vs. Ahrefs $129/month)

---

## Project Overview

Build a comprehensive, self-hosted SEO dashboard that replaces expensive tools like Ahrefs and Semrush with a pay-per-use API model. This system will provide keyword research, rank tracking, competitor analysis, and automated backlink outreach capabilities at a fraction of the cost (~$20/month vs $129+/month).

**Now available for both:**
- ✅ **Vercel Serverless** (recommended for most users)
- ✅ **Traditional VPS** (Docker + PostgreSQL + Redis + Celery)

---

## Core Philosophy

- **Project-based architecture**: Each website/domain is a separate project with isolated data
- **Snapshot-based data storage**: Query APIs on-demand, store results locally, refresh when needed
- **Pay-per-use economics**: Only pay for data you actually need
- **Multi-source data aggregation**: Combine Google Search Console (free) with DataForSEO APIs (cheap)
- **Own your data**: All historical data stored locally in your database
- **Modular architecture**: Build in phases, each module independent and testable
- **Progressive API onboarding**: System guides users through API setup when features are first accessed

---

## User Flow: Project-Based Workflow

```
1. User registers/logs in
   └─> Lands on dashboard (empty state if first time)

2. User clicks "Create New Project"
   └─> Modal: "What website do you want to track?"
       ├─> Input: Domain (e.g., "example.com")
       ├─> Input: Project Name (e.g., "My Blog")
       └─> Creates project → Redirects to project dashboard

3. Project Dashboard (per-project view)
   ├─> Tab: Overview (metrics summary)
   ├─> Tab: Keywords (manage keyword list)
   ├─> Tab: Rankings (track positions over time)
   ├─> Tab: Competitors (add competitors to monitor)
   ├─> Tab: AI Assistant (chat with Claude)
   └─> Tab: Settings (API keys, integrations)

4. When user first accesses a feature requiring API:
   └─> Shows modal: "This feature needs [API Name]"
       ├─> Explains what it does
       ├─> Shows cost estimate
       ├─> Link to get API key
       └─> Input field to paste API key

5. All data scoped to project_id
   └─> Switch projects via dropdown in header
```

**Key UX Principle:** Users can create unlimited projects (one per website they manage), and each project has its own keywords, rankings, competitors, and settings. Think of it like Google Analytics properties or Ahrefs projects.

---

## Tech Stack

### Backend
- **Python 3.10+** with FastAPI (async support for API calls)
- **SQLAlchemy** for ORM
- **PostgreSQL** for production (SQLite for development)
- **Celery** for background task processing
- **Redis** for task queue and caching

### Frontend
- **React** with TypeScript
- **TailwindCSS** for styling
- **Recharts** or **Chart.js** for data visualization
- **TanStack Query** for API state management

### APIs & Integrations
- **Google Search Console API** (free - your site's actual data)
- **DataForSEO Labs API** (keyword research, search volume, difficulty)
- **DataForSEO SERP API** (rank tracking, competitor analysis)
- **DataForSEO Backlinks API** (Phase 2 - backlink analysis)

### DevOps
- **Docker** & **Docker Compose** for containerization
- **GitHub Actions** for CI/CD
- **Nginx** as reverse proxy
- Environment-based configuration (.env files)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Dashboard, Reports, Keyword Research, Rank Tracking UI)   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Auth Module │  │ Keyword API  │  │  Rank API    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Competitor API│  │ Backlink API │  │ Outreach API │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Celery    │ │ PostgreSQL  │ │    Redis    │
    │Worker Queue │ │  Database   │ │   Cache     │
    └─────────────┘ └─────────────┘ └─────────────┘
            │
            │ API Calls
            ▼
┌─────────────────────────────────────────────────────────────┐
│                  External APIs                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Google Search │  │  DataForSEO  │  │  DataForSEO  │     │
│  │Console API   │  │   Labs API   │  │   SERP API   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Tables Overview

#### `users`
- `id` (UUID, primary key)
- `email` (string, unique)
- `password_hash` (string)
- `created_at` (timestamp)
- `api_credits_remaining` (decimal)

#### `projects`
- `id` (UUID, primary key)
- `user_id` (foreign key → users)
- `name` (string)
- `domain` (string)
- `gsc_connected` (boolean)
- `gsc_refresh_token` (encrypted string)
- `created_at` (timestamp)

#### `keywords`
- `id` (UUID, primary key)
- `project_id` (foreign key → projects)
- `keyword_text` (string)
- `search_volume` (integer, nullable)
- `keyword_difficulty` (integer, nullable)
- `cpc` (decimal, nullable)
- `competition` (decimal, nullable)
- `last_refreshed_at` (timestamp, nullable)
- `created_at` (timestamp)
- Index: `(project_id, keyword_text)`

#### `rank_tracking`
- `id` (UUID, primary key)
- `keyword_id` (foreign key → keywords)
- `project_id` (foreign key → projects)
- `tracked_url` (string)
- `rank_position` (integer, nullable)
- `search_engine` (enum: 'google', 'bing')
- `location_code` (integer) // DataForSEO location code
- `language_code` (string)
- `checked_at` (timestamp)
- Index: `(keyword_id, checked_at)`

#### `competitor_domains`
- `id` (UUID, primary key)
- `project_id` (foreign key → projects)
- `domain` (string)
- `notes` (text, nullable)
- `created_at` (timestamp)

#### `serp_snapshots`
- `id` (UUID, primary key)
- `keyword_id` (foreign key → keywords)
- `rank_position` (integer)
- `url` (string)
- `domain` (string)
- `title` (text)
- `description` (text)
- `serp_features` (JSONB) // featured_snippet, people_also_ask, etc.
- `snapshot_date` (date)
- Index: `(keyword_id, snapshot_date)`

#### `backlinks` (Phase 2)
- `id` (UUID, primary key)
- `project_id` (foreign key → projects)
- `source_domain` (string)
- `source_url` (text)
- `target_url` (text)
- `anchor_text` (text, nullable)
- `domain_rank` (integer, nullable)
- `first_seen` (timestamp)
- `last_checked` (timestamp)
- `is_active` (boolean)

#### `outreach_prospects` (Phase 2)
- `id` (UUID, primary key)
- `project_id` (foreign key → projects)
- `domain` (string)
- `domain_authority` (integer, nullable)
- `contact_email` (string, nullable)
- `contact_name` (string, nullable)
- `outreach_status` (enum: 'prospect', 'contacted', 'replied', 'placed', 'rejected')
- `last_contacted_at` (timestamp, nullable)
- `notes` (text, nullable)
- `created_at` (timestamp)

#### `api_usage_logs`
- `id` (UUID, primary key)
- `user_id` (foreign key → users)
- `api_provider` (string) // 'dataforseo', 'google'
- `endpoint` (string)
- `cost` (decimal)
- `request_payload` (JSONB, nullable)
- `response_status` (integer)
- `created_at` (timestamp)
- Index: `(user_id, created_at)`

#### `api_credentials` (NEW - Store per-user API keys)
- `id` (UUID, primary key)
- `user_id` (foreign key → users)
- `provider` (string) // 'dataforseo', 'google', 'anthropic'
- `credentials_encrypted` (text) // JSON blob with login/password or tokens
- `is_active` (boolean)
- `created_at` (timestamp)
- `last_verified_at` (timestamp, nullable)
- Unique index: `(user_id, provider)`

---

## API Setup & Onboarding Flow

### Progressive Disclosure Pattern

The system should **NOT** ask for all API keys upfront. Instead, prompt users when they first use a feature:

```
User clicks "Add Keywords" → System checks if DataForSEO credentials exist
  ├─> If YES: Proceed with keyword research
  └─> If NO: Show "Setup DataForSEO API" modal
      ├─> Explain: "To get keyword data, we use DataForSEO API"
      ├─> Cost: "~$0.07 per 1,000 keywords"
      ├─> Steps to get API key:
      │   1. Go to https://dataforseo.com/apis
      │   2. Sign up (they offer $1 free trial)
      │   3. Copy your Login and Password from dashboard
      ├─> Input fields:
      │   - DataForSEO Login: [_____________]
      │   - DataForSEO Password: [_____________]
      │   - [ ] Save for all my projects
      └─> Button: "Test & Save Credentials"
          └─> Backend: Test API call → Encrypt → Store in api_credentials
```

### API Credentials Flow by Feature

| Feature | Required API | When to Ask | Fallback |
|---------|-------------|-------------|----------|
| **Create Project** | None | N/A | N/A |
| **Add Keywords** | DataForSEO Labs API | First time clicking "Research Keywords" | Can add keywords manually without volume data |
| **Rank Tracking** | DataForSEO SERP API | When enabling rank tracking for first keyword | N/A |
| **Google Search Console** | Google OAuth | When clicking "Connect GSC" button | Optional feature |
| **AI Assistant** | Anthropic Claude API | When first opening AI chat | Can be admin-provided (not user) |
| **Backlinks** | DataForSEO Backlinks API | When accessing Backlinks tab | N/A |

### Implementation: API Setup Modal Component

```typescript
// frontend/src/components/APISetupModal.tsx
interface APISetupModalProps {
  provider: 'dataforseo' | 'google' | 'anthropic'
  feature: string // "keyword research", "rank tracking", etc.
  onComplete: () => void
}

export function APISetupModal({ provider, feature, onComplete }: APISetupModalProps) {
  const apiInfo = {
    dataforseo: {
      name: "DataForSEO",
      cost: "$0.07 per 1,000 keywords",
      signupUrl: "https://app.dataforseo.com/register",
      docsUrl: "https://docs.dataforseo.com/v3/",
      fields: [
        { name: "login", label: "Login/Email", type: "text" },
        { name: "password", label: "API Password", type: "password" }
      ],
      instructions: [
        "Go to https://app.dataforseo.com/register",
        "Sign up (get $1 free credits)",
        "Go to Dashboard > API Access",
        "Copy your Login and Password"
      ]
    },
    google: {
      name: "Google Search Console",
      cost: "Free!",
      signupUrl: "https://search.google.com/search-console",
      docsUrl: "https://developers.google.com/webmaster-tools",
      fields: [], // OAuth flow, no manual input
      instructions: [
        "Click 'Connect with Google' below",
        "Authorize access to your Search Console data",
        "Select which site to connect"
      ]
    },
    anthropic: {
      name: "Claude AI (Anthropic)",
      cost: "~$0.003 per message",
      signupUrl: "https://console.anthropic.com/",
      docsUrl: "https://docs.anthropic.com/",
      fields: [
        { name: "api_key", label: "API Key", type: "password" }
      ],
      instructions: [
        "Go to https://console.anthropic.com/",
        "Sign up for an account",
        "Get API key from Settings > API Keys",
        "Note: This may be admin-provided in self-hosted setups"
      ]
    }
  }

  const info = apiInfo[provider]

  return (
    <Modal title={`Setup ${info.name} API`}>
      <div className="space-y-4">
        <div className="bg-blue-50 p-4 rounded">
          <p className="font-semibold">Why do we need this?</p>
          <p className="text-sm">To use {feature}, we need access to {info.name}.</p>
          <p className="text-sm font-bold mt-2">Cost: {info.cost}</p>
        </div>

        <div className="space-y-2">
          <p className="font-semibold">How to get your API key:</p>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            {info.instructions.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
          <a href={info.signupUrl} target="_blank" className="text-blue-600 text-sm">
            → Open {info.name} signup page
          </a>
        </div>

        <form onSubmit={handleSubmit}>
          {info.fields.map(field => (
            <div key={field.name} className="mb-3">
              <label className="block text-sm font-medium mb-1">
                {field.label}
              </label>
              <input
                type={field.type}
                name={field.name}
                className="w-full p-2 border rounded"
                required
              />
            </div>
          ))}

          <div className="flex items-center mb-4">
            <input type="checkbox" id="saveForAll" className="mr-2" />
            <label htmlFor="saveForAll" className="text-sm">
              Save credentials for all my projects
            </label>
          </div>

          <div className="flex gap-3">
            <button type="submit" className="btn-primary">
              Test & Save Credentials
            </button>
            <button type="button" onClick={onSkip} className="btn-secondary">
              Skip for Now
            </button>
          </div>
        </form>

        <div className="text-xs text-gray-500">
          🔒 Your API credentials are encrypted and never shared. You can update or remove them anytime from Settings.
        </div>
      </div>
    </Modal>
  )
}
```

### Backend: API Credentials Management

```python
# backend/app/routers/api_credentials.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.encryption import encrypt_data, decrypt_data
from app.services.api_validators import test_dataforseo_credentials, test_google_oauth

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

@router.post("/setup/{provider}")
async def setup_api_credentials(
    provider: str,
    credentials: dict,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Store and test API credentials for a provider.
    Credentials are encrypted before storage.
    """

    # Validate provider
    valid_providers = ["dataforseo", "google", "anthropic"]
    if provider not in valid_providers:
        raise HTTPException(400, f"Invalid provider. Must be one of: {valid_providers}")

    # Test credentials first
    try:
        if provider == "dataforseo":
            test_result = await test_dataforseo_credentials(
                credentials.get("login"),
                credentials.get("password")
            )
        elif provider == "google":
            test_result = await test_google_oauth(credentials.get("access_token"))
        elif provider == "anthropic":
            test_result = await test_anthropic_key(credentials.get("api_key"))

        if not test_result["success"]:
            raise HTTPException(400, f"Invalid credentials: {test_result['error']}")

    except Exception as e:
        raise HTTPException(400, f"Failed to validate credentials: {str(e)}")

    # Encrypt credentials
    encrypted = encrypt_data(json.dumps(credentials))

    # Store in database (upsert)
    cred_record = db.query(ApiCredential)\
        .filter(ApiCredential.user_id == user_id, ApiCredential.provider == provider)\
        .first()

    if cred_record:
        cred_record.credentials_encrypted = encrypted
        cred_record.is_active = True
        cred_record.last_verified_at = datetime.now()
    else:
        cred_record = ApiCredential(
            user_id=user_id,
            provider=provider,
            credentials_encrypted=encrypted,
            is_active=True,
            last_verified_at=datetime.now()
        )
        db.add(cred_record)

    db.commit()

    return {
        "success": True,
        "provider": provider,
        "message": f"{provider} credentials saved successfully"
    }

@router.get("/check/{provider}")
async def check_credentials_exist(
    provider: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check if user has credentials for a provider.
    Used by frontend to determine if setup modal should show.
    """
    cred = db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == user_id,
            ApiCredential.provider == provider,
            ApiCredential.is_active == True
        )\
        .first()

    return {
        "exists": cred is not None,
        "provider": provider,
        "last_verified": cred.last_verified_at if cred else None
    }

@router.delete("/{provider}")
async def remove_credentials(
    provider: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove stored API credentials"""
    db.query(ApiCredential)\
        .filter(ApiCredential.user_id == user_id, ApiCredential.provider == provider)\
        .update({"is_active": False})

    db.commit()

    return {"success": True, "message": f"{provider} credentials removed"}
```

### Frontend: Hook for API Check

```typescript
// frontend/src/hooks/useAPICredentials.ts
export function useAPICredentials(provider: 'dataforseo' | 'google' | 'anthropic') {
  const [showSetup, setShowSetup] = useState(false)

  const { data: credCheck } = useQuery({
    queryKey: ['api-credentials', provider],
    queryFn: () => api.get(`/credentials/check/${provider}`)
  })

  const requireCredentials = (callback: () => void) => {
    if (credCheck?.exists) {
      callback() // Credentials exist, proceed
    } else {
      setShowSetup(true) // Show setup modal
    }
  }

  return {
    hasCredentials: credCheck?.exists,
    showSetup,
    setShowSetup,
    requireCredentials
  }
}

// Usage in a component:
function KeywordResearchButton() {
  const { hasCredentials, showSetup, setShowSetup, requireCredentials } =
    useAPICredentials('dataforseo')

  const handleClick = () => {
    requireCredentials(() => {
      // This only runs if credentials exist
      openKeywordResearchModal()
    })
  }

  return (
    <>
      <button onClick={handleClick}>Research Keywords</button>

      {showSetup && (
        <APISetupModal
          provider="dataforseo"
          feature="keyword research"
          onComplete={() => {
            setShowSetup(false)
            openKeywordResearchModal()
          }}
        />
      )}
    </>
  )
}
```

---

## Phase 1: MVP Core Features

### 1.1 Authentication & Project Setup

**User Stories:**
- As a user, I can register an account with email/password
- As a user, I can log in and receive a JWT token
- As a user, I can create multiple projects (each representing a website to track)
- As a user, I can connect my Google Search Console account to a project

**Technical Requirements:**
- Implement JWT-based authentication
- Password hashing with bcrypt
- OAuth 2.0 flow for Google Search Console
- Store refresh tokens securely (encrypted at rest)

**API Endpoints:**
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
GET    /api/auth/me

POST   /api/projects
GET    /api/projects
GET    /api/projects/:id
PUT    /api/projects/:id
DELETE /api/projects/:id

GET    /api/projects/:id/gsc/auth-url
POST   /api/projects/:id/gsc/connect (callback with code)
DELETE /api/projects/:id/gsc/disconnect
```

### 1.2 Keyword Research Module

**User Stories:**
- As a user, I can enter a keyword and get search volume, difficulty, CPC, competition
- As a user, I can bulk import keywords (CSV or text input)
- As a user, I can see keyword data cached from previous queries
- As a user, I can manually refresh keyword data
- As a user, I can see the cost of each API query before executing

**Technical Requirements:**
- Integrate DataForSEO Labs API
- Implement keyword data caching (check if data exists and is < 30 days old)
- Batch API requests (DataForSEO allows 1,000 keywords per request)
- Calculate and display API cost estimates
- Store historical keyword data with timestamps

**DataForSEO Integration:**
```python
# Endpoint: /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
# Cost: $0.07 per 1,000 keywords
# Returns: search_volume, keyword_difficulty, cpc, competition

# Example request:
POST https://api.dataforseo.com/v3/dataforseo_labs/google/bulk_keyword_difficulty/live
{
  "keywords": ["seo tools", "keyword research", ...],
  "location_code": 2840,  # USA
  "language_code": "en"
}
```

**API Endpoints:**
```
POST   /api/projects/:id/keywords              # Add single keyword
POST   /api/projects/:id/keywords/bulk         # Bulk import
GET    /api/projects/:id/keywords              # List all keywords
GET    /api/projects/:id/keywords/:keywordId   # Get keyword details
PUT    /api/projects/:id/keywords/:keywordId/refresh  # Force refresh data
DELETE /api/projects/:id/keywords/:keywordId   # Delete keyword
GET    /api/projects/:id/keywords/cost-estimate # Estimate API cost
```

**Frontend Components:**
- KeywordResearchForm (single keyword input)
- KeywordBulkImport (CSV upload or textarea)
- KeywordTable (sortable, filterable table)
- KeywordDetailModal (historical data charts)
- CostEstimator (shows cost before API call)

### 1.3 Rank Tracking Module

**User Stories:**
- As a user, I can enable rank tracking for any keyword
- As a user, I can specify the URL I want to track
- As a user, I can set location and language for rank checks
- As a user, I can see daily rank position history
- As a user, I can see current SERP results (top 100)
- As a user, I can schedule automated daily rank checks
- As a user, I can see my actual Google Search Console rankings for free

**Technical Requirements:**
- Integrate DataForSEO SERP API for rank tracking
- Integrate Google Search Console API for actual ranking data
- Celery scheduled tasks for daily checks
- Store full SERP snapshots (top 100 results)
- Calculate rank changes (day-over-day, week-over-week)
- Handle rank fluctuations and not-found cases

**DataForSEO Integration:**
```python
# Endpoint: /v3/serp/google/organic/live/advanced
# Cost: $0.002 per search (real-time) or $0.0006 (standard queue)
# Returns: top 100 organic results with positions

POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced
{
  "keyword": "seo tools",
  "location_code": 2840,
  "language_code": "en",
  "depth": 100
}
```

**Google Search Console Integration:**
```python
# Free API - get actual ranking data for YOUR site
# searchanalytics.query endpoint
POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query
{
  "startDate": "2025-01-01",
  "endDate": "2025-01-10",
  "dimensions": ["query", "page"],
  "rowLimit": 25000
}
# Returns: clicks, impressions, ctr, position for each query
```

**API Endpoints:**
```
POST   /api/projects/:id/rank-tracking                    # Enable tracking for keyword
GET    /api/projects/:id/rank-tracking                    # List all tracked keywords
GET    /api/projects/:id/rank-tracking/:keywordId/history # Historical rank data
GET    /api/projects/:id/rank-tracking/:keywordId/serp    # Latest SERP snapshot
DELETE /api/projects/:id/rank-tracking/:keywordId         # Stop tracking
POST   /api/projects/:id/rank-tracking/sync-gsc           # Sync GSC data

# Admin/Celery endpoints
POST   /api/admin/rank-tracking/check-all   # Trigger all rank checks
POST   /api/admin/rank-tracking/sync-gsc-all # Sync all GSC projects
```

**Celery Tasks:**
```python
@celery.task
def check_keyword_rank(keyword_id):
    # Fetch rank from DataForSEO
    # Store in rank_tracking and serp_snapshots tables
    # Calculate rank changes
    # Trigger notifications if significant change

@celery.task
def daily_rank_check_job():
    # Runs daily at 2 AM
    # Gets all tracked keywords
    # Queues individual check tasks

@celery.task
def sync_gsc_data(project_id):
    # Pulls last 7 days of GSC data
    # Stores in rank_tracking table with source='gsc'
```

**Frontend Components:**
- RankTrackingTable (current ranks, changes, sparklines)
- RankHistoryChart (line chart showing position over time)
- SerpViewer (visual SERP with your position highlighted)
- TrackingSettings (location, language, schedule config)

### 1.4 Dashboard & Visualization

**User Stories:**
- As a user, I see an overview dashboard when I log in
- As a user, I can see key metrics: tracked keywords, avg position, biggest movers
- As a user, I can filter data by date range
- As a user, I can export data to CSV
- As a user, I can see my API usage and costs

**Frontend Components:**
- DashboardOverview (key metrics cards)
- RankDistributionChart (pie chart: positions 1-3, 4-10, 11-20, 21+)
- KeywordMoversTable (biggest gainers/losers)
- ApiUsageTracker (monthly spend, per-API breakdown)
- DateRangePicker (filter all data)

**API Endpoints:**
```
GET /api/projects/:id/dashboard/overview
GET /api/projects/:id/dashboard/movers?period=7d
GET /api/projects/:id/api-usage?start_date=&end_date=
GET /api/projects/:id/export/csv?type=keywords|ranks
```

---

## Phase 2: Competitor Analysis & Intelligence

### 2.1 Competitor Rank Tracking

**User Stories:**
- As a user, I can add competitor domains to my project
- As a user, I can see competitor rankings for my tracked keywords
- As a user, I can compare my ranks vs competitors side-by-side
- As a user, I can identify keywords where competitors rank but I don't

**Technical Requirements:**
- Store competitor domains per project
- Parse SERP snapshots to identify competitor positions
- Calculate "rank gap" (competitor ranks, you don't)
- Visualize competitive landscape

**API Endpoints:**
```
POST   /api/projects/:id/competitors
GET    /api/projects/:id/competitors
DELETE /api/projects/:id/competitors/:competitorId
GET    /api/projects/:id/competitors/:competitorId/ranks
GET    /api/projects/:id/competitors/comparison?keyword_id=
GET    /api/projects/:id/competitors/opportunities  # Keywords they rank for, you don't
```

**Frontend Components:**
- CompetitorManager (add/remove competitors)
- CompetitorRankTable (side-by-side comparison)
- OpportunityFinder (gap analysis)

### 2.2 SERP Feature Analysis

**User Stories:**
- As a user, I can see which keywords trigger featured snippets
- As a user, I can see "People Also Ask" questions
- As a user, I can identify keywords with video/image results
- As a user, I can track SERP feature ownership (who owns the snippet)

**Technical Requirements:**
- Parse SERP features from DataForSEO responses
- Store in `serp_snapshots.serp_features` (JSONB)
- Identify opportunities (featured snippet available, no current owner)

**API Endpoints:**
```
GET /api/projects/:id/serp-features?type=featured_snippet
GET /api/projects/:id/serp-features/opportunities
```

---

## Phase 3: AI Assistant Integration

### 3.1 Claude AI Chat Assistant

**User Stories:**
- As a user, I can chat with an AI assistant that has access to my SEO data
- As a user, I can ask questions like "Which keywords are declining?" or "Find opportunities in my niche"
- As a user, I can ask the AI to perform actions like "Add these 10 keywords" or "Email my top 5 backlink prospects"
- As a user, I can give the AI access to my email to send outreach emails on my behalf
- As a user, the AI can suggest and execute API connector changes

**Technical Requirements:**
- Integrate Anthropic Claude API (claude-3-5-sonnet or claude-3-opus)
- Give Claude access to PostgreSQL via function calling/tool use
- Implement email integration (Gmail API or IMAP/SMTP)
- Create secure permission system for AI actions
- Implement conversation history and context management

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface (Frontend)                 │
│  User: "Which of my keywords dropped the most this week?"   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Assistant Service                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Claude API Integration                  │   │
│  │  - Conversation management                           │   │
│  │  - Context building from user's data                 │   │
│  │  - Tool/Function calling                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │                     │                        │
│              ▼                     ▼                        │
│  ┌────────────────────┐  ┌────────────────────┐           │
│  │   Database Tools   │  │    Action Tools    │           │
│  │  - Query keywords  │  │  - Send emails     │           │
│  │  - Get rank data   │  │  - Add keywords    │           │
│  │  - Analyze trends  │  │  - Update configs  │           │
│  └────────────────────┘  └────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
                            ▼
                ┌──────────────────────┐
                │   PostgreSQL + IMAP  │
                │   User's Email       │
                └──────────────────────┘
```

**Claude Tools/Functions:**

```python
# Tool 1: Query SEO Database
{
    "name": "query_seo_data",
    "description": "Query the user's SEO database for keywords, rankings, competitors, etc.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query_type": {
                "type": "string",
                "enum": ["keywords", "rankings", "competitors", "trends", "opportunities"],
                "description": "Type of data to query"
            },
            "filters": {
                "type": "object",
                "description": "Filters like date_range, project_id, min_volume, etc."
            },
            "sort_by": {"type": "string"},
            "limit": {"type": "integer"}
        },
        "required": ["query_type"]
    }
}

# Tool 2: Execute SEO Action
{
    "name": "execute_seo_action",
    "description": "Perform actions like adding keywords, starting rank checks, etc.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add_keywords", "start_rank_tracking", "refresh_keyword_data", "analyze_competitors"]
            },
            "parameters": {
                "type": "object",
                "description": "Action-specific parameters"
            }
        },
        "required": ["action", "parameters"]
    }
}

# Tool 3: Email Access (with user permission)
{
    "name": "send_outreach_email",
    "description": "Send an outreach email for backlink opportunities",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
            "prospect_id": {"type": "string", "description": "Link to prospect record"}
        },
        "required": ["to", "subject", "body"]
    }
}

# Tool 4: Data Analysis
{
    "name": "analyze_seo_trends",
    "description": "Perform statistical analysis on SEO data",
    "input_schema": {
        "type": "object",
        "properties": {
            "analysis_type": {
                "type": "string",
                "enum": ["rank_velocity", "keyword_cannibalization", "content_gaps", "competitor_movements"]
            },
            "project_id": {"type": "string"},
            "date_range": {"type": "object"}
        },
        "required": ["analysis_type", "project_id"]
    }
}

# Tool 5: Configure Integrations
{
    "name": "manage_api_connector",
    "description": "Add, remove, or configure API integrations",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "remove", "configure", "test"]
            },
            "connector_type": {
                "type": "string",
                "enum": ["email", "crm", "slack", "analytics", "third_party_api"]
            },
            "config": {
                "type": "object",
                "description": "Connector-specific configuration"
            }
        },
        "required": ["action", "connector_type"]
    }
}
```

**Database Schema Addition:**

```sql
-- New table for AI conversations
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    title TEXT,  -- Auto-generated from first message
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES ai_conversations(id),
    role VARCHAR(20),  -- 'user', 'assistant', 'system'
    content TEXT,
    tool_calls JSONB,  -- Store tool invocations
    tool_results JSONB,  -- Store tool outputs
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_permissions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    permission_type VARCHAR(50),  -- 'read_data', 'write_data', 'send_emails', 'manage_apis'
    granted BOOLEAN DEFAULT FALSE,
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE TABLE email_connections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    email_address VARCHAR(255),
    provider VARCHAR(50),  -- 'gmail', 'outlook', 'smtp'
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    connected_at TIMESTAMP,
    last_synced_at TIMESTAMP
);
```

**API Endpoints:**

```python
# Chat endpoints
POST   /api/ai/conversations                    # Start new conversation
GET    /api/ai/conversations                    # List conversations
GET    /api/ai/conversations/:id                # Get conversation history
POST   /api/ai/conversations/:id/messages       # Send message (streaming response)
DELETE /api/ai/conversations/:id                # Delete conversation

# Permission management
GET    /api/ai/permissions                      # Check current permissions
POST   /api/ai/permissions/grant                # Grant AI permission
POST   /api/ai/permissions/revoke               # Revoke AI permission

# Email integration
POST   /api/ai/email/connect                    # Start OAuth flow
GET    /api/ai/email/callback                   # OAuth callback
DELETE /api/ai/email/disconnect                 # Disconnect email
GET    /api/ai/email/status                     # Check connection status
```

**Implementation Example:**

```python
# backend/app/services/ai_assistant.py
import anthropic
from typing import AsyncIterator
import json

class AIAssistantService:
    def __init__(self, db_session, user_id, project_id):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.db = db_session
        self.user_id = user_id
        self.project_id = project_id

    async def chat_stream(
        self,
        message: str,
        conversation_id: str = None
    ) -> AsyncIterator[str]:
        """Stream AI responses with tool use"""

        # Build context from user's SEO data
        context = await self._build_context()

        # Get conversation history
        history = await self._get_conversation_history(conversation_id)

        # Define available tools
        tools = self._get_available_tools()

        # Stream response from Claude
        async with self.client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=f"""You are an SEO assistant with access to the user's SEO data.

            Current context:
            - Project: {context['project_name']}
            - Total keywords tracked: {context['keyword_count']}
            - Date range: {context['date_range']}

            You can:
            1. Query their SEO data (rankings, keywords, competitors)
            2. Analyze trends and provide insights
            3. Execute actions (add keywords, start tracking)
            4. Send outreach emails (if user granted permission)
            5. Manage API integrations

            Be concise, data-driven, and proactive in suggesting optimizations.""",
            messages=[
                *history,
                {"role": "user", "content": message}
            ],
            tools=tools
        ) as stream:
            async for text in stream.text_stream:
                yield text

            # Handle tool use
            final_message = await stream.get_final_message()

            if final_message.stop_reason == "tool_use":
                tool_results = await self._handle_tool_calls(
                    final_message.content
                )

                # Continue conversation with tool results
                async with self.client.messages.stream(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    messages=[
                        *history,
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": final_message.content},
                        {"role": "user", "content": tool_results}
                    ],
                    tools=tools
                ) as continuation:
                    async for text in continuation.text_stream:
                        yield text

    async def _handle_tool_calls(self, content: list) -> list:
        """Execute tool calls and return results"""
        results = []

        for block in content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Check permissions
                if not await self._check_permission(tool_name):
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "Permission denied. User must grant access."
                    })
                    continue

                # Execute tool
                if tool_name == "query_seo_data":
                    result = await self._query_seo_data(tool_input)
                elif tool_name == "execute_seo_action":
                    result = await self._execute_action(tool_input)
                elif tool_name == "send_outreach_email":
                    result = await self._send_email(tool_input)
                elif tool_name == "analyze_seo_trends":
                    result = await self._analyze_trends(tool_input)
                elif tool_name == "manage_api_connector":
                    result = await self._manage_connector(tool_input)

                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        return results

    async def _query_seo_data(self, params: dict):
        """Query PostgreSQL for SEO data"""
        query_type = params['query_type']
        filters = params.get('filters', {})

        if query_type == "keywords":
            keywords = await self.db.query(Keyword)\
                .filter(Keyword.project_id == self.project_id)\
                .limit(params.get('limit', 50))\
                .all()

            return {
                "count": len(keywords),
                "keywords": [
                    {
                        "text": k.keyword_text,
                        "volume": k.search_volume,
                        "difficulty": k.keyword_difficulty,
                        "current_rank": k.latest_rank
                    }
                    for k in keywords
                ]
            }

        elif query_type == "trends":
            # SQL query for rank changes
            result = await self.db.execute("""
                SELECT
                    k.keyword_text,
                    AVG(CASE WHEN rt.checked_at >= NOW() - INTERVAL '7 days'
                        THEN rt.rank_position END) as current_avg,
                    AVG(CASE WHEN rt.checked_at >= NOW() - INTERVAL '14 days'
                        AND rt.checked_at < NOW() - INTERVAL '7 days'
                        THEN rt.rank_position END) as previous_avg
                FROM keywords k
                JOIN rank_tracking rt ON k.id = rt.keyword_id
                WHERE k.project_id = :project_id
                GROUP BY k.id
                HAVING COUNT(*) > 5
            """, {"project_id": self.project_id})

            trends = result.fetchall()

            return {
                "trending_up": [
                    {"keyword": t[0], "improvement": t[2] - t[1]}
                    for t in trends if t[2] and t[1] and t[2] - t[1] > 3
                ],
                "trending_down": [
                    {"keyword": t[0], "decline": t[1] - t[2]}
                    for t in trends if t[2] and t[1] and t[1] - t[2] > 3
                ]
            }

    async def _send_email(self, params: dict):
        """Send outreach email via user's connected email"""
        # Check if email is connected
        email_conn = await self.db.query(EmailConnection)\
            .filter(EmailConnection.user_id == self.user_id)\
            .first()

        if not email_conn:
            return {"error": "No email account connected"}

        # Use Gmail API or SMTP
        if email_conn.provider == "gmail":
            # Use Gmail API
            await self._send_via_gmail(
                email_conn,
                params['to'],
                params['subject'],
                params['body']
            )

        # Log outreach
        await self.db.execute("""
            UPDATE outreach_prospects
            SET outreach_status = 'contacted',
                last_contacted_at = NOW()
            WHERE id = :prospect_id
        """, {"prospect_id": params.get('prospect_id')})

        return {"success": True, "sent_at": "now"}
```

**Frontend Chat Component:**

```typescript
// frontend/src/components/AIChat.tsx
import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'

export function AIChat({ projectId }: { projectId: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = async (content: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content }])
    setIsStreaming(true)

    // Stream AI response
    const response = await fetch(`/api/ai/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let assistantMessage = ''

    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      assistantMessage += chunk

      // Update last message
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1].content = assistantMessage
        return newMessages
      })
    }

    setIsStreaming(false)
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-lg p-3 ${
              msg.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-900'
            }`}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t p-4">
        <form onSubmit={(e) => { e.preventDefault(); sendMessage(input); setInput('') }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your SEO data, or request an action..."
            className="w-full p-3 border rounded-lg"
            disabled={isStreaming}
          />
        </form>
      </div>
    </div>
  )
}
```

**Permission Management UI:**

```typescript
// frontend/src/components/AIPermissions.tsx
export function AIPermissions() {
  const permissions = [
    {
      id: 'read_data',
      title: 'Read SEO Data',
      description: 'Allow AI to query your keywords, rankings, and analytics',
      required: true
    },
    {
      id: 'write_data',
      title: 'Modify SEO Data',
      description: 'Allow AI to add keywords, update tracking, etc.',
      recommended: true
    },
    {
      id: 'send_emails',
      title: 'Send Emails',
      description: 'Allow AI to send outreach emails on your behalf',
      dangerous: true
    },
    {
      id: 'manage_apis',
      title: 'Manage Integrations',
      description: 'Allow AI to add/remove API connectors',
      dangerous: true
    }
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">AI Assistant Permissions</h2>
      {permissions.map(perm => (
        <div key={perm.id} className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">{perm.title}</h3>
              <p className="text-sm text-gray-600">{perm.description}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          {perm.dangerous && (
            <div className="mt-2 text-xs text-red-600">
              ⚠️ This permission allows significant actions. Use with caution.
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

**Example Conversations:**

```
User: "Which keywords dropped the most this week?"

AI: Let me check your ranking data...
[Uses query_seo_data tool]

Based on your data, here are the top 5 keywords that dropped:

1. "seo tools comparison" - dropped 8 positions (was #5, now #13)
2. "keyword research guide" - dropped 6 positions (was #12, now #18)
3. "backlink analysis" - dropped 5 positions (was #8, now #13)

The drops seem to correlate with a Google algorithm update on Jan 15th.
Would you like me to analyze your competitors' movements for these keywords?
```

```
User: "Find 10 high-authority sites in the 'digital marketing' niche and draft outreach emails"

AI: I'll search for high-authority prospects and draft personalized emails.
[Uses query_seo_data + DataForSEO APIs to find prospects]

Found 10 prospects with Domain Authority 50+:

1. neilpatel.com (DA: 91)
2. backlinko.com (DA: 89)
... [8 more]

I've drafted personalized emails for each. Here's an example for neilpatel.com:

---
Subject: Quick question about your digital marketing resources

Hi Neil,

I'm [Your Name] from [Your Site]. I recently published a comprehensive
guide on technical SEO that I think would be valuable for your audience...

[Rest of email]
---

Would you like me to send these? (Requires email permission)
```

```
User: "Add a Slack integration so you can notify me about rank changes"

AI: I can help set up a Slack integration. Here's what I'll need:
[Uses manage_api_connector tool with action='configure']

1. Your Slack webhook URL
2. Which events to notify:
   - Keywords entering top 10?
   - Drops of 5+ positions?
   - New ranking opportunities?

Once you provide the webhook, I can configure this immediately.
```

**Cost Considerations:**

- Claude API costs: ~$0.003 per message (Claude 3.5 Sonnet)
- Average conversation: 10 messages = $0.03
- Power user (100 conversations/month) = $3/month
- Still WAY cheaper than Ahrefs!

**Security:**

- All AI permissions require explicit user consent
- Email access tokens encrypted at rest
- Audit log of all AI actions
- User can revoke permissions anytime
- Rate limiting on AI requests (prevent abuse)

---

## Phase 4: Backlink Analysis & Outreach

### 3.1 Backlink Profile Analysis

**User Stories:**
- As a user, I can see my backlink profile (referring domains, total backlinks)
- As a user, I can see new/lost backlinks over time
- As a user, I can filter backlinks by domain authority, anchor text
- As a user, I can export backlink data

**Technical Requirements:**
- Integrate DataForSEO Backlinks API
- Store backlink data with timestamps
- Track status changes (new, lost, active)
- Calculate domain authority metrics

**DataForSEO Integration:**
```python
# Endpoint: /v3/backlinks/backlinks/live
# Cost: ~$0.01 per domain check
POST https://api.dataforseo.com/v3/backlinks/backlinks/live
{
  "target": "example.com",
  "mode": "as_is",
  "filters": ["dofollow", "=", true]
}
```

**API Endpoints:**
```
POST   /api/projects/:id/backlinks/analyze    # Trigger backlink crawl
GET    /api/projects/:id/backlinks             # List backlinks
GET    /api/projects/:id/backlinks/summary     # Overview stats
GET    /api/projects/:id/backlinks/new         # New backlinks (last 30 days)
GET    /api/projects/:id/backlinks/lost        # Lost backlinks
```

### 3.2 Prospect Discovery

**User Stories:**
- As a user, I can find high-authority domains in my niche
- As a user, I can see domains linking to competitors but not to me
- As a user, I can filter prospects by domain authority, relevance
- As a user, I can mark prospects as "contacted", "replied", etc.

**Technical Requirements:**
- Analyze competitor backlinks to find prospects
- Use DataForSEO domain metrics API for authority scores
- Scrape contact information (email, LinkedIn)
- Store outreach status and notes

**API Endpoints:**
```
POST   /api/projects/:id/prospects/discover       # Find prospects
GET    /api/projects/:id/prospects                # List prospects
PUT    /api/projects/:id/prospects/:id/status     # Update outreach status
GET    /api/projects/:id/prospects/competitor-backlinks  # Domains linking to competitors
```

### 3.3 Automated Outreach (Optional Advanced Feature)

**User Stories:**
- As a user, I can create email templates for outreach
- As a user, I can send personalized emails to prospects
- As a user, I can track email opens and replies
- As a user, I can set up automated follow-up sequences

**Technical Requirements:**
- Email template system with variables
- Integration with email API (SendGrid, AWS SES)
- Tracking pixels for open tracking
- Webhook handling for replies

**API Endpoints:**
```
POST   /api/projects/:id/outreach/templates
GET    /api/projects/:id/outreach/templates
POST   /api/projects/:id/outreach/campaigns
POST   /api/projects/:id/outreach/campaigns/:id/send
GET    /api/projects/:id/outreach/campaigns/:id/stats
```

---

## Development Workflow

### Setup Instructions

1. **Clone Repository:**
```bash
git clone <repo-url>
cd seo-dashboard
```

2. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
alembic upgrade head  # Run migrations
uvicorn main:app --reload
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend URL
npm run dev
```

4. **Docker Setup:**
```bash
docker-compose up -d
```

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql://user:pass@localhost:5432/seo_dashboard
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<generate-strong-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200

# DataForSEO
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password

# Google Search Console
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Email (optional - for outreach)
SENDGRID_API_KEY=your_key

# App Config
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SEO Dashboard
```

### Testing Strategy

**Backend Tests:**
```bash
pytest tests/
pytest tests/unit/  # Fast unit tests
pytest tests/integration/  # API integration tests
pytest --cov=app tests/  # With coverage
```

**Frontend Tests:**
```bash
npm run test
npm run test:e2e  # Playwright E2E tests
```

**Test Coverage Requirements:**
- Unit tests: 80%+ coverage
- Integration tests for all API endpoints
- E2E tests for critical user flows

---

## API Rate Limiting & Cost Management

### Built-in Cost Controls

**User Budget System:**
- Each user has `api_credits_remaining` balance
- Check balance before making paid API calls
- Deduct costs from balance after successful calls
- Prevent calls if balance insufficient

**Rate Limiting:**
```python
# FastAPI rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/keywords/bulk")
@limiter.limit("10/hour")  # Max 10 bulk imports per hour
async def bulk_import_keywords():
    pass
```

**Cost Estimation:**
```python
def estimate_cost(operation, params):
    costs = {
        'keyword_research': 0.00007,  # per keyword
        'rank_check_live': 0.002,      # per check
        'rank_check_standard': 0.0006,  # per check
        'backlink_analysis': 0.01       # per domain
    }
    return costs[operation] * params['count']
```

**API Usage Dashboard:**
- Show daily/monthly spend
- Break down by API provider and endpoint
- Alert when approaching budget limits

---

## Deployment Guide

### Docker Deployment

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/seo_dashboard
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/seo_dashboard
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery_beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/seo_dashboard
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=seo_dashboard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

### VPS Deployment (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx

# Clone repo
git clone <repo-url> /var/www/seo-dashboard
cd /var/www/seo-dashboard

# Setup environment
cp .env.example .env
nano .env  # Add production values

# Start services
docker-compose up -d

# Setup SSL
sudo certbot --nginx -d yourdomain.com

# Setup automated backups
sudo crontab -e
# Add: 0 2 * * * docker exec seo-dashboard-db pg_dump -U postgres seo_dashboard > /backups/db-$(date +\%Y\%m\%d).sql
```

---

## Security Considerations

### Authentication & Authorization
- JWT tokens with short expiration (refresh token pattern)
- Password hashing with bcrypt (cost factor 12+)
- Rate limiting on auth endpoints
- CORS configuration for production

### API Key Management
- Never commit API keys to git
- Encrypt DataForSEO credentials at rest
- Rotate keys periodically
- Use environment variables

### Data Protection
- Encrypt Google OAuth refresh tokens
- HTTPS only in production
- Input validation on all endpoints
- SQL injection prevention (use ORM)
- XSS protection in frontend

### Compliance
- GDPR: User data export and deletion
- Cookie consent banner
- Privacy policy and terms of service

---

## Monitoring & Logging

### Application Monitoring
```python
# Sentry for error tracking
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")

# Prometheus metrics
from prometheus_client import Counter, Histogram

api_request_count = Counter('api_requests_total', 'Total API requests')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')
```

### Logging Strategy
```python
import logging
import structlog

# Structured logging
logger = structlog.get_logger()
logger.info("rank_check_completed", keyword_id=keyword_id, position=5, duration_ms=234)
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    # Check database connection
    # Check Redis connection
    # Check Celery workers
    return {"status": "healthy", "checks": {...}}
```

---

## Performance Optimization

### Database Optimization
- Index frequently queried columns
- Use connection pooling
- Implement read replicas for analytics queries
- Archive old data (> 1 year) to separate tables

### Caching Strategy
```python
# Redis caching for expensive queries
@cache(ttl=3600)  # 1 hour
async def get_keyword_data(keyword_id):
    return await db.query(...)

# Cache keyword research results for 30 days
# Cache SERP results for 1 day
# Cache GSC data for 6 hours
```

### API Optimization
- Batch DataForSEO requests (1,000 keywords per call)
- Use DataForSEO standard queue (70% cheaper) for non-urgent checks
- Implement request deduplication
- Use async/await for parallel API calls

### Frontend Optimization
- Lazy load components
- Virtualized tables for large datasets
- Debounce search inputs
- Optimize bundle size (code splitting)

---

## Cost Analysis & ROI

### Monthly Cost Breakdown (Example Usage)

**Scenario: Small Agency (5 clients, 500 keywords tracked)**

| Service | Usage | Cost |
|---------|-------|------|
| DataForSEO - Keyword Research | 2,000 keywords/month | $0.14 |
| DataForSEO - Rank Tracking | 500 keywords × 30 days × $0.0006 | $9.00 |
| Google Search Console | Unlimited | $0.00 |
| VPS Hosting (DigitalOcean) | 2GB RAM, 1 CPU | $12.00 |
| **Total** | | **~$21.14/month** |

**vs. Ahrefs Lite:** $129/month
**Savings:** $107.86/month ($1,294/year)

**Scenario: Solo Entrepreneur (1 site, 100 keywords tracked)**

| Service | Usage | Cost |
|---------|-------|------|
| DataForSEO - Keyword Research | 500 keywords/month | $0.04 |
| DataForSEO - Rank Tracking | 100 keywords × 30 days × $0.0006 | $1.80 |
| Google Search Console | Unlimited | $0.00 |
| VPS Hosting (shared or free tier) | Vercel/Railway free tier | $0.00 |
| **Total** | | **~$1.84/month** |

**vs. Semrush Pro:** $139.95/month
**Savings:** $138.11/month ($1,657/year)

---

## Roadmap & Future Enhancements

### Phase 4: Advanced Features (Future)
- [ ] AI-powered content gap analysis
- [ ] Automatic meta description generator
- [ ] Internal linking suggestions
- [ ] Technical SEO audit (page speed, mobile-friendly)
- [ ] Integration with Google Analytics 4
- [ ] Multi-user team collaboration
- [ ] White-label reporting for agencies
- [ ] Zapier/Make.com integration
- [ ] Mobile app (React Native)

### Phase 5: Machine Learning (Future)
- [ ] Rank prediction models
- [ ] Anomaly detection for sudden rank drops
- [ ] Keyword clustering and topic modeling
- [ ] Competitor strategy analysis
- [ ] Automated A/B testing recommendations

---

## Getting Started (For Claude Code)

### Immediate Next Steps

1. **Initialize Project Structure:**
```
seo-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── core/
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/
└── README.md
```

2. **Backend Bootstrap:**
   - Setup FastAPI with basic project structure
   - Configure SQLAlchemy models (all tables from schema)
   - Setup Alembic migrations
   - Implement authentication (JWT)
   - Create health check endpoint

3. **Frontend Bootstrap:**
   - Setup React + TypeScript + Vite
   - Configure TailwindCSS
   - Create basic layout (navbar, sidebar, main content)
   - Setup React Router
   - Implement authentication flow (login/register)

4. **First Feature: Keyword Research Module**
   - Backend: Implement DataForSEO Labs API integration
   - Backend: Create keyword CRUD endpoints
   - Frontend: Build KeywordResearchForm component
   - Frontend: Build KeywordTable component
   - Test end-to-end flow

5. **Second Feature: Google Search Console Integration**
   - Backend: Implement OAuth flow
   - Backend: Create GSC data sync endpoint
   - Frontend: Build connection UI
   - Test with real GSC account

6. **Third Feature: Rank Tracking**
   - Backend: Implement DataForSEO SERP API
   - Backend: Setup Celery + Redis
   - Backend: Create scheduled rank check task
   - Frontend: Build rank tracking table and charts
   - Test automated daily checks

### Development Priorities

**Week 1-2:** Project setup, authentication, database schema
**Week 3-4:** Keyword research module (Phase 1.2)
**Week 5-6:** Google Search Console integration (Phase 1.1)
**Week 7-8:** Rank tracking basics (Phase 1.3)
**Week 9-10:** Dashboard and visualization (Phase 1.4)
**Week 11-12:** Testing, bug fixes, documentation
**Week 13+:** Phase 2 features (competitor analysis)

---

## Support & Resources

### DataForSEO Documentation
- API Docs: https://docs.dataforseo.com/v3/
- Python Client: https://github.com/dataforseo/PythonClient
- Pricing: https://dataforseo.com/pricing

### Google Search Console API
- API Reference: https://developers.google.com/webmaster-tools
- Python Client: https://github.com/googleapis/google-api-python-client
- OAuth Setup: https://developers.google.com/identity/protocols/oauth2

### Community Resources
- SEO API Slack Community
- DataForSEO Support: client@dataforseo.com
- FastAPI Discord
- r/SEO on Reddit

---

## Contributing Guidelines

### Code Style
- Python: Black formatter, flake8 linter, type hints
- TypeScript: ESLint + Prettier
- Commit messages: Conventional Commits format

### Pull Request Process
1. Create feature branch from `develop`
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
5. Submit PR with clear description

### Issue Reporting
- Use issue templates
- Include reproduction steps
- Attach logs/screenshots
- Label appropriately (bug, feature, enhancement)

---

## License

MIT License - feel free to use for personal or commercial projects

---

## Acknowledgments

- DataForSEO for affordable API access
- Google Search Console for free ranking data
- Open source community for amazing tools

---

**Built with ❤️ by someone who was tired of paying $129/month for SEO tools**

---

## Appendix A: DataForSEO API Reference

### Most Common Endpoints

```python
# 1. Keyword Research (Bulk)
POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
{
    "keywords": ["keyword1", "keyword2", ...],
    "location_code": 2840,
    "language_code": "en"
}
# Cost: $0.00007 per keyword
# Returns: search_volume, keyword_difficulty, cpc, competition

# 2. Rank Tracking
POST /v3/serp/google/organic/live/advanced
{
    "keyword": "your keyword",
    "location_code": 2840,
    "language_code": "en",
    "device": "desktop",
    "depth": 100
}
# Cost: $0.002 (live) or $0.0006 (standard)
# Returns: Top 100 organic results with full SERP data

# 3. Historical Search Volume
POST /v3/dataforseo_labs/google/historical_search_volume/live
{
    "keywords": ["keyword1", "keyword2"],
    "location_code": 2840,
    "language_code": "en"
}
# Returns: Monthly search volume for last 12 months

# 4. Backlink Analysis (Phase 2)
POST /v3/backlinks/backlinks/live
{
    "target": "example.com",
    "mode": "as_is"
}
# Cost: ~$0.01 per domain
# Returns: All backlinks pointing to domain

# 5. Domain Overview (Phase 2)
POST /v3/dataforseo_labs/google/domain_overview/live
{
    "target": "example.com",
    "location_code": 2840,
    "language_code": "en"
}
# Returns: Organic traffic estimate, keywords ranking, visibility
```

### Location Codes (Common)
```python
LOCATION_CODES = {
    'USA': 2840,
    'United Kingdom': 2826,
    'Canada': 2124,
    'Australia': 2036,
    'Germany': 2276,
    'France': 2250,
    'Spain': 2724,
    'Italy': 2380,
    'Netherlands': 2528,
    'New York': 1023191,
    'Los Angeles': 1023768,
    'Chicago': 1014044,
    'London': 1006886,
    'Sydney': 2036,
}
```

---

## Appendix B: Sample API Response Schemas

### Keyword Research Response
```json
{
  "tasks": [{
    "result": [{
      "keyword": "seo tools",
      "keyword_info": {
        "search_volume": 8100,
        "competition": 0.89,
        "cpc": 15.23
      },
      "keyword_properties": {
        "keyword_difficulty": 67
      },
      "serp_info": {
        "se_results_count": "1450000000"
      }
    }]
  }]
}
```

### Rank Tracking Response
```json
{
  "tasks": [{
    "result": [{
      "items": [
        {
          "type": "organic",
          "rank_group": 1,
          "rank_absolute": 1,
          "position": "left",
          "url": "https://example.com/page",
          "domain": "example.com",
          "title": "Page Title",
          "description": "Meta description...",
          "breadcrumb": "Home > Category > Page"
        },
        ...
      ],
      "se_results_count": "1450000000"
    }]
  }]
}
```

### Google Search Console Response
```json
{
  "rows": [
    {
      "keys": ["keyword query", "https://example.com/page"],
      "clicks": 45,
      "impressions": 1234,
      "ctr": 0.0365,
      "position": 5.2
    }
  ]
}
```

---

## Final Notes for Claude Code

This is a **production-ready specification**. Every feature is technically feasible with current APIs and technologies. The cost estimates are real (verified from DataForSEO's official pricing as of January 2025).

**Key Success Factors:**
1. Start with Phase 1 MVP - don't try to build everything at once
2. Test DataForSEO API integration early (they have a free $50 trial)
3. Google Search Console OAuth can be tricky - follow their docs carefully
4. Use Celery for background tasks from day 1 (don't build synchronous rank checks)
5. Cache aggressively - you're paying per API call

**Most Important: Ship Phase 1 fast**, then iterate based on real usage. The MVP (keyword research + rank tracking + GSC integration) is already 10x better than paying for Ahrefs if you only need basic features.

Good luck building! 🚀
