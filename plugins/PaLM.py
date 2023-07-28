import re
from pyrogram import Clients, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API_KEY

palm.configure(api_key=PALM_API_KEY)



@Clients.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    await message.reply_text('Hi, I am PaLM. I can generate text based on the input you give me')



@Clients.on_message(filters.text & filters.private)
async def generate(client, message):
    if message.text.startswith('/'):
        return
    # Check if the user's message contains any inappropriate words
    if profanity.contains_profanity(message.text):
        await message.reply_text("Sorry, I cannot respond to inappropriate messages.")
        return
    # check if the user's message contains any external links
    if re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.text):
        await message.reply_text("Sorry, I have been restricted to give information on external link.")
        return
    
    try:
        # Generate text based on the user's input
        defaults = {
            'model': 'models/chat-bison-001',
            'temperature': 0.25,
            'candidate_count': 1,
            'top_k': 40,
            'top_p': 0.95,
            }
        context = ""
        response = palm.chat(
            **defaults,
            context=context,
            messages=message.text
            )

        await message.reply_text(f"{response}")

    except Exception as e:
        await message.reply_text(f"Error: {e}")
        return