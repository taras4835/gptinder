import os
import sys
import time
import argparse
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Используемые модели
GPT_MODEL = "gpt-4.1-nano-2025-04-14"
EMBEDDING_MODEL = "text-embedding-3-small"

def print_heading(text):
    """Печать заголовка для лучшей читаемости вывода"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Запуск эксперимента с синтетическими данными')
    parser.add_argument('--users', type=int, default=5, help='Количество пользователей для генерации (по умолчанию: 5)')
    parser.add_argument('--mode', choices=['generate', 'analyze', 'both'], default='both', 
                        help='Режим работы: только генерация данных, только анализ, или оба (по умолчанию: both)')
    
    args = parser.parse_args()
    
    # Проверка наличия API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("ОШИБКА: Не найден ключ OPENAI_API_KEY в файле .env")
        sys.exit(1)
    
    print_heading("ИНФОРМАЦИЯ О МОДЕЛЯХ")
    print(f"Модель для генерации текста и оценки релевантности: {GPT_MODEL}")
    print(f"Модель для генерации эмбеддингов: {EMBEDDING_MODEL}")
    
    if args.mode in ['generate', 'both']:
        print_heading("ГЕНЕРАЦИЯ СИНТЕТИЧЕСКИХ ДАННЫХ")
        # Модифицируем файл generate_data.py, чтобы использовать указанное количество пользователей
        with open('generate_data.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        code = code.replace('num_users = 3', f'num_users = {args.users}')
        
        with open('generate_data.py', 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"Запуск генерации данных для {args.users} пользователей...")
        
        # Запуск генерации данных
        os.system('python generate_data.py')
        
        print("Генерация синтетических данных завершена!")
        
    if args.mode in ['analyze', 'both']:
        # Если мы запускаем оба процесса, даем небольшую паузу между генерацией и анализом
        if args.mode == 'both':
            print("\nПодождите, подготовка к анализу данных...")
            time.sleep(3)
        
        print_heading("АНАЛИЗ ДАННЫХ И ЭКСПЕРИМЕНТ")
        
        # Проверка наличия сгенерированных данных
        if not os.path.exists('data/user_profiles.json'):
            print("ОШИБКА: Файл с профилями пользователей не найден. Сначала запустите генерацию данных.")
            sys.exit(1)
        
        # Запуск анализа данных
        os.system('python analyze_data.py')
        
        print("Анализ данных завершен!")
    
    if args.mode == 'both':
        print_heading("ЭКСПЕРИМЕНТ ЗАВЕРШЕН")
        print("Результаты сохранены в директории data/results/")
        print("Метрики можно посмотреть в файле data/results/summary.json")
        print("Визуализация результатов: data/results/metrics_comparison.png")

if __name__ == "__main__":
    main() 