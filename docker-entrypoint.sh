#!/bin/bash
set -e

if [ -e ./env/pyvenv.cfg ]; then
    echo "Venv found"
else
    echo "No virtualenv found, creating new one..."
    python3.9 -m venv --copies env
fi

echo "Installing requirements..."
source env/bin/activate
python -m pip install -r requirements.txt --no-cache-dir --exists-action=w
echo "Finished installing requirements"

echo "Installing nltk punkt"
python -c "import nltk; nltk.download('punkt_tab')"
echo "Finished installing nltk punkt"

echo "Environment ready"

tail -f /dev/null