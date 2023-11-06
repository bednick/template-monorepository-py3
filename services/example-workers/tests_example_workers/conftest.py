import unittest.mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import async_database_postgresql


@pytest.fixture(autouse=True, scope="package")
def settings():
    from example_workers import config

    settings_ = config.Settings(
        database=async_database_postgresql.config.Settings(
            hosts=["localhost"], username="postgres", password="postgres", database_name="postgres"
        )
    )
    with unittest.mock.patch("example_workers.config.get_settings", return_value=settings_) as fixture_:
        yield fixture_


@pytest.fixture
def app() -> FastAPI:
    from example_workers import application

    application.app.dependency_overrides = {}

    return application.app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
