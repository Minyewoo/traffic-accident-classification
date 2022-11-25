FROM python:3.10.8-alpine3.16

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY ./src .

ENTRYPOINT [ "python", "main.py"]