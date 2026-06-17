# pett

Микросервисный проект (auth, user, order и др.) с Docker Compose и `uv` для зависимостей.

## Требования

- [Docker](https://www.docker.com/) и Docker Compose
- [uv](https://docs.astral.sh/uv/)
- Make (на Windows — через Git Bash, WSL или [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm))

## Быстрый старт

### 1. Зависимости

Из корня репозитория:

```bash
make develop
```

### 2. Переменные окружения

Скопируйте примеры и заполните секреты:

```bash
cp .env-example .env
cp auth_service/.env-example auth_service/.env
cp user_service/.env-example user_service/.env
```

### 3. Инфраструктура

Поднять Postgres, Kafka и сервисы:

```bash
make up-build
```

Остановить:

```bash
make down
```

С удалением томов БД:

```bash
make down-volumes
```

### 4. Миграции (локально)


```bash
make create-migration-local service=auth_service
```


## Тесты

Из **корня** репозитория:

```bash
make test-ci
```

Команда запускает pytest по всем `testpaths` из `pyproject.toml`, считает покрытие по `auth_service` (без `main.py`, тестов и миграций) и требует **≥ 80%**.

Для тестов `auth_service` нужен Postgres на `localhost:5432` (как в `docker-compose` для `auth-db`). Тестовая БД `auth_test` создаётся и пересоздаётся автоматически.

Запуск только тестов auth без проверки покрытия:

```bash
uv run pytest auth_service/tests -v
```

## API

После `make up-build` gateway доступен на [http://localhost:8000](http://localhost:8000).

Примеры auth:

- `GET /api/v1/auth/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

## Полезные команды

| Команда | Описание |
|---------|----------|
| `make develop` | Установить зависимости workspace |
| `make up` | `docker-compose up -d` |
| `make up-build` | Собрать и поднять контейнеры |
| `make down` | Остановить контейнеры |
| `make test-ci` | Тесты + coverage ≥ 80% |
