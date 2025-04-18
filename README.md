# Telegram-бот для фитнес-тренеров

Телеграм-бот на Python с использованием библиотеки aiogram, интегрированный с OpenAI GPT-4.1 nano и системой RAG для поиска информации. Бот предназначен для автоматизации работы фитнес-тренеров.

## Функциональные возможности

- Ведение базы клиентов
- Расчет КБЖУ по формуле Бенедикта
- Составление индивидуальных планов питания с учетом ограничений
- Интеграция с OpenAI GPT-4.1 nano
- RAG-система для поиска информации

## Установка и запуск

1. Клонируйте репозиторий:
```
git clone <repository-url>
cd TELEGRAMM_BOT_PROD
```

2. Создайте виртуальное окружение и установите зависимости:
```
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate  # Для Windows
pip install -r requirements.txt
```

3. Создайте файл .env на основе .env.example и заполните необходимые переменные окружения.

4. Запустите бота:
```
python bot.py
```

## Структура проекта

- `bot.py` - основной файл запуска бота
- `config/` - конфигурационные файлы
- `data/` - данные для RAG-системы
- `database/` - модели и операции с БД
- `handlers/` - обработчики команд бота
- `keyboards/` - клавиатуры и меню
- `models/` - модели данных и состояний
- `rag/` - система RAG для поиска информации
- `services/` - бизнес-логика (расчет КБЖУ, планы питания)
- `utils/` - вспомогательные функции

## Окружения

Бот поддерживает три режима работы:
- `dev` - для разработки
- `test` - для тестирования
- `prod` - для продакшн

## Лицензия

MIT
