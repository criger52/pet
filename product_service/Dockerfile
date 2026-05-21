FROM python:3.12

WORKDIR /product_service

RUN pip install uv

COPY product_service/ .
COPY uv.lock .

RUN uv sync

CMD ["uv", "run", "python", "main.py"]