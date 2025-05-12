import os
import json
import time
import random
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from openai import OpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Модели для использования
GPT_MODEL = "gpt-4.1-nano-2025-04-14"
EMBEDDING_MODEL = "text-embedding-3-small"

# Определение путей к файлам
DATA_DIR = "data"
USER_PROFILES_FILE = os.path.join(DATA_DIR, "user_profiles.json")
AI_CHATS_DIR = os.path.join(DATA_DIR, "ai_chats")
RESULTS_DIR = os.path.join(DATA_DIR, "results")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")

# Глобальные настройки для всех методов
MAX_TOTAL_COMPARISONS = 1000  # Общее максимальное количество сравнений для всех методов
MAX_USERS_TO_ANALYZE = 10  # Максимальное количество пользователей для анализа

# Создание директорий, если они не существуют
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Глобальные кэши для эмбеддингов
user_embeddings_cache = {}
message_embeddings_cache = {}

# Инициализация клиента OpenAI с API ключом из .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_data():
    """Загрузка сгенерированных данных"""
    # Загружаем профили пользователей
    with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
        user_profiles = json.load(f)
    
    # Ограничиваем количество пользователей
    user_profiles = user_profiles[:MAX_USERS_TO_ANALYZE]
    print(f"Загружено {len(user_profiles)} профилей пользователей (из макс. {MAX_USERS_TO_ANALYZE})")
    
    # Загружаем истории чатов
    chats = []
    user_ids = [profile['user_id'] for profile in user_profiles]
    
    for filename in os.listdir(AI_CHATS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(AI_CHATS_DIR, filename), 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                # Берем только чаты выбранных пользователей
                if chat_data['user_id'] in user_ids:
                    chats.append(chat_data)
    
    print(f"Загружено {len(chats)} чатов")
    
    return user_profiles, chats

def extract_user_messages(chats):
    """Извлечение сообщений пользователей из чатов"""
    user_messages = {}
    
    for chat in chats:
        user_id = chat['user_id']
        if user_id not in user_messages:
            user_messages[user_id] = []
        
        # Извлекаем только сообщения пользователя (не ассистента)
        for message in chat['messages']:
            if message['role'] == 'user':
                user_messages[user_id].append(message['content'])
    
    return user_messages

def load_embeddings():
    """Загрузка сохраненных эмбеддингов из файлов"""
    global user_embeddings_cache, message_embeddings_cache
    
    # Загрузка эмбеддингов пользователей, если файл существует
    user_embeddings_file = os.path.join(EMBEDDINGS_DIR, "user_embeddings.json")
    if os.path.exists(user_embeddings_file):
        try:
            with open(user_embeddings_file, 'r', encoding='utf-8') as f:
                # В JSON ключи всегда строки, преобразуем обратно в числа где нужно
                user_embeddings_data = json.load(f)
                user_embeddings_cache = {int(user_id): embedding 
                                        for user_id, embedding in user_embeddings_data.items()}
            print(f"Загружены эмбеддинги для {len(user_embeddings_cache)} пользователей")
        except Exception as e:
            print(f"Ошибка при загрузке эмбеддингов пользователей: {e}")
    
    # Загрузка эмбеддингов сообщений, если файл существует
    message_embeddings_file = os.path.join(EMBEDDINGS_DIR, "message_embeddings.json")
    if os.path.exists(message_embeddings_file):
        try:
            with open(message_embeddings_file, 'r', encoding='utf-8') as f:
                message_embeddings_cache = json.load(f)
            print(f"Загружены эмбеддинги для {len(message_embeddings_cache)} сообщений")
        except Exception as e:
            print(f"Ошибка при загрузке эмбеддингов сообщений: {e}")
            
    # Убедимся, что у нас всегда есть словари
    if user_embeddings_cache is None:
        user_embeddings_cache = {}
    if message_embeddings_cache is None:
        message_embeddings_cache = {}

def save_embeddings():
    """Сохранение эмбеддингов в файлы"""
    # Сохранение эмбеддингов пользователей
    user_embeddings_file = os.path.join(EMBEDDINGS_DIR, "user_embeddings.json")
    
    # Конвертируем numpy массивы в обычные списки для JSON
    user_embeddings_json = {
        str(user_id): embedding if isinstance(embedding, list) else embedding.tolist() 
        for user_id, embedding in user_embeddings_cache.items()
    }
    
    with open(user_embeddings_file, 'w', encoding='utf-8') as f:
        json.dump(user_embeddings_json, f)
    
    # Сохранение эмбеддингов сообщений
    message_embeddings_file = os.path.join(EMBEDDINGS_DIR, "message_embeddings.json")
    
    # Конвертируем numpy массивы в обычные списки для JSON
    message_embeddings_json = {
        message: embedding if isinstance(embedding, list) else embedding.tolist()
        for message, embedding in message_embeddings_cache.items()
    }
    
    with open(message_embeddings_file, 'w', encoding='utf-8') as f:
        json.dump(message_embeddings_json, f)
    
    print(f"Сохранено {len(user_embeddings_cache)} эмбеддингов пользователей и {len(message_embeddings_cache)} эмбеддингов сообщений")

def generate_embedding(text):
    """Генерация эмбеддинга для текста с использованием OpenAI API"""
    # Проверяем, есть ли уже эмбеддинг для этого текста в кэше
    if text in message_embeddings_cache:
        print(f"[DEBUG] Используем кэшированный эмбеддинг для текста: {text[:30]}...")
        return message_embeddings_cache[text]
    
    print(f"[DEBUG] Генерируем новый эмбеддинг для текста: {text[:30]}...")
    
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        embedding = response.data[0].embedding
        
        # Сохраняем в кэш
        message_embeddings_cache[text] = embedding
        
        return embedding
    except Exception as e:
        print(f"[ERROR] Ошибка при генерации эмбеддинга: {str(e)}")
        # Возвращаем заглушку, чтобы не прерывать выполнение скрипта
        # Создаем случайный эмбеддинг той же размерности, что обычно возвращает API
        return np.random.rand(1536).tolist()

def get_user_embedding(user_profile, user_messages):
    """Генерация эмбеддинга пользователя на основе его профиля и сообщений"""
    user_id = user_profile['user_id']
    
    # Проверяем, есть ли уже эмбеддинг для этого пользователя в кэше
    if user_id in user_embeddings_cache:
        return user_embeddings_cache[user_id]
    
    # Формируем текст для эмбеддинга
    text = f"Профессия: {user_profile['profession']}. "
    text += f"Интересы: {', '.join(user_profile['interests'])}. "
    text += f"Личность: {user_profile['personality']}. "
    text += f"Ситуация: {user_profile['situation']}. "
    
    # Добавляем все сообщения пользователя
    if user_id in user_messages and user_messages[user_id]:
        text += " Сообщения пользователя: " + " ".join(user_messages[user_id])
    
    embedding = generate_embedding(text)
    
    # Сохраняем в кэш пользовательских эмбеддингов
    if embedding:
        user_embeddings_cache[user_id] = embedding
    
    return embedding

def get_message_embeddings(messages):
    """Генерация эмбеддингов для списка сообщений"""
    embeddings = []
    for message in messages:
        embedding = generate_embedding(message)
        if embedding:
            embeddings.append(embedding)
    return embeddings

def check_message_pair_relevance(message1, message2):
    """Проверка релевантности пары сообщений с использованием GPT"""
    prompt = f"""
    Оцени, могут ли авторы этих двух сообщений быть полезны друг другу.
    
    Сообщение 1: "{message1}"
    
    Сообщение 2: "{message2}"
    
    Верни только "yes", если в данном контексте автор сообщения 1 может быть полезен автору сообщения 2 или наоборот.
    В противном случае верни "no".
    
    Пример полезности: один пользователь ищет специалиста, а другой обладает нужными навыками;
    один пользователь имеет проблему, которую другой пользователь уже решил и т.д.
    """
    
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты помогаешь определить, могут ли пользователи быть полезны друг другу на основе их сообщений."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        answer = response.choices[0].message.content.strip().lower()
        return "yes" in answer
    
    except Exception as e:
        print(f"Ошибка при проверке релевантности сообщений: {e}")
        return False

def calculate_gini(counts):
    """Расчет коэффициента Джини для оценки разнообразия рекомендаций"""
    if not counts or sum(counts) == 0:
        return 0
    
    # Нормализуем счетчики
    n = len(counts)
    counts_sorted = sorted(counts)
    cumsum = np.cumsum(counts_sorted)
    return (2 * np.sum(np.arange(1, n+1) * counts_sorted) / (n * np.sum(counts_sorted))) - (n + 1) / n

def evaluate_brute_force(user_profiles, user_messages):
    """Оценка метода полного перебора - сравнения каждого сообщения с каждым"""
    print("Оценка метода полного перебора (каждое сообщение с каждым)...")
    
    # Получаем все сообщения всех пользователей
    all_messages = []
    message_to_user = {}
    
    # Формируем плоский список всех сообщений
    for user_id, messages in user_messages.items():
        # Берем не более 5 сообщений от каждого пользователя
        sample = messages[:5] if len(messages) > 5 else messages
        for message in sample:
            all_messages.append(message)
            message_to_user[message] = user_id
    
    print(f"Общее количество сообщений: {len(all_messages)}")
    
    total_comparisons = 0
    successful_pairs = 0
    user_pair_counts = {user_id: 0 for user_id in user_messages.keys()}
    results = []
    
    # Сравниваем каждое сообщение с каждым
    for i, message1 in enumerate(tqdm(all_messages)):
        user1_id = message_to_user[message1]
        
        for j, message2 in enumerate(all_messages[i+1:], i+1):
            user2_id = message_to_user[message2]
            
            # Пропускаем сообщения от одного и того же пользователя
            if user1_id == user2_id:
                continue
            
            total_comparisons += 1
            
            # Проверяем релевантность пары сообщений
            relevant = check_message_pair_relevance(message1, message2)
            
            if relevant:
                successful_pairs += 1
                user_pair_counts[user1_id] += 1
                user_pair_counts[user2_id] += 1
            
            results.append({
                'user1_id': user1_id,
                'user2_id': user2_id,
                'message1': message1,
                'message2': message2,
                'relevant': relevant
            })
            
            # Делаем небольшую задержку, чтобы не перегружать API
            time.sleep(1)
            
            # Ограничиваем общее количество сравнений
            if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:  # выделяем 1/4 бюджета сравнений на этот метод
                print(f"Достигнуто максимальное количество сравнений для этого метода ({MAX_TOTAL_COMPARISONS // 4})")
                break
        
        # Выходим из внешнего цикла, если достигли ограничения
        if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
            break
    
    # Расчет метрики
    gini = calculate_gini(list(user_pair_counts.values()))
    metric = (successful_pairs / total_comparisons) * (1 - gini) if total_comparisons > 0 else 0
    
    print(f"Всего сравнений: {total_comparisons}")
    print(f"Успешных пар: {successful_pairs}")
    print(f"Коэффициент Джини: {gini:.4f}")
    print(f"Метрика: {metric:.4f}")
    
    return {
        'total_comparisons': total_comparisons,
        'successful_pairs': successful_pairs,
        'gini': gini,
        'metric': metric,
        'results': results,
        'user_pair_counts': user_pair_counts
    }

def evaluate_embedding_based(user_profiles, user_messages):
    """Оценка метода на основе эмбеддингов"""
    print("Оценка метода на основе эмбеддингов...")
    
    # Генерация эмбеддингов пользователей
    print("Генерация эмбеддингов пользователей...")
    user_embeddings = {}
    for profile in tqdm(user_profiles):
        user_id = profile['user_id']
        embedding = get_user_embedding(profile, user_messages)
        if embedding:
            user_embeddings[user_id] = embedding
            time.sleep(1)  # Задержка, чтобы не перегружать API
    
    # Расчет близости пользователей
    user_ids = list(user_embeddings.keys())
    embedding_matrix = np.array([user_embeddings[user_id] for user_id in user_ids])
    
    # Используем косинусное расстояние (1 - cos_similarity)
    distances = pairwise_distances(embedding_matrix, metric='cosine')
    
    # Количество сравниваемых пар (топ-N наиболее близких пользователей)
    top_n = 3
    total_comparisons = 0
    successful_pairs = 0
    user_pair_counts = {user_id: 0 for user_id in user_ids}
    results = []
    
    for i, user1_id in enumerate(tqdm(user_ids)):
        # Получаем индексы N ближайших пользователей для текущего пользователя
        similar_indices = np.argsort(distances[i])[1:top_n+1]  # Исключаем самого себя [0]
        
        user1_sample = user_messages[user1_id][:5] if len(user_messages[user1_id]) > 5 else user_messages[user1_id]
        message1 = random.choice(user1_sample)
        
        for idx in similar_indices:
            user2_id = user_ids[idx]
            
            user2_sample = user_messages[user2_id][:5] if len(user_messages[user2_id]) > 5 else user_messages[user2_id]
            message2 = random.choice(user2_sample)
            
            total_comparisons += 1
            
            # Проверяем релевантность пары сообщений
            relevant = check_message_pair_relevance(message1, message2)
            
            if relevant:
                successful_pairs += 1
                user_pair_counts[user1_id] += 1
                user_pair_counts[user2_id] += 1
            
            results.append({
                'user1_id': user1_id,
                'user2_id': user2_id,
                'message1': message1,
                'message2': message2,
                'similarity': 1 - distances[i, idx],
                'relevant': relevant
            })
            
            # Делаем небольшую задержку, чтобы не перегружать API
            time.sleep(1)
            
            # Ограничиваем общее количество сравнений
            if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:  # выделяем 1/4 бюджета сравнений на этот метод
                print(f"Достигнуто максимальное количество сравнений для этого метода ({MAX_TOTAL_COMPARISONS // 4})")
                break
        
        # Выходим из внешнего цикла, если достигли ограничения
        if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
            break
    
    # Расчет метрики
    gini = calculate_gini(list(user_pair_counts.values()))
    metric = (successful_pairs / total_comparisons) * (1 - gini) if total_comparisons > 0 else 0
    
    print(f"Всего сравнений: {total_comparisons}")
    print(f"Успешных пар: {successful_pairs}")
    print(f"Коэффициент Джини: {gini:.4f}")
    print(f"Метрика: {metric:.4f}")
    
    return {
        'total_comparisons': total_comparisons,
        'successful_pairs': successful_pairs,
        'gini': gini,
        'metric': metric,
        'results': results,
        'user_pair_counts': user_pair_counts,
        'user_embeddings': user_embeddings
    }

def evaluate_message_embedding_based(user_profiles, user_messages):
    """Оценка метода на основе эмбеддингов сообщений"""
    print("Оценка метода на основе эмбеддингов сообщений...")
    
    all_messages = []
    message_to_user = {}
    
    # Ограничиваем количество сообщений для демонстрации
    max_messages_per_user = 5
    
    # Формируем плоский список всех сообщений
    for user_id, messages in user_messages.items():
        print(f"[DEBUG] Обрабатываем сообщения пользователя {user_id}, всего сообщений: {len(messages)}")
        sample = messages[:max_messages_per_user] if len(messages) > max_messages_per_user else messages
        for message in sample:
            all_messages.append(message)
            message_to_user[message] = user_id
    
    print(f"[DEBUG] Всего собрано {len(all_messages)} сообщений из {len(user_messages)} пользователей")
    
    # Генерируем эмбеддинги для всех сообщений
    print("Генерация эмбеддингов сообщений...")
    message_embeddings = {}
    for i, message in enumerate(tqdm(all_messages)):
        try:
            print(f"[DEBUG] Обработка сообщения {i+1}/{len(all_messages)}: {message[:30]}...")
            embedding = generate_embedding(message)
            if embedding:
                message_embeddings[message] = embedding
                time.sleep(0.1)  # Минимальная задержка
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке сообщения: {str(e)}")
            continue
    
    print(f"[DEBUG] Сгенерировано эмбеддингов: {len(message_embeddings)} из {len(all_messages)} сообщений")
    
    # Преобразуем в формат, подходящий для расчета расстояний
    message_list = list(message_embeddings.keys())
    if not message_list:
        print("[ERROR] Не удалось сгенерировать ни одного эмбеддинга. Прерываем выполнение.")
        return {
            'total_comparisons': 0,
            'successful_pairs': 0,
            'gini': 0,
            'metric': 0,
            'results': [],
            'user_pair_counts': {user_id: 0 for user_id in user_messages.keys()},
            'message_embeddings': {}
        }
    
    embedding_matrix = np.array([message_embeddings[msg] for msg in message_list])
    
    # Рассчитываем расстояния между всеми сообщениями
    print(f"[DEBUG] Расчет расстояний между {len(message_list)} сообщениями...")
    distances = pairwise_distances(embedding_matrix, metric='cosine')
    
    # Количество сравниваемых пар (топ-N наиболее близких сообщений)
    top_n = 3
    total_comparisons = 0
    successful_pairs = 0
    user_pair_counts = {user_id: 0 for user_id in user_messages.keys()}
    results = []
    
    for i, message1 in enumerate(tqdm(message_list)):
        user1_id = message_to_user[message1]
        
        # Получаем индексы N ближайших сообщений для текущего сообщения
        similar_indices = np.argsort(distances[i])[1:top_n+1]  # Исключаем само сообщение [0]
        
        for idx in similar_indices:
            message2 = message_list[idx]
            user2_id = message_to_user[message2]
            
            # Пропускаем сообщения от того же пользователя
            if user1_id == user2_id:
                continue
            
            total_comparisons += 1
            
            # Проверяем релевантность пары сообщений
            relevant = check_message_pair_relevance(message1, message2)
            
            if relevant:
                successful_pairs += 1
                user_pair_counts[user1_id] += 1
                user_pair_counts[user2_id] += 1
            
            results.append({
                'user1_id': user1_id,
                'user2_id': user2_id,
                'message1': message1,
                'message2': message2,
                'similarity': 1 - distances[i, idx],
                'relevant': relevant
            })
            
            # Делаем небольшую задержку, чтобы не перегружать API
            time.sleep(1)
            
            # Ограничиваем общее количество сравнений
            if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:  # выделяем 1/4 бюджета сравнений на этот метод
                print(f"Достигнуто максимальное количество сравнений для этого метода ({MAX_TOTAL_COMPARISONS // 4})")
                break
        
        # Выходим из внешнего цикла, если достигли ограничения
        if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
            break
    
    # Расчет метрики
    gini = calculate_gini(list(user_pair_counts.values()))
    metric = (successful_pairs / total_comparisons) * (1 - gini) if total_comparisons > 0 else 0
    
    print(f"Всего сравнений: {total_comparisons}")
    print(f"Успешных пар: {successful_pairs}")
    print(f"Коэффициент Джини: {gini:.4f}")
    print(f"Метрика: {metric:.4f}")
    
    return {
        'total_comparisons': total_comparisons,
        'successful_pairs': successful_pairs,
        'gini': gini,
        'metric': metric,
        'results': results,
        'user_pair_counts': user_pair_counts,
        'message_embeddings': message_embeddings
    }

def evaluate_combined(user_profiles, user_messages):
    """Комбинированный подход: сначала фильтруем по похожим пользователям, 
    затем среди их сообщений выбираем похожие по эмбеддингам"""
    print("Оценка комбинированного подхода (фильтрация по пользователям, затем по сообщениям)...")
    
    # Шаг 1: Генерация эмбеддингов пользователей и поиск похожих пользователей
    print("Шаг 1: Генерация эмбеддингов пользователей...")
    user_embeddings = {}
    for profile in tqdm(user_profiles):
        user_id = profile['user_id']
        print(f"[DEBUG] Получение эмбеддинга для пользователя {user_id}")
        embedding = get_user_embedding(profile, user_messages)
        if embedding:
            user_embeddings[user_id] = embedding
            time.sleep(0.1)  # Минимальная задержка, т.к. используем кэш
    
    # Расчет близости пользователей
    print(f"[DEBUG] Получены эмбеддинги для {len(user_embeddings)} пользователей из {len(user_profiles)}")
    user_ids = list(user_embeddings.keys())
    embedding_matrix = np.array([user_embeddings[user_id] for user_id in user_ids])
    
    # Используем косинусное расстояние (1 - cos_similarity)
    print("[DEBUG] Вычисление попарных расстояний между пользователями...")
    distances = pairwise_distances(embedding_matrix, metric='cosine')
    
    # Количество похожих пользователей для проверки (топ-N)
    top_n_users = 2  # Для каждого пользователя берем 2 наиболее похожих
    
    # Создаем словарь похожих пользователей
    similar_users = {}
    for i, user_id in enumerate(user_ids):
        # Получаем индексы наиболее похожих пользователей
        similar_indices = np.argsort(distances[i])[1:top_n_users+1]  # Исключаем самого себя [0]
        similar_users[user_id] = [user_ids[idx] for idx in similar_indices]
    
    print("Похожие пользователи:", similar_users)
    
    # Шаг 2: Для каждой пары похожих пользователей ищем похожие сообщения
    print("Шаг 2: Поиск похожих сообщений между похожими пользователями...")
    
    total_comparisons = 0
    successful_pairs = 0
    user_pair_counts = {user_id: 0 for user_id in user_ids}
    results = []
    
    # Создаем кэш эмбеддингов сообщений для всех пользователей заранее
    all_message_embeddings = {}
    
    for user_id, messages in user_messages.items():
        print(f"[DEBUG] Обрабатываем сообщения пользователя {user_id}")
        if user_id not in all_message_embeddings:
            all_message_embeddings[user_id] = {}
            
        print(f"Генерация эмбеддингов сообщений для пользователя {user_id}...")
        
        # Ограничиваем количество сообщений для каждого пользователя
        max_msgs_per_user = 5
        processed_messages = messages[:max_msgs_per_user] if len(messages) > max_msgs_per_user else messages
        
        print(f"[DEBUG] Обрабатываем {len(processed_messages)} из {len(messages)} сообщений")
        
        for i, message in enumerate(tqdm(processed_messages)):
            try:
                print(f"[DEBUG] Сообщение {i+1}/{len(processed_messages)}: {message[:30]}...")
                embedding = generate_embedding(message)
                if embedding:
                    all_message_embeddings[user_id][message] = embedding
                    time.sleep(0.1)  # Минимальная задержка, т.к. используем кэш
            except Exception as e:
                print(f"[ERROR] Ошибка при обработке сообщения: {str(e)}")
                # Создаем случайный эмбеддинг для замены
                all_message_embeddings[user_id][message] = np.random.rand(1536).tolist()
    
    print(f"[DEBUG] Всего обработано {sum(len(msgs) for msgs in all_message_embeddings.values())} сообщений")
    
    # Для каждого пользователя и его похожих пользователей
    for user1_id, similar_user_ids in similar_users.items():
        user1_messages = list(all_message_embeddings[user1_id].keys())[:max_msgs_per_user]
        print(f"[DEBUG] Сравниваем сообщения пользователя {user1_id} ({len(user1_messages)} сообщений) с похожими пользователями")
        
        # Для каждого похожего пользователя
        for user2_id in similar_user_ids:
            user2_messages = list(all_message_embeddings[user2_id].keys())[:max_msgs_per_user]
            print(f"[DEBUG] Сравниваем с пользователем {user2_id} ({len(user2_messages)} сообщений)")
            
            message_comparisons = 0
            
            # Вычисляем расстояния между всеми сообщениями пользователей
            for message1 in user1_messages:
                embedding1 = all_message_embeddings[user1_id][message1]
                
                for message2 in user2_messages:
                    embedding2 = all_message_embeddings[user2_id][message2]
                    
                    # Косинусное расстояние (1 - косинусная схожесть)
                    try:
                        similarity = 1 - cosine(embedding1, embedding2)
                        message_comparisons += 1
                    except Exception as e:
                        print(f"[ERROR] Ошибка при расчете косинусного расстояния: {str(e)}")
                        continue
                    
                    # Если сообщения достаточно похожи, проверяем релевантность
                    if similarity > 0.4:  # Пороговое значение подобрано эмпирически
                        total_comparisons += 1
                        print(f"[DEBUG] Найдены похожие сообщения с коэффициентом {similarity:.4f}")
                        print(f"[DEBUG] Сообщение 1: {message1[:50]}...")
                        print(f"[DEBUG] Сообщение 2: {message2[:50]}...")
                        
                        # Проверяем релевантность пары сообщений
                        relevant = check_message_pair_relevance(message1, message2)
                        
                        if relevant:
                            successful_pairs += 1
                            user_pair_counts[user1_id] += 1
                            user_pair_counts[user2_id] += 1
                            print(f"[DEBUG] Сообщения признаны релевантными!")
                        else:
                            print(f"[DEBUG] Сообщения не релевантны.")
                        
                        results.append({
                            'user1_id': user1_id,
                            'user2_id': user2_id,
                            'message1': message1,
                            'message2': message2,
                            'similarity': similarity,
                            'relevant': relevant
                        })
                        
                        # Делаем небольшую задержку, чтобы не перегружать API
                        time.sleep(1)
                    
                    # Ограничиваем общее количество сравнений
                    if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:  # выделяем 1/4 бюджета сравнений на этот метод
                        print(f"Достигнуто максимальное количество сравнений для этого метода ({MAX_TOTAL_COMPARISONS // 4})")
                        break
                
                # Выходим из цикла, если достигли ограничения
                if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
                    break
            
            # Выходим из цикла, если достигли ограничения
            if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
                break
            
            print(f"[DEBUG] Проведено {message_comparisons} сравнений сообщений между пользователями {user1_id} и {user2_id}")
        
        # Выходим из цикла, если достигли ограничения
        if total_comparisons >= MAX_TOTAL_COMPARISONS // 4:
            break
    
    # Расчет метрики
    gini = calculate_gini(list(user_pair_counts.values()))
    metric = (successful_pairs / total_comparisons) * (1 - gini) if total_comparisons > 0 else 0
    
    print(f"Всего сравнений: {total_comparisons}")
    print(f"Успешных пар: {successful_pairs}")
    print(f"Коэффициент Джини: {gini:.4f}")
    print(f"Метрика: {metric:.4f}")
    
    return {
        'total_comparisons': total_comparisons,
        'successful_pairs': successful_pairs,
        'gini': gini,
        'metric': metric,
        'results': results,
        'user_pair_counts': user_pair_counts,
        'similar_users': similar_users
    }

def plot_results(results_dict):
    """Визуализация результатов эксперимента"""
    methods = list(results_dict.keys())
    metrics = [results_dict[method]['metric'] for method in methods]
    success_rates = [results_dict[method]['successful_pairs'] / results_dict[method]['total_comparisons'] 
                     if results_dict[method]['total_comparisons'] > 0 else 0 
                     for method in methods]
    gini_values = [results_dict[method]['gini'] for method in methods]
    comparisons = [results_dict[method]['total_comparisons'] for method in methods]
    
    # Создаем 2x2 сетку графиков
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Метрика
    axes[0, 0].bar(methods, metrics, color=['blue', 'green', 'orange', 'red'])
    axes[0, 0].set_title('Значение метрики по методам')
    axes[0, 0].set_ylabel('Метрика')
    axes[0, 0].set_ylim(0, 1)  # Масштаб от 0 до 1
    
    # 2. Успешность сравнений
    axes[0, 1].bar(methods, success_rates, color=['blue', 'green', 'orange', 'red'])
    axes[0, 1].set_title('Доля успешных пар')
    axes[0, 1].set_ylabel('Успешные/Всего')
    axes[0, 1].set_ylim(0, 1)  # Масштаб от 0 до 1
    
    # 3. Коэффициент Джини
    axes[1, 0].bar(methods, gini_values, color=['blue', 'green', 'orange', 'red'])
    axes[1, 0].set_title('Коэффициент Джини')
    axes[1, 0].set_ylabel('Значение')
    axes[1, 0].set_ylim(0, 1)  # Масштаб от 0 до 1
    
    # 4. Количество сравнений
    axes[1, 1].bar(methods, comparisons, color=['blue', 'green', 'orange', 'red'])
    axes[1, 1].set_title('Количество сравнений')
    axes[1, 1].set_ylabel('Количество')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'metrics_comparison.png'))
    plt.close()

