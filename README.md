# image-processing 

## Описание проекта
Данный проект представляет собой систему обработки изображений, разделенную на три ключевых компонента: 

1. API - интерфейс для взаимодействия с пользователем.
2. Служба обработки изображений - отвечает за выполнение трансформаций, включая добавление текста на изображение.
3. Служба сохранения данных - обеспечивает хранение обработанных изображений в базе данных.

### Технологии:
- База данных: PostgreSQL
- Обмен данными между службами: Redis Streams
- API и служба обработки изображений: Python (c использованием библиотек FastAPI + Pillow)
- Служба сохранения в БД: Golang

### Как это работает:
Пользователь отправляет запрос через API с изображением и текстом для добавления. API передает задачу на обработку в специальную службу. После завершения обработки, обработанное изображение сохраняется в БД через службу сохранения. 

## Для чего?
Этот проект был реализован в качестве демонстрации моих навыков в разработке и архитектуре приложений.

# Запуск в контейнере

## 1. Клониронивае репозитория

```shell
git clone https://github.com/3x0d2s/image-processing.git
cd image-processing/
```

## 2. Создание docker-compose файла

```shell
cp example.docker-compose.yml docker-compose.yml
```

Для каждого сервиса в volumes предопределено расположение различных дерикторий:

- **./media** - директория для хранения обработанных изображений
- **./fonts** - директория для хранения доступных шрифтов
- **./image_handler_logs** - директория для логов службы обработки изображений
- **./db_saver_logs** - директория для хранения логов службы сохранения в БД
- **./postgresql** - директория для хранения данных БД

Изменять эти директории и другие параметры docker-compose файла не рекомендуется.

## 3. Создание файла с переменными окружения

```shell
cp example.env .env
```

Файл example.env содержит заготовленные значения для корректного запуска проекта в контейнере.

### 3.1 Изменение шрифта и его размера

Для изменения шрифта требуется в директорию **./fonts** скопировать новый шрифт, 
затем изменить в файле **.env** переменную **FONT_NAME** на имя нового шрифта.

Для изменения размера шрифта требуется изменить значение переменной **FONT_SIZE** в файле **.env** 

## 4. Сборка образов

```shell
cd api/
docker build -t test-task-api:latest .
```
```shell
cd image_handler/
docker build -t image_handler:latest .
```
```shell
cd db_saver/
docker build -t db_saver:latest .
```

## 5. Запуск

```shell
docker-compose up -d
```

После запуска будут доступны следующие эндпоинты:

- POST http://localhost:8001/api/images
- GET http://localhost:8001/api/images
- GET http://localhost:8001/api/images/{image_id}
- GET http://localhost:8001/docs

# Запуск по отдельности каждой службы

Предполагается наличие **Python 3.10** и Golang в системе, запущенных PostgreSQL и Redis с модулем redis-search, а так же установленного пакетного менеджера [Poetry](https://python-poetry.org/docs/#installation).

## API

```shell
cd api
cp example.env .env
```

Требуется отредактировать файл **.env** для конфигурации строк подключения к PostgreSQL и Redis.

```shell
poetry env use python3.10
poetry install
poetry shell
alembic upgrade head
uvicorn app.main:app
```

## image_handler

```shell
cd image_handler
cp example.env .env
```

Требуется отредактировать файл **.env** для конфигурации строки подключения Redis.

```shell
poetry env use python3.10
poetry install
poetry shell
python -m src.main
```

## db_saver

```shell
cd db_saver
cp example.env .env
```

Требуется отредактировать файл **.env** для конфигурации строк подключения к PostgreSQL и Redis.

```shell
go run main.go
```
