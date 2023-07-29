import re
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API
from database import db


palm.configure(api_key=PALM_API)


@Client.on_message(filters.command('start', prefixes='/'))
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


@Client.on_message(filters.text & filters.private)
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
        try:
            resp = await custom_palm(context, message.text)
            await message.reply(resp)
            print(resp)
            print(context)
        except:
            await message.reply_text("Sorry, I am not able to respond to this message.")
            return

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

@Client.on_message(filters.command('model'))
async def set_model(client, message):
    context = await client.ask(message.chat.id, "Please Enter the Context", filters=filters.text, timeout=60)
    if context.text.startswith('/'):
        return
    await db.update_user_context(message.from_user.id, context.text)
    await message.reply_text(f"Context set to {context.text}") 


@Client.on_message(filters.command('reset'))
async def reset_model(client, message):
    await db.update_user_context(message.from_user.id, None)
    await message.reply_text("Context reset successfully")
