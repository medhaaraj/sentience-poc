
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import json

app = FastAPI()

# User pool (simulated employees)
USERS = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry"]

# AI tool domains (mix of licensed and shadow)
AI_DOMAINS = [
    "chat.openai.com",           # ChatGPT - Licensed
    "claude.ai",                 # Claude - Licensed
    "copilot.github.com",        # Copilot - Licensed
    "gemini.google.com",         # Gemini - Shadow
    "midjourney.com",            # Midjourney - Shadow
    "perplexity.ai",             # Perplexity - Shadow
    "huggingface.co",            # HuggingFace - Shadow
    "runwayml.com",              # Runway - Shadow
    "api.openai.com",            # OpenAI API
    "api.anthropic.com"          # Anthropic API
]

# Non-AI domains for realistic traffic mix
NON_AI_DOMAINS = [
    "google.com",
    "github.com",
    "stackoverflow.com",
    "docs.microsoft.com",
    "slack.com",
    "gmail.com",
    "drive.google.com"
]

class GenerateRequest(BaseModel):
    count: int = 10

def generate_log_entry(timestamp):
    user = random.choice(USERS)
    if random.random() < 0.7:
        domain = random.choice(AI_DOMAINS)
    else:
        domain = random.choice(NON_AI_DOMAINS)
    
    return {
        "timestamp": timestamp.isoformat(),
        "user": user,
        "domain": domain,
        "method": "GET",
        "status": 200
    }

@app.post("/telemetry/generate")
async def generate_telemetry(req: GenerateRequest):
    """
    Generate synthetic telemetry data.
    """
    logs = []
    # Generate logs for "now" mostly, for real-time simulation feel, 
    # but we can spread them slightly if needed. 
    # For now, let's just generate them as recent events.
    base_time = datetime.utcnow()
    
    for i in range(req.count):
        # timestamp slightly varied
        timestamp = base_time - timedelta(seconds=random.randint(0, 300)) 
        logs.append(generate_log_entry(timestamp))
        
    return {"logs": logs}

@app.get("/")
async def root():
    return {"status": "Simulator running"}
