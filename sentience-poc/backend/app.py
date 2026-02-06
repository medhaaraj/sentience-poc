from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from db import get_connection
from detection import detect_tool
from aggregation import aggregate_usage
from mcp import list_tools, get_tool_details, list_recent_logs, list_recent_logs
from mcp import list_tools, get_tool_details, list_recent_logs
# ... (rest of imports are fine, I will just update the import line first)

# Actually I'll do this in two chunks if needed, or just update the import and add the route at the end of the file or near other mcp routes.

# Strategy: Update line 9 to include list_recent_logs
# Then add the route after mcp_tool_detail.
from models import TelemetryEvent
import requests
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

# Initialize FastAPI application
app = FastAPI(
    title="Sentience POC API",
    description="AI Usage Visibility and Governance Platform",
    version="0.1.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB connection
def get_db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# -------------------------
# AI AGENT ENDPOINT
# -------------------------
@app.post("/api/chat")
def chat_agent(request: ChatRequest, conn = Depends(get_db_conn)):
    """
    Generate response using Gemini with system context
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Context Gathering
    cur = conn.cursor()
    
    # 1. Stats
    cur.execute("SELECT COUNT(*) FROM tools")
    total_tools = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM tools WHERE licensed = FALSE")
    shadow_tools = cur.fetchone()[0]
    
    # 2. Key Risks (Shadow tools with high users)
    # Fix: Join with ai_usage_events to count users, as 'users' column doesn't exist in tools table
    cur.execute("""
        SELECT t.tool_id, COUNT(DISTINCT e.user_id) as user_count
        FROM tools t
        JOIN ai_usage_events e ON t.tool_id = e.tool_id
        WHERE t.licensed = FALSE 
        GROUP BY t.tool_id
        ORDER BY user_count DESC 
        LIMIT 5
    """)
    risky_tools = cur.fetchall()

    # 3. Full Registry (Limit 100 for context window safety)
    # Fix: Join with ai_usage_events to count users
    cur.execute("""
        SELECT t.tool_id, t.vendor, t.category, t.licensed, COUNT(DISTINCT e.user_id) as user_count
        FROM tools t
        LEFT JOIN ai_usage_events e ON t.tool_id = e.tool_id
        GROUP BY t.tool_id, t.vendor, t.category, t.licensed
        ORDER BY user_count DESC 
        LIMIT 100
    """)
    all_tools = cur.fetchall()
    
    cur.close()

    # Format Data for LLM
    registry_text = []
    for t in all_tools:
        status = "Approved" if t[3] else "Shadow/Unapproved"
        registry_text.append(f"- {t[0]} (Vendor: {t[1]}, Category: {t[2]}, Status: {status}, Users: {t[4]})")
    registry_str = "\n".join(registry_text)

    context_str = f"""
    SYSTEM OVERVIEW:
    - Total Tools: {total_tools}
    - Shadow Tools: {shadow_tools}
    - Top Risks (Unapproved High Usage): {', '.join([f'{t[0]} ({t[1]} users)' for t in risky_tools])}

    FULL TOOL REGISTRY DATA:
    {registry_str}
    """

    api_key = os.getenv("OPENAI_API_KEY")

    # ... (context building logic remains same, but let's just replace the block)

    registry_text = []
    # ... (I need to preserve the surrounding context logic if I don't replace it all)
    # Actually, I'll just look at the lines 122-157 which contain the specific gemini constraints.

    if not api_key:
        return {
            "response": "**System Notice**: OFFLINE MODE. Missing `OPENAI_API_KEY`."
        }

    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = f"""
        You are Sentience, an expert AI Security & Governance Agent.
        
        Your Mission: Assist the administrator by analyzing the provided live system data.
        
        LIVE DATA CONTEXT:
        {context_str}
        
        GUIDELINES:
        1. **Be Specific**: Use the data provided. If asked "How many tools?", count them from the list.
        2. **Risk Focus**: Always highlight shadow/unapproved tools if relevant to the question.
        3. **Tone**: Professional, precise, slightly futuristic.
        4. **Format**: Use Markdown. Use Bold for tool names and numbers.
        5. **Unknowns**: If the data isn't in the list, state that you don't have that visibility.
        """
        
        completion = client.chat.completions.create(
            model="gpt-4o",  # Or gpt-3.5-turbo if preferred, but user implies high capability
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ]
        )
        
        return {"response": completion.choices[0].message.content}
        
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return {"response": f"**API Error**: {str(e)}"}
            

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
def root():
    """
    Health check endpoint
    Returns service status
    """
    return {
        "status": "ok",
        "service": "Sentience POC API",
        "version": "0.1.0"
    }


# -------------------------
# TELEMETRY INGESTION
# -------------------------
@app.post("/telemetry/ingest")
def ingest(event: TelemetryEvent, conn = Depends(get_db_conn)):
    """
    Ingest telemetry event from SWG logs
    """
    cur = conn.cursor()
    try:
        # Run detection algorithm
        tool_id, licensed, explanation = detect_tool(cur, event.domain)

        # Store normalized event
        cur.execute(
            """
            INSERT INTO ai_usage_events
            (timestamp, user_id, tool_id, licensed, explanation)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                datetime.utcnow(),
                event.user,
                tool_id,
                licensed,
                explanation
            )
        )
        conn.commit()

        return {
            "status": "ok",
            "tool_id": tool_id,
            "licensed": licensed,
            "explanation": explanation
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()


# -------------------------
# MCP QUERY ENDPOINTS
# -------------------------
@app.get("/mcp/tools")
def mcp_tools(conn = Depends(get_db_conn)):
    """
    MCP Query: List all tools
    """
    cur = conn.cursor()
    try:
        return list_tools(cur)
    finally:
        cur.close()


@app.get("/mcp/tools/{tool_id}")
def mcp_tool_detail(tool_id: str, conn = Depends(get_db_conn)):
    """
    MCP Query: Get tool details
    """
    cur = conn.cursor()
    try:
        return get_tool_details(cur, tool_id)
    finally:
        cur.close()


@app.get("/mcp/logs")
def mcp_logs(limit: int = 50, conn = Depends(get_db_conn)):
    """
    MCP Query: Get recent logs
    """
    cur = conn.cursor()
    try:
        return list_recent_logs(cur, limit)
    finally:
        cur.close()


# -------------------------
# STATISTICS
# -------------------------
@app.get("/stats")
def get_stats(conn = Depends(get_db_conn)):
    """
    Get overall system statistics
    """
    cur = conn.cursor()
    try:
        # Total unique tools detected
        cur.execute("SELECT COUNT(DISTINCT tool_id) FROM ai_usage_events")
        total_tools = cur.fetchone()[0]
        
        # Total unique users
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM ai_usage_events")
        total_users = cur.fetchone()[0]
        
        # Licensed vs shadow tools
        cur.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN licensed = true THEN tool_id END) as licensed,
                COUNT(DISTINCT CASE WHEN licensed = false THEN tool_id END) as shadow
            FROM ai_usage_events
            WHERE tool_id != 'unknown'
        """)
        licensed, shadow = cur.fetchone()
        
        return {
            "total_tools": total_tools,
            "total_users": total_users,
            "licensed_tools": licensed or 0,
            "shadow_tools": shadow or 0
        }
    finally:
        cur.close()


@app.get("/stats/trends")
def get_usage_trends(conn = Depends(get_db_conn)):
    """
    Get hourly usage volume for the last 24 hours
    """
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                date_trunc('hour', timestamp) as bucket,
                COUNT(*)
            FROM ai_usage_events
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY bucket
            ORDER BY bucket ASC
        """)
        
        # Format for frontend
        results = []
        for row in cur.fetchall():
            # Append Z to indicate UTC
            results.append({"time": row[0].isoformat() + "Z", "count": row[1]})
            
        return results
    finally:
        cur.close()


