import fastapi

from example_service.api import ping, root

router = fastapi.APIRouter()

router.include_router(ping.router)
router.include_router(root.router)
