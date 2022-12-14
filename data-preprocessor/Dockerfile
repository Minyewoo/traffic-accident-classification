FROM python:3.8.16-slim-buster

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    ca-certificates-java && \
    apt-get clean

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY ./src .

ENTRYPOINT [ "python", "main.py"]