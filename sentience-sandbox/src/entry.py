
from js import Response
import json
import random
from datetime import datetime, timedelta

async def on_fetch(request, env):
    # Static data
    for i in range(5):
        timestamp = base_time - timedelta(seconds=i*10)
        logs.append({
            "timestamp": timestamp.isoformat(),
            "user": random.choice(USERS),
            "domain": random.choice(DOMAINS),
            "method": "GET",
            "status": 200
        })

    return Response.new(json.dumps({"logs": logs}))
