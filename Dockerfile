FROM python:3.9.21-slim-bookworm

ARG USER_ID

RUN apt-get update && apt-get install -y \
    gcc \
    graphviz \
    graphviz-dev \
    python3-lxml \
    python3.9-dev \
    libxml2-dev \
    libxslt-dev \
    git

RUN useradd -m -u $USER_ID -s /bin/bash appuser

WORKDIR /app
RUN chown -R appuser:appuser /app

USER appuser

ENTRYPOINT [ "./docker-entrypoint.sh" ]
