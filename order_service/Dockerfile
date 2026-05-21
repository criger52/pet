FROM python:3.12

WORKDIR /order_service

RUN pip install uv

COPY order_service/ .
COPY uv.lock .

RUN uv sync

CMD ["uv", "run", "python", "main.py"]