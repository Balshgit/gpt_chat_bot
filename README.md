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
	poetry run uvicorn --factory --host 0.0.0.0 --port 8080 --reload --workers 2 --log-level warning
```

To start on polling mode set `START_WITH_WEBHOOK` to blank


### Delete or set webhook manually

url: https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}Webhook?url={WEBHOOK_URL}

methods:
- delete
- set


## Admin:

http://localhost:8858/{URL_PREFIX}/admin


## Chat:

```shell
docker run --rm --net=host --name freegpt --rm -e CHAT_PATH=/chat balshdocker/freegpt:latest
docker run --rm --net=host --name zeus --rm balshdocker/freegpt-zeus:latest
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
LOCALTEST=1 STAGE=runtests poetry run pytest
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


## Create migrations

Init alembic

    alembic init alembic


```bash
cd bot_microservice
alembic revision --autogenerate -m 'create_quads_table'
alembic upgrade head
```


Create table in alembic versions

```bash
alembic --config ./alembic.ini revision -m "create account table"
alembic --config ./alembic.ini revision --autogenerate -m 'create_quads_table'
```



Run migrations

```bash
cd ./bot_microservice # alembic root
alembic --config ./alembic.ini upgrade head
alembic --config ./alembic.ini downgrade 389018a3e0f0
```


## Help article

[Следить за обновлениями этого репозитория](https://github.com/fantasy-peak/cpp-freegpt-webui)


## TODO

- [x] add Database and models
- [x] add alembic migrations
- [x] add models priority 
- [ ] and models rotation
- [x] add update model priority endpoint
- [x] add more tests for gpt model selection
- [ ] add authorisation for api
- [x] reformat conftest.py file
- [x] Add sentry
- [x] Add graylog integration and availability to log to file
