import re
from pyrogram import Client, filters
import google.generativeai as palm
from better_profanity import profanity
from config import PALM_API, API_ID, API_HASH, BOT_TOKEN
from script import script
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

palm.configure(api_key=PALM_API)

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
        # Get the page number from the command, default to 1
        page = int(message.text.split('/model')[-1].strip()) if len(message.text.split()) > 1 else 1

        # Create an inline keyboard with options from the `script` class for the given page
        options = []
        total_roles = len(script.__dict__.values())
        per_page = 5
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_roles)

        for i, role in enumerate(list(script.__dict__.values())[start_idx:end_idx]):
            if isinstance(role, dict):
                emoji = "✅ " if role["name"] in await db.get_user_context(str(message.from_user.id)) else ""
                options.append([InlineKeyboardButton(f"{emoji}{role['name']}", callback_data=role["name"])])

        # Add the "Next" button if there are more pages
        if end_idx < total_roles:
            next_page = page + 1
            options.append([InlineKeyboardButton("Next", callback_data=f"next_page:{next_page}")])

        # Add the "Previous" button if there are previous pages
        if page > 1:
            prev_page = page - 1
            options.append([InlineKeyboardButton("Previous", callback_data=f"prev_page:{prev_page}")])

        # Add the "Reset" button at the bottom
        options.append([InlineKeyboardButton("Reset", callback_data="reset")])

        reply_markup = InlineKeyboardMarkup(options)
        await message.reply_text("Choose a model", reply_markup=reply_markup)

    except Exception as e:
        # Handle any unexpected errors and log them
        print(f"Error in 'model' command handler: {e}")



@app.on_callback_query()
async def callback_handler(client, callback_query):
    try:
        data = callback_query.data

        if data.startswith("next_page"):
            # If the callback data indicates the "Next" button, go to the next page
            await model(client, callback_query.message)
            return

        if data.startswith("prev_page"):
            # If the callback data indicates the "Previous" button, go to the previous page
            await model(client, callback_query.message)
            return

        if data == "reset":
            # If the callback data indicates the "Reset" button, reset the user's context
            user_id = str(callback_query.from_user.id)
            await db.update_user_context(user_id, [])
            await model(client, callback_query.message)
            return

        # The user has selected a model
        selected_model = next((role for role in script.__dict__.values() if role["name"] == data), None)
        if selected_model:
            # Save the context to the database
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
