FROM python:3.10.8-alpine3.16 as builder

RUN apk add --update --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    curl

#See https://github.com/mozilla/geckodriver/releases
ENV GECKO_VERSION=v0.32.0
ENV MACHINE_TYPE=linux-aarch64
ENV GECKO_DRIVER_NAME=geckodriver-$GECKO_VERSION-$MACHINE_TYPE

RUN curl -SL https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/$GECKO_DRIVER_NAME.tar.gz | tar xvz -C /opt

COPY requirements.txt .
RUN pip install --user -r requirements.txt


FROM python:3.10.8-alpine3.16 as runner

RUN apk add --update --no-cache firefox

COPY --from=builder /root/.local /root/.local

ENV DRIVER_PATH=/app/gecko/geckodriver
COPY --from=builder /opt/geckodriver $DRIVER_PATH

WORKDIR /app
COPY ./src .

ENTRYPOINT [ "python", "main.py"]