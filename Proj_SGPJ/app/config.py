import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    SECRET_KEY = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin2024@localhost:5432/data_sgpj'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
