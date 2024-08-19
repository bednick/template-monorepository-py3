import uvicorn

from example_service import application

if __name__ == "__main__":
    uvicorn.run(application.get_application(), host="127.0.0.1", port=8080, access_log=True)
