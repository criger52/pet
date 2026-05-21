FROM python:3.12

WORKDIR /auth_service

RUN pip install uv

COPY auth_service/ .
COPY uv.lock .
COPY entrypoint.sh .

RUN chmod +x ./entrypoint.sh

RUN uv sync

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uv", "run", "python", "main.py"]