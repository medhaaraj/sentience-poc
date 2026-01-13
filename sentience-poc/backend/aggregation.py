"""
Usage Aggregation Engine
Computes metrics over time windows from normalized events
"""


def aggregate_usage(cursor):
    """
    Aggregate AI usage events into summary metrics
    
    Process:
    1. Clear old aggregations
    2. Compute unique users per tool (7-day window)
    3. Store results in tool_usage_summary table
    
    Metrics computed:
    - Active users per tool (last 7 days)
    - Can be extended to 30-day, 90-day windows
    
    Args:
        cursor: PostgreSQL cursor
    """
    # Clear existing aggregations
    cursor.execute("DELETE FROM tool_usage_summary")

    # Aggregate 7-day active users per tool
    cursor.execute(
        """
        INSERT INTO tool_usage_summary (tool_id, time_window, active_users)
        SELECT tool_id, '7d', COUNT(DISTINCT user_id)
        FROM ai_usage_events
        WHERE timestamp > NOW() - INTERVAL '7 days'
        GROUP BY tool_id
        """
    )
    
    print("Aggregation complete: 7-day active users computed")