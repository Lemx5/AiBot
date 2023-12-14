import os
import re
import google.generativeai as gemini
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

# gemini Client Configuration
gemini.configure(api_key=os.getenv("PALM_API"))

# Pyrogram Client Configuration
bot = Client(
    name="geminibot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

patterns_responses = ({
    r"(hi|hello|hey)": "Hello! How can I assist you?",
    r"(how are you)": "I'm operating as expected!",
    r"(who are you)": "I'm your assistant.",
    r"(what can you do)": "I can answer questions and assist with tasks.",
    r"(what is your name)": "I'm called Azalea.",
    r"(good (morning|afternoon|evening|night))": "Hello! How can I assist you?",
    r"(thanks|thank you)": "You're welcome!",
    r"(bye|goodbye)": "Farewell! Feel free to return if you have more questions.",
    r"(how's it going|what's up|what is up)": "I'm here to help! What can I do for you today?",
    r"(can you help)": "Of course! What do you need assistance with?",
    r"(are you real|are you a robot|are you a bot)": "Yes, I am a digital assistant. How can I help you today?",
    r"(how old are you|do you sleep|can you think|do you have feelings|can you see)": "I'm a digital entity, I don't have human characteristics. But I'm here to help!",
    r"(why)": "I'm here to provide information and answer questions. How can I assist you further?",
    r"(you're great|you're awesome|you're smart)": "Thank you! How else can I assist you?",
    r"(what's your purpose)": "My main purpose is to provide information and assist users.",
    r"(i don't understand)": "I apologize for that. Please let me know your query, and I'll do my best to assist you."
})
regex_pattern = "|".join(patterns_responses.keys())


# ------------------ Gemini ------------------
def google(text):
    try:
        model = gemini.GenerativeModel('gemini-pro')        
        response = model.generate_content(text)
        return response.text
    
    except Exception as e:
        return f"Error generating text: {str(e)}"


# Start the command handler
@bot.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    # Send a welcome message to the user
    user_name = message.from_user.first_name
    await message.reply_text(f"Hi <b>{user_name}</b>,\nI'm Jenie and I can generate answers of your questions")

# generate response from patterns
@bot.on_message(filters.regex(regex_pattern) & filters.private & filters.incoming)
async def common(client, message):
    for pattern, response in patterns_responses.items():
        if re.search(pattern, message.text, re.IGNORECASE):
            await message.reply_text(response)
            return
        
# Generate a response to the user's message
@bot.on_message(filters.text & filters.private & filters.incoming & ~filters.regex(regex_pattern))
async def generate(client, message):
                                  
    try:
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
        
        m = await message.reply_text("Generating...")

        # Generate a response to the user's message
        response = google(message.text)

        # Send the response to the user
        await m.edit(response)        

    except Exception as e:
        # Handle any unexpected errors and log them
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
