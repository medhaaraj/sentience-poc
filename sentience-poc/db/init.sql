-- ============================================
-- Sentience POC Database Schema
-- PostgreSQL initialization script
-- ============================================

-- Tool Registry Table
-- Stores canonical definitions of AI tools
CREATE TABLE IF NOT EXISTS tools (
    tool_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    vendor VARCHAR(255),
    category VARCHAR(100),
    licensed BOOLEAN DEFAULT FALSE,
    known_domains TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Usage Events Table
-- Normalized telemetry events from all sources
CREATE TABLE IF NOT EXISTS ai_usage_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    tool_id VARCHAR(100) NOT NULL,
    licensed BOOLEAN DEFAULT FALSE,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tool Usage Summary Table
-- Pre-aggregated metrics for fast queries
CREATE TABLE IF NOT EXISTS tool_usage_summary (
    tool_id VARCHAR(100),
    time_window VARCHAR(10),
    active_users INT,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (tool_id, time_window)
);

-- ============================================
-- Seed Data: Tool Registry
-- ============================================

-- Licensed AI Tools (Sanctioned)
INSERT INTO tools (tool_id, name, vendor, category, licensed, known_domains) VALUES
    ('chatgpt', 'ChatGPT', 'OpenAI', 'LLM Chat', TRUE, ARRAY['chat.openai.com', 'chatgpt.com']),
    ('github-copilot', 'GitHub Copilot', 'GitHub/Microsoft', 'Code Assistant', TRUE, ARRAY['copilot.github.com', 'api.github.com']),
    ('claude', 'Claude', 'Anthropic', 'LLM Chat', TRUE, ARRAY['claude.ai', 'api.anthropic.com'])
ON CONFLICT (tool_id) DO NOTHING;

-- Shadow AI Tools (Unsanctioned)
INSERT INTO tools (tool_id, name, vendor, category, licensed, known_domains) VALUES
    ('gemini', 'Google Gemini', 'Google', 'LLM Chat', FALSE, ARRAY['gemini.google.com', 'aistudio.google.com']),
    ('midjourney', 'Midjourney', 'Midjourney', 'Image Generation', FALSE, ARRAY['midjourney.com', 'www.midjourney.com']),
    ('perplexity', 'Perplexity', 'Perplexity AI', 'Search', FALSE, ARRAY['perplexity.ai', 'www.perplexity.ai']),
    ('huggingface', 'Hugging Face', 'Hugging Face', 'ML Platform', FALSE, ARRAY['huggingface.co', 'api-inference.huggingface.co']),
    ('runway', 'Runway', 'Runway', 'Video Generation', FALSE, ARRAY['runwayml.com', 'app.runwayml.com'])
ON CONFLICT (tool_id) DO NOTHING;

-- ============================================
-- Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON ai_usage_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_tool_id ON ai_usage_events(tool_id);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON ai_usage_events(user_id);

-- ============================================
-- Initialization Complete
-- ============================================