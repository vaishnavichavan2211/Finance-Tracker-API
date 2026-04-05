

from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordCategory, TransactionType
from app.models.user import User, UserRole
from app.schemas.record import RecordCreateRequest, RecordUpdateRequest


# ────────────────────────────────────────────────────────────────────────────
# CRUD helpers
# ────────────────────────────────────────────────────────────────────────────

def create_record(db: Session, payload: RecordCreateRequest, owner: User) -> FinancialRecord:
    """Add a new income/expense record for the logged-in user."""
    new_record = FinancialRecord(
        amount   = payload.amount,
        txn_type = payload.txn_type,
        category = payload.category,
        txn_date = payload.txn_date,
        notes    = payload.notes,
        owner_id = owner.user_id,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


def get_record_by_id(db: Session, record_id: int, requesting_user: User) -> FinancialRecord:
    """
    Fetch one record.
    Admins can see any record; other users only see their own.
    """
    db_record = db.query(FinancialRecord).filter(
        FinancialRecord.record_id == record_id
    ).first()

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record {record_id} not found.",
        )

    # Non-admins cannot peek at other users' data
    if requesting_user.role != UserRole.ADMIN and db_record.owner_id != requesting_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this record.",
        )

    return db_record


def get_filtered_records(
    db: Session,
    requesting_user: User,
    txn_type: Optional[TransactionType] = None,
    category: Optional[RecordCategory]  = None,
    start_date: Optional[date]          = None,
    end_date: Optional[date]            = None,
    page: int  = 1,
    page_size: int = 10,
):
    """
    Return paginated records with optional filters.
    Admins see all records; regular users see only theirs.
    Returns a tuple: (records_list, total_count).
    """
    query = db.query(FinancialRecord)

    # Scope to current user unless admin
    if requesting_user.role != UserRole.ADMIN:
        query = query.filter(FinancialRecord.owner_id == requesting_user.user_id)

    # Apply optional filters
    if txn_type:
        query = query.filter(FinancialRecord.txn_type == txn_type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if start_date:
        query = query.filter(FinancialRecord.txn_date >= start_date)
    if end_date:
        query = query.filter(FinancialRecord.txn_date <= end_date)

    # Sort newest first
    query = query.order_by(FinancialRecord.txn_date.desc())

    total_count = query.count()

    # Paginate: skip earlier pages, take `page_size` records
    offset = (page - 1) * page_size
    records = query.offset(offset).limit(page_size).all()

    return records, total_count


def update_record(
    db: Session,
    record_id: int,
    payload: RecordUpdateRequest,
    requesting_user: User,
) -> FinancialRecord:
    """Partially update a record. Only the owner or an Admin may do this."""
    db_record = get_record_by_id(db, record_id, requesting_user)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, record_id: int, requesting_user: User) -> dict:
    """Delete a record. Only the owner or an Admin may do this."""
    db_record = get_record_by_id(db, record_id, requesting_user)
    db.delete(db_record)
    db.commit()
    return {"message": f"Record {record_id} deleted successfully."}


# ────────────────────────────────────────────────────────────────────────────
# Analytics / Summary queries
# ────────────────────────────────────────────────────────────────────────────

def _base_query(db: Session, user: User):
    """Helper: return a query scoped to the right user(s)."""
    q = db.query(FinancialRecord)
    if user.role != UserRole.ADMIN:
        q = q.filter(FinancialRecord.owner_id == user.user_id)
    return q


def get_balance_summary(db: Session, user: User) -> dict:
    """Compute total income, total expenses, and net balance."""
    base = _base_query(db, user)

    # SQLAlchemy's func.sum returns None if there are no rows — default to 0
    total_income = base.filter(
        FinancialRecord.txn_type == TransactionType.INCOME
    ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0.0

    total_expenses = base.filter(
        FinancialRecord.txn_type == TransactionType.EXPENSE
    ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0.0

    return {
        "total_income":   round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance":    round(total_income - total_expenses, 2),
    }


def get_monthly_summary(db: Session, user: User) -> List[dict]:
    """
    Group records by year and month, returning income/expense totals per month.
    Great for building bar charts in a frontend dashboard!
    """
    base = _base_query(db, user)

    rows = (
        base.with_entities(
            extract("year",  FinancialRecord.txn_date).label("yr"),
            extract("month", FinancialRecord.txn_date).label("mo"),
            FinancialRecord.txn_type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .group_by("yr", "mo", FinancialRecord.txn_type)
        .order_by("yr", "mo")
        .all()
    )

    # Pivot rows into one dict per (year, month)
    monthly: dict = {}
    for row in rows:
        key = (int(row.yr), int(row.mo))
        if key not in monthly:
            monthly[key] = {"year": key[0], "month": key[1],
                             "total_income": 0.0, "total_expenses": 0.0}
        if row.txn_type == TransactionType.INCOME:
            monthly[key]["total_income"] = round(row.total, 2)
        else:
            monthly[key]["total_expenses"] = round(row.total, 2)

    result = []
    for entry in monthly.values():
        entry["net_balance"] = round(entry["total_income"] - entry["total_expenses"], 2)
        result.append(entry)

    return result


def get_category_breakdown(db: Session, user: User) -> List[dict]:
    """
    Breakdown spending/earning by category.
    Each row shows the category, type, total amount, and record count.
    """
    base = _base_query(db, user)

    rows = (
        base.with_entities(
            FinancialRecord.category,
            FinancialRecord.txn_type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.record_id).label("count"),
        )
        .group_by(FinancialRecord.category, FinancialRecord.txn_type)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )

    return [
        {
            "category":  row.category,
            "txn_type":  row.txn_type,
            "total":     round(row.total, 2),
            "count":     row.count,
        }
        for row in rows
    ]
