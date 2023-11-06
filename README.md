# Шаблон проекта py3
Шаблон python 3 проекта в виде оформленного в виде монорепозитория.

## Настройка окружения

На весь проект предлагается использовать одно виртуальное окружение в директории `.venv`.

Для корректной работы Docker (чтобы избежать проблем) все файлы должны иметь Unix Line Separator.

## Встроенные скрипты

Для автоматизации был разработан набор скриптов, для их работы нужно
установить необходимые зависимости:

```commandline
python -m pip install --upgrade pip
pip install -r ./requirements-local.txt
pip install -U -e ./scripts/local-support[gen,docs]
pre-commit install
pre-commit run
```

### Создание новых библиотек и сервисов

Создание новой библиотеки:

```commandline
local.gen --library название-новой-библиотеки
```

Создание нового сервиса:

```commandline
local.gen --service название-нового-сервиса
```

### Запуск форматеров и линтеров

Применение **isort** на библиотеке `example-library`:

```commandline
isort --known-local-folder example-library libraries/example-library
```

Применение **black** на библиотеке `example-library` и на весь проект:

```commandline
black libraries/example-library
black .
```

Применение **flake8** на библиотеке `example-library` и на весь проект:

```commandline
flake8 libraries/example-library
flake8 .
```

### Запуск тестов

Тестирование библиотеки `example-library` и все модули проекта:

```commandline
py.test libraries/example-library
py.test .
```

### Сборка whl зависимостей

Для сервиса **example-service**:

```commandline
local.build_libraries
local.build_service example-service
```

### Сборка docker image

Для сервиса **example-service**:

```commandline
local.docker example-service
```

Или напрямую:
```commandline
docker build -t example-service -f ./services/example-service/Dockerfile .
```

После этого его можно запустить как:
```commandline
docker run --rm -it -p 8080:8080 example-service
```

Сервис будет доступен по адресу [localhost:8080](http://localhost:8080/)


### Генерация документации

Генерация API документации для fastapi сервиса example-service:

```commandline
local.docs example-service --app example_service.routers:app
```


## PyCharm

### Mark Directory as
Для корректной подсветки импортов необходимо пометить все папки библиотек и сервисов как `Mark Directory as -> Sources Root`.
Т.е. таким образом необходимо пометить все поддиректории в `libraries` и `services`.

### [Unix Line Separator](https://www.jetbrains.com/help/pycharm/configuring-line-endings-and-line-separators.html)

### Externals Tools `isort`:

| Setting           | Value                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------|
| `Name`              | `isort`                                                                                              |
| `Program`           | `$PyInterpreterDirectory$/isort`                                                                     |
| `Arguments`         | `--known-local-folder $FileDirName$ $FilePathRelativeToProjectRoot$ $FilePathRelativeToProjectRoot$` |
| `Working directory` | `$ProjectFileDir$`                                                                                   |

### Externals Tools `black`:

| Setting           | Value                               |
|-------------------|-------------------------------------|
| `Name`              | `black`                           |
| `Program`           | `$PyInterpreterDirectory$/black`  |
| `Arguments`         | `$FilePathRelativeToProjectRoot$` |
| `Working directory` | `$ProjectFileDir$`                |
