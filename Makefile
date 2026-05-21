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

up-build:
	docker-compose up --build -d

down:
	docker-compose down

down-volumes:
	docker-compose down -v

create-migration-local:
	cd $(service) && powershell -Command "$$db_user = ((Get-Content .env | Select-String '^POSTGRES_USER=') -replace '^POSTGRES_USER=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_password = ((Get-Content .env | Select-String '^POSTGRES_PASSWORD=') -replace '^POSTGRES_PASSWORD=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_name = ((Get-Content .env | Select-String '^POSTGRES_DB=') -replace '^POSTGRES_DB=','' | ForEach-Object { $$_.ToString().Trim() }); $$env:DB_URL = 'postgresql+asyncpg://' + $$db_user + ':' + $$db_password + '@localhost:5432/' + $$db_name; if ('$(m)' -eq '') { alembic revision --autogenerate } else { alembic revision --autogenerate -m '$(m)' }"

apply-migration-local:
	cd $(service) && powershell -Command "$$db_user = ((Get-Content .env | Select-String '^POSTGRES_USER=') -replace '^POSTGRES_USER=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_password = ((Get-Content .env | Select-String '^POSTGRES_PASSWORD=') -replace '^POSTGRES_PASSWORD=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_name = ((Get-Content .env | Select-String '^POSTGRES_DB=') -replace '^POSTGRES_DB=','' | ForEach-Object { $$_.ToString().Trim() }); $$env:DB_URL = 'postgresql+asyncpg://' + $$db_user + ':' + $$db_password + '@localhost:5432/' + $$db_name; alembic upgrade head"

test-ci:
	uv run pytest --cov=. --cov-fail-under=80