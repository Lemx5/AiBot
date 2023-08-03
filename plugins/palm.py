import re
import asyncio
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API
from database import db

# configure palm api key
palm.configure(api_key=PALM_API)

# Start the command handler
@Client.on_message(filters.command('start', prefixes='/'))
async def start(client, message):
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id)
        
        # Send a welcome message to the user
        user_name = message.from_user.first_name
        await message.reply_text(f"Hi {user_name},\nI am **Azalea**, I can generate text based on the input you give me")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'start' command handler: {e}")

# help command handler 
@Client.on_message(filters.command('help'))
async def help(client, message):
    await message.reply_text(f"<b>Usage:</b>\nJust send me a message and I will generate a response based on your message\n\n<b>Commands:</b>\n/context - Set your context\n/reset - Reset your context")

@Client.on_message(filters.command('context'))
async def set_context(client, message):
    context = await db.get_user_context(message.from_user.id)
    if len(message.text.split(' ', 1)) == 1:
        await message.reply_text(f"Your current context is :- <b>{context}</b>\n\nTo set new context send <b>/context <your_context></b>\n<b>Example</b> - <code>/context Pretend to be my girlfriend</code>\n\nTo reset context send /reset")
        return
    try:
        # Get the user's context from the database
        user_id = message.from_user.id
        user_context = message.text.split(' ', 1)[1]
        
        await db.update_user_context(user_id, user_context)
        await message.reply_text(f"Context updated successfully to **{user_context}**")
    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'context' command handler: {e}")

# reset command handler
@Client.on_message(filters.command('reset'))
async def reset_model(client, message):
    await db.update_user_context(message.from_user.id, "")
    await message.reply_text("Context reset successfully")

# Generate a response to the user's message
@Client.on_message(filters.text & filters.private & filters.incoming)
async def generate(client, message):

    # Check if the user is already in the database if not add the user
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
                                  
    m = await message.reply_text("Gener.....")
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
        animation_frames = ["Genera....", "Generat...", "Generati..", "Generatin.", "Generating..", "Generating...", "Generating...."]
        for frame in animation_frames:
            await asyncio.sleep(0.9)  # Adjust the delay as desired
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

# Get the response from palm api
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

