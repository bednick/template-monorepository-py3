# RUN BULD ONLY ROOT PROJECT!!!
# docker build -t example-service -f ./services/example-service/Dockerfile .

FROM python:3.11.9-slim AS app

WORKDIR /usr/src

COPY ./constraints.txt /usr/src/constraints.txt
COPY ./services/example-service/requirements.txt /usr/src/services/example-service/requirements.txt
RUN python3 -m pip install -r /usr/src/services/example-service/requirements.txt -c /usr/src/constraints.txt

COPY ./scripts/local-support /usr/src/scripts/local-support
RUN python3 -m pip install -e /usr/src/scripts/local-support -c /usr/src/constraints.txt
COPY ./libraries /usr/src/libraries
COPY ./services/example-service /usr/src/services/example-service
RUN python3 -m local.install --libraries --services

WORKDIR /usr/app

COPY ./scripts/internal /usr/app/scripts

ENTRYPOINT ["uvicorn", "example_service.asgi:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log", "--proxy-headers"]
