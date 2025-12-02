"""Domain objects (Pydantic)."""
from pydantic import BaseModel, Field
from datetime import datetime


class YieldPoint(BaseModel):
    """Single yield data observation."""

    tenor: str
    value: float = Field(..., gt=0)
    instrument: str = "OIS"
    currency: str = "TRY"
    valuationDate: str
    publishedAt: str

    # pydantic config
    class Config:
        frozen = True
        alias_generator = lambda s: s  # keep names verbatim


class Alert(BaseModel):
    """Threshold breach notification."""

    tenor: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
