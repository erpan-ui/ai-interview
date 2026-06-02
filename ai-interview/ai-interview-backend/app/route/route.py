from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# 路由导入已移动到路由注册中心统一管理

from app.core.config import settings
from app.configs.docs_apps import create_client_app, create_backoffice_app
from fastapi.exceptions import RequestValidationError
from app.exceptions.http_exceptions import APIException
from app.schemas.response import ApiResponse
from contextlib import asynccontextmanager
from app.core.log_config import setup_logging, shutdown_logging, is_master_process
from app.services.common.redis import redis_client
from app.services.common.thread_pool import thread_pool_service
from app.db.base import close_db_engine
from app.schedule.schedule import setup_scheduler, shutdown_scheduler
import logging
from app.common.log_consumer import consume_logs_forever
import threading
import asyncio

logger = logging.getLogger(__name__)

# 根据环境设置CORS来源
ALLOWED_ORIGINS = ["*"] if settings.ENV == "development" or settings.ENV == "preview" else [
    "*"  # TODO: 替换为生产环境域名
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    # 启动时执行
    setup_logging()
    logger.info("Application starting up")

    # 日志消费线程（仅主进程启动，防止多进程重复）
    if is_master_process():
        try:
            # 创建一个包装函数在线程中运行异步函数
            def run_log_consumer():
                asyncio.run(consume_logs_forever())
                
            log_thread = threading.Thread(target=run_log_consumer, daemon=True)
            log_thread.start()
            logger.info("[LogConsumer] 日志消费线程已启动（主进程）")
        except Exception as e:
            logger.warning(f"[LogConsumer] 启动日志消费线程失败: {e}")

    # 单进程运行定时任务是打开下面的代码，多进程运行定时任务是关闭下面的代码使用celery_worker来运行
    # 初始化定时任务调度器（仅主进程启动）
    # if is_master_process():
    #     setup_scheduler(application)
    #     logger.info("任务调度器已初始化（主进程）")
    # else:
    #     logger.debug("当前为工作进程，跳过任务调度器初始化")

    yield  # 应用运行期间

    # 关闭时执行
    if is_master_process():
        shutdown_logging()  # 关闭日志
        # shutdown_scheduler()  # 关闭定时任务调度器
    await close_db_engine()  # 清理数据库引擎
    await redis_client.close()  # 关闭Redis连接
    thread_pool_service.shutdown()  # 关闭邮件线程池
    logger.info("Application shutting down")


def create_app():
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        description="FastAPI Template - 统一入口",
        version="1.0.0",
        docs_url=None,  # 禁用默认文档
        redoc_url=None,  # 禁用默认ReDoc
        openapi_url=None,  # 禁用默认OpenAPI
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 开发环境提供文档访问指引，生产环境隐藏
    if settings.ENV in ["development", "preview"]:
        @app.get("/", tags=["文档导航"])
        async def swagger_navigation():
            """
            开发环境 Swagger 文档导航
            """
            return {
                "message": "FastAPI Template - 开发环境",
                "environment": settings.ENV,
                "documentation": {
                    "client_api": {
                        "swagger": "/client/docs",
                        "redoc": "/client/redoc",
                        "openapi": "/client/openapi.json",
                        "description": "客户端API文档（无需认证）"
                    },
                    "backoffice_api": {
                        "swagger": "/backoffice/docs",
                        "redoc": "/backoffice/redoc",
                        "openapi": "/backoffice/openapi.json",
                        "description": "后台管理API文档（需要JWT认证）"
                    }
                },
                "api_exports": {
                    "client_json": "/api-docs/client.json",
                    "backoffice_json": "/api-docs/backoffice.json",
                    "info": "/api-docs/"
                },
                "health_check": "/api/v1/config/health"
            }

    # 使用路由注册中心统一注册所有路由
    from app.route.router_registry import register_routes, get_client_routes, get_backoffice_routes, get_common_routes

    # 注册客户端路由
    register_routes(app, get_client_routes())

    # 注册后台路由
    register_routes(app, get_backoffice_routes())

    # 注册公共路由
    register_routes(app, get_common_routes())

    # 挂载分离的文档应用
    client_docs_app = create_client_app()
    backoffice_docs_app = create_backoffice_app()
    
    app.mount("/client", client_docs_app)
    app.mount("/backoffice", backoffice_docs_app)

    # 提供上传文件的静态访问（头像、简历等）
    from fastapi.staticfiles import StaticFiles
    import os
    os.makedirs("uploads/avatars", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logger.error(f"API Exception: {exc.status_code} - {exc.code} - {exc.detail}",
                    extra={"request": f"{request.method} {request.url}"})
        return ApiResponse.failed(
            message=exc.detail,
            body_code=exc.code,  # 业务错误码
            http_code=exc.status_code,
            data=exc.data
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}",
                    extra={"request": f"{request.method} {request.url}"})
        return ApiResponse.failed(
            message=exc.detail,
            body_code=exc.status_code,  # 回落使用 HTTP 状态码
            http_code=exc.status_code,
            data=None
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation Error: {exc.errors()}",
                    extra={"request": f"{request.method} {request.url}"})
        return ApiResponse.failed(
            message="参数验证错误",
            body_code=1001,
            http_code=status.HTTP_400_BAD_REQUEST,
            data=exc.errors()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception: {str(exc)}",
                        extra={"request": f"{request.method} {request.url}"})
        return ApiResponse.failed(
            message="服务器内部错误",
            body_code=1005,
            http_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return app