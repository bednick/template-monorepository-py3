import fastapi

from example_workers import api

app = fastapi.FastAPI(title="example-workers")

app.include_router(api.ping.router)
app.include_router(api.root.router)
