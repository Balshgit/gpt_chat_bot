#! /bin/bash

echo "starting the bot"

if [[ "${START_WITH_WEBHOOK}" == "true" ]]
then
  echo "Starting bot in webhook mode..."
  gunicorn main:create_app \
    --bind ${WEBAPP_HOST}:${WEBAPP_PORT} \
    --worker-class aiohttp.GunicornWebWorker \
    --timeout 150 \
    --max-requests 2000 \
    --max-requests-jitter 400
else
  echo "Starting bot in polling mode..."
  python main.py
fi
