import os
import re
import google.generativeai as gem
from pyrogram import Client, filters
from flask import Flask
from threading import Thread
from profanity import profanity
# ------------------ Configuration ------------------

id_pattern = re.compile(r'^.\d+$')

# Environmental Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# gemini Client Configuration
gem.configure(api_key=GENAI_API_KEY)

# Pyrogram Client Configuration
bot = Client(
    name="geminibot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

patterns_responses = {
    re.compile(r"(hi|hello|hey)", re.IGNORECASE): "Hello! How can I assist you?",
    re.compile(r"(how are you)", re.IGNORECASE): "I'm operating as expected!",
    re.compile(r"(who are you)", re.IGNORECASE): "I'm your assistant.",
    re.compile(r"(what can you do)", re.IGNORECASE): "I can answer questions and assist with tasks.",
    re.compile(r"(what is your name)", re.IGNORECASE): "I'm called Azalea.",
    re.compile(r"(good (morning|afternoon|evening|night))", re.IGNORECASE): "Hello! How can I assist you?",
    re.compile(r"(thanks|thank you)", re.IGNORECASE): "You're welcome!",
    re.compile(r"(bye|goodbye)", re.IGNORECASE): "Farewell! Feel free to return if you have more questions.",
    re.compile(r"(how's it going|what's up|what is up)", re.IGNORECASE): "I'm here to help! What can I do for you today?",
    re.compile(r"(can you help)", re.IGNORECASE): "Of course! What do you need assistance with?",
    re.compile(r"(are you real|are you a robot|are you a bot)", re.IGNORECASE): "Yes, I am a digital assistant. How can I help you today?",
    re.compile(r"(how old are you|do you sleep|can you think|do you have feelings|can you see)", re.IGNORECASE): "I'm a digital entity, I don't have human characteristics. But I'm here to help!",
    re.compile(r"(why)", re.IGNORECASE): "I'm here to provide information and answer questions. How can I assist you further?",
    re.compile(r"(you're great|you're awesome|you're smart)", re.IGNORECASE): "Thank you! How else can I assist you?",
    re.compile(r"(what's your purpose)", re.IGNORECASE): "My main purpose is to provide information and assist users.",
    re.compile(r"(i don't understand)", re.IGNORECASE): "I apologize for that. Please let me know your query, and I'll do my best to assist you."
}

def google(text):
    try:
        model = gem.GenerativeModel("gemini-pro")
        convo = model.start_chat(history=[])
        convo.send_message(text)
        return convo.last.text
    except Exception as e:
        return f"Error generating text: {str(e)}"
    

# Start the command handler
@bot.on_message(filters.command('start', prefixes='/'))
async def start(_, message):
    await message.reply_text(
        f"Hi <b>{message.from_user.first_name}</b>,\nI'm Gemini & I can help in finding answers of your questions"
        )

# Generate a response to the user's message
@bot.on_message(filters.text & filters.private & filters.incoming)
async def generate(_, message):

    for pattern, response in patterns_responses.items():
        if pattern.search(message.text):
            await message.reply_text(response)
            return
                                  
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

# Flask configuration
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
