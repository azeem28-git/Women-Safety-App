import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file if present.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = os.environ.get('DATABASE_URL') or (
    'sqlite:////tmp/women_safety.db'
    if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('VERCEL') == '1'
    else f"sqlite:///{INSTANCE_DIR / 'women_safety.db'}"
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'women-safety-secret-key-2024-change-in-production')
    SQLALCHEMY_DATABASE_URI = DEFAULT_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'check_same_thread': False}}
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///women_safety_dev.db'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
