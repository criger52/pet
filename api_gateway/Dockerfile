FROM python:3.12

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY ../uv.lock ./

RUN uv sync

COPY api_gateway/ .

CMD ["uv", "run", "python", "main.py"]