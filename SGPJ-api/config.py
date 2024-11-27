import os
import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://admin:admin2024@localhost:5432/data_sgpj')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY', '895a8p82-5k40-37w7-z595-99abxn8q4fgx')
    #320e986c-e33c-4782-a677-e5e3ce57ad9d