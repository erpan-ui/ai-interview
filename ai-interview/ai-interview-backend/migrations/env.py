from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
import glob
import importlib
from pathlib import Path

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到 Python 路径
sys.path.append(BASE_DIR)

# 导入项目配置
from app.core.config import settings
from app.db.models import Base


def import_all_models():
    """自动导入 models 目录下的所有模型"""
    models_path = Path(BASE_DIR) / "app" / "models"
    model_files = glob.glob(str(models_path / "*.py"))

    for model_file in model_files:
        if not model_file.endswith("__init__.py"):
            module_name = Path(model_file).stem
            importlib.import_module(f"app.models.{module_name}")


# 导入所有模型
import_all_models()

# Alembic 配置对象
config = context.config

# 使用项目的数据库 URL 覆盖 alembic.ini 中的配置
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# 解析配置文件中的 Python 日志设置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以离线模式运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以在线模式运行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
