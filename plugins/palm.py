import re
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API, API_ID, API_HASH, BOT_TOKEN
from database import db
from bot import app


palm.configure(api_key=PALM_API)


@app.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    try:
        if not await db.is_user_exist(str(message.from_user.id)):
            await db.add_user(str(message.from_user.id))
        
        # Send a welcome message to the user
        user_name = message.from_user.first_name
        await message.reply_text(f"Hi {user_name}, I am Azalea. I can generate text based on the input you give me")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'start' command handler: {e}")


@app.on_message(filters.text & filters.private)
async def generate(client, message):
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

        # Get the user's context from the database
        user_id = message.from_user.id
        context = await db.get_user_context(user_id)

        if context is None:
            resp = await default_palm(message.text)
            await message.reply(resp)

        else:
            resp = await custom_palm(context, message.text)
            await message.reply(resp)

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'generate' message handler: {e}")


async def custom_palm(context, message):
    defaults = {
        'model': 'models/chat-bison-001',
        'temperature': 0.25,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.95,
        }
    response = palm.chat(
        **defaults,
        context=context,
        messages=message
        )
    return response.last

# default set 
async def default_palm(message):
    defaults = {
        'model': 'models/text-bison-001',
        'temperature': 0.7,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.95,
        'max_output_tokens': 1024,
        'stop_sequences': [],
        'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},{"category":"HARM_CATEGORY_SEXUAL","threshold":2},{"category":"HARM_CATEGORY_MEDICAL","threshold":2},{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
        }
    response = palm.generate_text(
        **defaults,
        prompt=message
        )
    return response.result


@app.on_message(filters.command('model', prefixes='/'))
async def set_model(client, message):
    context = await client.ask(message.chat.id, "Please Enter the Context", filters=filters.text, timeout=60)
    if context.text.startswith('/'):
        return
    await db.set_user_context(message.from_user.id, context.text)
    await message.reply_text(f"Context set to {context.text}") 


@app.on_message(filters.command('reset', prefixes='/'))
async def reset_model(client, message):
    await db.set_user_context(message.from_user.id, None)
    await message.reply_text("Context reset successfully")
