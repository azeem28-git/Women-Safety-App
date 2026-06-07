import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file if present.
load_dotenv()


def normalize_database_url(url: str) -> str:
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url

DEFAULT_DATABASE_URL = normalize_database_url(
    os.environ.get('DATABASE_URL', 'postgresql+psycopg://neondb_owner:npg_LGlYeIU1juE0@ep-small-bread-ap96sguq-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'women-safety-secret-key-2024-change-in-production')
    SQLALCHEMY_DATABASE_URI = DEFAULT_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
