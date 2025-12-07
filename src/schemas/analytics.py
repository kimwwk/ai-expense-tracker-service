"""
Analytics schemas for request/response models.
"""
from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    """Response model for summary analytics."""
    total: float = Field(..., description="Total sum of transaction amounts")
    count: int = Field(..., description="Total count of transactions")


class AnalyticsBreakdownResponse(BaseModel):
    """Response model for breakdown analytics."""
    labels: List[str] = Field(..., description="Dimension labels (category names, payee names, or account names)")
    values: List[float] = Field(..., description="Aggregated values for each label")


class AnalyticsTrendResponse(BaseModel):
    """Response model for trend analytics."""
    dates: List[str] = Field(..., description="Time period labels (dates in ISO format)")
    values: List[float] = Field(..., description="Aggregated values for each time period")


# Query parameter types
BreakdownDimension = Literal["category", "payee", "account"]
BreakdownMetric = Literal["sum", "count"]
TrendTimeGrain = Literal["day", "week", "month"]
AnalyticsTransactionType = Literal["expense", "income"]
