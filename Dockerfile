FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y gcc python3-dev

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
