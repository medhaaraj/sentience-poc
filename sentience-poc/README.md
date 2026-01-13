# Sentience POC - AI Usage Visibility Platform

**Read-only AI governance platform for detecting and visualizing AI tool usage within corporate networks**

---

## 🎯 What This Does

This POC demonstrates:
- ✅ Detection of AI tool usage from network telemetry (SWG logs)
- ✅ Classification of tools as **Licensed** (sanctioned) or **Shadow AI** (unsanctioned)
- ✅ Real-time dashboard showing AI adoption metrics
- ✅ MCP-based query interface for AI-native data access
- ✅ Cloudflare Workers integration for synthetic log generation
- ✅ Explainable, registry-driven detection

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose
- Python 3.8+

### Step 1: Create Project Structure

```bash
# Create all directories
mkdir -p sentience-poc/{backend,db,scripts,frontend,telemetry}
cd sentience-poc
```

### Step 2: Copy All Files

**Copy each file from the artifacts above into your project:**

1. `docker-compose.yml` (root)
2. `backend/__init__.py`
3. `backend/models.py`
4. `backend/db.py`
5. `backend/detection.py`
6. `backend/aggregation.py`
7. `backend/mcp.py`
8. `backend/app.py`
9. `backend/requirements.txt`
10. `backend/Dockerfile`
11. `db/init.sql`
12. `scripts/generate_logs.py`
13. `scripts/ingest_logs.py`
14. `frontend/index.html`

### Step 3: Generate Sample Data

```bash
python3 scripts/generate_logs.py
```

**Output:**
```
🔄 Generating 200 SWG log entries...
✅ Generated 200 log entries
   📁 Output: telemetry/swg_logs.jsonl
   🤖 AI-related logs: 140 (70%)
   🌐 Non-AI logs: 60
   👥 Unique users: 8
   🔧 Unique AI domains: 10
```

### Step 4: Start All Services

```bash
docker-compose up --build -d
```

**Wait 30 seconds for services to initialize**

### Step 5: Ingest Telemetry

```bash
python3 scripts/ingest_logs.py

# OR for continuous real-time ingestion from Cloudflare:
python3 backend/telemetry_consumer.py
```

**Output:**
```
🔄 Waiting for backend to be ready...
✅ Backend is ready
📥 Starting log ingestion...
   ✓ Ingested 20 logs...
   ✓ Ingested 40 logs...
   ...
✅ Ingestion Complete
   ✓ Successfully ingested: 200
🔄 Triggering aggregation...
✅ Aggregation complete
🎉 All done! View dashboard at: http://localhost:3000
```

### Step 6: View Dashboard

Open browser to: **http://localhost:3000**

---

## 📊 What You'll See

### Dashboard Components

**1. Stats Cards:**
- AI Tools Detected: Total unique AI tools found
- Licensed Tools: Sanctioned tools (ChatGPT, Copilot, Claude)
- Shadow AI Tools: Unsanctioned tools (Midjourney, Perplexity, etc.)
- Active Users: Total users using AI tools

**2. Tool Usage Table:**
| Status | Tool | Vendor | Category | Users | Classification |
|--------|------|--------|----------|-------|----------------|
| ✅ | ChatGPT | OpenAI | LLM Chat | 5 | ✓ Licensed |
| ✅ | Claude | Anthropic | LLM Chat | 3 | ✓ Licensed |
| ⚠️ | Midjourney | Midjourney | Image Gen | 4 | ⚠ Shadow AI |

---

## 🏗️ How It Works

### Architecture Flow

