from typing import Dict

from fastapi.testclient import TestClient


def test_ping_get(client: TestClient):
    headers: Dict[str, str] = {}
    response = client.request("GET", "/ping", headers=headers)
    assert response.status_code == 200
