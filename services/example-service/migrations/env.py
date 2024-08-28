from alembic import context

import logging_settings
import service_settings

from example_service import config as service_config
from example_service.database import tables

settings = service_config.get_settings()

config = context.config
config.set_main_option("sqlalchemy.url", str(settings.database.sync_dsn))

logging_settings.basic_config(settings.logging)

target_metadata = tables.metadata

if context.is_offline_mode():
    service_settings.alembic.run_migrations_offline(context, target_metadata)
else:
    service_settings.alembic.run_migrations_online(context, target_metadata)
