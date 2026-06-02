"""
Client-side Swagger UI Configuration File
Dedicated to client API documentation
"""

from typing import Dict, Any
from app.core.config import settings

# Client Swagger UI Configuration
CLIENT_SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "list",  # Expand tags but not operations
    "operationsSorter": "alpha",  # Sort alphabetically
    "filter": True,
    "tryItOutEnabled": True,
}

# Client OpenAPI Metadata Configuration
CLIENT_OPENAPI_INFO = {
    "title": f"{settings.PROJECT_NAME} - Client API",
    "description": f"""
# Client API Service

This is the public API interface documentation for client applications.

## Functional Modules

### Authentication Management (Auth)
- User registration and email verification
- User login/logout
- JWT token management and refresh
- Password reset operations
- User profile retrieval

### Demo Functions (Demo)
- Basic demonstration interfaces
- Function testing interfaces

### Configuration Management (Config)
- Client configuration retrieval
- System configuration queries

### Cloud Storage Service (AWS)
- File upload functionality
- S3 storage integration
- Temporary credentials (requires authentication)

### Waiting List Management
- Waiting list application submission
- Email verification for waiting list
- Resend verification emails

## Authentication Instructions

⚠️ **Some interfaces require JWT authentication**

### Public Interfaces (No authentication required):
- Registration and email verification
- Login and logout
- Token refresh
- Password reset
- Configuration queries
- Waiting list operations

### Protected Interfaces (Authentication required):
- User profile retrieval (`/auth/me`)
- AWS temporary credentials (`/aws/temporary-credentials`)

### How to use authentication:
1. Call the `/auth/login` interface to get an access token
2. Click the 🔒 **Authorize** button in the top right corner
3. Enter in the input box: `Bearer your-access-token`
4. Click **Authorize** to complete authentication setup

## Technical Features

- 🔒 **Security**: JWT authentication for protected resources
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
- **Documentation Type**: Client API
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

# Client OpenAPI Tags Configuration
CLIENT_OPENAPI_TAGS = [
    {
        "name": "client-auth",
        "description": "Client authentication interfaces (registration, login, password reset, user profile)",
        "externalDocs": {
            "description": "Authentication documentation",
            "url": "https://fastapi.tiangolo.com/tutorial/security/",
        },
    },
    {
        "name": "client-demo",
        "description": "Client demonstration interfaces",
        "externalDocs": {
            "description": "Learn more",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "client-config",
        "description": "Client configuration interfaces",
        "externalDocs": {
            "description": "Configuration documentation",
            "url": "https://fastapi.tiangolo.com/tutorial/",
        },
    },
    {
        "name": "client-aws",
        "description": "Client cloud storage interfaces (requires authentication for temporary credentials)",
        "externalDocs": {
            "description": "AWS S3 documentation",
            "url": "https://docs.aws.amazon.com/s3/",
        },
    },
    {
        "name": "client-waiting-list",
        "description": "Waiting list management interfaces (application, verification, resend)",
        "externalDocs": {
            "description": "Waiting list documentation",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

# JWT Authentication Configuration
CLIENT_SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT authentication token, format: Bearer {token}. Please obtain the token through the login interface first.",
    }
}

def get_client_openapi_config() -> Dict[str, Any]:
    """
    Get client OpenAPI configuration
    """
    return {
        **CLIENT_OPENAPI_INFO,
        "openapi": "3.0.2",
        "tags": CLIENT_OPENAPI_TAGS,
        "components": {
            "securitySchemes": CLIENT_SECURITY_SCHEMES
        },
    }