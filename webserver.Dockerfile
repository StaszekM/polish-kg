FROM python:3.9-slim-bookworm
RUN apt-get update && apt-get install -y \
    gcc \
    graphviz \
    graphviz-dev \
    python3-lxml \
    libxml2-dev \
    libxslt-dev \
    git \ 
    gosu

WORKDIR /app

COPY . /app

ENTRYPOINT [ "/app/docker-entrypoint-webserver.sh" ]
