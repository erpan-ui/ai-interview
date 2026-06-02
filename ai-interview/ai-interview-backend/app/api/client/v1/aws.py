from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils import utils
from app.db.session import get_db
from app.api.client.deps import get_current_user
from app.exceptions.http_exceptions import APIException
from app.schemas.response import ApiResponse
from typing import Optional

router = APIRouter()


@router.get("/temporary-credentials")
async def get_temporary_credentials(
    language: str = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取S3临时访问凭证"""
    try:
        temporary_credentials = utils.get_temporary_credentials()
        return ApiResponse.success(data=temporary_credentials)
    except Exception as e:
        raise APIException(status_code=500, message=str(e), language=language)
