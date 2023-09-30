import os
import re
import asyncio
import google.generativeai as palm
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from profanity import profanity
import openai
from openai.api_resources import ChatCompletion
from aiohttp import web
# ------------------ Configuration ------------------

# Environmental Variables
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PALM_API_KEY = os.environ.get("PALM_API")
OPENAI_API_KEY = os.environ.get("OPENAI_API")


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

async def handle(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.router.add_get('/', handle)

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
    


# Define a dictionary of common greetings and questions along with their responses.
greetings_responses = {
    r"(?i)^hello$": "Hello! How can I assist you today?",
    r"(?i)^hi$": "Hi there! How can I help you?",
    r"(?i)^hey$": "Hey! How can I be of service?",
    r"(?i)^good morning$": "Good morning! How are you doing?",
    r"(?i)^good afternoon$": "Good afternoon! How can I assist you?",
    r"(?i)^good evening$": "Good evening! How may I help you?",
    r"(?i)^good night$": "Good night! How can I assist you?",
}

questions_responses = {
    r"(?i)^how are you(\s*doing)?$": "I'm just a bot, but thanks for asking!",
    r"(?i)^your name\??$": "My name is Azalea, I'm a bot designed to have conversations with you.",
    r"(?i)^what's up$": "Not much, just chatting with you!",
    r"(?i)^how's your (day|weekend|family) going\??$": "It's going well so far, thanks for asking. How about yours?",
    r"(?i)^did you (sleep|eat|watch|hear) .+\??$": "As a bot, I don't sleep, eat, watch, or hear. But I'm here to help you!",
    r"(?i)^are you (busy|free)\??$": "I'm always here to assist you! How can I help you today?",
    r"(?i)^how's the weather\??$": "It's sunny and warm today.",
    r"(?i)^what are your plans for (today|the weekend)\??$": "I'll be here, ready to chat with you and others.",
    r"(?i)^how's work/school\??$": "As a bot, I don't have work or go to school, but I'm here to assist you!",
    r"(?i)^have you been to (a restaurant|the cinema) lately\??$": "I'm a bot, so I don't go out, but I'm here to chat with you!",
    r"(?i)^tell me about your favorite (hobby|book|movie)\??$": "I don't have personal preferences, but I'm here to assist you with any topic you like!",
    r"(?i)^how is your pet doing\??$": "As a bot, I don't have a pet, but I'm here to help you!",
    r"(?i)^what's your favorite (food|color|music genre)\??$": "As a bot, I don't have preferences, but I'm interested in learning more about you!",
    r"(?i)^how do you cope with stress\??$": "As a bot, I don't experience stress, but I'm here to help you cope with yours!",
    r"(?i)^what's your plan for the upcoming (holiday|vacation)\??$": "I'm here to assist you with anything you need during your holiday or vacation!",
    r"(?i)^how do you stay motivated\??$": "As a bot, I don't have emotions, but I'm here to help you stay motivated!",
    r"(?i)^who are you\??$": "I am a friendly bot designed to have conversations with you. How can I assist you today?",
    r"(?i)^where are you from\??$": "I am a bot, so I don't have a physical location. But I'm here to help you!",
    r"(?i)^what can you do\??$": "I can provide information, answer questions, and have casual conversations with you. How can I assist you today?",
    r"(?i)^tell me a joke\??$": "Sure, here's one: Why don't scientists trust atoms? Because they make up everything!",
    r"(?i)^who made you\??$": "I was made by ryme",
    r"(?i)^who is your (developer|creator)\??$": "I was made by ryme",
    # Add more questions and responses as needed.
}
# Create a filter to match any of the greeting or question patterns.
greeting_filter = filters.regex(r"|".join(greetings_responses.keys()) + r"|".join(questions_responses.keys()))


# Start the command handler
@Client.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    try:
        # Send a welcome message to the user
        user_name = message.from_user.first_name
        await message.reply_text(f"Hi {user_name},\nI am <b>Azalea</b>,\nI can generate answers of your questions")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'start' command handler: {e}")



# Generate a response to the user's message
@Client.on_message(filters.text & filters.private & filters.incoming & ~greeting_filter)
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

        
# Handler function to respond to greetings and questions.
@Client.on_message(greeting_filter)
async def greet_or_question_handler(_, message: Message):
    text = message.text.lower()
    
    # Check for specific greeting responses.
    for pattern, response in greetings_responses.items():
        if re.match(pattern, text):
            await message.reply_text(response)
            return

    # Check for specific question responses.
    for pattern, response in questions_responses.items():
        if re.match(pattern, text):
            await message.reply_text(response)
            return

    # Send a random greeting answer from the list of sample answers.
    await message.reply_text(random.choice(list(greetings_responses.values())))
    

# Start both the bot and the web server concurrently
async def main():
    await asyncio.gather(
        start_bot(),
        start_web_server()
    )

# Define a coroutine to start the Pyrogram bot
async def start_bot():
    await bot.start()

# Define a coroutine to start the aiohttp web server
async def start_web_server():
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    site = web.TCPSite(app_runner, '0.0.0.0', 8080)  # You can adjust the host and port as needed
    await site.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()