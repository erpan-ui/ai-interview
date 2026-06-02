import json
import logging
from decimal import Decimal
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.interview import Interview
from app.models.interview_message import InterviewMessage
from app.models.resume import Resume
from app.services.client.ai_service import AIService
from app.exceptions.http_exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class InterviewService:

    @staticmethod
    async def start_interview(
        db: AsyncSession,
        user_id: int,
        resume_id: int,
        target_position: str,
        difficulty: str,
        total_questions: int
    ) -> Dict:
        """开始新的面试会话"""
        # 验证简历是否存在且已解析
        query = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id
        )
        result = await db.execute(query)
        resume = result.scalar_one_or_none()

        if not resume:
            raise NotFoundError(message="简历不存在")
        if resume.status != "completed":
            raise ValidationError(message="简历尚未解析完成")

        parsed_resume = json.loads(resume.parsed_content)

        # 通过 AI 生成面试题目
        questions = await AIService.generate_questions(
            parsed_resume=parsed_resume,
            target_position=target_position,
            difficulty=difficulty,
            count=total_questions
        )

        # 创建面试记录
        interview = Interview(
            user_id=user_id,
            resume_id=resume_id,
            target_position=target_position,
            difficulty=difficulty,
            total_questions=total_questions,
            current_question_index=0,
            questions_data=questions,
            status="in_progress"
        )
        db.add(interview)
        await db.commit()
        await db.refresh(interview)

        # 保存第一道题作为面试官消息
        first_question = questions[0]["question"]
        msg = InterviewMessage(
            interview_id=interview.id,
            role="interviewer",
            content=first_question,
            question_index=0
        )
        db.add(msg)
        await db.commit()

        return {
            "interview_id": interview.id,
            "first_question": first_question,
            "question_index": 0,
            "total_questions": total_questions
        }

    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        user_id: int,
        interview_id: int,
        answer: str
    ) -> Dict:
        """提交当前题目的回答并获取 AI 评估"""
        # 获取面试记录
        query = select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id
        )
        result = await db.execute(query)
        interview = result.scalar_one_or_none()

        if not interview:
            raise NotFoundError(message="面试记录不存在")
        if interview.status == "completed":
            raise ValidationError(message="面试已结束")

        # 获取简历上下文
        resume_query = select(Resume).where(Resume.id == interview.resume_id)
        resume_result = await db.execute(resume_query)
        resume = resume_result.scalar_one_or_none()
        parsed_resume = json.loads(resume.parsed_content) if resume and resume.parsed_content else {}

        # 获取对话历史
        msg_query = select(InterviewMessage).where(
            InterviewMessage.interview_id == interview_id
        ).order_by(InterviewMessage.id)
        msg_result = await db.execute(msg_query)
        messages = msg_result.scalars().all()
        chat_history = [{"role": m.role, "content": m.content} for m in messages]

        # 当前题目
        current_index = interview.current_question_index
        questions = interview.questions_data
        current_question = questions[current_index]["question"]

        # 保存候选人回答
        candidate_msg = InterviewMessage(
            interview_id=interview_id,
            role="candidate",
            content=answer,
            question_index=current_index
        )
        db.add(candidate_msg)

        # 调用 AI 评估回答
        evaluation = await AIService.evaluate_answer(
            question=current_question,
            answer=answer,
            resume_context=parsed_resume,
            chat_history=chat_history
        )

        score = float(evaluation.get("score", 5.0))
        feedback = evaluation.get("feedback", "")

        # 更新候选人消息的评分
        candidate_msg.score = Decimal(str(score))
        candidate_msg.feedback = feedback

        # 检查是否为最后一题
        next_index = current_index + 1
        is_finished = next_index >= interview.total_questions

        response = {
            "score": score,
            "feedback": feedback,
            "question_index": current_index,
            "is_finished": is_finished,
            "next_question": None
        }

        if is_finished:
            # 生成最终报告
            interview.status = "completed"
            interview.current_question_index = next_index

            # 计算总分
            all_scores = []
            score_query = select(InterviewMessage).where(
                InterviewMessage.interview_id == interview_id,
                InterviewMessage.role == "candidate",
                InterviewMessage.score.isnot(None)
            )
            score_result = await db.execute(score_query)
            scored_msgs = score_result.scalars().all()
            all_scores = [float(m.score) for m in scored_msgs]
            all_scores.append(score)  # 加上当前评分

            overall = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
            interview.overall_score = Decimal(str(overall))

            # 生成评估报告
            qa_data = []
            for i, q in enumerate(questions):
                q_msgs = [m for m in messages if m.role == "candidate" and m.question_index == i]
                qa_data.append({
                    "question": q["question"],
                    "answer": q_msgs[0].content if q_msgs else answer if i == current_index else "未回答",
                    "score": float(q_msgs[0].score) if q_msgs and q_msgs[0].score else score if i == current_index else 0
                })

            try:
                report = await AIService.generate_report(
                    parsed_resume=parsed_resume,
                    target_position=interview.target_position,
                    questions_and_scores=qa_data
                )
                # 将每题评分加入报告
                report["question_scores"] = [
                    {"question": q["question"], "score": qa["score"], "feedback": ""}
                    for q, qa in zip(questions, qa_data)
                ]
                interview.report = json.dumps(report, ensure_ascii=False)
            except Exception as e:
                logger.error(f"报告生成失败: {e}")
                interview.report = json.dumps({"summary": "报告生成失败", "strengths": [], "weaknesses": [], "suggestions": []})

        else:
            # 进入下一题
            interview.current_question_index = next_index
            next_question = questions[next_index]["question"]
            response["next_question"] = next_question

            # 保存下一题作为面试官消息
            interviewer_msg = InterviewMessage(
                interview_id=interview_id,
                role="interviewer",
                content=next_question,
                question_index=next_index
            )
            db.add(interviewer_msg)

        await db.commit()
        return response

    @staticmethod
    async def submit_answer_stream(
        db: AsyncSession,
        user_id: int,
        interview_id: int,
        answer: str
    ):
        """流式提交回答 - 通过 SSE 逐块推送 AI 评语"""
        import re

        # 获取面试记录
        query = select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id
        )
        result = await db.execute(query)
        interview = result.scalar_one_or_none()

        if not interview:
            yield f"data: {json.dumps({'type': 'error', 'content': '面试记录不存在'})}\n\n"
            return
        if interview.status == "completed":
            yield f"data: {json.dumps({'type': 'error', 'content': '面试已结束'})}\n\n"
            return

        # 获取简历上下文
        resume_query = select(Resume).where(Resume.id == interview.resume_id)
        resume_result = await db.execute(resume_query)
        resume = resume_result.scalar_one_or_none()
        parsed_resume = json.loads(resume.parsed_content) if resume and resume.parsed_content else {}

        # 获取对话历史
        msg_query = select(InterviewMessage).where(
            InterviewMessage.interview_id == interview_id
        ).order_by(InterviewMessage.id)
        msg_result = await db.execute(msg_query)
        messages = msg_result.scalars().all()
        chat_history = [{"role": m.role, "content": m.content} for m in messages]

        current_index = interview.current_question_index
        questions = interview.questions_data
        current_question = questions[current_index]["question"]

        # 保存候选人回答
        candidate_msg = InterviewMessage(
            interview_id=interview_id,
            role="candidate",
            content=answer,
            question_index=current_index
        )
        db.add(candidate_msg)
        await db.flush()

        # 流式评估回答
        full_text = ""
        async for chunk in AIService.evaluate_answer_stream(
            question=current_question,
            answer=answer,
            resume_context=parsed_resume,
            chat_history=chat_history
        ):
            full_text += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

        # 从流式文本中提取评分
        score = 5.0
        feedback = full_text.strip()
        json_match = re.search(r'\{[^}]*"score"\s*:\s*([\d.]+)[^}]*\}', full_text)
        if json_match:
            try:
                score = float(json_match.group(1))
                # 从反馈中移除 JSON 块
                feedback = re.sub(r'```json\s*\{[^}]*\}\s*```', '', feedback).strip()
                feedback = re.sub(r'\{[^}]*"score"[^}]*\}', '', feedback).strip()
            except (ValueError, IndexError):
                pass

        candidate_msg.score = Decimal(str(score))
        candidate_msg.feedback = feedback[:200]

        # 检查是否为最后一题
        next_index = current_index + 1
        is_finished = next_index >= interview.total_questions

        if is_finished:
            interview.status = "completed"
            interview.current_question_index = next_index

            # 计算总分
            all_scores = []
            score_query = select(InterviewMessage).where(
                InterviewMessage.interview_id == interview_id,
                InterviewMessage.role == "candidate",
                InterviewMessage.score.isnot(None)
            )
            score_result = await db.execute(score_query)
            scored_msgs = score_result.scalars().all()
            all_scores = [float(m.score) for m in scored_msgs]
            if candidate_msg.score:
                all_scores.append(float(candidate_msg.score))
            overall = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
            interview.overall_score = Decimal(str(overall))

            # 生成评估报告
            qa_data = []
            for i, q in enumerate(questions):
                q_msgs = [m for m in messages if m.role == "candidate" and m.question_index == i]
                qa_data.append({
                    "question": q["question"],
                    "answer": q_msgs[0].content if q_msgs else answer if i == current_index else "未回答",
                    "score": float(q_msgs[0].score) if q_msgs and q_msgs[0].score else score if i == current_index else 0
                })
            try:
                report = await AIService.generate_report(
                    parsed_resume=parsed_resume,
                    target_position=interview.target_position,
                    questions_and_scores=qa_data
                )
                report["question_scores"] = [
                    {"question": q["question"], "score": qa["score"], "feedback": ""}
                    for q, qa in zip(questions, qa_data)
                ]
                interview.report = json.dumps(report, ensure_ascii=False)
            except Exception as e:
                logger.error(f"报告生成失败: {e}")
                interview.report = json.dumps({"summary": "报告生成失败", "strengths": [], "weaknesses": [], "suggestions": []})

            await db.commit()
            yield f"data: {json.dumps({'type': 'done', 'score': score, 'feedback': feedback[:200], 'is_finished': True, 'question_index': current_index}, ensure_ascii=False)}\n\n"
        else:
            # 进入下一题
            interview.current_question_index = next_index
            next_question = questions[next_index]["question"]

            interviewer_msg = InterviewMessage(
                interview_id=interview_id,
                role="interviewer",
                content=next_question,
                question_index=next_index
            )
            db.add(interviewer_msg)
            await db.commit()
            yield f"data: {json.dumps({'type': 'done', 'score': score, 'feedback': feedback[:200], 'is_finished': False, 'next_question': next_question, 'question_index': current_index}, ensure_ascii=False)}\n\n"

    @staticmethod
    async def get_report(
        db: AsyncSession,
        user_id: int,
        interview_id: int
    ) -> Dict:
        """获取面试评估报告"""
        query = select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id
        )
        result = await db.execute(query)
        interview = result.scalar_one_or_none()

        if not interview:
            raise NotFoundError(message="面试记录不存在")
        if interview.status != "completed":
            raise ValidationError(message="面试尚未完成")

        report = {}
        if interview.report:
            try:
                report = json.loads(interview.report)
            except json.JSONDecodeError:
                report = {}

        return {
            "interview_id": interview.id,
            "overall_score": float(interview.overall_score) if interview.overall_score else 0,
            "total_questions": interview.total_questions,
            "report": report
        }

    @staticmethod
    async def get_interviews(
        db: AsyncSession,
        user_id: int
    ) -> Dict:
        """获取用户的所有面试记录"""
        query = select(Interview).where(
            Interview.user_id == user_id
        ).order_by(Interview.created_at.desc())
        result = await db.execute(query)
        interviews = result.scalars().all()

        items = [
            {
                "interview_id": i.id,
                "target_position": i.target_position,
                "difficulty": i.difficulty,
                "overall_score": float(i.overall_score) if i.overall_score else None,
                "total_questions": i.total_questions,
                "status": i.status,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in interviews
        ]

        return {
            "total": len(items),
            "items": items
        }

    @staticmethod
    async def get_interview_messages(
        db: AsyncSession,
        user_id: int,
        interview_id: int
    ) -> List[Dict]:
        """获取面试的所有对话消息"""
        # 验证面试归属权
        interview_query = select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id
        )
        interview_result = await db.execute(interview_query)
        interview = interview_result.scalar_one_or_none()
        if not interview:
            raise NotFoundError(message="面试记录不存在")

        query = select(InterviewMessage).where(
            InterviewMessage.interview_id == interview_id
        ).order_by(InterviewMessage.id)
        result = await db.execute(query)
        messages = result.scalars().all()

        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "question_index": m.question_index,
                "score": float(m.score) if m.score else None,
                "feedback": m.feedback,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in messages
        ]

    @staticmethod
    async def delete_interview(
        db: AsyncSession,
        user_id: int,
        interview_id: int
    ) -> Dict:
        """删除面试记录及其关联的对话消息"""
        from sqlalchemy import delete as sql_delete

        query = select(Interview).where(
            Interview.id == interview_id,
            Interview.user_id == user_id
        )
        result = await db.execute(query)
        interview = result.scalar_one_or_none()

        if not interview:
            raise NotFoundError(message="面试记录不存在")

        # 先删除关联的对话消息
        await db.execute(
            sql_delete(InterviewMessage).where(InterviewMessage.interview_id == interview_id)
        )
        # 再删除面试记录
        await db.delete(interview)
        await db.commit()

        return {"message": "面试记录已删除"}

    @staticmethod
    async def delete_interview_admin(
        db: AsyncSession,
        interview_id: int
    ) -> Dict:
        """管理员删除面试记录（不校验用户归属）"""
        from sqlalchemy import delete as sql_delete

        interview = await db.get(Interview, interview_id)
        if not interview:
            raise NotFoundError(message="面试记录不存在")

        await db.execute(
            sql_delete(InterviewMessage).where(InterviewMessage.interview_id == interview_id)
        )
        await db.delete(interview)
        await db.commit()

        return {"message": "面试记录已删除"}


interview_service = InterviewService()
