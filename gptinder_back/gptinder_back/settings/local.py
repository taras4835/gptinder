from .base import *

DEBUG = True

# Максимально ослабленные настройки CORS для локальной разработки
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*'] 
CORS_EXPOSE_HEADERS = ['*']
CORS_ALLOW_PRIVATE_NETWORK = True
CORS_PREFLIGHT_MAX_AGE = 86400  # 1 day

# База данных для локальной разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Простой кэш для локальной разработки вместо Redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Отключаем Celery для локальной разработки
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# Конфигурация статики (чтобы удобно развивать)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
