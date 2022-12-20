FROM python:3.8.16-slim-buster

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    ca-certificates-java \
    firefox-esr \
    curl  && \
    apt-get clean

#See https://github.com/mozilla/geckodriver/releases
ENV GECKO_VERSION=v0.32.0
ENV MACHINE_TYPE=linux64
ENV GECKO_DRIVER_NAME=geckodriver-$GECKO_VERSION-$MACHINE_TYPE

WORKDIR /app

RUN curl -SL https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/$GECKO_DRIVER_NAME.tar.gz | tar xvz -C /app
ENV DRIVER_PATH=/app/geckodriver

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src .

ENTRYPOINT [ "python", "main.py"]