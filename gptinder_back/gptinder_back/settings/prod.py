import dj_database_url
from .base import *

DEBUG = True

# База данных для продакшн
DATABASES = {
        "default": dj_database_url.parse(os.getenv("DATABASE_URL")),
}



# Дополнительные настройки безопасности
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True



AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')


AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_LOCATION = os.getenv('AWS_LOCATION')

AWS_QUERYSTRING_AUTH = False


STATIC_URL = f'https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/'
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/'

STORAGES = {
    "default": {
        "BACKEND": 'homecheck.cdn.backends.MediaRootS3Boto3Storage',
        "OPTIONS": {
        },
    },
    "staticfiles": {
        "BACKEND": 'homecheck.cdn.backends.StaticRootS3Boto3Storage',
        "OPTIONS": {
        },
    },
}
