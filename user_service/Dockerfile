FROM python:3.12

WORKDIR /user_service

RUN pip install uv

COPY user_service/ .
COPY uv.lock .
COPY entrypoint.sh .

RUN chmod +x ./entrypoint.sh

RUN uv sync

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uv", "run", "python", "main.py"]