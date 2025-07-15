import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "LocalChatGPT")
    ENV: str = os.getenv("ENV", "development")
    # Add more config variables as needed

settings = Settings() 