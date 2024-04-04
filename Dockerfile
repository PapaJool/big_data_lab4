FROM python:3.9-slim
USER root
RUN apt-get install gcc python3-dev
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
