# CheckHomeworkBot
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.

Что делает бот:
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
- логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

## Для запуска

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:SowaSova/homework_bot.git
```

```
cd homework_bot/
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Создаем .env файл с токенами:

```
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
```

Запускаем бота:

```
python homework.py
```
