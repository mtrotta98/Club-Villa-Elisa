from distutils.command.config import config
from os import environ
from datetime import datetime


class Config(object):
    """Base configuration."""

    SECRET_KEY = "secret"
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = "secret_key"
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_ACCESS_CSRF_HEADER_NAME = "csrf_access_token"
    JWT_COOKIE_CSRF_PROTECT = False
    # Desactivar CSRF para testear API POST de registrar pagos
    # WTF_CSRF_CHECK_DEFAULT = False


class ProductionConfig(Config):
    """Production configuration."""

    DB_USER = environ.get("DB_USER")
    DB_PASS = environ.get("DB_PASS")
    DB_HOST = environ.get("DB_HOST")
    DB_NAME = environ.get("DB_NAME")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
    SESSION_TYPE = "filesystem"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    DB_SERVER = "localhost"
    DB_DATABASE = "proyecto_db"
    DB_USER = "postgres"
    DB_PASSWORD = "proyecto"
    DB_PORT = "5432"
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DATABASE}"
    SESSION_TYPE = "filesystem"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
}
