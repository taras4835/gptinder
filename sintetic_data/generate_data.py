import os
import json
import random
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Инициализация клиента OpenAI с API ключом из .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Определение путей к файлам
DATA_DIR = "data"
USER_PROFILES_FILE = os.path.join(DATA_DIR, "user_profiles.json")
AI_CHATS_DIR = os.path.join(DATA_DIR, "ai_chats")

# Создание директорий, если они не существуют
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AI_CHATS_DIR, exist_ok=True)

# Модель для генерации текста
GPT_MODEL = "gpt-4.1-nano-2025-04-14"

# Список возможных профессий и интересов для разнообразия пользователей
PROFESSIONS = [
    "программист", "дизайнер", "маркетолог", "учитель", "врач", "юрист", 
    "бухгалтер", "инженер", "писатель", "фотограф", "журналист", "ученый",
    "предприниматель", "художник", "музыкант", "менеджер", "HR-специалист",
    "аналитик данных", "психолог", "архитектор", "переводчик", "тренер",
    "воспитатель детского сада", "повар", "фрилансер"
]

INTERESTS = [
    "программирование", "дизайн", "маркетинг", "образование", "медицина", "право",
    "финансы", "инженерия", "литература", "фотография", "журналистика", "наука",
    "бизнес", "искусство", "музыка", "менеджмент", "HR", "анализ данных", "психология",
    "архитектура", "языки", "фитнес", "дети", "кулинария", "путешествия", "технологии",
    "саморазвитие", "история", "кино", "природа", "спорт", "игры", "рукоделие",
    "садоводство", "животные", "космос", "робототехника", "экология", "здоровье",
    "мода", "недвижимость", "инвестиции"
]

PERSONALITIES = [
    "творческий", "аналитический", "общительный", "интроверт", "прагматичный",
    "эмоциональный", "логичный", "заботливый", "амбициозный", "расслабленный",
    "перфекционист", "авантюрный", "консервативный", "оптимистичный", "скептичный",
    "любознательный", "самоуверенный", "сдержанный", "чуткий", "требовательный"
]

REAL_LIFE_SITUATIONS = [
    "ищет новую работу", "планирует переезд", "хочет сменить профессию",
    "воспитывает детей", "ищет детский сад", "изучает новый навык",
    "готовится к важному экзамену", "запускает свой бизнес", "ремонтирует дом",
    "планирует путешествие", "ищет партнеров для проекта", "восстанавливается после травмы",
    "готовится к выступлению", "пишет книгу", "создает свой сайт",
    "ищет репетитора", "выбирает университет", "инвестирует деньги",
    "ищет вдохновение для творчества", "ищет единомышленников", "хочет улучшить здоровье",
    "планирует сюрприз для близких", "ищет новое хобби", "открывает онлайн-магазин",
    "пытается освоить новую технологию", "ищет решение технической проблемы"
]

def generate_user_profile(user_id):
    """Генерация профиля пользователя с уникальными характеристиками"""
    
    # Выбираем случайные характеристики для разнообразия
    profession = random.choice(PROFESSIONS)
    num_interests = random.randint(3, 6)
    interests = random.sample(INTERESTS, num_interests)
    personality = random.choice(PERSONALITIES)
    situation = random.choice(REAL_LIFE_SITUATIONS)
    
    # Формируем промпт для генерации детального профиля пользователя
    prompt = f"""
    Создай профиль пользователя со следующими характеристиками:
    - Профессия: {profession}
    - Характер: {personality}
    - Жизненная ситуация: {situation}
    - Интересы: {', '.join(interests)}
    
    Сформируй полноценное описание человека с его потребностями, целями, болями и желаниями.
    Добавь 1-2 специфических запроса/проблемы, с которыми этот человек обратился бы за помощью.
    """
    
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты помогаешь создавать реалистичные профили пользователей для исследовательских целей."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        description = response.choices[0].message.content.strip()
        
        # Формируем итоговый профиль
        return {
            "user_id": user_id,
            "profession": profession,
            "interests": interests,
            "personality": personality,
            "situation": situation,
            "description": description
        }
    except Exception as e:
        print(f"Ошибка при генерации профиля пользователя: {e}")
        # Возвращаем базовый профиль в случае ошибки
        return {
            "user_id": user_id,
            "profession": profession,
            "interests": interests,
            "personality": personality,
            "situation": situation,
            "description": f"Пользователь {user_id} - {profession}, интересуется {', '.join(interests)}."
        }

