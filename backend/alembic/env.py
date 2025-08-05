# /code/alembic/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- INÍCIO DA CONFIGURAÇÃO CUSTOMIZADA ---

# 1. Adiciona o caminho da pasta raiz do seu projeto ao Python Path.
#    Isso é crucial para que o Alembic consiga encontrar seus módulos 'app'.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 2. Importa a 'Base' dos seus modelos e a variável 'settings' da sua aplicação.
from app.db.models import Base
from app.core.config import settings

# --- FIM DA CONFIGURAÇÃO CUSTOMIZADA ---


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- INÍCIO DA MODIFICAÇÃO PRINCIPAL ---

# 3. Define programaticamente a 'sqlalchemy.url' usando as configurações
#    importadas do seu projeto. Isso SOBRESCREVE a linha do alembic.ini.
#    Dessa forma, ele sempre usará a DATABASE_URL do seu ambiente.
if settings.DATABASE_URL:
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
else:
    # Lança um erro se a DATABASE_URL não estiver definida no ambiente.
    raise ValueError("A variável de ambiente DATABASE_URL não está configurada.")

# --- FIM DA MODIFICAÇÃO PRINCIPAL ---


# Interpret the config file for Python logging.
# This line needs to be placed after "config" is defined.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# --- DEFINA O target_metadata AQUI ---
target_metadata = Base.metadata
# -------------------------------------


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
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
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()