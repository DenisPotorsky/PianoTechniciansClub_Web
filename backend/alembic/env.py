import sys
import os
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

from app.models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# Читаем DATABASE_URL из окружения, если не задан в alembic.ini
db_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline():
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
