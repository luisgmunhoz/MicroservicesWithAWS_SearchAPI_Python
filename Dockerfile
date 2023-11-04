# Build stage
FROM python:3.10-alpine AS builder
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN apk update && apk add curl gcc musl-dev libffi-dev
RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev

ENV host=$host
ENV hotelCreatedEventIdsTable=$hotelCreatedEventIdsTable
ENV indexName=$indexName
ENV username=$username
ENV password=$password

# Runtime stage
FROM python:3.10-alpine
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . /app
EXPOSE 80
ENTRYPOINT [ "python3", "app.py"]