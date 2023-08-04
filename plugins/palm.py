import re
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API
from database import db


# configure palm api key
palm.configure(api_key=PALM_API)


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
    await message.reply_text(f"<b>Usage:</b>\nJust send me a message and I will generate a response based on your message\n\n<b>Commands:</b>\n/start - Start the bot\n/model - Get your current model\n/context - Set your context\n/reset - Reset your context")

# model command handler
@Client.on_message(filters.command('model'))
async def set_model(client, message):
    context = db.get_user_context(message.from_user.id)
    await message.reply_text(f"Your current context is <b>{context}</b>\nTo change it, use /context <context>\neg - <code>/context Pretend to be my girfriend</code>\n\nTo reset your context, use /reset")

# context command handler
@Client.on_message(filters.command('context'))
async def set_context(client, message):
    if len(message.text.split(' ', 1)) == 1:
        await message.reply_text(f"Please provide a context\nEg - <code>/context Pretend to be my girfriend</code>")
        return
    try:
        # Get the user's context from the database
        user_id = message.from_user.id
        context = message.text.split(' ', 1)[1]
        await db.update_user_context(user_id, context)
        await message.reply_text(f"Context updated successfully to **{context}**")
    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'context' command handler: {e}")

# reset command handler
@Client.on_message(filters.command('reset'))
async def reset_model(client, message):
    await db.update_user_context(message.from_user.id, None)
    await message.reply_text("Context reset successfully")

"""
# Generate a response to the user's message
@Client.on_message(filters.text & filters.private & filters.incoming)
async def generate(client, message):

    # Check if the user is already in the database if not add the user
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
                                  
    m = await message.reply_text("G.........")
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
        animation_frames = ["Ge........", "Gen.......", "Gene......", "Gener.....", "Genera....", "Generat...", "Generati..", "Generatin.", "Generating"]
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

        """


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Define a dictionary of common greetings and questions along with their responses.
greetings_responses = {
    r"(?i)^hello$": "Hello! How can I assist you today?",
    r"(?i)^hi$": "Hi there! How can I help you?",
    r"(?i)^hey$": "Hey! How can I be of service?",
    r"(?i)^good morning$": "Good morning! How are you doing?",
    r"(?i)^good afternoon$": "Good afternoon! How can I assist you?",
    r"(?i)^good evening$": "Good evening! How may I help you?",
}

questions_responses = {
    r"(?i)^how are you(\s*doing)?$": "I'm just a bot, but thanks for asking!",
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
    # Add more questions and responses as needed.
}

# Create a filter to match any of the greeting or question patterns.
greeting_filter = filters.regex(r"|".join(greetings_responses.keys()) + r"|".join(questions_responses.keys()))

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
    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
