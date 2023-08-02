FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr libxml2-dev libxslt-dev

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --require-hashes --no-deps -r requirements.txt

COPY src/ .
