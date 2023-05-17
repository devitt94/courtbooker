FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr 

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ .

ENTRYPOINT [ "python", "main.py" ]

