FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x ./entrypoint.sh

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["./entrypoint.sh"]