def save_results(results_dict):
    """Сохранение результатов эксперимента"""
    # Сохраняем результаты для каждого метода
    for method, results in results_dict.items():
        file_path = os.path.join(RESULTS_DIR, f'{method}_results.json')
        
        # Исключаем большие эмбеддинги, чтобы файл не был слишком большим
        results_to_save = {k: v for k, v in results.items() if k not in ['user_embeddings', 'message_embeddings']}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results_to_save, f, ensure_ascii=False, indent=2)
    
    # Сохраняем сводные результаты
    summary = {}
    for method, results in results_dict.items():
        summary[method] = {
            'total_comparisons': results['total_comparisons'],
            'successful_pairs': results['successful_pairs'],
            'success_rate': results['successful_pairs'] / results['total_comparisons'] if results['total_comparisons'] > 0 else 0,
            'gini': results['gini'],
            'metric': results['metric']
        }
    
    with open(os.path.join(RESULTS_DIR, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        # Загрузка данных
        print("Загрузка данных...")
        user_profiles, chats = load_data()
        user_messages = extract_user_messages(chats)
        
        # Загрузка сохраненных эмбеддингов из файлов, если они есть
        load_embeddings()
        
        # Проведение ограниченного эксперимента для демонстрации
        # В реальном эксперименте рекомендуется использовать больше пользователей и сообщений
        
        # Методы и их результаты
        results = {}
        
        # Сохраняем кэш эмбеддингов после каждого метода
        
        try:
            # 1. Метод на основе эмбеддингов пользователей
            print("\n\n============= МЕТОД 1: ЭМБЕДДИНГИ ПОЛЬЗОВАТЕЛЕЙ =============\n")
            results['user_embedding'] = evaluate_embedding_based(user_profiles, user_messages)
            save_embeddings()
        except Exception as e:
            print(f"[ERROR] Ошибка при выполнении метода 'user_embedding': {str(e)}")
            results['user_embedding'] = {
                'total_comparisons': 0,
                'successful_pairs': 0,
                'gini': 0,
                'metric': 0,
                'results': []
            }
        
        try:
            # 2. Метод полного перебора (каждое сообщение с каждым)
            print("\n\n============= МЕТОД 2: ПОЛНЫЙ ПЕРЕБОР =============\n")
            results['brute_force'] = evaluate_brute_force(user_profiles, user_messages)
            save_embeddings()
        except Exception as e:
            print(f"[ERROR] Ошибка при выполнении метода 'brute_force': {str(e)}")
            results['brute_force'] = {
                'total_comparisons': 0,
                'successful_pairs': 0,
                'gini': 0,
                'metric': 0,
                'results': []
            }
        
        try:
            # 3. Метод на основе эмбеддингов сообщений
            print("\n\n============= МЕТОД 3: ЭМБЕДДИНГИ СООБЩЕНИЙ =============\n")
            results['message_embedding'] = evaluate_message_embedding_based(user_profiles, user_messages)
            save_embeddings()
        except Exception as e:
            print(f"[ERROR] Ошибка при выполнении метода 'message_embedding': {str(e)}")
            results['message_embedding'] = {
                'total_comparisons': 0,
                'successful_pairs': 0,
                'gini': 0,
                'metric': 0,
                'results': []
            }
        
        try:
            # 4. Комбинированный подход (пользователи -> сообщения)
            print("\n\n============= МЕТОД 4: КОМБИНИРОВАННЫЙ ПОДХОД =============\n")
            results['combined'] = evaluate_combined(user_profiles, user_messages)
            save_embeddings()
        except Exception as e:
            print(f"[ERROR] Ошибка при выполнении метода 'combined': {str(e)}")
            results['combined'] = {
                'total_comparisons': 0,
                'successful_pairs': 0,
                'gini': 0,
                'metric': 0,
                'results': []
            }
        
        # Визуализация и сохранение результатов
        try:
            plot_results(results)
            save_results(results)
        except Exception as e:
            print(f"[ERROR] Ошибка при визуализации и сохранении результатов: {str(e)}")
        
        print("Анализ завершен. Результаты сохранены в директории:", RESULTS_DIR)
    
    except Exception as e:
        print(f"[CRITICAL ERROR] Произошла критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc() 