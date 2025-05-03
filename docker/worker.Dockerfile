FROM python:3.11-slim

RUN apt-get update

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "config", "worker", "-l", "info"]
