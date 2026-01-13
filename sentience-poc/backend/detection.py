"""
AI Tool Detection Engine
Registry-based, deterministic detection of AI tools from domains
"""


def detect_tool(cursor, domain: str):
    """
    Detect AI tool from domain using Tool Registry
    
    Algorithm:
    1. Normalize domain (lowercase)
    2. Query tools table for domain match
    3. Return tool_id, licensed status, and explanation
    
    Args:
        cursor: PostgreSQL cursor
        domain: Destination domain from telemetry
        
    Returns:
        tuple: (tool_id, licensed, explanation)
        
    Example:
        detect_tool(cursor, "chat.openai.com")
        → ("chatgpt", True, "Matched known tool via registry")
        
        detect_tool(cursor, "unknown-ai.com")
        → ("unknown", False, "No registry match")
    """
    # Normalize domain
    domain_normalized = domain.lower().strip()
    
    # Query tool registry for matching domain
    cursor.execute(
        """
        SELECT tool_id, licensed
        FROM tools
        WHERE %s = ANY(known_domains)
        """,
        (domain_normalized,)
    )

    row = cursor.fetchone()

    if row:
        # Domain matched a known tool in registry
        tool_id, licensed = row
        explanation = "Matched known tool via registry"
    else:
        # Domain not in registry - mark as unknown
        tool_id = "unknown"
        licensed = False
        explanation = "No registry match"

    return tool_id, licensed, explanation