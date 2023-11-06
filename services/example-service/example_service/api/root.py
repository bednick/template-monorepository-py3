import fastapi

router = fastapi.APIRouter()


@router.get("/", operation_id="root", status_code=fastapi.status.HTTP_200_OK)
def root():
    return {"service": "example-service"}
