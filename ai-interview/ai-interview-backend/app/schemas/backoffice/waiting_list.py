from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class WaitingListQueryParams(BaseModel):
    """Waiting list query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search by email or name")
    status: Optional[Literal['active', 'invited', 'all']] = Field(
        'all',
        description="Filter by status. 'active' = verified users, 'invited' = unverified users, 'all' = all users",
        json_schema_extra={"enum": ["active", "invited", "all"]}
    )
    start_date: Optional[datetime] = Field(None, description="Start date for application date filter")
    end_date: Optional[datetime] = Field(None, description="End date for application date filter")
    sort_by: Optional[str] = Field('created_at', description="Sort field (created_at, email, university)")
    sort_order: Optional[Literal['asc', 'desc']] = Field(
        'desc',
        description="Sort order. 'asc' = ascending, 'desc' = descending",
        json_schema_extra={"enum": ["asc", "desc"]}
    )


class WaitingListItemResponse(BaseModel):
    """Waiting list item response"""
    id: int
    first_name: str
    last_name: str
    email: str
    university: Optional[str]
    is_verified: bool
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def status(self) -> str:
        """Get status label"""
        return 'Active' if self.is_verified else 'Invited'

    class Config:
        from_attributes = True