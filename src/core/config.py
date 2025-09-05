import os
from dotenv import load_dotenv

# load .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "IELTS app"
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db") # TODO: will change it to mongodb

settings = Settings()