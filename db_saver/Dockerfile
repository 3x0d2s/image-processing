FROM python:3.10.14-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    # not to ask any interactive questions
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:${PATH}"

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.in-project true

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main && yes | poetry cache clear . --all

FROM python:3.10.14-slim-bookworm as runtime

ENV PATH "/app/.venv/bin:$PATH"

COPY --from=builder /app /app
#
RUN mkdir -p \
    /code/src \
    /code/src/media
WORKDIR /code
COPY ./src /code/src

RUN touch ./.env

EXPOSE 8000

CMD ["python3", "-m", "src.main"]
