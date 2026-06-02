from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 环境配置
    ENV: str = "development"  # 默认值为 "development"

    # 基础配置
    PROJECT_NAME: str = "FastAPI Template"
    API_V1_STR: str = "/api/v1"
    API_PORT: int = 8001
    FRONTEND_URL: str = "http://localhost:3000"

    # Docker 端口配置（可选，用于 docker-compose）
    REDIS_EXTERNAL_PORT: int = 6386
    NGINX_HTTP_PORT: int = 8086
    NGINX_HTTPS_PORT: int = 8446
    FLOWER_PORT: int = 5556

    # 数据库配置
    POSTGRES_USER: str = "demo"
    POSTGRES_PASSWORD: str = "demo123"
    POSTGRES_HOST: str = "192.168.110.90"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "demo"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # Celery 配置
    CELERY_BROKER_URL: str = ""  # 在 __init__ 中设置
    CELERY_RESULT_BACKEND: str = ""  # 在 __init__ 中设置

    # HTTP 代理配置 - 仅在测试环境使用
    USE_HTTP_PROXY: bool = False  # 默认不使用代理
    HTTP_PROXY: str = "http://127.0.0.1:7890"
    HTTPS_PROXY: str = "http://127.0.0.1:7890"

    # 邮件配置
    MAIL_MAILER: str = "smtp"
    MAIL_HOST: str = "localhost"
    MAIL_PORT: int = 1025
    MAIL_USERNAME: str = "user"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM_ADDRESS: str = "noreply@example.com"
    MAIL_FROM_NAME: str = "Seiki"
    MAIL_ENCRYPTION: str = "none"

    # Brevo 配置
    BREVO_API_KEY: str = "dummy-api-key"
    BREVO_EMAIL_FROM: str = "noreply@example.com"
    BREVO_EMAIL_FROM_NAME: str = "Seiki"

    # 管理员邮箱
    ADMIN_EMAIL: str = "dev@zetos.fr"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # S3 配置
    AWS_ACCESS_KEY_ID: str = "your-access-key"
    AWS_SECRET_ACCESS_KEY: str = "your-secret-key"
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str = "your-bucket-name"
    AWS_ENDPOINT: str = "https://s3.amazonaws.com"

    # OpenAI 配置
    OPENAI_API_KEY: str = "your-openai-api-key"

    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = "your-deepseek-api-key"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # 可选，指定编码

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 在所有属性从 env 加载后设置 Celery URL
        if self.REDIS_PASSWORD:
            redis_url = (
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
            )
        else:
            redis_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        self.CELERY_BROKER_URL = redis_url
        self.CELERY_RESULT_BACKEND = redis_url


settings = Settings()
