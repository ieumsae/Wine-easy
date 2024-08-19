import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    DB_USER = os.getenv('root')
    DB_PASSWORD = os.getenv('1234')
    DB_HOST = os.getenv('localhost')
    DB_NAME = os.getenv('wine_DB')