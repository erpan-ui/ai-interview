from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
from datetime import datetime

from app.db.session import get_db
from app.schemas.backoffice.waiting_list import WaitingListItemResponse
from app.services.backoffice.waiting_list import waiting_list_service
from app.api.backoffice.deps import get_current_admin
from app.models.admin import Admin
from app.schemas.paginator import Paginator


router = APIRouter()


@router.get("")
async def list_waiting_list(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search keyword (supports first_name + last_name combination for 'name' type, e.g., 'sky bao')"),
    search_type: Optional[Literal['all', 'name', 'email']] = Query(
        'all',
        description="Search type: 'all' (search in name and email), 'name' (search in first_name and last_name), 'email' (search in email only)"
    ),
    status: Optional[str] = Query('all', description="Filter by status: 'active' (verified), 'invited' (unverified), 'all'"),
    start_date: Optional[datetime] = Query(None, description="Start date for application date filter (ISO 8601 format)"),
    end_date: Optional[datetime] = Query(None, description="End date for application date filter (ISO 8601 format)"),
    sort_by: str = Query('created_at', description="Sort field: 'created_at', 'email', 'university'"),
    sort_order: str = Query('desc', description="Sort order: 'asc' or 'desc'"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get waiting list with pagination, search, and filters

    This endpoint retrieves the waiting list entries with support for:
    - Pagination (page, per_page)
    - Search with type specification (all/name/email)
      - 'all': Search in both name (first_name + last_name) and email
      - 'name': Search in first_name and last_name (supports combination like 'sky bao')
      - 'email': Search in email only
    - Status filter: 'active' (verified users), 'invited' (unverified users), 'all' (default)
    - Date range filter (start_date, end_date)
    - Sorting by created_at, email, or university
    - Sort order: ascending or descending

    Returns paginated results with metadata.
    """
    query = await waiting_list_service.get_waiting_list_query(
        db=db,
        search=search,
        search_type=search_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )

    paginator = Paginator(query, db)
    result = await paginator.paginate(page, per_page)
    result = result.map(WaitingListItemResponse)

    return result.response()