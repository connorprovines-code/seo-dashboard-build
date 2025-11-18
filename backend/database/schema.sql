-- SEO Dashboard - PostgreSQL Schema for Vercel Deployment
-- This schema is optimized for serverless deployment on Vercel with Vercel Postgres/Neon/Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    api_credits_remaining DECIMAL(10, 2) DEFAULT 0.00
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- PROJECTS TABLE
-- ============================================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    gsc_connected BOOLEAN DEFAULT FALSE,
    gsc_refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_domain ON projects(domain);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- ============================================================================
-- KEYWORDS TABLE
-- ============================================================================
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    keyword_text VARCHAR(500) NOT NULL,
    search_volume INTEGER,
    keyword_difficulty INTEGER,
    cpc DECIMAL(10, 2),
    competition DECIMAL(5, 4),
    last_refreshed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_keywords_project_id ON keywords(project_id);
CREATE INDEX idx_keywords_keyword_text ON keywords(keyword_text);
CREATE INDEX idx_keywords_project_keyword ON keywords(project_id, keyword_text);
CREATE INDEX idx_keywords_search_volume ON keywords(search_volume DESC NULLS LAST);

-- ============================================================================
-- RANK TRACKING TABLE
-- ============================================================================
CREATE TYPE search_engine_type AS ENUM ('google', 'bing', 'yahoo');

CREATE TABLE rank_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tracked_url TEXT NOT NULL,
    rank_position INTEGER,
    search_engine search_engine_type DEFAULT 'google',
    location_code INTEGER NOT NULL,
    language_code VARCHAR(10) NOT NULL DEFAULT 'en',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_rank_tracking_keyword_id ON rank_tracking(keyword_id);
CREATE INDEX idx_rank_tracking_project_id ON rank_tracking(project_id);
CREATE INDEX idx_rank_tracking_checked_at ON rank_tracking(checked_at DESC);
CREATE INDEX idx_rank_tracking_keyword_checked ON rank_tracking(keyword_id, checked_at DESC);

-- ============================================================================
-- COMPETITOR DOMAINS TABLE
-- ============================================================================
CREATE TABLE competitor_domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_competitor_domains_project_id ON competitor_domains(project_id);
CREATE UNIQUE INDEX idx_competitor_domains_unique ON competitor_domains(project_id, domain);

-- ============================================================================
-- SERP SNAPSHOTS TABLE
-- ============================================================================
CREATE TABLE serp_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    rank_position INTEGER NOT NULL,
    url TEXT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    title TEXT,
    description TEXT,
    serp_features JSONB,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_serp_snapshots_keyword_id ON serp_snapshots(keyword_id);
CREATE INDEX idx_serp_snapshots_snapshot_date ON serp_snapshots(snapshot_date DESC);
CREATE INDEX idx_serp_snapshots_keyword_date ON serp_snapshots(keyword_id, snapshot_date DESC);
CREATE INDEX idx_serp_snapshots_domain ON serp_snapshots(domain);

-- GIN index for JSONB serp_features
CREATE INDEX idx_serp_snapshots_features ON serp_snapshots USING GIN (serp_features);

-- ============================================================================
-- BACKLINKS TABLE (Phase 2)
-- ============================================================================
CREATE TABLE backlinks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    source_domain VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    target_url TEXT NOT NULL,
    anchor_text TEXT,
    domain_rank INTEGER,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_backlinks_project_id ON backlinks(project_id);
CREATE INDEX idx_backlinks_source_domain ON backlinks(source_domain);
CREATE INDEX idx_backlinks_is_active ON backlinks(is_active);
CREATE INDEX idx_backlinks_first_seen ON backlinks(first_seen DESC);

-- ============================================================================
-- OUTREACH PROSPECTS TABLE (Phase 2)
-- ============================================================================
CREATE TYPE outreach_status_type AS ENUM ('prospect', 'contacted', 'replied', 'placed', 'rejected');

CREATE TABLE outreach_prospects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    domain_authority INTEGER,
    contact_email VARCHAR(255),
    contact_name VARCHAR(255),
    outreach_status outreach_status_type DEFAULT 'prospect',
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_outreach_prospects_project_id ON outreach_prospects(project_id);
CREATE INDEX idx_outreach_prospects_status ON outreach_prospects(outreach_status);
CREATE INDEX idx_outreach_prospects_domain ON outreach_prospects(domain);

-- ============================================================================
-- API USAGE LOGS TABLE
-- ============================================================================
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_provider VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    cost DECIMAL(10, 4) NOT NULL,
    request_payload JSONB,
    response_status INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_api_usage_logs_user_id ON api_usage_logs(user_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at DESC);
CREATE INDEX idx_api_usage_logs_user_created ON api_usage_logs(user_id, created_at DESC);
CREATE INDEX idx_api_usage_logs_provider ON api_usage_logs(api_provider);

