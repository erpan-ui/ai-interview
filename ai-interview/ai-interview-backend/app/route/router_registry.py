"""
路由注册中心
统一管理所有路由配置，避免重复定义
"""

from typing import List, Dict
from app.core.config import settings


class RouteConfig:
    """路由配置类"""
    def __init__(self, module_path: str, prefix: str, tags: List[str]):
        self.module_path = module_path
        self.prefix = prefix
        self.tags = tags


# 客户端路由配置
CLIENT_ROUTES = [
    RouteConfig(
        module_path="app.api.client.v1.auth",
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["client-auth"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.demo",
        prefix=f"{settings.API_V1_STR}/demo",
        tags=["client-demo"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.config",
        prefix=f"{settings.API_V1_STR}/config",
        tags=["client-config"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.aws",
        prefix=f"{settings.API_V1_STR}/aws",
        tags=["client-aws"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.waiting_list",
        prefix=f"{settings.API_V1_STR}/waiting-list",
        tags=["client-waiting-list"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.resume",
        prefix=f"{settings.API_V1_STR}/resumes",
        tags=["client-resume"]
    ),
    RouteConfig(
        module_path="app.api.client.v1.interview",
        prefix=f"{settings.API_V1_STR}/interviews",
        tags=["client-interview"]
    ),
]

# 后台路由配置
BACKOFFICE_ROUTES = [
    RouteConfig(
        module_path="app.api.backoffice.v1.auth",
        prefix=f"{settings.API_V1_STR}/backoffice/auth",
        tags=["backoffice-auth"]
    ),
    RouteConfig(
        module_path="app.api.backoffice.v1.admin",
        prefix=f"{settings.API_V1_STR}/backoffice/admins",
        tags=["backoffice-admin"]
    ),
    RouteConfig(
        module_path="app.api.backoffice.v1.aws",
        prefix=f"{settings.API_V1_STR}/backoffice/aws",
        tags=["backoffice-aws"]
    ),
    RouteConfig(
        module_path="app.api.backoffice.v1.waiting_list",
        prefix=f"{settings.API_V1_STR}/backoffice/waiting-list",
        tags=["backoffice-waiting-list"]
    ),
    RouteConfig(
        module_path="app.api.backoffice.v1.users",
        prefix=f"{settings.API_V1_STR}/backoffice/users",
        tags=["backoffice-users"]
    ),
    RouteConfig(
        module_path="app.api.backoffice.v1.interviews",
        prefix=f"{settings.API_V1_STR}/backoffice/interviews",
        tags=["backoffice-interviews"]
    ),
]

# 公共路由配置（不分客户端和后台的路由）
COMMON_ROUTES = [
    RouteConfig(
        module_path="app.api.docs_export",
        prefix="",
        tags=["API文档导出"]
    ),
]


def register_routes(app, route_configs: List[RouteConfig]):
    """
    动态注册路由

    Args:
        app: FastAPI 应用实例
        route_configs: 路由配置列表
    """
    for route_config in route_configs:
        # 动态导入模块
        module_parts = route_config.module_path.split('.')
        module_name = module_parts[-1]

        # 导入模块
        module = __import__(route_config.module_path, fromlist=[module_name])

        # 注册路由
        app.include_router(
            module.router,
            prefix=route_config.prefix,
            tags=route_config.tags
        )


def get_client_routes() -> List[RouteConfig]:
    """获取客户端路由配置"""
    return CLIENT_ROUTES


def get_backoffice_routes() -> List[RouteConfig]:
    """获取后台路由配置"""
    return BACKOFFICE_ROUTES


def get_common_routes() -> List[RouteConfig]:
    """获取公共路由配置"""
    return COMMON_ROUTES


def get_all_routes() -> Dict[str, List[RouteConfig]]:
    """获取所有路由配置"""
    return {
        "client": CLIENT_ROUTES,
        "backoffice": BACKOFFICE_ROUTES,
        "common": COMMON_ROUTES
    }