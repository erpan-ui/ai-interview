from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from app.models.waiting_list import WaitingList
from typing import Optional
from datetime import datetime


class WaitingListService:
    @staticmethod
    async def get_waiting_list_query(
        db: AsyncSession,
        search: Optional[str] = None,
        search_type: Optional[str] = 'all',
        status: Optional[str] = 'all',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ):
        """
        获取等待列表查询对象用于分页

        Args:
            db: 数据库会话
            search: 搜索关键词
            search_type: 搜索类型 ('all', 'name', 'email')
                - 'all': 在姓名（first_name + last_name）和邮箱中搜索
                - 'name': 仅在 first_name 和 last_name 中搜索（支持组合搜索）
                - 'email': 仅在邮箱中搜索
            status: 按状态筛选 ('active', 'invited', 'all')
            start_date: 申请日期筛选起始日期
            end_date: 申请日期筛选结束日期
            sort_by: 排序字段 (created_at, email, university)
            sort_order: 排序方向 (asc, desc)
        """
        query = select(WaitingList)

        # 应用筛选条件
        filters = []

        # 带类型的搜索筛选
        if search:
            search_pattern = f"%{search}%"

            if search_type == 'email':
                # 仅在邮箱中搜索
                filters.append(WaitingList.email.ilike(search_pattern))
            elif search_type == 'name':
                # 仅在姓名字段中搜索
                # 支持 "first_name last_name" 组合搜索
                search_parts = search.strip().split()
                if len(search_parts) >= 2:
                    # 如果搜索词有多个部分，尝试匹配 first_name + last_name
                    first_name_pattern = f"%{search_parts[0]}%"
                    last_name_pattern = f"%{' '.join(search_parts[1:])}%"
                    filters.append(
                        or_(
                            # 匹配单个部分
                            WaitingList.first_name.ilike(search_pattern),
                            WaitingList.last_name.ilike(search_pattern),
                            # 匹配组合：first_name + last_name
                            and_(
                                WaitingList.first_name.ilike(first_name_pattern),
                                WaitingList.last_name.ilike(last_name_pattern)
                            )
                        )
                    )
                else:
                    # 单关键词在姓名字段中搜索
                    filters.append(
                        or_(
                            WaitingList.first_name.ilike(search_pattern),
                            WaitingList.last_name.ilike(search_pattern)
                        )
                    )
            else:  # 'all' 或默认
                # 在所有字段中搜索（邮箱、first_name、last_name）
                search_parts = search.strip().split()
                if len(search_parts) >= 2:
                    # 支持组合搜索
                    first_name_pattern = f"%{search_parts[0]}%"
                    last_name_pattern = f"%{' '.join(search_parts[1:])}%"
                    filters.append(
                        or_(
                            WaitingList.email.ilike(search_pattern),
                            WaitingList.first_name.ilike(search_pattern),
                            WaitingList.last_name.ilike(search_pattern),
                            # 匹配组合：first_name + last_name
                            and_(
                                WaitingList.first_name.ilike(first_name_pattern),
                                WaitingList.last_name.ilike(last_name_pattern)
                            )
                        )
                    )
                else:
                    # 单关键词在所有字段中搜索
                    filters.append(
                        or_(
                            WaitingList.email.ilike(search_pattern),
                            WaitingList.first_name.ilike(search_pattern),
                            WaitingList.last_name.ilike(search_pattern)
                        )
                    )

        # 状态筛选
        if status and status != 'all':
            if status == 'active':
                filters.append(WaitingList.is_verified == True)
            elif status == 'invited':
                filters.append(WaitingList.is_verified == False)

        # 日期范围筛选
        if start_date:
            filters.append(WaitingList.created_at >= start_date)
        if end_date:
            filters.append(WaitingList.created_at <= end_date)

        # 应用所有筛选条件
        if filters:
            query = query.where(and_(*filters))

        # 应用排序
        sort_column = getattr(WaitingList, sort_by, WaitingList.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        return query


waiting_list_service = WaitingListService()