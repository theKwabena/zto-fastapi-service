FROM python:3.10-slim-bookworm
WORKDIR /app


COPY ../pyproject.toml ../poetry.lock* ./

RUN apt-get update && apt-get install -y \
curl



RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 &&\
    cd /usr/local/bin  && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


RUN poetry install

COPY . .
ENTRYPOINT celery -A Celery worker --autoscale 10 --loglevel=info