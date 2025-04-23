# GPTinder Backend

Бэкенд для социальной сети GPTinder, обеспечивающий API для чатов с ИИ и рекомендаций пользователей.

## Основные возможности

- Аутентификация и управление пользователями
- Чаты с искусственным интеллектом (AI Chat)
- Чаты между пользователями (User Chat)
- Система рекомендаций на основе векторных эмбеддингов
- Персонализированные объяснения рекомендаций с помощью GPT

## Установка и запуск

1. Клонировать репозиторий
2. Создать виртуальное окружение и активировать его
3. Установить зависимости: `pip install -r requirements.txt`
4. Настроить переменные окружения в файле `.env`
5. Применить миграции: `python manage.py migrate`
6. Запустить сервер: `python manage.py runserver`

## Работа с системой рекомендаций

### Управление эмбеддингами

Система использует OpenAI для создания эмбеддингов пользователей на основе их интересов и био,
а затем сохраняет их в Pinecone для быстрого поиска по сходству.

Для обновления эмбеддингов всех пользователей:

```bash
python manage.py update_user_embeddings
```

### Генерация рекомендаций

Для генерации рекомендаций для пользователей:

```bash
# Для всех пользователей
python manage.py generate_recommendations

# Для конкретного пользователя
python manage.py generate_recommendations --user username

# С объяснениями рекомендаций
python manage.py generate_recommendations --user username --explain
```

### API-эндпоинты для рекомендаций

- `GET /api/recommendations/` - получить список рекомендаций для текущего пользователя
- `POST /api/recommendations/generate/` - сгенерировать новые рекомендации
- `POST /api/recommendations/{id}/mark_viewed/` - отметить рекомендацию как просмотренную

## Пример объяснения рекомендации

```json
{
  "id": 5,
  "recommended_user": {
    "id": 3,
    "username": "science_geek",
    "first_name": "Michael",
    "last_name": "Brown",
    "profile_picture": null,
    "bio": "PhD student in physics with a passion for explaining complex concepts.",
    "interests": "physics, quantum mechanics, astronomy"
  },
  "similarity_score": 0.92,
  "common_interests": ["physics", "quantum mechanics"],
  "explanation": "Hey Alex, Michael is also into physics! He's currently researching quantum mechanics, maybe you two could discuss the latest discoveries in the field?"
}
```

## Обновление интересов и профиля

Пользователи могут обновлять свои интересы и профиль через API:

```
PATCH /api/users/me/
{
  "interests": "machine learning, web development, cybersecurity",
  "bio": "Software engineer passionate about AI"
}
```

После этого рекомендуется обновить эмбеддинги и сгенерировать новые рекомендации. 