def generate_chat_history(user_profile, num_messages=10):
    """Генерация истории чата с ИИ на основе профиля пользователя"""
    
    # Формируем промпт для генерации чата с ИИ
    prompt = f"""
    Создай историю диалога между пользователем и ИИ-ассистентом (GPT) из примерно {num_messages} сообщений.
    
    Вот профиль пользователя:
    {json.dumps(user_profile, ensure_ascii=False, indent=2)}
    
    Диалог должен быть реалистичным и отражать потребности, интересы и проблемы пользователя.
    В диалоге пользователь должен обсуждать свои специфические проблемы и запросы, указанные в профиле.
    
    Формат возвращаемых данных - строго JSON:
    {{
        "chat_id": "chat_{user_profile['user_id']}",
        "user_id": {user_profile['user_id']},
        "messages": [
            {{"role": "user", "content": "Первое сообщение пользователя"}},
            {{"role": "assistant", "content": "Ответ ассистента"}},
            ...
        ]
    }}
    
    Диалог должен начинаться с сообщения пользователя и чередоваться сообщениями пользователя и ассистента.
    """
    
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты создаешь реалистичные диалоги между пользователем и ИИ-ассистентом для исследовательских целей. Возвращай только JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        chat_json = response.choices[0].message.content.strip()
        chat_data = json.loads(chat_json)
        
        return chat_data
    
    except Exception as e:
        print(f"Ошибка при генерации чата: {e}")
        # Возвращаем базовый чат в случае ошибки
        return {
            "chat_id": f"chat_{user_profile['user_id']}",
            "user_id": user_profile['user_id'],
            "messages": [
                {"role": "user", "content": f"Привет! Я {user_profile['profession']} и меня интересует {user_profile['interests'][0]}."},
                {"role": "assistant", "content": f"Здравствуйте! Рад помочь вам с вопросами по {user_profile['interests'][0]}. Чем могу быть полезен?"},
                {"role": "user", "content": f"У меня проблема с {user_profile['situation']}."},
                {"role": "assistant", "content": "Я понимаю вашу ситуацию. Давайте разберемся с этим."}
            ]
        }

def generate_synthetic_data(num_users=3):
    """Генерация синтетических данных для эксперимента"""
    
    print(f"Генерация профилей {num_users} пользователей...")
    user_profiles = []
    
    for user_id in tqdm(range(1, num_users + 1)):
        profile = generate_user_profile(user_id)
        user_profiles.append(profile)
        # Небольшая задержка, чтобы не перегружать API
        time.sleep(1)
    
    # Сохраняем профили пользователей
    with open(USER_PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_profiles, f, ensure_ascii=False, indent=2)
    
    print("Профили пользователей сохранены.")
    
    print("Генерация историй чатов...")
    chats = []
    
    for profile in tqdm(user_profiles):
        # Генерируем от 1 до 3 чатов для каждого пользователя с разным количеством сообщений
        num_chats = random.randint(1, 3)
        
        for chat_index in range(num_chats):
            num_messages = random.randint(8, 15)
            chat_data = generate_chat_history(profile, num_messages)
            chat_data["chat_id"] = f"chat_{profile['user_id']}_{chat_index+1}"
            chats.append(chat_data)
            
            # Сохраняем чат в отдельный файл
            chat_file = os.path.join(AI_CHATS_DIR, f"{chat_data['chat_id']}.json")
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            # Небольшая задержка, чтобы не перегружать API
            time.sleep(1)
    
    print(f"Сгенерировано и сохранено {len(chats)} историй чатов.")
    return user_profiles, chats

if __name__ == "__main__":
    # Генерация данных
    num_users = 3  # Можно изменить количество пользователей
    user_profiles, chats = generate_synthetic_data(num_users)
    
    print("Генерация данных завершена.")
    print(f"Профили пользователей: {USER_PROFILES_FILE}")
    print(f"Истории чатов: {AI_CHATS_DIR}/") 