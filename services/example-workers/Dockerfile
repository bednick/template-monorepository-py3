# RUN BULD ONLY ROOT PROJECT!!!
# docker build -t example-workers -f ./services/example-workers/Dockerfile .

FROM python:3.9-bookworm AS builder

WORKDIR /usr/src

COPY ./constraints.txt /usr/src/constraints.txt
COPY ./services/example-workers/requirements.txt /usr/src/services/example-workers/requirements.txt
RUN python3 -m pip install -r /usr/src/services/example-workers/requirements.txt -c /usr/src/constraints.txt

COPY ./scripts/local-support /usr/src/scripts/local-support
RUN python3 -m pip install -e /usr/src/scripts/local-support -c /usr/src/constraints.txt
COPY ./libraries /usr/src/libraries
COPY ./services/example-workers /usr/src/services/example-workers
RUN python3 -m local.install --libraries --services

WORKDIR /usr/app

COPY ./scripts/internal /usr/app/scripts

ENTRYPOINT ["uvicorn", "example_workers.application:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]
