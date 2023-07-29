import re
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API, API_ID, API_HASH, BOT_TOKEN
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import yaml

palm.configure(api_key=PALM_API)

# Read the model information from script.yaml
with open("script.yaml", "r") as file:
    models = yaml.safe_load(file)

# Initialize the Pyrogram Client and Database
app = Client(
    "palmbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


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

        # Generate text based on the user's input
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
            messages=message.text
        )

        await message.reply_text(response.last)

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'generate' message handler: {e}")


@app.on_message(filters.command('model', prefixes='/'))
async def model(client, message):
    try:
        # Use the models read from script.yaml
        options = []
        for role in models:
            options.append([InlineKeyboardButton(role['name'], callback_data=str(role))])

        # ... (existing code to paginate the options if needed)

        reply_markup = InlineKeyboardMarkup(options)
        await message.reply_text("Choose a model", reply_markup=reply_markup)

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'model' command handler: {e}")


@app.on_callback_query()
async def callback_handler(client, callback_query):
    try:
        data = callback_query.data

        # The user has selected a model
        selected_model = next((role for role in models if str(role) == data), None)
        if selected_model:
            # Save the context to the database (you need to implement this)
            user_id = str(callback_query.from_user.id)
            await db.update_user_context(user_id, [selected_model["name"]])

            # Send the selected model's welcome text and context to the user
            await callback_query.message.edit_text(selected_model["welcome_text"])
            await callback_query.message.reply_text(f"Your context: {selected_model['context']}")

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'callback_handler': {e}")


if __name__ == "__main__":
    app.run()
