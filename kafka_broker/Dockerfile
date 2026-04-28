FROM python:3.12

WORKDIR /app

RUN pip install uv

COPY kafka_broker/ .
COPY uv.lock ./

RUN uv sync

CMD ["uv", "run", "python", "main.py"]