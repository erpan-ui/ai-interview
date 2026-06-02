from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.client.deps import get_current_user
from app.services.client.resume_service import resume_service
from app.schemas.response import ApiResponse
from app.models.user import User
from app.exceptions.http_exceptions import ValidationError

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    target_position: str = Form(default="Python后端开发工程师"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传简历 PDF 并触发 AI 解析"""
    # 验证文件类型
    if not file.filename.lower().endswith(".pdf"):
        raise ValidationError(message="仅支持 PDF 格式文件")

    # 验证文件大小（最大 10MB）
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise ValidationError(message="文件大小不能超过 10MB")

    result = await resume_service.upload_and_parse(
        db=db,
        user_id=current_user.id,
        file_content=content,
        file_name=file.filename,
        target_position=target_position
    )
    return ApiResponse.success(data=result)


@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取简历详情（含解析内容和分析报告）"""
    result = await resume_service.get_resume(db, resume_id, current_user.id)
    return ApiResponse.success(data=result)


@router.get("")
async def get_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有简历列表"""
    result = await resume_service.get_user_resumes(db, current_user.id)
    return ApiResponse.success(data=result)
