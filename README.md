# GPTinder

GPTinder - это приложение для общения с ИИ и знакомства с людьми со схожими интересами на основе истории общения с искусственным интеллектом.

## Возможности

- 🤖 Чат с AI через OpenAI API
- 👥 Рекомендации пользователей на основе схожести интересов
- 💬 Чат между пользователями
- 🔐 Аутентификация и пользовательские профили

## Технологии

- **Бэкенд**: Django, Django REST Framework
- **Фронтенд**: React, TypeScript, Redux, Tailwind CSS

## Запуск приложения

### Предварительные требования

- Python 3.11+
- Node.js 20+
- API-ключ OpenAI

### Настройка переменных окружения

1. Откройте файл `gptinder_back/.env` и установите свой API-ключ OpenAI:

```
OPENAI_API_KEY=sk-your-api-key
```

### Запуск бэкенда

```bash
cd gptinder_back
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Запуск фронтенда

```bash
cd gptinder_front
npm install
npm run dev
```

## Структура проекта

- `gptinder_back/` - Django бэкенд
  - `users/` - Управление пользователями
  - `ai_chat/` - Чат с ИИ
  - `recommendations/` - Система рекомендаций и чаты между пользователями

- `gptinder_front/` - React фронтенд
  - `src/features/auth/` - Аутентификация
  - `src/features/chat/` - Чат с ИИ
  - `src/features/recommendations/` - Рекомендации и чаты с пользователями

## Лицензия

MIT