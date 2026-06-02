"""
OpenAPI JSON 导出路由
提供独立的API文档JSON下载功能，方便导入到其他API管理工具
"""

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from app.configs.docs_apps import create_client_app, create_backoffice_app
import json

router = APIRouter(prefix="/api-docs", tags=["API文档导出"])

@router.get("/client.json", summary="客户端API文档JSON", description="下载客户端API的OpenAPI JSON格式文档，可导入到Postman、Insomnia等工具")
async def get_client_openapi_json():
    """
    获取客户端API的OpenAPI JSON文档
    用于导入到Postman、Insomnia、ApiPost等API管理工具
    """
    client_app = create_client_app()
    openapi_schema = client_app.openapi()
    
    # 设置响应头，提示下载
    headers = {
        "Content-Disposition": "attachment; filename=client-api.json",
        "Content-Type": "application/json"
    }
    
    return JSONResponse(
        content=openapi_schema,
        headers=headers
    )

@router.get("/backoffice.json", summary="后台管理API文档JSON", description="下载后台管理API的OpenAPI JSON格式文档，包含JWT认证配置")
async def get_backoffice_openapi_json():
    """
    获取后台管理API的OpenAPI JSON文档
    包含完整的JWT认证配置，用于导入到API管理工具
    """
    backoffice_app = create_backoffice_app()
    openapi_schema = backoffice_app.openapi()
    
    # 设置响应头，提示下载
    headers = {
        "Content-Disposition": "attachment; filename=backoffice-api.json",
        "Content-Type": "application/json"
    }
    
    return JSONResponse(
        content=openapi_schema,
        headers=headers
    )

@router.get("/", summary="API文档导出说明")
async def api_docs_info():
    """
    API文档导出功能说明
    """
    return {
        "message": "FastAPI Template - API文档导出功能",
        "description": "提供OpenAPI JSON格式的API文档，可导入到各种API管理工具",
        "downloads": {
            "client": {
                "url": "/api-docs/client.json",
                "description": "客户端API文档（无认证，包含AWS功能）",
                "filename": "client-api.json",
                "features": ["演示接口", "配置管理", "AWS S3上传"]
            },
            "backoffice": {
                "url": "/api-docs/backoffice.json", 
                "description": "后台管理API文档（包含JWT认证）",
                "filename": "backoffice-api.json",
                "features": ["认证管理", "管理员管理", "AWS管理", "权限控制"]
            }
        },
        "import_guides": {
            "postman": "在Postman中选择 Import > Upload Files 导入JSON文件",
            "insomnia": "在Insomnia中选择 Import/Export > Import Data 导入JSON文件",
            "apipost": "在ApiPost中选择导入 > OpenAPI 导入JSON文件",
            "swagger_editor": "在Swagger Editor中选择 File > Import File 导入JSON文件",
            "apifox": "在Apifox中选择导入 > 从URL/文件导入 > OpenAPI格式"
        },
        "authentication": {
            "client": "客户端API无需认证，直接使用",
            "backoffice": "后台API需要JWT认证，导入后请在工具中配置Bearer Token认证方式"
        },
        "technical_info": {
            "openapi_version": "3.0.2",
            "framework": "FastAPI",
            "authentication": "JWT Bearer Token",
            "response_format": "统一ApiResponse格式"
        }
    }