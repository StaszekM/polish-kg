#!/bin/bash
docker compose exec python /bin/bash -c "source env/bin/activate; dvc $@"