@app.get("/stats/top_users")
def get_top_users(limit: int = 5, conn = Depends(get_db_conn)):
    """
    Get top users by total events
    """
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT user_id, COUNT(*) as events
            FROM ai_usage_events
            GROUP BY user_id
            ORDER BY events DESC
            LIMIT %s
        """, (limit,))
        
        return [{"user": row[0], "events": row[1]} for row in cur.fetchall()]
    finally:
        cur.close()
        
        
@app.get("/stats/risk")
def get_risk_score(conn = Depends(get_db_conn)):
    """
    Get risk breakdown (Shadow AI volume vs Licensed)
    """
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE licensed=false) as shadow_events,
                COUNT(*) FILTER (WHERE licensed=true) as licensed_events,
                COUNT(*) as total
            FROM ai_usage_events
            WHERE timestamp >= NOW() - INTERVAL '7 days'
        """)
        row = cur.fetchone()
        shadow_events = row[0] or 0
        total = row[2] or 1
        
        # Simple risk score: percentage of shadow events
        risk_score = int((shadow_events / total) * 100) if total > 0 else 0
        
        return {
            "risk_score": risk_score, 
            "shadow_events": shadow_events,
            "licensed_events": row[1] or 0
        }
    finally:
        cur.close()


# -------------------------
# AGGREGATION
# -------------------------
@app.post("/aggregate")
def run_aggregation(conn = Depends(get_db_conn)):
    """
    Trigger aggregation
    """
    cur = conn.cursor()
    try:
        aggregate_usage(cur)
        conn.commit()
        return {"status": "aggregation complete"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()


# -------------------------
# DEBUG ENDPOINTS
# -------------------------
@app.get("/events/recent")
def recent_events(limit: int = 50, conn = Depends(get_db_conn)):
    """
    Get recent AI usage events for debugging
    
    Args:
        limit: Maximum number of events to return
        
    Returns:
        list: Recent events with timestamps
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, user_id, tool_id, licensed, explanation
        FROM ai_usage_events
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    events = []
    for row in cur.fetchall():
        events.append({
            "timestamp": row[0].isoformat(),
            "user_id": row[1],
            "tool_id": row[2],
            "licensed": row[3],
            "explanation": row[4]
        })
    
    return events


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)