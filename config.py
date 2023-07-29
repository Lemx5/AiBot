import os


API_ID = int(os.environ.get("API_ID", "11948995"))
API_HASH = os.environ.get("API_HASH", "cdae9279d0105638165415bf2769730d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6197051152:AAHb2-RxyQGd1WCqtKHHM20XzxV3tEAfEaA")

# PaLM api
PALM_API = os.environ.get("PALM_API", "AIzaSyBzo-WEIY25kL5wHQ5H1YUQp2VVANRxWNI")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://ryme:ryme@ryme.jrvxshk.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("DB_NAME", "palmbot")