```
1. TELEMETRY GENERATION
   scripts/generate_logs.py
   ↓
   Creates simulated SWG logs (JSONL format)

2. LOG INGESTION
   scripts/ingest_logs.py
   ↓
   POST /telemetry/ingest for each log entry

3. REAL-TIME TELEMETRY (Cloudflare Worker)
   sentience-sandbox/src/entry.py
   ↓
   Generates logs on demand (POST /telemetry/generate)
   ↓
   backend/telemetry_consumer.py polls and pushes to /telemetry/ingest

4. DETECTION (backend/detection.py)
   ↓
   Query Tool Registry: Does domain match known AI tool?
   ↓
   Return: (tool_id, licensed, explanation)

4. NORMALIZATION (backend/app.py)
   ↓
   INSERT INTO ai_usage_events
   (timestamp, user_id, tool_id, licensed, explanation)

5. AGGREGATION (backend/aggregation.py)
   ↓
   Compute metrics:
   - Unique users per tool (7-day window)
   - Licensed vs Shadow breakdown

6. MCP QUERY LAYER (backend/mcp.py)
   ↓
   GET /mcp/tools
   Returns: [{tool_id, users, licensed, name, vendor, ...}]

7. VISUALIZATION (frontend/index.html)
   ↓
   Fetch data every 5 seconds
   Display real-time dashboard
```

### Key Components

**Backend (FastAPI + PostgreSQL):**
- `app.py` - Main API server with CORS
- `db.py` - Database connection with retry logic
- `detection.py` - Registry-based AI tool detection
- `aggregation.py` - Usage metrics computation
- `mcp.py` - MCP query interface
- `models.py` - Pydantic data models

**Database (PostgreSQL):**
- `tools` - Tool Registry (8 seeded AI tools)
- `ai_usage_events` - Normalized telemetry events
- `tool_usage_summary` - Pre-aggregated metrics

**Frontend (HTML/Tailwind):**
- Standalone HTML dashboard
- Auto-refreshes every 5 seconds
- Color-coded tool classification

**Scripts:**
- `generate_logs.py` - Creates simulated SWG logs
- `ingest_logs.py` - Loads logs into backend
- `backend/telemetry_consumer.py` - Real-time poller for Cloudflare Sandbox

---

## 🔍 Detection Algorithm

```python
def detect_tool(domain):
    # 1. Normalize domain
    domain = domain.lower().strip()
    
    # 2. Query Tool Registry
    result = db.query("""
        SELECT tool_id, licensed
        FROM tools
        WHERE domain = ANY(known_domains)
    """)
    
    # 3. Classification
    if result:
        return result.tool_id, result.licensed, "Matched via registry"
    else:
        return "unknown", False, "No registry match"
```

**Characteristics:**
- ✅ Deterministic (same input → same output)
- ✅ Explainable (reason provided)
- ✅ Fast (single DB query)
- ✅ Extensible (add tools by updating registry)

---

## 📋 API Endpoints

### Backend (http://localhost:8000)

```bash
# Health check
GET /
→ {"status": "ok", "service": "Sentience POC API"}

# Ingest telemetry
POST /telemetry/ingest
Body: {"user": "alice", "domain": "chat.openai.com"}
→ {"status": "ok", "tool_id": "chatgpt", "licensed": true, ...}

# MCP: List all tools
GET /mcp/tools
→ [{"tool_id": "chatgpt", "users": 5, "licensed": true, ...}]

# MCP: Tool details
GET /mcp/tools/{tool_id}
→ {"tool_id": "chatgpt", "name": "ChatGPT", ...}

# Statistics
GET /stats
→ {"total_tools": 8, "licensed_tools": 3, "shadow_tools": 5, ...}

# Trigger aggregation
POST /aggregate
→ {"status": "aggregation complete"}

# Recent events (debug)
GET /events/recent?limit=50
→ [{"timestamp": "...", "user_id": "alice", "tool_id": "chatgpt", ...}]
```

### API Documentation

**Swagger UI:** http://localhost:8000/docs

---

## 🗄️ Database Schema

