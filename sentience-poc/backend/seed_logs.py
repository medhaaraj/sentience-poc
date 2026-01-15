
import psycopg2
from datetime import datetime, timedelta
import random
from db import get_connection

# Comprehensive Tool List from User Screenshots
TOOLS = [
    # Coding & Tech
    ('GitHub Copilot', 'GitHub', 'Coding Assistant', True),
    ('Cursor', 'Anysphere', 'Coding Assistant', False),
    ('Replit', 'Replit', 'Coding Environment', False),
    
    # Generative AI (General)
    ('ChatGPT', 'OpenAI', 'Generative AI', True),
    ('Claude 3.5 Sonnet', 'Anthropic', 'Generative AI', True),
    ('Gemini Ultra', 'Google', 'Generative AI', True),
    ('Perplexity', 'Perplexity AI', 'Search', False),
    
    # Productivity & Knowledge
    ('Notion AI', 'Notion', 'Productivity', True),
    ('Microsoft 365 Copilot', 'Microsoft', 'Productivity', True),
    ('Workspace AI', 'Google', 'Productivity', True),
    ('Obsidian AI', 'Obsidian', 'Knowledge Mgmt', False),

    # Sales & Support
    ('Einstein GPT', 'Salesforce', 'CRM', True),
    ('Gong AI', 'Gong.io', 'Sales Intelligence', True),
    ('Intercom Fin', 'Intercom', 'Customer Support', True),
    ('Zendesk AI', 'Zendesk', 'Customer Support', True),
    ('HubSpot AI', 'HubSpot', 'Marketing', True),

    # Marketing & Content
    ('Jasper', 'Jasper AI', 'Marketing', False),
    ('Copy.ai', 'Copy.ai', 'Marketing', False),
    ('Grammarly', 'Grammarly', 'Writing Assistant', True),
    ('Writer', 'Writer.com', 'Enterprise Writing', True),

    # Design & Creative
    ('Midjourney', 'Midjourney', 'Image Gen', False),
    ('Figma AI', 'Figma', 'Design', True),
    ('Canva AI', 'Canva', 'Design', False),
    ('Miro AI', 'Miro', 'Collaboration', True),
    ('Loom AI', 'Loom', 'Video Messaging', False),

    # Management & Ops
    ('Asana Intelligence', 'Asana', 'Project Management', True),
    ('Monday AI', 'Monday.com', 'Project Management', True),
    ('Zapier AI', 'Zapier', 'Automation', False),
    ('Otter.ai', 'Otter.ai', 'Meeting Assistant', False),
    ('Zoom AI Companion', 'Zoom', 'Meeting Assistant', True),
    ('Slack AI', 'Slack', 'Communication', True),
]

# Generate a realistic user pool to match the "100+ users" scale
DEPARTMENTS = ['eng', 'sales', 'mkt', 'hr', 'finance', 'exec']
USERS = []
for dept in DEPARTMENTS:
    for i in range(1, 40): # ~240 users total
        USERS.append(f"{dept}.user{i}@sentience.ai")

# Special "VIP" users
VIP_USERS = ['admin@sentience.ai', 'ciso@sentience.ai', 'cto@sentience.ai']
USERS.extend(VIP_USERS)

def seed_data():
    conn = get_connection()
    cur = conn.cursor()
    
    print("--- EXPANDED SEEDING SEQUENCE INITIATED ---")
    
    try:
        # Determine start time (fill gaps or just add more density)
        # We'll just generate purely fresh data for the last 24h to ensure high density
        # Deleting old data from last 24h to avoid duplication if running multiple times? 
        # No, let's just append. "More usage" is good for the demo.
        
        start_time = datetime.utcnow() - timedelta(hours=24)
        print(f"Generating massive dataset from {start_time} to Now...")
        
        current = start_time
        now = datetime.utcnow()
        total_inserted = 0
        
        while current < now:
            # Create a "wave" of activity using sine-like probability or just Work Hours
            hour = current.hour
            is_peak = 9 <= hour <= 17 # Work hours
            
            # Probability of an event occurring in this minute
            # Peak: High traffic. Off-peak: Low traffic.
            if is_peak:
                # Heavy traffic: 5-20 events per minute
                num_events = random.randint(5, 25)
            else:
                # Light traffic: 0-3 events per minute
                num_events = random.randint(0, 3)
                
            for _ in range(num_events):
                # Pick tool (weighted: ChatGPT/Copilot more popular)
                # Weights: First 5 tools = 3x likelihood
                weights = [3]*5 + [1]*(len(TOOLS)-5)
                tool = random.choices(TOOLS, weights=weights, k=1)[0]
                tool_name, vendor, category, licensed = tool
                
                # Pick user
                user = random.choice(USERS)
                
                # Jitter timestamp within the minute
                event_ts = current + timedelta(seconds=random.randint(0, 59))
                if event_ts > now: continue

                cur.execute("""
                    INSERT INTO ai_usage_events 
                    (timestamp, user_id, tool_id, licensed, explanation)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    event_ts,
                    user,
                    tool_name,
                    licensed,
                    f"Traffic fingerprint match: {tool_name} ({category})"
                ))
                total_inserted += 1
            
            current += timedelta(minutes=1)
            
        conn.commit()
        print(f"SUCCESS: Injected {total_inserted} events across {len(TOOLS)} unique AI tools.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_data()
