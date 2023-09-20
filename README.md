# Chat gpt bot
Бот для запросов в chatgpt

Использует **Selenium** и API chatgpt для запросов 

## Install & Update

install service

    sudo cp scripts/chat-gpt.service /etc/systemd/system

```bash
cd ~/PycharmProjects/mosgortrans
sudo systemctl stop healthcheck_bot.service
git pull balshgit master
udo rsync -a --delete --progress ~/mosgortrans/* /opt/mosgortrans/ --exclude .git
sudo systemctl start healthcheck_bot.service
```

## Local start
```bash
python main.py
```

- set `START_WITH_WEBHOOK` to blank

## Delete or set webhook manually

url: https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}Webhook?url={WEBHOOK_URL}

methods:
- delete
- set


## Local development clean:

```bash
killall geckodriver
killall firefox
killall python
```

## Tests

```bash
cd tests
SELENOIDTEST=1 docker-compose run test-bot python -m pytest tests/bot/test_bot_selenoid.py::test_selenoid_text -vv
```

## Help article

[Пишем асинхронного Телеграм-бота](https://habr.com/ru/company/kts/blog/598575/)

[fast_api_aiogram](https://programtalk.com/vs4/python/daya0576/he-weather-bot/telegram_bot/dependencies.py/)

## TODO

- [x] Добавить очередь сообщений
- [x] Исправить запуск локально
- [x] Добавить тестов
- [x] Close connection
