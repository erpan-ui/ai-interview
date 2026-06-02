import json
import logging
import os
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.resume import Resume
from app.services.client.ai_service import AIService
from app.exceptions.http_exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

# 简历上传目录
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ResumeService:

    @staticmethod
    async def upload_and_parse(
        db: AsyncSession,
        user_id: int,
        file_content: bytes,
        file_name: str,
        target_position: str
    ) -> Dict:
        """上传简历文件并触发 AI 解析和分析"""
        # 保存文件到本地
        file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{file_name}")
        with open(file_path, "wb") as f:
            f.write(file_content)

        # 创建简历记录
        resume = Resume(
            user_id=user_id,
            file_url=file_path,
            file_name=file_name,
            target_position=target_position,
            status="parsing"
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        # 从 PDF 中提取文本
        try:
            resume_text = ResumeService._extract_pdf_text(file_path)
            if not resume_text.strip():
                raise ValidationError(message="无法从 PDF 中提取文本内容")
        except Exception as e:
            resume.status = "failed"
            await db.commit()
            raise ValidationError(message=f"PDF 解析失败: {str(e)}")

        # 调用 AI 解析简历
        try:
            parsed = await AIService.parse_resume(resume_text)
            resume.parsed_content = json.dumps(parsed, ensure_ascii=False)

            # 调用 AI 分析简历质量
            analysis = await AIService.analyze_resume(parsed, target_position)
            resume.analysis = json.dumps(analysis, ensure_ascii=False)

            resume.status = "completed"
            await db.commit()
            await db.refresh(resume)
        except Exception as e:
            logger.error(f"AI 简历解析失败: {e}")
            resume.status = "failed"
            await db.commit()
            raise

        return {
            "resume_id": resume.id,
            "status": resume.status,
            "message": "简历上传并解析成功"
        }

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """从 PDF 文件中提取文本内容"""
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    async def get_resume(db: AsyncSession, resume_id: int, user_id: int) -> Dict:
        """根据 ID 获取简历详情"""
        query = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id
        )
        result = await db.execute(query)
        resume = result.scalar_one_or_none()

        if not resume:
            raise NotFoundError(message="简历不存在")

        parsed_content = None
        if resume.parsed_content:
            try:
                parsed_content = json.loads(resume.parsed_content)
            except json.JSONDecodeError:
                parsed_content = None

        analysis = None
        if resume.analysis:
            try:
                analysis = json.loads(resume.analysis)
            except json.JSONDecodeError:
                analysis = None

        return {
            "resume_id": resume.id,
            "status": resume.status,
            "file_name": resume.file_name,
            "target_position": resume.target_position,
            "parsed_content": parsed_content,
            "analysis": analysis,
            "created_at": resume.created_at.isoformat() if resume.created_at else None
        }

    @staticmethod
    async def get_user_resumes(db: AsyncSession, user_id: int) -> list:
        """获取用户的所有简历列表"""
        query = select(Resume).where(
            Resume.user_id == user_id
        ).order_by(Resume.created_at.desc())
        result = await db.execute(query)
        resumes = result.scalars().all()

        return [
            {
                "resume_id": r.id,
                "file_name": r.file_name,
                "target_position": r.target_position,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in resumes
        ]


resume_service = ResumeService()
