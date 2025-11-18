# API Keys Guide - SEO Dashboard

This guide lists all the external APIs needed for the SEO Dashboard and how to obtain your API keys. The platform follows a **progressive onboarding** approach - you only need to provide API keys when you use features that require them.

---

## 📊 Required APIs by Feature

### Phase 1: Core SEO Features

#### 1. DataForSEO API ⭐ **REQUIRED for Keyword Research & Rank Tracking**

**What it's used for:**
- Keyword research (search volume, difficulty, CPC, competition)
- Rank tracking and SERP analysis
- Competitor keyword analysis

**Cost:** Pay-as-you-go
- Keyword research: $0.07 per 1,000 keywords
- Rank tracking: $0.002 per live check OR $0.0006 per standard check
- First-time signup: $1 free credit

**How to get your API key:**

1. **Sign up:** Go to https://app.dataforseo.com/register
2. **Verify email:** Check your inbox and verify your account
3. **Get API credentials:**
   - Log in to DataForSEO dashboard
   - Navigate to **Dashboard** → **API Access**
   - Copy your **Login (email)** and **Password** (not your account password!)
4. **Add to SEO Dashboard:**
   - In your SEO Dashboard, try to add a keyword or enable rank tracking
   - When prompted, enter your DataForSEO Login and Password
   - The system will test and encrypt your credentials

**API Documentation:** https://docs.dataforseo.com/v3/

**Endpoints used:**
- `/v3/dataforseo_labs/google/bulk_keyword_difficulty/live` - Keyword metrics
- `/v3/serp/google/organic/live/advanced` - Rank tracking

---

#### 2. Google Search Console API ⭐ **FREE - Recommended**

**What it's used for:**
- Free rank tracking data (no DataForSEO cost)
- Historical search performance
- Clicks, impressions, CTR, average position
- Top performing pages and queries

