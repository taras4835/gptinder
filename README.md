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
- **Контейнеризация**: Docker, Docker Compose

## Запуск приложения с помощью Docker

### Предварительные требования

- Docker и Docker Compose
- API-ключ OpenAI

### Настройка переменных окружения

1. Откройте файл `gptinder_back/.env` и установите свой API-ключ OpenAI:

```
OPENAI_API_KEY=sk-your-api-key
```

### Запуск в производственном режиме

```bash
# Сборка и запуск контейнеров
docker-compose up -d --build

# Приложение будет доступно по адресу:
# - Frontend: http://localhost
# - Backend API: http://localhost/api
```

### Запуск в режиме разработки

```bash
# Сборка и запуск контейнеров для разработки
docker-compose -f docker-compose.dev.yml up -d --build

# Приложение будет доступно по адресу:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000/api
```

## Разработка без Docker

### Бэкенд

```bash
cd gptinder_back
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Фронтенд

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