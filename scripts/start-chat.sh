#! /bin/bash

echo "starting chat"

gunicorn run:create_app \
  -- workers ${WORKERS_COUNT} \
  --bind ${APP_HOST}:${APP_PORT} \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 150 \
  --max-requests 2000 \
  --max-requests-jitter 400