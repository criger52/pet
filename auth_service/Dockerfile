FROM python:3.12

WORKDIR /auth_service

RUN pip install uv

COPY auth_service/ .
COPY uv.lock .

RUN uv sync

CMD ["uv", "run", "python", "main.py"]