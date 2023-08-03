import re
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API
from database import db
import asyncio


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

@Client.on_message(filters.command('model'))
async def set_model(client, message):
    context = db.get_user_context(message.from_user.id)
    await message.reply_text(f"Your current context is {context}\nTo change it, use /context <context>\nEg - ```/context Pretend to be my girfriend```\n\nTo reset your context, use /reset")


@Client.on_message(filters.command('context'))
async def set_context(client, message):
    try:
        # Get the user's context from the database
        user_id = message.from_user.id
        context = message.text.split(' ', 1)[1]
        await db.update_user_context(user_id, context)
        await message.reply_text(f"Context updated successfully to {context}")
    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'context' command handler: {e}")

@Client.on_message(filters.command('reset'))
async def reset_model(client, message):
    await db.update_user_context(message.from_user.id, None)
    await message.reply_text("Context reset successfully")


@Client.on_message(filters.text & filters.private & filters.incoming) 
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

        # Get the user's context from the database
        user_id = message.from_user.id
        context = await db.get_user_context(user_id)

        # Start the text animation
        animation_frames = ["Generating", "Generating.", "Generating..", "Generating..."]
        for frame in animation_frames:
            await asyncio.sleep(0.5)  # Adjust the delay as desired
            await m.edit(frame)

        try:
            resp = await get_palm(context, message.text)
            await m.edit(resp)
            print(resp)
            print(context)
        except Exception as e:
            print(e)
            
    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'generate' message handler: {e}")



async def get_palm(context, message):
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

