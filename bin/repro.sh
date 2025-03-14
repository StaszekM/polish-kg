#!/bin/bash
docker compose exec python /bin/bash -c "source env/bin/activate; cd pipelines/edc_baseline; dvc repro $*"
