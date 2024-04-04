FROM python:3.11.9-alpine3.19

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
