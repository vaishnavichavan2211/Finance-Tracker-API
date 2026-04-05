

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, require_analyst_or_above
from app.models.record import RecordCategory, TransactionType
from app.models.user import User
from app.schemas.record import (
    PaginatedRecordsResponse,
    RecordCreateRequest,
    RecordResponse,
    RecordUpdateRequest,
)
from app.services import record_service

router = APIRouter()


@router.post(
    "/",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new income or expense record",
)
def add_record(
    payload: RecordCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),  # Viewers blocked
):
   
    return record_service.create_record(db, payload, owner=current_user)


@router.get(
    "/",
    response_model=PaginatedRecordsResponse,
    summary="List records with optional filters and pagination",
)
def list_records(
    # ── Filter params ──────────────────────────────────────────────
    txn_type:   Optional[TransactionType] = Query(None, description="Filter by income/expense"),
    category:   Optional[RecordCategory]  = Query(None, description="Filter by category"),
    start_date: Optional[date]            = Query(None, description="From date (YYYY-MM-DD)"),
    end_date:   Optional[date]            = Query(None, description="To date (YYYY-MM-DD)"),
    # ── Pagination params ──────────────────────────────────────────
    page:       int = Query(1,  ge=1,  description="Page number (starts at 1)"),
    page_size:  int = Query(10, ge=1, le=100, description="Records per page (max 100)"),
    # ── Injected dependencies ──────────────────────────────────────
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records, total_count = record_service.get_filtered_records(
        db, current_user,
        txn_type=txn_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    return PaginatedRecordsResponse(
        total_count  = total_count,
        page         = page,
        page_size    = page_size,
        total_pages  = math.ceil(total_count / page_size) if total_count else 1,
        records      = records,
    )


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Get a single record by ID",
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a specific record. You can only view your own (Admins see all)."""
    return record_service.get_record_by_id(db, record_id, current_user)


@router.put(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Update a record (Analyst/Admin)",
)
def update_record(
    record_id: int,
    payload: RecordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
    """
    Partially update a financial record.
    Only the record owner or an Admin may make changes.
    """
    return record_service.update_record(db, record_id, payload, current_user)


@router.delete(
    "/{record_id}",
    summary="Delete a record (Admin only)",
    status_code=status.HTTP_200_OK,
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),   # Only admins can delete
):
    """Permanently delete a financial record. Admin access required."""
    return record_service.delete_record(db, record_id, current_user)
