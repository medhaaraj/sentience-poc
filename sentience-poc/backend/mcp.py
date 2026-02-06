"""
MCP Query Layer
Model Context Protocol interface for AI-native queries
Provides read-only, explainable access to AI usage data
"""


def list_tools(cursor):
    """
    List all detected AI tools with usage metrics
    
    Returns data for dashboard visualization:
    - Tool identification (id, name, vendor, category)
    - Usage metrics (active users)
    - Licensing status (licensed/shadow)
    
    Args:
        cursor: PostgreSQL cursor
        
    Returns:
        list: Array of tool dictionaries with usage data
        
    Example output:
    [
        {
            "tool_id": "chatgpt",
            "users": 5,
            "licensed": true,
            "name": "ChatGPT",
            "vendor": "OpenAI",
            "category": "LLM Chat"
        },
        ...
    ]
    """
    cursor.execute("""
        SELECT 
            e.tool_id,
            COUNT(DISTINCT e.user_id) AS users,
            BOOL_OR(e.licensed) AS licensed,
            t.name,
            t.vendor,
            t.category
        FROM ai_usage_events e
        LEFT JOIN tools t ON e.tool_id = t.tool_id
        GROUP BY e.tool_id, t.name, t.vendor, t.category
        ORDER BY users DESC
    """)
    
    results = []
    for row in cursor.fetchall():
        tool_id, users, licensed, name, vendor, category = row
        results.append({
            "tool_id": tool_id,
            "users": users,
            "licensed": licensed if licensed is not None else False,
            "name": name or tool_id,
            "vendor": vendor or "Unknown",
            "category": category or "Unknown"
        })
    
    return results


def get_tool_details(cursor, tool_id: str):
    """
    Get detailed information about a specific tool
    Includes registry data and usage statistics
    
    Args:
        cursor: PostgreSQL cursor
        tool_id: Tool identifier to query
        
    Returns:
        dict: Detailed tool information
    """
    # Get tool registry info
    cursor.execute("""
        SELECT tool_id, name, vendor, category, licensed, known_domains
        FROM tools
        WHERE tool_id = %s
    """, (tool_id,))
    
    tool_row = cursor.fetchone()
    
    if not tool_row:
        # Tool not in registry (unknown/new tool)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id), MIN(timestamp), MAX(timestamp)
            FROM ai_usage_events
            WHERE tool_id = %s
        """, (tool_id,))
        stats = cursor.fetchone()
        
        return {
            "tool_id": tool_id,
            "in_registry": False,
            "users": stats[0] if stats else 0,
            "first_seen": stats[1].isoformat() if stats and stats[1] else None,
            "last_seen": stats[2].isoformat() if stats and stats[2] else None
        }
    
    # Tool is in registry
    tid, name, vendor, category, licensed, domains = tool_row
    
    # Get usage stats
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT user_id) as users,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen,
            COUNT(*) as total_events
        FROM ai_usage_events
        WHERE tool_id = %s
    """, (tool_id,))
    
    stats = cursor.fetchone()
    
    return {
        "tool_id": tid,
        "name": name,
        "vendor": vendor,
        "category": category,
        "licensed": licensed,
        "known_domains": domains,
        "in_registry": True,
        "users": stats[0] if stats else 0,
        "first_seen": stats[1].isoformat() if stats and stats[1] else None,
        "last_seen": stats[2].isoformat() if stats and stats[2] else None,
        "total_events": stats[3] if stats else 0
    }


def list_recent_logs(cursor, limit: int = 50):
    """
    List recent raw telemetry logs
    
    Args:
        cursor: PostgreSQL cursor
        limit: Max records to return
        
    Returns:
        list: Recent event dictionaries
    """
    cursor.execute("""
        SELECT timestamp, user_id, tool_id, licensed, explanation
        FROM ai_usage_events
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            "timestamp": row[0].isoformat() if row[0] else None,
            "user_id": row[1],
            "tool_id": row[2],
            "licensed": row[3],
            "explanation": row[4]
        })
    
    return events