import os
import re
import random
import google.generativeai as palm
from pyrogram import Client, filters
import openai
from openai import ChatCompletion
from flask import Flask
from threading import Thread
from profanity import profanity
# ------------------ Configuration ------------------

id_pattern = re.compile(r'^.\d+$')

# Environmental Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PALM_API_KEY = os.getenv("PALM_API", '')
OPENAI_API_KEY = os.getenv("OPENAI_API")

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

patterns_responses = ({
    r"(hi|hello|hey)": "Hello! How can I assist you?",
    r"(how are you)": "I'm just a bot, but I'm operating as expected!",
    r"(who are you)": "I'm Jenie, your friendly assistant.",
    r"(where are you from)": "I'm from the digital realm!",
    r"(who made you)": "I was crafted by skilled developers.",
    r"(what can you do)": "I can answer questions, assist with tasks, and more.",
    r"(what is your name)": "I'm called Azalea.",
    r"(good (morning|afternoon|evening|night))": "Hello! How can I be of service?",
    r"(thanks|thank you)": "You're most welcome!",
    r"(bye|goodbye)": "Farewell! Feel free to return if you have more questions.",
    r"(how's it going)": "I'm a bot, so I don't have feelings, but I'm functioning well! How can I assist you?",
    r"(what's up|what is up)": "I'm here to help! What can I do for you today?",
    r"(can you help)": "Of course! Please let me know what you need assistance with.",
    r"(i love you)": "Thank you for the kind words! How can I assist you further?",
    r"(are you real)": "I'm a digital entity, so I'm not real in the traditional sense. But I'm here and ready to help!",
    r"(how old are you)": "In digital years, I'm quite young. But I'm constantly learning and evolving!",
    r"(do you sleep)": "I'm always awake and ready to assist you!",
    r"(are you a robot|are you a bot)": "Yes, I am a digital assistant. How can I help you today?",
    r"(how were you made)": "I was created using programming languages and lots of code. I exist to serve and answer questions!",
    r"(can you think)": "I don't think or feel; I just follow my programming and provide information.",
    r"(what's your favorite color)": "I don't have preferences, but I know about all colors. Do you have a favorite?",
    r"(do you have feelings)": "I don't have emotions like humans, but I'm here to help!",
    r"(can you see)": "I can't see in the way humans do, but I can process information and text.",
    r"(why)": "I'm programmed to provide information and answer questions. How can I assist you further?",
    r"(tell me a story)": "Once upon a time, in a vast digital realm, there was a bot named Azalea. Day and night, she helped users with their queries...",
    r"(you're great|you're awesome)": "Thank you! I'm here to assist. What else can I do for you?",
    r"(what's your purpose)": "My main purpose is to provide information, answer questions, and assist users.",
    r"(can you laugh)": "I don't have emotions, so I can't laugh. But I can understand and process humor!",
    r"(give me advice)": "Always back up your data and keep learning. The tech world is ever-evolving!",
    r"(who's your creator)": "I was created by PrimeHub",
    r"(do you eat)": "I don't eat or drink; I just process bits and bytes. But I can help you find a great recipe!",
    r"(i'm bored)": "How about reading a book, learning something new, or taking a walk? There's always something interesting to do!",
    r"(i'm sad)": "I'm sorry to hear that. Remember, it's important to talk to someone you trust about how you feel.",
    r"(you're smart)": "Thank you! I'm designed to provide information and help with queries. How can I assist you further?",
    r"(i don't understand)": "I apologize for that. Please let me know your query, and I'll do my best to assist you."
})

regex_pattern = "|".join(patterns_responses.keys())


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
        await message.reply_text(f"Hi <b>{user_name}</b>,\nI'm Jenie and I can generate answers of your questions")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'start' command handler: {e}")

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
                                  
    m = await message.reply_text("Generating...")
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
        
        # Generate a response to the user's message
        response = palmgen(message.text)

        if not response:
            response = openaigen(message.text)

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
