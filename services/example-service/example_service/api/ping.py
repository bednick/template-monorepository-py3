import fastapi

router = fastapi.APIRouter()


@router.get("/ping", operation_id="ping", status_code=fastapi.status.HTTP_200_OK)
def ping():
    return {}
