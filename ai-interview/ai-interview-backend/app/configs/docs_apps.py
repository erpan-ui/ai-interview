"""
分离的FastAPI应用工厂
提供Client和Backoffice的独立文档应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.configs.client_swagger_config import (
    CLIENT_OPENAPI_INFO,
    CLIENT_OPENAPI_TAGS,
    CLIENT_SWAGGER_UI_PARAMETERS,
    CLIENT_SECURITY_SCHEMES
)
from app.configs.backoffice_swagger_config import (
    BACKOFFICE_OPENAPI_INFO,
    BACKOFFICE_OPENAPI_TAGS,
    BACKOFFICE_SWAGGER_UI_PARAMETERS,
    BACKOFFICE_SECURITY_SCHEMES
)

# 根据环境设置CORS来源
ALLOWED_ORIGINS = ["*"] if settings.ENV == "development" or settings.ENV == "preview" else [
    "*"  # TODO: replace with production domain
]

def create_client_app() -> FastAPI:
    """
    创建客户端API文档应用
    """
    app = FastAPI(
        title=CLIENT_OPENAPI_INFO["title"],
        description=CLIENT_OPENAPI_INFO["description"],
        version=CLIENT_OPENAPI_INFO["version"],
        contact=CLIENT_OPENAPI_INFO["contact"],
        license_info=CLIENT_OPENAPI_INFO["license_info"],
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=CLIENT_OPENAPI_TAGS,
        swagger_ui_parameters=CLIENT_SWAGGER_UI_PARAMETERS,
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 使用路由注册中心注册客户端路由
    from app.route.router_registry import register_routes, get_client_routes
    register_routes(app, get_client_routes())

    # 定义无需认证的接口路径模式
    PUBLIC_PATHS = [
        "/auth/register",
        "/auth/send-verification-code",
        "/auth/verify-email",
        "/auth/login",
        "/auth/refresh",
        "/auth/logout",
        "/auth/password-reset/",
        "/demo",
        "/config/",
        "/waiting-list/",
    ]

    # 自定义OpenAPI schema以添加JWT认证配置
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=CLIENT_OPENAPI_INFO["title"],
            version=CLIENT_OPENAPI_INFO["version"],
            description=CLIENT_OPENAPI_INFO["description"],
            routes=app.routes,
            openapi_version="3.0.2",
            contact=CLIENT_OPENAPI_INFO["contact"],
            license_info=CLIENT_OPENAPI_INFO["license_info"],
        )

        # 添加JWT认证配置
        openapi_schema["components"]["securitySchemes"] = CLIENT_SECURITY_SCHEMES

        # 为需要认证的接口添加安全配置
        for path, methods in openapi_schema["paths"].items():
            # 检查路径是否为公开接口
            is_public = any(public_path in path for public_path in PUBLIC_PATHS)

            if not is_public:
                for method_name, method_info in methods.items():
                    if method_name in ["get", "post", "put", "delete", "patch"]:
                        method_info["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app


def create_backoffice_app() -> FastAPI:
    """
    创建后台管理API文档应用
    """
    app = FastAPI(
        title=BACKOFFICE_OPENAPI_INFO["title"],
        description=BACKOFFICE_OPENAPI_INFO["description"],
        version=BACKOFFICE_OPENAPI_INFO["version"],
        contact=BACKOFFICE_OPENAPI_INFO["contact"],
        license_info=BACKOFFICE_OPENAPI_INFO["license_info"],
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=BACKOFFICE_OPENAPI_TAGS,
        swagger_ui_parameters=BACKOFFICE_SWAGGER_UI_PARAMETERS,
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 使用路由注册中心注册后台路由
    from app.route.router_registry import register_routes, get_backoffice_routes
    register_routes(app, get_backoffice_routes())

    # 自定义OpenAPI schema以添加JWT认证配置
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=BACKOFFICE_OPENAPI_INFO["title"],
            version=BACKOFFICE_OPENAPI_INFO["version"],
            description=BACKOFFICE_OPENAPI_INFO["description"],
            routes=app.routes,
            openapi_version="3.0.2",
            contact=BACKOFFICE_OPENAPI_INFO["contact"],
            license_info=BACKOFFICE_OPENAPI_INFO["license_info"],
        )
        
        # 添加JWT认证配置
        openapi_schema["components"]["securitySchemes"] = BACKOFFICE_SECURITY_SCHEMES
        
        # 为需要认证的接口添加安全配置（除了登录接口）
        for path, methods in openapi_schema["paths"].items():
            if "/backoffice/auth/login" not in path:  # 登录接口不需要认证
                for method_name, method_info in methods.items():
                    if method_name in ["get", "post", "put", "delete", "patch"]:
                        method_info["security"] = [{"BearerAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app