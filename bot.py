import os
import re
import google.generativeai as gem
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from profanity import profanity

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

gem.configure(api_key=GENAI_API_KEY)

bot = Client(
    name="geminibot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

def google(text):
    try:
        model = gem.GenerativeModel("gemini-pro")
        convo = model.start_chat(history=[])
        convo.send_message(text)
        return convo.last.text
    except Exception as e:
        return f"Error generating text: {str(e)}"
    

@bot.on_message(filters.command('start', prefixes='/'))
async def start(_, message):
    await message.reply_text(
        f"Hi <b>{message.from_user.first_name}</b>,\nI'm Gemini & I can help in finding answers of your questions"
        )

@bot.on_message(filters.text & filters.private & filters.incoming)
async def generate(_, message):
    if message.text.startswith('/'):
        return
    # check if the user's message contains any external links
    if re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.text):
        await message.reply_text("Sorry, I have been restricted to give information on external links.")
        return
    # Check if the user's message contains any inappropriate words
    if profanity.contains_profanity(message.text):
        await message.reply_text("Sorry, I cannot respond to inappropriate messages.")
        return         
    try:
        m = await message.reply_text("Processing...")
        response = google(message.text)
        await m.edit(response)        
    except Exception as e:
        print(f"Error in 'generate' message handler: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.run()      
