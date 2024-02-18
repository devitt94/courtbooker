FROM python:3.10-slim-bullseye

ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr libxml2-dev libxslt-dev libpq-dev gcc

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --require-hashes --no-deps -r requirements.txt

COPY courtbooker/ .
