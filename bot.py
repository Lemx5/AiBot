import os
import re
import asyncio
import google.generativeai as palm
from pyrogram import Client, filters
from profanity import profanity
import openai
from openai.api_resources import ChatCompletion
from flask import Flask
from threading import Thread
# ------------------ Configuration ------------------

id_pattern = re.compile(r'^.\d+$')

# Environmental Variables
API_ID = os.environ.get("API_ID", "11948995")
API_HASH = os.environ.get("API_HASH", "cdae9279d0105638165415bf2769730d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6197051152:AAHb2-RxyQGd1WCqtKHHM20XzxV3tEAfEaA")
PALM_API_KEY = os.environ.get("PALM_API")
OPENAI_API_KEY = os.environ.get("OPENAI_API")
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMINS', '1247742004 2012121532 2141736280').split()]


# Palm Client Configuration
palm.configure(api_key=PALM_API_KEY)
# openai api key
openai.api_key = OPENAI_API_KEY

# Pyrogram Client Configuration
bot = Client(
    name="PalmUserBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ------------------ Palm Generator ------------------
def palmgen(text):
    try:
        response = palm.generate_text(
            model='models/text-bison-001',
            prompt=text,
            temperature=0.7,
            candidate_count=1,
            top_k=40,
            top_p=0.95,
            max_output_tokens=1024,
        )
        return response.result
    except Exception as e:
        return f"Error generating text: {str(e)}"

# ------------------ OpenAI Generator ------------------
def openaigen(text):
    messages = [{"role": "assistant", "content": text}]
    try:
        MODEL = "gpt-3.5-turbo"    # gpt-3.5-turbo model
        resp = ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
        )
        rep = resp['choices'][0]["message"]["content"]
        return rep
    except Exception as e:
        return f"Error generating text: {str(e)}"
    

# Start the command handler
@bot.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    try:
        # Send a welcome message to the user
        user_name = message.from_user.first_name
        await message.reply_text(f"Hi <b>{user_name}</b>,\nI'm Azalea and I can generate answers of your questions")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'start' command handler: {e}")


# Generate a response to the user's message
@bot.on_message(filters.text & filters.private & filters.incoming & filters.user(ADMINS))
async def generate(client, message):
                                  
    m = await message.reply_text("Generating...")
    try:
        if message.text.startswith('/'):
            return
        
        # Check if the user's message contains any inappropriate words
        if profanity.contains_profanity(message.text):
            await message.reply_text("Sorry, I cannot respond to inappropriate messages.")
            return

        # check if the user's message contains any external links
        if re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.text):
            await message.reply_text("Sorry, I have been restricted to give information on external links.")
            return
        
        # Generate a response to the user's message
        response = openaigen(message.text)

        if not response:
            response = palmgen(message.text)

        # Send the response to the user
        await message.reply_text(response)        

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'generate' message handler: {e}")

    finally:
        await m.delete()    

# Flask configuration
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.run()      
