# Chat gpt bot
Telegram bot with proxy to chatgpt

## Install & Update

### Install service

```bash
git clone https://github.com/Balshgit/gpt_chat_bot.git
cd gpt_chat_bot
sudo rsync -a --delete --progress ./* /opt/gpt_chat_bot/ --exclude .git
cd /opt/gpt_chat_bot
sudo cp ./bot_microservice/settings/.env.template ./bot_microservice/settings/.env
sudo cp ./scripts/gptchatbot.service /etc/systemd/system
sudo systemctl enable gptchatbot.service
sudo systemctl start gptchatbot.service
```

### Update service

```bash
git pull balshgit main
sudo rsync -a --delete --progress ./* /opt/gpt_chat_bot/ --exclude .git
cd /opt/gpt_chat_bot/
docker pull balshdocker/freegpt
docker compose build
sudo systemctl stop gptchatbot.service
sudo systemctl start gptchatbot.service
```

## Local start

### Bot:

```bash
cd bot_microservice
python main.py
```

```shell
cd bot_microservice
	poetry run uvicorn --host 0.0.0.0 --factory main:create_app --port 8000 --reload
```

To start on polling mode set `START_WITH_WEBHOOK` to blank


### Delete or set webhook manually

url: https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}Webhook?url={WEBHOOK_URL}

methods:
- delete
- set


## Chat:

```shell
docker run -p 8858:8858 -it --name freegpt --rm -e CHAT_PATH=/chat balshdocker/freegpt:latest
```
Open http://localhost:8858/chat/


```bash
cd bot_microservice
gunicorn main:create_app --workers 10 --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --timeout 150 --max-requests 2000 --max-requests-jitter 400
```


## Tests

### Run local tests:
```bash
cd bot_microservice
STAGE=runtests poetry run pytest
```

### Run tests in docker compose:
```bash
cd bot_microservice
STAGE=runtests docker compose run bot bash -c "coverage run -m pytest -vv --exitfirst && poetry run coverage report"
```

## Docs
Docs can be found at

- {domain}/{url_prefix}/{api_prefix}/docs
- {domain}/{url_prefix}/{api_prefix}/redoc

on local start can be found at http://localhost/gpt/api/docs

prod docs https://bot.mywistr.ru/gpt/api/docs/

## Help article

[Следить за обновлениями этого репозитория](https://github.com/fantasy-peak/cpp-freegpt-webui)


## TODO

- [] add Database and models
- [] add alembic migrations
- [] add models priority and their rotation
- [] add more tests
- [] reformat conftest.py file
- [x] Add sentry
- [x] Add graylog integration and availability to log to file
