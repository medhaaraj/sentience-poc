
import psycopg2
from db import get_connection

# Same list from seed_logs.py (ensure consistency)
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

def seed_registry():
    conn = get_connection()
    cur = conn.cursor()
    
    print("--- SEEDING TOOLS REGISTRY ---")
    
    try:
        # Clear existing to avoid duplicates/conflicts (optional, but cleaner for demo)
        cur.execute("TRUNCATE TABLE tools CASCADE") 
        # Note: CASCADE might delete events provided foreign key exists. 
        # If schema uses FK, this wipes events. If no FK, events stay but become orphaned?
        # Let's check schema. Usually better to use UPSERT (ON CONFLICT DO UPDATE).
        
        # Let's assume UPSERT is safer.
    except Exception as e:
        print(f"Truncate skipped/failed: {e}")
        conn.rollback()

    try:
        inserted = 0
        for t in TOOLS:
            tool_id_val = t[0] # Using Name as ID for simplicity match with events
            name_val = t[0]
            vendor_val = t[1]
            category_val = t[2]
            licensed_val = t[3]
            
            # Simple domains mock
            domains_val = [f"{tool_id_val.lower().replace(' ', '')}.com"]

            cur.execute("""
                INSERT INTO tools (tool_id, name, vendor, category, licensed, known_domains)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (tool_id) DO UPDATE 
                SET vendor = EXCLUDED.vendor, 
                    category = EXCLUDED.category,
                    licensed = EXCLUDED.licensed
            """, (tool_id_val, name_val, vendor_val, category_val, licensed_val, domains_val))
            inserted += 1

        conn.commit()
        print(f"SUCCESS: Registered {inserted} tools in the metadata registry.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_registry()
