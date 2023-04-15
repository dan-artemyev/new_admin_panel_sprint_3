"""
Django settings for movies_admin project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:8080', ]

LOCALE_PATHS = ['movies/locale']

include(
    'components/logging.py',
    'components/database.py',
    'components/application.py',
    'components/password_validation.py',
    'components/internationalization.py',
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/app/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
