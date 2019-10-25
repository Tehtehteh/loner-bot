FROM python:3.7-alpine

LABEL maintainer="tehfvpr@gmail.com"

RUN apk update --no-cache && apk upgrade --no-cache && pip install pipenv

WORKDIR /app

ADD src/Pipfile.lock Pipfile.lock

ADD src/Pipfile Pipfile

ENV PIPENV_PIPFILE=/app/Pipfile PIPENV_VENV_IN_PROJECT=1

RUN pipenv install --deploy --ignore-pipfile

COPY . .


ENTRYPOINT [".venv/bin/python", "src/main.py"]
