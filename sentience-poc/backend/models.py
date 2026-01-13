"""
Data models for API validation
"""
from pydantic import BaseModel


class TelemetryEvent(BaseModel):
    """
    Incoming telemetry event from SWG logs
    Contains user identifier and destination domain
    """
    user: str
    domain: str