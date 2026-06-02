"""
Backoffice Swagger UI Configuration File
Dedicated to backoffice management API documentation
"""

from typing import Dict, Any
from app.core.config import settings

# Backoffice Swagger UI Configuration
BACKOFFICE_SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "list",  # Expand tags but not operations
    "operationsSorter": "alpha",  # Sort alphabetically
    "filter": True,
    "tryItOutEnabled": True,
}

# Backoffice OpenAPI Metadata Configuration
BACKOFFICE_OPENAPI_INFO = {
    "title": f"{settings.PROJECT_NAME} - Backoffice Management API",
    "description": f"""
# Backoffice Management API Service

This is the internal API interface documentation for the backoffice management system.

## Functional Modules

### Authentication Management (Auth)
- Administrator login/logout
- JWT token management
- Token refresh operations

### Administrator Management (Admin)
- Administrator account CRUD operations
- Permission management
- User information maintenance
- Password management functions

### Cloud Storage Management (AWS)
- File management functionality
- S3 storage operations
- Upload permission control

## Authentication Instructions

⚠️ **All backoffice interfaces require JWT authentication** (except login interface)

### How to use authentication:
1. Call the `/login` interface to get an access token
2. Click the 🔒 **Authorize** button in the top right corner
3. Enter in the input box: `Bearer your-access-token`
4. Click **Authorize** to complete authentication setup

## Technical Features

- 🔒 **Security**: JWT authentication + permission control
- 🚀 **High Performance**: Based on FastAPI async framework
- 📊 **Database**: PostgreSQL + SQLAlchemy ORM
- 🎯 **Cache**: Redis cache system
- ☁️ **Cloud Storage**: AWS S3 integration
- 📝 **Documentation**: Auto-generated OpenAPI documentation
- ⚡ **Async**: Full async processing for improved performance

## Response Format

All API responses follow a unified format:

```json
{{
    "success": true,
    "message": "Operation successful",
    "data": {{}},
    "code": 200
}}
```

## Error Code Description

- **400**: Parameter error (displayed to users)
- **401**: Authentication failed
- **403**: Insufficient permissions
- **404**: Resource not found
- **500**: Server error

## Environment Information

- **Current Environment**: {settings.ENV}
- **API Version**: v1
- **Documentation Type**: Backoffice Management API
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Development Team",
        "email": settings.ADMIN_EMAIL,
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# Backoffice OpenAPI Tags Configuration
BACKOFFICE_OPENAPI_TAGS = [
    {
        "name": "backoffice-auth",
        "description": "Backoffice authentication interfaces",
        "externalDocs": {
            "description": "Authentication documentation",
            "url": "https://fastapi.tiangolo.com/tutorial/security/",
        },
    },
    {
        "name": "backoffice-admin",
        "description": "Backoffice administrator interfaces",
        "externalDocs": {
            "description": "Administrator documentation",
            "url": "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/",
        },
    },
    {
        "name": "backoffice-aws",
        "description": "Backoffice cloud storage management",
        "externalDocs": {
            "description": "AWS management documentation",
            "url": "https://docs.aws.amazon.com/s3/",
        },
    },
]

# JWT Authentication Configuration
BACKOFFICE_SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT authentication token, format: Bearer {token}. Please obtain the token through the login interface first.",
    }
}

def get_backoffice_openapi_config() -> Dict[str, Any]:
    """
    Get backoffice management OpenAPI configuration
    """
    return {
        **BACKOFFICE_OPENAPI_INFO,
        "openapi": "3.0.2",
        "tags": BACKOFFICE_OPENAPI_TAGS,
        "components": {
            "securitySchemes": BACKOFFICE_SECURITY_SCHEMES
        },
    }