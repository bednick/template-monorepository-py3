Встроенные скрипты
---------------------

Для автоматизации были разработаны наборы скриптов, поставляемые как:
```commandline
pip install -U -e "./scripts/local-support[gen,docs]" -с ./constraints-dev.txt
```
Доступный функционал:
- [Editable установка](#install)
- [Генерация зависисмостей](#requirements)
- [Кодогенерация](#codegen)
- [Сборка whl](#whls)
- [Docker](#docker)
- [Docs](#docs)

Также часть этого предоставлена для удобного использования в `pre-commit` хуках.

<a name="install"><h2>Установка локальных библиотек и сервисов</h2></a>
Для установки библиотек и разработанных сервисов в
[develop mode](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs):
```commandline
local.install --libraries
local.install --services
```

<a name="requirements"><h2>Генерация requirements.txt для сервисов</h2></a>
Для генерации `requirements.txt` файла для сервсеса **example-service**:
```commandline
local.req example-service
```
Для генерации `requirements.txt` файлов для всех сервисов:
```commandline
local.req __all__
```

<a name="codegen"><h2>Создание новых библиотек и сервисов</h2></a>
Создание новой библиотеки:
```commandline
local.gen --library название-новой-библиотеки
```
Создание нового сервиса:
```commandline
local.gen --service название-нового-сервиса
```

<a name="whls"><h2>Сборка whl зависимостей</h2></a>
Для сервиса **example-service**:
```commandline
local.build_libraries
local.build_service example-service
```

<a name="docker"><h2>Сборка docker image</h2></a>
Для сервиса **example-service**:
```commandline
local.docker example-service
```

<a name="docs"><h2>Генерация документации</h2></a>
Генерация API документации для fastapi сервиса `example-service`:
```commandline
local.docs example-service --app example_service.routers:app
```
