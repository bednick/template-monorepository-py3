# Шаблон проекта py3
Шаблон python 3 проекта в виде оформленного в виде монорепозитория.

Проект разделен на несколько логических частей/директорий:
- `libraries`: Набор внутренних библиотек/пакетов которые могут использоваться в других библиотеках и/или сервисах
- `scripts`: Скрипты, используемые в разработки, которые не должны поставляться в сборку сервисов
- `services`: Набор независимых сервисов проекта. Код сервиса НЕ может импортироваться в библиотеках или других сервисах

## Правила разработки
Для разработки предлагается придерживаться следующих правил:
- На весь проект используется одно виртуальное окружение в директории `.venv`, версия Python `3.11`:
  ```commandline
  pip install -r constraints.txt
  ```
- Создавать новые библиотеки и сервисы используя кодогенератор: (подробнее в файле `./scripts/local-support/README.md`)
  ```commandline
  pip install -U --constraint ./constraints.txt -e "./scripts/local-support[gen,docs]"
  ```
- Для корректной работы консольных утилит (pytest и т.п.) необходимо установить библиотеки и сервисы через `-e` флаг:
  ```commandline
  local.install --libraries --services
  ```
- Для работы обязательны `pre-commit` хуки, которые отвечают за форматирование/проверку кода и вспомогательный функционал:
  ```commandline
  pre-commit install
  pre-commit run
  ```
- Для корректной работы Docker все файлы кода/данных/скриптов должны иметь `Unix Line Separator`

## Управление зависимостями
В корне проекта содержатся следующие файлы зависимостей:
1. `requirements.in` - Содержит внешние зависимости от всех внутренних библиотек и сервисов.
**Важно**: все библиотеки и сервисы __обязаны__ иметь одинаковые версии зависимостей!
2. `requirements-dev.in` - Содержит внешние зависимости необходимые для разработки
3. `constraints.txt` - Генерируется на основе `requirements.in` и `requirements-dev.in` с помощью команды:
    ```commandline
    uv pip compile requirements.in requirements-dev.in -o constraints.txt
    ```

Для библиотек (`libraries/...`) создается минимум 2 файла зависимостей:
1. `requirements.txt` - Внешние зависимости необходимые для работы библиотеки
2. `requirements-editable.txt` - Внутренние зависимости (обязательно совпадают с названием директории в `libraries`)

Для сервисов (`services/...`) создается минимум 3 файла зависимостей:
1. `requirements.in` - Внешние зависимости необходимые для работы сервиса
2. `requirements-editable.txt` - Внутренние зависимости (обязательно совпадают с названием директории в `libraries`)
3. `requirements.txt` - Генерируется автоматически прекоммитом и/или скриптами на основе `requirements.in` и `requirements-editable.txt`

### Добавление зависимости
Из всего вышеперечисленного следует что, чтобы добавить новую зависимость в проект необходимо:
1. Добавить зависимость в корневой файл `requirements.in` (или `requirements-dev.in` если это dev зависимость)
2. Добавить зависимость в `requirements.txt` библиотеки и/или в `requirements.in` сервиса, в котором она будет использоваться
3. Сгенерировать обновленный `constraints.txt`:
    ````
    uv pip compile requirements.in requirements-dev.in -o constraints.txt
    ````

## Тестирование проекта
Каждая библиотека и сервис имеет свой набор тестов в директории каждого из пакетов.

Для тестирование сервиса `example-service` необходимо выполнить:
```commandline
py.test services/example-service
```
А для тестирование всех пакетов проекта:
```commandline
py.test .
```

## Сборка docker image
Необходимо обратить внимание, что для сборки любого из сервисов необходимо использовать в качестве контекста
корень всего проекта, а не отдельного сервиса, например для сервиса **example-service**::
```commandline
docker build -t example-service -f ./services/example-service/Dockerfile .
```
После этого его можно запустить как:
```commandline
docker run --rm -it -p 8080:8080 example-service
```
Сервис будет доступен по адресу [localhost:8080](http://localhost:8080/)

## PyCharm
Для удобства разработки через PyCharm предлагается произвести следующие настройки

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
