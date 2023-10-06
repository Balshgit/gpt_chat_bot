#! /bin/bash

set -e

alembic upgrade "head"

echo "starting the bot"

if [[ "${START_WITH_WEBHOOK}" == "true" ]]
then
  echo "Starting bot in webhook mode..."
  gunicorn main:create_app \
    --workers ${WORKERS_COUNT} \
    --bind ${APP_HOST}:${APP_PORT} \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 150 \
    --max-requests 2000 \
    --max-requests-jitter 400
else
  echo "Starting bot in polling mode..."
  python main.py
fi
