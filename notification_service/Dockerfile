FROM python:3.12

WORKDIR /notification_service

RUN pip install uv

COPY notification_service/ .
COPY uv.lock ./

RUN uv sync

CMD ["uv", "run", "python", "main.py"]