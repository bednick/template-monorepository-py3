# Сервис example-workers
Сервис `example-workers` предоставляет примеры для используемых воркеров.
Для его запуска вам потребуется произвести минимальныую настройку:
1. Поднять и настроить RabbitMQ
2. Поднять и настроить PostgreSQL
3. Создать очередь в RabbitMQ
4. Передать настройки в переменные окружения example-workers

Данные настройки уже произведены в `docker-compose.yml`, можно сделать по аналогии или
воспользоваться ими (запускать из корня ПРОЕКТА, а не сервиса!):
```commandline
docker-compose --project-directory ./ -f ./services/example-workers/docker-compose.yml up
```
Для создания сообщения в очереди можно воспользоватсья `http://localhost:15672/#/queues/%2F/demo`,
пользователь `guest`/`guest`.
**Важно**: Текст сообщения (Payload) должен быть валидныи json'ом.

Для запуска исходников без использования docker можно:
1. Создать файл `services/example-workers/.env`:
    ```.env
    ## LOGGING
    # LOGGING_LEVEL=20
    # LOGGING_FILE_PATH=./logs/log.txt

    ## WORKERS
    # SKIP_WORKERS=["example-workers-cron", "example-workers-rabbitmq"]

    ### WORKER example-workers-cron
    DATABASE_POSTGRESQL_HOSTS=["localhost"]
    DATABASE_POSTGRESQL_USERNAME=postgres
    DATABASE_POSTGRESQL_PASSWORD=postgres
    DATABASE_POSTGRESQL_DATABASE_NAME=postgres

    ### WORKER example-workers-rabbitmq
    RABBITMQ_HOST=localhost
    RABBITMQ_PORT=5672
    RABBITMQ_LOGIN=guest
    RABBITMQ_PASSWORD=guest
    RABBITMQ_QUEUE=demo
    ```
2. Запустить только окружение: `docker-compose --project-directory ./ -f ./services/example-workers/docker-compose.override.yml up`
3. Запустить сервис используя `example_workers/__main__.py` или:
   ```commandline
   cd ./services/example-workers
   python -m example_workers
   ```
