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
	docker compose up -d

up-build:
	docker compose up --build -d

down:
	docker compose down

down-volumes:
	docker compose down -v

create-migration-local:
	cd $(service) && powershell -Command "$$service_upper = '$(service)' | ForEach-Object { $$_.ToUpper() }; $$db_user = ((Get-Content .env | Select-String '^POSTGRES_USER=') -replace '^POSTGRES_USER=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_password = ((Get-Content .env | Select-String '^POSTGRES_PASSWORD=') -replace '^POSTGRES_PASSWORD=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_name = ((Get-Content .env | Select-String '^POSTGRES_DB=') -replace '^POSTGRES_DB=','' | ForEach-Object { $$_.ToString().Trim() }); $$db_port = ((Get-Content .env | Select-String '^POSTGRES_PORT=') -replace '^POSTGRES_PORT=','' | ForEach-Object { $$_.ToString().Trim() }); $$url = 'postgresql+asyncpg://' + $$db_user + ':' + $$db_password + '@localhost:' + $$db_port + '/' + $$db_name; Write-Host \"DB_URL: $$url\"; Set-Item -Path \"env:$${service_upper}_DB_URL\" -Value $$url; alembic revision --autogenerate -m '$(m)'"

test-ci:
	uv run pytest auth_service/tests/ --cov=auth_service/src
	uv run pytest user_service/tests/ --cov=user_service/src
