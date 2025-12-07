"""
Analytics API router implementing REST endpoints for transaction analytics.
Provides endpoints for summary statistics, breakdowns, and time series trends.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import analytics_service
from src.schemas.analytics import (
    AnalyticsSummaryResponse,
    AnalyticsBreakdownResponse,
    AnalyticsTrendResponse,
    BreakdownDimension,
    BreakdownMetric,
    TrendTimeGrain,
    AnalyticsTransactionType,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get summary statistics for filtered transactions"
)
def get_summary(
    start_date: Optional[date] = Query(None, description="Filter by transaction date >= start_date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by transaction date <= end_date (YYYY-MM-DD)"),
    transaction_type: Optional[AnalyticsTransactionType] = Query(None, description="Filter by transaction type (expense or income)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    payee_id: Optional[int] = Query(None, description="Filter by payee ID"),
    db: Session = Depends(get_db)
):
    """
    Calculate summary statistics (total amount and count) for transactions.

    **Purpose**: Get simple totals for filtered transactions (e.g., "Total spending this month")

    **Filters:**
    - **start_date**: Show transactions on or after this date
    - **end_date**: Show transactions on or before this date
    - **transaction_type**: 'expense' or 'income' (transfers are automatically excluded)
    - **category_id**: Filter by specific category
    - **account_id**: Filter by specific account
    - **payee_id**: Filter by specific payee

    **Returns:**
    - **total**: Sum of all transaction amounts (in base currency)
    - **count**: Number of transactions

    **Note**: Transfer transactions are automatically excluded from analytics.
    """
    total, count = analytics_service.get_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category_id=category_id,
        account_id=account_id,
        payee_id=payee_id
    )

    return AnalyticsSummaryResponse(total=total, count=count)


@router.get(
    "/breakdown",
    response_model=AnalyticsBreakdownResponse,
    summary="Get breakdown of transactions by dimension"
)
def get_breakdown(
    dimension: BreakdownDimension = Query(..., description="Group by dimension (category, payee, or account)"),
    metric: BreakdownMetric = Query("sum", description="Aggregation metric (sum or count)"),
    start_date: Optional[date] = Query(None, description="Filter by transaction date >= start_date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by transaction date <= end_date (YYYY-MM-DD)"),
    transaction_type: Optional[AnalyticsTransactionType] = Query(None, description="Filter by transaction type (expense or income)"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: Session = Depends(get_db)
):
    """
    Group transactions by a dimension and calculate aggregated metrics.

    **Purpose**: Visualize spending/income distribution (e.g., "How much per category?", "Top payees")

    **Dimensions:**
    - **category**: Group by category names (e.g., "Groceries", "Transportation")
    - **payee**: Group by payee names (e.g., "Amazon", "Whole Foods")
    - **account**: Group by account names (e.g., "Checking", "Savings")

    **Metrics:**
    - **sum**: Total amount for each group (default)
    - **count**: Number of transactions for each group

    **Filters:**
    - **start_date**: Show transactions on or after this date
    - **end_date**: Show transactions on or before this date
    - **transaction_type**: 'expense' or 'income' (transfers are automatically excluded)
    - **account_id**: Filter by specific account (not used when dimension=account)

    **Returns:**
    - **labels**: Names of dimension values (sorted by value descending)
    - **values**: Aggregated metric for each label

    **Example Use Cases:**
    - Pie chart of spending by category
    - Bar chart of top merchants
    - Account balance comparison

    **Note**: Transfer transactions are automatically excluded from analytics.
    """
    labels, values = analytics_service.get_breakdown(
        db=db,
        dimension=dimension,
        metric=metric,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        account_id=account_id
    )

    return AnalyticsBreakdownResponse(labels=labels, values=values)


@router.get(
    "/trend",
    response_model=AnalyticsTrendResponse,
    summary="Get time series trend of transactions"
)
def get_trend(
    time_grain: TrendTimeGrain = Query(..., description="Time granularity (day, week, or month)"),
    start_date: Optional[date] = Query(None, description="Filter by transaction date >= start_date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by transaction date <= end_date (YYYY-MM-DD)"),
    transaction_type: Optional[AnalyticsTransactionType] = Query(None, description="Filter by transaction type (expense or income)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: Session = Depends(get_db)
):
    """
    Calculate time series trend of transaction amounts over time.

    **Purpose**: Visualize spending/income patterns over time (e.g., "Monthly spending trend")

    **Time Granularity:**
    - **day**: Group by each day
    - **week**: Group by week (starting Monday in PostgreSQL)
    - **month**: Group by month

    **Filters:**
    - **start_date**: Show transactions on or after this date
    - **end_date**: Show transactions on or before this date
    - **transaction_type**: 'expense' or 'income' (transfers are automatically excluded)
    - **category_id**: Filter by specific category
    - **account_id**: Filter by specific account

    **Returns:**
    - **dates**: Time period labels in ISO format (YYYY-MM-DD)
    - **values**: Sum of transaction amounts for each period

    **Example Use Cases:**
    - Line chart of monthly expenses
    - Area chart of daily income
    - Weekly spending comparison

    **Note**: Transfer transactions are automatically excluded from analytics.
    """
    dates, values = analytics_service.get_trend(
        db=db,
        time_grain=time_grain,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category_id=category_id,
        account_id=account_id
    )

    return AnalyticsTrendResponse(dates=dates, values=values)