-- GIN index for JSONB request_payload
CREATE INDEX idx_api_usage_logs_payload ON api_usage_logs USING GIN (request_payload);

-- ============================================================================
-- API CREDENTIALS TABLE
-- ============================================================================
CREATE TABLE api_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    credentials_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_verified_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX idx_api_credentials_user_provider ON api_credentials(user_id, provider);
CREATE INDEX idx_api_credentials_is_active ON api_credentials(is_active);

-- ============================================================================
-- AI CONVERSATIONS TABLE (Phase 3)
-- ============================================================================
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_project_id ON ai_conversations(project_id);
CREATE INDEX idx_ai_conversations_updated_at ON ai_conversations(updated_at DESC);

-- ============================================================================
-- AI MESSAGES TABLE (Phase 3)
-- ============================================================================
CREATE TYPE ai_role_type AS ENUM ('user', 'assistant', 'system');

CREATE TABLE ai_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role ai_role_type NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_messages_conversation_id ON ai_messages(conversation_id);
CREATE INDEX idx_ai_messages_created_at ON ai_messages(created_at);

-- GIN indexes for JSONB columns
CREATE INDEX idx_ai_messages_tool_calls ON ai_messages USING GIN (tool_calls);
CREATE INDEX idx_ai_messages_tool_results ON ai_messages USING GIN (tool_results);

-- ============================================================================
-- AI PERMISSIONS TABLE (Phase 3)
-- ============================================================================
CREATE TYPE permission_type AS ENUM ('read_data', 'write_data', 'send_emails', 'manage_apis');

CREATE TABLE ai_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_type permission_type NOT NULL,
    granted BOOLEAN DEFAULT FALSE,
    granted_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_permissions_user_id ON ai_permissions(user_id);
CREATE UNIQUE INDEX idx_ai_permissions_user_permission ON ai_permissions(user_id, permission_type);

-- ============================================================================
-- EMAIL CONNECTIONS TABLE (Phase 3)
-- ============================================================================
CREATE TABLE email_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_address VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX idx_email_connections_user ON email_connections(user_id);
CREATE INDEX idx_email_connections_email ON email_connections(email_address);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_domains_updated_at BEFORE UPDATE ON competitor_domains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outreach_prospects_updated_at BEFORE UPDATE ON outreach_prospects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_conversations_updated_at BEFORE UPDATE ON ai_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE (Optional)
-- ============================================================================

-- View for latest keyword rankings
CREATE MATERIALIZED VIEW mv_latest_rankings AS
SELECT DISTINCT ON (keyword_id)
    keyword_id,
    rank_position,
    checked_at,
    search_engine,
    tracked_url
FROM rank_tracking
ORDER BY keyword_id, checked_at DESC;

CREATE UNIQUE INDEX idx_mv_latest_rankings_keyword ON mv_latest_rankings(keyword_id);

-- View for project statistics
CREATE MATERIALIZED VIEW mv_project_stats AS
SELECT
    p.id as project_id,
    p.name as project_name,
    p.domain,
    COUNT(DISTINCT k.id) as total_keywords,
    COUNT(DISTINCT rt.id) as total_rank_checks,
    AVG(rt.rank_position) as avg_rank_position,
    COUNT(DISTINCT CASE WHEN rt.rank_position <= 10 THEN k.id END) as keywords_in_top_10,
    MAX(rt.checked_at) as last_rank_check
FROM projects p
LEFT JOIN keywords k ON k.project_id = p.id
LEFT JOIN rank_tracking rt ON rt.keyword_id = k.id
GROUP BY p.id, p.name, p.domain;

CREATE UNIQUE INDEX idx_mv_project_stats_project ON mv_project_stats(project_id);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE users IS 'User accounts with authentication and API credits';
COMMENT ON TABLE projects IS 'Website projects tracked by users';
COMMENT ON TABLE keywords IS 'Keywords tracked within each project';
COMMENT ON TABLE rank_tracking IS 'Historical rank position data for keywords';
COMMENT ON TABLE serp_snapshots IS 'Full SERP result snapshots for keywords';
COMMENT ON TABLE backlinks IS 'Backlink profile data for projects';
COMMENT ON TABLE outreach_prospects IS 'Link building outreach prospects';
COMMENT ON TABLE api_usage_logs IS 'API call tracking for cost management';
COMMENT ON TABLE api_credentials IS 'Encrypted user API credentials for third-party services';
COMMENT ON TABLE ai_conversations IS 'AI assistant conversation threads';
COMMENT ON TABLE ai_messages IS 'Individual messages in AI conversations';
COMMENT ON TABLE ai_permissions IS 'User-granted permissions for AI assistant';
COMMENT ON TABLE email_connections IS 'Connected email accounts for outreach';
