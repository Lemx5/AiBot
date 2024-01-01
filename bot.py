import os
import re
import google.generativeai as genai
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from profanity import profanity
import json
from collections import deque
import pytz
from datetime import datetime

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)

bot = Client(
    name="geminibot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

kol = pytz.timezone('Asia/Kolkata')
current_hour = kol.localize(datetime.datetime.now()).hour

if current_hour < 12:
    wish = "Good Morning"
elif current_hour < 16:
    wish = "Good Afternoon"
elif current_hour < 20:
    wish = "Good Evening"
else:
    wish = "Good Night"

histories = {}
def gemini(user_id, text):
    try:
        generation_config = {
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
            }

        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        ]

        model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

        if user_id not in histories:
            histories[user_id] = []

        # Initialize the history for a user
        if user_id not in histories:
            histories[user_id] = deque(maxlen=10)

        # Start the chat with the user's history
        convo = model.start_chat(history=[item for sublist in histories[user_id] for item in sublist])  # Flatten the list of lists
        convo.send_message(text)

        # Add the user's message and the model's response to the history together
        histories[user_id].append([
            {
                "role": "user",
                "parts": f"{text}"
            },
            {
                "role": "model",
                "parts": f"{convo.last.text}"
            }
        ])
        return f"{convo.last.text}"
    except Exception as e:
        return f"Error generating text: {str(e)}"
    

@bot.on_message(filters.command('start', prefixes='/'))
async def start(_, message):
    await message.reply_text(
        f"<b>{wish}!</b> {message.from_user.mention},\nI'm Gemini & I can chat with you or answer your questions. Just ask!",
        )
    
@bot.on_message(filters.command('clear', prefixes='/'))
async def delete_history(_, message):
    user_id = message.from_user.id
    if user_id in histories:
        del histories[user_id]
        await message.reply_text("Your conversation history has been deleted.")
    else:
        await message.reply_text("No conversation found.")

@bot.on_message(filters.command('log', prefixes='/'))
async def read_log(_, message):
    user_id = message.from_user.id
    if user_id in histories:
        history_json = json.dumps(histories[user_id], indent=4)
        await message.reply_text(history_json)
    else:
        await message.reply_text("No logs found.")

@bot.on_message(filters.command('history', prefixes='/'))
async def read_history(_, message):
    user_id = message.from_user.id
    if user_id in histories:
        history_text = ""
        for pair in histories[user_id]:
            user_msg = pair[0]["parts"]
            model_msg = pair[1]["parts"]
            history_text += f"<b>You</b>: <code>{user_msg}</code>\n<b>Model</b>: <code>{model_msg}</code>\n\n"
        await message.reply_text(f"{history_text}\n\n<b>Note</b>: This uses a Python dictionary to temporarily store your last 10 chat messages, preventing memory outage")
    else:
        await message.reply_text("You have no conversation history.")
    
@bot.on_message(filters.media & filters.private & filters.incoming)
async def media(_, message):
    await message.reply_text("Sorry, I have been restricted to give information on media files.")  

@bot.on_message(filters.text & filters.private & filters.incoming)
async def generate(_, message):
    if message.text.startswith("/"):
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
        response = gemini(message.from_user.id, message.text)
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
