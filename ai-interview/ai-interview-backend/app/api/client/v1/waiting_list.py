from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.waiting_list import (
    WaitingListSubmitRequest,
    WaitingListSubmitResponse,
    WaitingListResendRequest,
    WaitingListVerifyResponse
)
from app.services.client.waiting_list import waiting_list_service
from app.schemas.response import ApiResponse

router = APIRouter()


@router.post("/submit")
async def submit_waiting_list(
    request: WaitingListSubmitRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit waiting list application
    """
    ip_address = req.client.host
    user_agent = req.headers.get("user-agent", "")

    result = await waiting_list_service.submit_application(
        db,
        request.model_dump(),
        ip_address,
        user_agent
    )

    return ApiResponse.success(data=result)


@router.get("/verify")
async def verify_waiting_list_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify waiting list email
    """
    result = await waiting_list_service.verify_email(db, token)
    return ApiResponse.success(data=result)


@router.post("/resend-verification")
async def resend_waiting_list_verification(
    request: WaitingListResendRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend waiting list verification email
    """
    ip_address = req.client.host

    result = await waiting_list_service.resend_verification(
        db,
        request.email,
        ip_address
    )

    return ApiResponse.success(data=result)