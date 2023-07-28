import os


API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

ADMINS = os.environ.get("ADMINS", "123")

# PaLM api
PALM_API = os.environ.get("PALM_API", "")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DATABASE_NAME = os.environ.get("DB_NAME", "palm")