from config import Config

def validate_api_key(api_key):
    return api_key == Config.API_KEY
