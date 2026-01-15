
from js import Response
import json
import random
from datetime import datetime

# Expanded Tool List (Synced with Local Seed)
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

def generate_users():
    users = []
    depts = ['eng', 'sales', 'mkt', 'hr', 'finance', 'exec']
    for dept in depts:
        for i in range(1, 10):
            users.append(f"{dept}.user{i}@sentience.ai")
    users.extend(['admin@sentience.ai', 'ciso@sentience.ai'])
    return users

USERS = generate_users()

async def on_fetch(request, env):
    logs = []
    
    # Generate 1-5 random logs per request to simulate "live" trickle
    num_logs = random.randint(1, 5)
    
    for _ in range(num_logs):
        tool = random.choice(TOOLS)
        tool_name = tool[0]
        # Simulate simple domain mapping
        domain = f"{tool_name.lower().replace(' ', '').replace('.', '')}.com"
        
        logs.append({
            "timestamp": datetime.utcnow().isoformat() + "Z", # UTC
            "user": random.choice(USERS),
            "domain": domain,
            "method": "CONNECT",
            "status": 200,
            "bytes": random.randint(1000, 50000)
        })

    return Response.new(json.dumps({"logs": logs}))
