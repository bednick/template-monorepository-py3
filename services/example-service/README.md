# Сервис example-service
Сервис `example-service` предоставляет примеры использования шаблона сервисов.

Сервис содержит минимальную настройку в виде docker-compose файла.
Для запуска примера необходимо выполнить:
```commandline
docker-compose --project-directory ./ -f ./services/example-service/docker-compose.yml up
```
После чего сервис будет доступен по адресу http://localhost:8080/.

Для создания сообщения в очереди RabbitMQ можно воспользоваться [Manager'ом](http://localhost:15672/#/queues/%2F/demo),
пользователь `guest`/`guest`.
**Важно**: Текст сообщения (Payload) должен быть валидным json'ом.
