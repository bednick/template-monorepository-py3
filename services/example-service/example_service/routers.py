import fastapi

from example_service import api

app = fastapi.FastAPI(title="example-service")

app.include_router(api.ping.router)
app.include_router(api.root.router)
