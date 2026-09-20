FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV DEBUG=False
ENV PORT=5000
ENV LOG_FILE=/data/logs/logs.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]