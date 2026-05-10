FROM python:3.12

WORKDIR /user_service

RUN pip install uv

COPY user_service/ .
COPY uv.lock .

RUN uv sync

CMD ["uv", "run", "python", "main.py"]