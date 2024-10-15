FROM python:3.9-slim

ENV PYTHONPATH /app

COPY requirements.txt /app/requirements.txt
COPY src /app/src

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8080 src.app:app"]