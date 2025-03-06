ARG WORKDIR="/app"

# --- Builder image ---

FROM python:3.12-alpine AS builder

ARG WORKDIR

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR "${WORKDIR}"

RUN pip install --no-cache-dir poetry==2.1.1 \
    && poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./

ARG ENV=prod
RUN if [ "$ENV" = "dev" ]; then \
        poetry install; \
    else \
        poetry install --without dev; \
    fi

# --- Target image ---

FROM python:3.12-alpine

ARG WORKDIR

USER 1000

WORKDIR "${WORKDIR}"

COPY --chown=1000:1000 --from=builder "${WORKDIR}" .

COPY --chown=1000:1000 ./src/ ./src

ENV PYTHONPATH="/app/src"
ENV PATH="/app/.venv/bin:$PATH"
