import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.api.backoffice.deps import get_current_admin
from app.models.admin import Admin
from app.models.interview import Interview
from app.models.interview_message import InterviewMessage
from app.models.user import User
from app.schemas.response import ApiResponse
from app.services.client.interview_service import interview_service

router = APIRouter()


@router.get("")
async def list_interviews(
    page: int = 1,
    per_page: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取面试记录列表"""
    query = select(Interview, User.email).join(User, Interview.user_id == User.id).order_by(Interview.created_at.desc())
    count_query = select(func.count()).select_from(Interview)

    if status:
        query = query.where(Interview.status == status)
        count_query = count_query.where(Interview.status == status)

    total = await db.scalar(count_query)
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    rows = result.all()

    items = [
        {
            "id": interview.id,
            "user_email": email,
            "target_position": interview.target_position,
            "difficulty": interview.difficulty,
            "total_questions": interview.total_questions,
            "overall_score": float(interview.overall_score) if interview.overall_score else None,
            "status": interview.status,
            "created_at": interview.created_at.isoformat() if interview.created_at else None
        }
        for interview, email in rows
    ]

    return ApiResponse.success(data={"items": items, "total": total, "page": page, "per_page": per_page})


@router.get("/{interview_id}")
async def get_interview_detail(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取面试详情（含对话记录和报告）"""
    interview = await db.get(Interview, interview_id)
    if not interview:
        return ApiResponse.failed(message="面试记录不存在", body_code=404, http_code=404)

    # 获取对话记录
    msg_query = select(InterviewMessage).where(
        InterviewMessage.interview_id == interview_id
    ).order_by(InterviewMessage.id)
    msg_result = await db.execute(msg_query)
    messages = msg_result.scalars().all()

    report = {}
    if interview.report:
        try:
            report = json.loads(interview.report)
        except json.JSONDecodeError:
            report = {}

    return ApiResponse.success(data={
        "id": interview.id,
        "target_position": interview.target_position,
        "difficulty": interview.difficulty,
        "total_questions": interview.total_questions,
        "overall_score": float(interview.overall_score) if interview.overall_score else None,
        "status": interview.status,
        "report": report,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "question_index": m.question_index,
                "score": float(m.score) if m.score else None,
                "feedback": m.feedback
            }
            for m in messages
        ],
        "created_at": interview.created_at.isoformat() if interview.created_at else None
    })


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """管理员删除面试记录"""
    result = await interview_service.delete_interview_admin(db, interview_id)
    return ApiResponse.success(data=result)
