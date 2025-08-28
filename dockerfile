FROM python:3.12-slim

RUN pip install telethon requests redis grafana-api boto3

WORKDIR /app
COPY . /app

CMD ["python", "gui.py"]