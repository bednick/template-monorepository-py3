import fastapi
import httpx


def test_ping_get(app: fastapi.FastAPI, client: httpx.Client):
    response = client.get(app.url_path_for("ping"))
    assert response.status_code == 200
