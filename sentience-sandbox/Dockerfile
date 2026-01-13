
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn requests

# Copy application code
COPY sandbox-simulator.py .

# Expose port (Cloudflare Sandbox uses 8080 by default usually, but we can configure or use standard)
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "sandbox-simulator:app", "--host", "0.0.0.0", "--port", "8080"]
