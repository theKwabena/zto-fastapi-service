FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /home/app

COPY ./pyproject.toml ./poetry.lock* ./

RUN apt-get update && apt-get install -y \
curl



RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 &&\
    cd /usr/local/bin  && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


RUN poetry install

COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

CMD ["celery", "-A .Celery.celery_app", "worker", "--concurrency=1", "--loglevel=INFO"]
