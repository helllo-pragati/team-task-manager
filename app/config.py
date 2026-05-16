"""Application configuration."""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Database
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///taskmanager.db')
    # Railway uses postgres:// but SQLAlchemy requires postgresql://
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_DECODE_ALGORITHMS = ['HS256']

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'flask-secret-key-change-in-production')
