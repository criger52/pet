FROM python:3.12

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY notification_service/ .

CMD ["uv", "run", "python", "main.py"]