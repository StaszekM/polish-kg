#!/bin/bash
set -e

# 1) Runtime-configurable UID/username
USER_ID=${USER_ID:-1000}
USER_NAME=${USER_NAME:-appuser}

# 2) Create the user if it doesn't exist
if ! id "$USER_NAME" &>/dev/null; then
    echo "Creating user $USER_NAME (UID: $USER_ID)"
    useradd -u "$USER_ID" -m -s /bin/bash "$USER_NAME"
fi

# 3) Ensure proper ownership before stepping down
chown -R "$USER_NAME":"$USER_NAME" /app

# 4) If still root, re-exec this script as the target user
if [ "$(id -u)" = '0' ]; then
    echo "Switching to user $USER_NAME"
    exec gosu "$USER_NAME" "$0" "$@"
fi

# ———————— now running as non-root $USER_NAME ————————

cd /app

if [ -e ./env/pyvenv.cfg ]; then
    echo "Venv found"
else
    echo "Creating new virtualenv..."
    python3.9 -m venv --copies env
fi

echo "Installing requirements..."
source env/bin/activate
python -m pip install -r requirements.txt --no-cache-dir --exists-action=w
echo "Requirements installed"

echo "Downloading NLTK punkt..."
python - <<PYCODE
import nltk
nltk.download('punkt')
PYCODE
echo "NLTK punkt ready"

echo "Environment is ready. (running as UID $(id -u))"

python -u src/rest_api/app.py