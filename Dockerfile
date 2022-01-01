FROM python:3.8-slim

ENV PATH=/root/.poetry/bin:$PATH
WORKDIR /src
COPY vendor/get-poetry.py .

RUN apt-get update \
 && apt-get install --no-install-recommends -y git \
 && rm -rf /var/lib/apt/lists/* \
 && python get-poetry.py \
 && rm get-poetry.py

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-root --no-interaction --no-ansi

COPY . /src
