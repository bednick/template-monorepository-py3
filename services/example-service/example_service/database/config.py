import pydantic

import async_database_postgresql.config as base_config


class Settings(base_config.Settings):
    database_name: str = pydantic.Field("example-service", validation_alias="DATABASE_POSTGRESQL_DATABASE_NAME")