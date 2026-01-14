from logging.config import fileConfig
import os

from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv
from app.models import *
from app.db.base import Base

# Import ALL models so Alembic can detect tables
from app.models.user import User
from app.models.center import Center
from app.models.class_type import ClassType
from app.models.session import Session
from app.models.booking import Booking
from app.models.ticket import Ticket

# Load .env
load_dotenv()

# Alembic config
config = context.config

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")

    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()