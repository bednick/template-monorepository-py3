import os
import pathlib
from typing import Generator

import alembic.command
import alembic.config
import fastapi.testclient
import pytest
import sqlalchemy_utils

from example_service import application, config, database


@pytest.fixture(scope="package", autouse=True)
def settings() -> config.Settings:
    return config.Settings(
        database=database.config.Settings(
            DATABASE_POSTGRESQL_DATABASE_NAME="example-service-tests",
            DATABASE_POSTGRESQL_POOL_SIZE=-1,
        ),
    )


@pytest.fixture(scope="package")
def app(settings: config.Settings) -> fastapi.FastAPI:
    app = application.get_application(settings)
    app.dependency_overrides = {}

    return app


@pytest.fixture(scope="package", autouse=True)
def init_database(settings: config.Settings):
    """Init test database (create DB, apply migrations)"""
    dsn = settings.database.sync_dsn
    if sqlalchemy_utils.database_exists(dsn):
        sqlalchemy_utils.drop_database(dsn)
    sqlalchemy_utils.create_database(dsn)
    try:
        os.environ["DATABASE_POSTGRESQL_DATABASE_NAME"] = settings.database.database_name
        alembic_cfg = alembic.config.Config(pathlib.Path(__file__).parent.parent / "alembic.ini")
        alembic.command.upgrade(alembic_cfg, "head")
        yield
    finally:
        if sqlalchemy_utils.database_exists(dsn):
            sqlalchemy_utils.drop_database(dsn)


@pytest.fixture()
def client(app: fastapi.FastAPI, init_database) -> Generator[fastapi.testclient.TestClient, None, None]:
    with fastapi.testclient.TestClient(app) as client:
        yield client
