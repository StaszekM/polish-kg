#!/bin/bash
set -e;
source env/bin/activate;

echo "Running EDC Baseline Pipeline in virtual Environment: $VIRTUAL_ENV";

cd pipelines/edc_baseline;
dvc repro "$@";