**Cost:** **FREE!** (Google's official API)

**How to connect:**

1. **Verify site ownership:**
   - Go to https://search.google.com/search-console
   - Add and verify your website

2. **Connect in SEO Dashboard:**
   - Go to your project settings
   - Click "Connect Google Search Console"
   - Authorize the OAuth connection
   - Select which Search Console property to connect

**Why use this:**
- Get **free** ranking data directly from Google
- See actual search performance metrics
- No API costs for rank tracking
- Historical data going back 16 months

**API Documentation:** https://developers.google.com/webmaster-tools

---

### Phase 3: AI Assistant Features

#### 3. Anthropic Claude API (Optional)

**What it's used for:**
- AI-powered content analysis
- Keyword research suggestions
- Content optimization recommendations
- Automated reporting
- Competitor analysis insights

**Cost:** Pay-per-use
- Claude 3.5 Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
- Typical SEO query: $0.003 - $0.01 per interaction

**How to get your API key:**

1. **Sign up:** Go to https://console.anthropic.com/
2. **Create account:** Use your email or Google account
3. **Get API key:**
   - Navigate to **Settings** → **API Keys**
   - Click **Create Key**
   - Copy your API key (starts with `sk-ant-`)
   - Store it securely (you can't view it again!)
4. **Add to SEO Dashboard:**
   - Go to Settings → API Credentials
   - Select "Anthropic Claude"
   - Paste your API key
   - System will validate and encrypt it

**API Documentation:** https://docs.anthropic.com/

**Note:** In self-hosted deployments, admins may provide a shared Claude API key for all users.

---

### Phase 4: Email Outreach (Optional)

#### 4. SendGrid API (Optional)

**What it's used for:**
- Automated outreach emails
- Link building campaigns
- Prospect contact management

**Cost:**
- Free tier: 100 emails/day
- Essentials: $19.95/month for 50,000 emails

**How to get your API key:**

1. **Sign up:** https://signup.sendgrid.com/
2. **Verify account:** Complete email verification
3. **Create API key:**
   - Go to **Settings** → **API Keys**
   - Click **Create API Key**
   - Name it (e.g., "SEO Dashboard")
   - Select **Full Access** or **Mail Send** permissions
   - Copy the API key
4. **Add to SEO Dashboard:**
   - Go to Settings → Integrations
   - Select "Email Provider"
   - Enter SendGrid API key

**API Documentation:** https://docs.sendgrid.com/

**Alternative:** You can also use SMTP directly without SendGrid.

---

## 🔐 Security & Best Practices

### How Your API Keys Are Stored

1. **Encrypted at rest:** All API credentials are encrypted using AES-256 before being stored in the database
2. **User-scoped:** Each user's API keys are stored separately and cannot be accessed by other users
3. **Never logged:** API keys are never written to application logs
4. **Secure transmission:** All API calls use HTTPS/TLS encryption

### Best Practices

✅ **DO:**
- Use API keys with minimal required permissions
- Monitor your API usage in each provider's dashboard
- Set up billing alerts on API provider dashboards
- Rotate API keys periodically (every 90 days recommended)
- Use different API keys for development and production

❌ **DON'T:**
- Share your API keys with anyone
- Commit API keys to version control
- Use the same API key across multiple applications
- Ignore billing alerts from API providers

---

## 💰 Cost Estimation

### Typical Monthly Costs for Small Blog (Example)

**Scenario:** Blog with 50 keywords tracked daily

- **DataForSEO Rank Tracking:**
  - 50 keywords × 30 days × $0.0006 = **$0.90/month**

- **DataForSEO Keyword Research:**
  - Adding 50 new keywords/month × $0.00007 = **$0.004/month**
  - Refreshing metrics monthly: 50 × $0.00007 = **$0.004/month**

- **Google Search Console:**
  - **$0/month** (free!)

- **Claude AI (if used):**
  - 10 AI queries/day × $0.005 × 30 = **$1.50/month**

**Total:** ~$2.50/month (or $1/month without AI)

### Typical Monthly Costs for Agency (100 clients)

**Scenario:** Managing 100 client sites, 100 keywords each

- **DataForSEO Rank Tracking:**
  - 10,000 keywords × 30 days × $0.0006 = **$180/month**

- **DataForSEO Keyword Research:**
  - 1,000 new keywords/month × $0.00007 = **$0.07/month**

- **Google Search Console:**
  - **$0/month** (free!)

- **Claude AI:**
  - 100 queries/day × $0.005 × 30 = **$15/month**

**Total:** ~$195/month

---

## 🚀 Getting Started Checklist

Use this checklist to set up your SEO Dashboard:

### Minimum Required (Free Start)
- [ ] Create account on SEO Dashboard
- [ ] Create your first project
- [ ] Add keywords manually (no API needed yet)
- [ ] Connect Google Search Console (free rank data)

### To Enable DataForSEO Features
- [ ] Sign up for DataForSEO ($1 free credit)
- [ ] Get API login and password
- [ ] Add credentials in SEO Dashboard
- [ ] Refresh keyword data (search volume, difficulty, CPC)
- [ ] Enable rank tracking for keywords

### To Enable AI Assistant (Optional)
- [ ] Sign up for Anthropic Claude
- [ ] Get API key
- [ ] Add to SEO Dashboard Settings
- [ ] Start using AI-powered recommendations

### To Enable Email Outreach (Optional)
- [ ] Sign up for SendGrid (or use SMTP)
- [ ] Get API key
- [ ] Add to SEO Dashboard
- [ ] Configure email templates

---

## 📖 API Provider Dashboards

Quick links to check your usage and billing:

- **DataForSEO Dashboard:** https://app.dataforseo.com/
- **Google Search Console:** https://search.google.com/search-console
- **Anthropic Console:** https://console.anthropic.com/
- **SendGrid Dashboard:** https://app.sendgrid.com/

---

## ❓ FAQ

### Do I need all these API keys to use the SEO Dashboard?

No! The only **required** API is DataForSEO, and even that is only needed when you want to:
- Get keyword metrics (search volume, difficulty, CPC)
- Track rankings via DataForSEO

You can use Google Search Console for **free rank tracking** without any DataForSEO costs.

### Can I use the dashboard without any API keys?

Yes! You can:
- Create projects and add keywords
- Manually enter data
- Use the dashboard for organization
- Connect Google Search Console (free)

But you won't be able to:
- Auto-fetch keyword metrics
- Automatically track rankings (unless GSC connected)
- Use AI features

### What happens if I run out of DataForSEO credits?

- Existing data remains visible
- You can't fetch new keyword data or rank checks
- Add more credits to your DataForSEO account
- Or connect Google Search Console for free rank tracking

### Is my API key data safe?

Yes! All API credentials are:
- Encrypted with AES-256 before storage
- Never visible in the UI after setup
- Scoped per-user (other users can't see your keys)
- Never logged or exposed in errors

### Can I change or remove API keys later?

Yes! Go to Settings → API Credentials to:
- View which APIs are connected
- Update credentials
- Remove API access
- Test connection

---

## 🆘 Support

Having trouble with API setup?

1. **Check API provider status pages:**
   - DataForSEO: https://status.dataforseo.com/
   - Google: https://www.google.com/appsstatus
   - Anthropic: https://status.anthropic.com/

2. **Verify credentials are correct:**
   - Use the "Test Connection" button in SEO Dashboard
   - Check for typos in API keys
   - Ensure API keys have required permissions

3. **Check billing:**
   - Ensure you have credits/active subscription
   - Review API provider's billing dashboard

4. **Contact support:**
   - SEO Dashboard: support@yourdomain.com
   - DataForSEO: https://dataforseo.com/contact
   - Anthropic: https://support.anthropic.com/

---

## 📝 Summary

**To get started immediately (free):**
1. Create a project
2. Connect Google Search Console
3. Start tracking keywords for free!

**To unlock full features:**
1. Sign up for DataForSEO ($1 free credit)
2. Add keywords and enable rank tracking
3. Monitor costs in DataForSEO dashboard

**For AI-powered insights:**
1. Get Anthropic Claude API key
2. Enable AI assistant features
3. Get content recommendations

That's it! You're ready to dominate search rankings! 🚀
