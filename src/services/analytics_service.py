"""
Analytics service layer implementing business logic for analytics operations.
Handles aggregation and analysis of transaction data for visualizations.
"""
from typing import Optional, Tuple, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.transaction import Transaction
from src.models.category import Category
from src.models.payee import Payee
from src.models.account import Account


def get_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    payee_id: Optional[int] = None,
) -> Tuple[float, int]:
    """
    Calculate summary statistics (total amount and count) for filtered transactions.

    Args:
        db: Database session
        start_date: Filter by transaction date >= start_date
        end_date: Filter by transaction date <= end_date
        transaction_type: Filter by transaction type ('expense' or 'income')
        category_id: Filter by category ID
        account_id: Filter by account ID
        payee_id: Filter by payee ID

    Returns:
        Tuple of (total_amount, transaction_count)

    Note:
        Transfer transactions are automatically excluded from analytics.
    """
    # Start with base query, excluding transfers
    query = db.query(
        func.coalesce(func.sum(Transaction.base_amount), 0).label("total"),
        func.count(Transaction.transaction_id).label("count")
    ).filter(Transaction.transaction_type != "transfer")

    # Apply filters
    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)
    if transaction_type is not None:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)
    if payee_id is not None:
        query = query.filter(Transaction.payee_id == payee_id)

    # Execute query
    result = query.one()
    return float(result.total), result.count


def get_breakdown(
    db: Session,
    dimension: str,
    metric: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    account_id: Optional[int] = None,
) -> Tuple[List[str], List[float]]:
    """
    Group transactions by a dimension and calculate metrics.

    Args:
        db: Database session
        dimension: Grouping dimension ('category', 'payee', or 'account')
        metric: Aggregation metric ('sum' or 'count')
        start_date: Filter by transaction date >= start_date
        end_date: Filter by transaction date <= end_date
        transaction_type: Filter by transaction type ('expense' or 'income')
        account_id: Filter by account ID

    Returns:
        Tuple of (labels, values) where labels are dimension names and values are aggregated metrics

    Note:
        Transfer transactions are automatically excluded from analytics.
    """
    # Determine which field to aggregate
    if metric == "sum":
        metric_field = func.sum(Transaction.base_amount)
    else:  # count
        metric_field = func.count(Transaction.transaction_id)

    # Determine which dimension to group by
    if dimension == "category":
        dimension_table = Category
        dimension_key = Transaction.category_id
        dimension_fk = Category.category_id
        dimension_name = Category.category_name
    elif dimension == "payee":
        dimension_table = Payee
        dimension_key = Transaction.payee_id
        dimension_fk = Payee.payee_id
        dimension_name = Payee.payee_name
    else:  # account
        dimension_table = Account
        dimension_key = Transaction.account_id
        dimension_fk = Account.account_id
        dimension_name = Account.account_name

    # Build query with join
    query = db.query(
        dimension_name.label("label"),
        metric_field.label("value")
    ).select_from(Transaction).join(
        dimension_table, dimension_key == dimension_fk
    ).filter(
        Transaction.transaction_type != "transfer"
    )

    # Apply filters
    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)
    if transaction_type is not None:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if account_id is not None and dimension != "account":
        query = query.filter(Transaction.account_id == account_id)

    # Group by dimension and order by value descending
    query = query.group_by(dimension_name).order_by(func.coalesce(metric_field, 0).desc())

    # Execute query
    results = query.all()

    # Separate into labels and values
    labels = [row.label for row in results]
    values = [float(row.value) if row.value is not None else 0.0 for row in results]

    return labels, values


def get_trend(
    db: Session,
    time_grain: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
) -> Tuple[List[str], List[float]]:
    """
    Calculate time series trend of transaction amounts.

    Args:
        db: Database session
        time_grain: Time granularity ('day', 'week', or 'month')
        start_date: Filter by transaction date >= start_date
        end_date: Filter by transaction date <= end_date
        transaction_type: Filter by transaction type ('expense' or 'income')
        category_id: Filter by category ID
        account_id: Filter by account ID

    Returns:
        Tuple of (dates, values) where dates are ISO format strings and values are summed amounts

    Note:
        Transfer transactions are automatically excluded from analytics.
    """
    # Determine date truncation based on time_grain
    if time_grain == "day":
        date_trunc = func.date(Transaction.transaction_date)
    elif time_grain == "week":
        # PostgreSQL: date_trunc('week', transaction_date)
        date_trunc = func.date_trunc('week', Transaction.transaction_date)
    else:  # month
        # PostgreSQL: date_trunc('month', transaction_date)
        date_trunc = func.date_trunc('month', Transaction.transaction_date)

    # Build query
    query = db.query(
        date_trunc.label("period"),
        func.sum(Transaction.base_amount).label("value")
    ).filter(
        Transaction.transaction_type != "transfer"
    )

    # Apply filters
    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)
    if transaction_type is not None:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)

    # Group by period and order by period
    query = query.group_by("period").order_by("period")

    # Execute query
    results = query.all()

    # Format dates and values
    dates = []
    values = []
    for row in results:
        if row.period:
            # Convert to date and format as ISO string (check datetime first since it's a subclass of date)
            if isinstance(row.period, datetime):
                dates.append(row.period.date().isoformat())
            elif isinstance(row.period, date):
                dates.append(row.period.isoformat())
            else:
                dates.append(str(row.period))
            values.append(float(row.value) if row.value is not None else 0.0)

    return dates, values
