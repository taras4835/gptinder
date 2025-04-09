import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if ENVIRONMENT == 'prod':
    from .prod import *
elif ENVIRONMENT == 'local':
    from .local import *
else:
    from .base import * 