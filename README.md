# Chat gpt bot
Бот для запросов в chatgpt

Использует **Selenium** и API chatgpt для запросов 

## Install & Update

install service

```bash
sudo cp scripts/gptchatbot.service /etc/systemd/system
sudo systemctl enable gptchatbot.service
sudo systemctl start gptchatbot.service
sudo 
```

### Update

```bash
git pull balshgit main
sudo rsync -a --delete --progress /home/balsh/Pycharmprojects/gpt_chat_bot/* /opt/gpt_chat_bot/ --exclude .git
cd /opt/gpt_chat_bot/
docker pull balshdocker/freegpt
STAGE=production docker compose build
sudo systemctl stop gptchatbot.service
sudo systemctl start gptchatbot.service
```

    

```bash
cd ~/PycharmProjects/chat_gpt_bot
sudo systemctl stop chat_gpt_bot.service
git pull balshgit main
sudo rsync -a --delete --progress ~/PycharmProjects/chat_gpt_bot/* /opt/chat_gpt_bot/ --exclude .git
sudo systemctl start chat_gpt_bot.service
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
cd bot_microservice
python3 run.py
```


```bash
cd bot_microservice
poetry run uvicorn --host 0.0.0.0 --factory run:create_app --port 1338 --reload
```

```bash
cd bot_microservice
gunicorn main:create_app --workers 10 --bind 0.0.0.0:8083 --worker-class uvicorn.workers.UvicornWorker --timeout 150 --max-requests 2000 --max-requests-jitter 400
```


## Tests

### Run local tests:
```bash
poetry run pytest
```

### Run tests in docker compose:
```bash
STAGE=runtests docker compose run bot bash -c "coverage run -m pytest -vv --exitfirst && poetry run coverage report"
```

## Docs
Docs can be found at

- {domain}/{url_prefix}/{api_prefix}/docs
- {domain}/{url_prefix}/{api_prefix}/redoc

on local start can be found at http://localhost/gpt/api/docs

## Help article

[Пишем асинхронного Телеграм-бота](https://habr.com/ru/company/kts/blog/598575/)


## TODO

- [x] Добавить очередь сообщений
- [x] Исправить запуск локально
- [x] Добавить тестов
- [x] Close connection
