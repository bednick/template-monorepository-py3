import unittest.mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True, scope="package")
def settings():
    from example_service import config

    settings_ = config.Settings()
    with unittest.mock.patch("example_service.config.get_settings", return_value=settings_) as fixture_:
        yield fixture_


@pytest.fixture
def app() -> FastAPI:
    from example_service import application

    application.app.dependency_overrides = {}

    return application.app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
