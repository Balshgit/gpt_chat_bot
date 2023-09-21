# Chat gpt bot
Бот для запросов в chatgpt

Использует **Selenium** и API chatgpt для запросов 

## Install & Update

install service

    sudo cp scripts/chat-gpt.service /etc/systemd/system

```bash
cd ~/PycharmProjects/chat_gpt_bot
sudo systemctl stop chat_gpt_bot.service
git pull balshgit main
sudo rsync -a --delete --progress ~/PycharmProjects/chat_gpt_bot/* /opt/chat_gpt_bot/ --exclude .git
sudo systemctl start chat_gpt_bot.service
```

## Local start
```bash
python main.py
```

```shell
	poetry run uvicorn --host 0.0.0.0 --factory app.main:create_app --port 8000 --reload --reload-dir=app --reload-dir=settings
```

- set `START_WITH_WEBHOOK` to blank

## Delete or set webhook manually

url: https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}Webhook?url={WEBHOOK_URL}

methods:
- delete
- set


## Tests

```bash
poetry run pytest
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