```sql
-- Tool Registry
tools (
    tool_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    vendor VARCHAR(255),
    category VARCHAR(100),
    licensed BOOLEAN,
    known_domains TEXT[]  -- Array of domains
)

-- Normalized Events
ai_usage_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    user_id VARCHAR(255),
    tool_id VARCHAR(100),
    licensed BOOLEAN,
    explanation TEXT  -- Why it was classified
)

-- Aggregated Metrics
tool_usage_summary (
    tool_id VARCHAR(100),
    time_window VARCHAR(10),  -- '7d', '30d'
    active_users INT,
    PRIMARY KEY (tool_id, time_window)
)
```

### Seeded Tools

**Licensed (✅):**
- ChatGPT - OpenAI - LLM Chat
- GitHub Copilot - GitHub/Microsoft - Code Assistant
- Claude - Anthropic - LLM Chat

**Shadow AI (⚠️):**
- Google Gemini - Google - LLM Chat
- Midjourney - Midjourney - Image Generation
- Perplexity - Perplexity AI - Search
- Hugging Face - Hugging Face - ML Platform
- Runway - Runway - Video Generation

---

## 🧪 Testing & Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just database
docker-compose logs -f db
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U sentience -d sentience

# Inside psql:
SELECT * FROM tools;
SELECT COUNT(*) FROM ai_usage_events;
SELECT * FROM ai_usage_events ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM tool_usage_summary;
```

### Manual Testing

```bash
# Test backend health
curl http://localhost:8000/

# Test MCP endpoint
curl http://localhost:8000/mcp/tools | jq

# Manual log ingestion
curl -X POST http://localhost:8000/telemetry/ingest \
  -H "Content-Type: application/json" \
  -d '{"user": "test", "domain": "chat.openai.com"}'

# Check stats
curl http://localhost:8000/stats | jq
```

### Generate More Data

```bash
# Generate 500 logs instead of 200
# Edit scripts/generate_logs.py, change:
# generate_logs(500)

python3 scripts/generate_logs.py
python3 scripts/ingest_logs.py
```

---

## 🔧 Troubleshooting

### Services won't start

```bash
# Check what's failing
docker-compose ps

# Rebuild
docker-compose down
docker-compose up --build
```

### No data in dashboard

```bash
# Check if logs exist
ls -la telemetry/swg_logs.jsonl

# Check if backend has data
curl http://localhost:8000/mcp/tools

# Re-ingest
python3 scripts/ingest_logs.py
```

### Database connection errors

```bash
# Restart database
docker-compose restart db

# Check health
docker-compose exec db pg_isready -U sentience

# Nuclear option: wipe and restart
docker-compose down -v
docker-compose up -d
sleep 30
python3 scripts/generate_logs.py
python3 scripts/ingest_logs.py
```

### CORS errors in browser

Make sure you're using the correct `app.py` with CORS middleware.

---

## 🛑 Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes (deletes database)
docker-compose down -v

# Remove generated logs
rm -rf telemetry/
```

---

## 📝 Design Principles

1. **Read-Only by Design** - No blocking or enforcement
2. **Metadata-Only** - No content inspection
3. **Registry-Driven** - Single source of truth for tools
4. **Explainable** - Every classification has reasoning
5. **Extensible** - Easy to add new telemetry sources

---

## 🎯 Success Criteria

✅ **POC is successful if:**
- AI tools are detected from SWG logs
- Tools classified as licensed/shadow/unknown
- Metrics aggregated (tools in use, active users)
- MCP queries return explainable data
- Dashboard visualizes usage clearly
- System runnable by non-author (reproducible)

---

## 🔮 Future Extensions (Post-POC)

- Add more telemetry sources (DNS, firewall, cloud logs)
- Real-time streaming instead of batch processing
- ML-based detection for unknown tools
- Policy recommendation engine
- Automated alerting for shadow AI
- Department/team breakdowns
- Cost estimation per tool

---

## 📞 Support

**Check these resources:**
- API Documentation: http://localhost:8000/docs
- Database Console: `docker-compose exec db psql -U sentience -d sentience`
- Logs: `docker-compose logs -f`

---

**Sentience POC v0.1 - Built with FastAPI, PostgreSQL, and Tailwind CSS**