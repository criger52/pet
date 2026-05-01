ifeq ($(OS), Windows_NT)
    VENV_BIN = $(VENV)\Scripts\
    RM = rmdir /s /q
else
    VENV_BIN = $(VENV)/bin/
    RM = rm -rf
endif

develop:
	uv sync --all-packages

up:
	docker-compose up -d

down:
	docker-compose down

down-volumes:
	docker-compose down -v

apply-migrations:
	alembic upgrade head

create-migrations:
	alembic revision --autogenerate