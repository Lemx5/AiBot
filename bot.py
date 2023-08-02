from pyrogram import Client, __version__
from config import API_ID, API_HASH, BOT_TOKEN
from aiohttp import web
from route import web_server

class Bot(Client):

    def __init__(self):
        super().__init__(
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
        )

    async def start(self):
        await super().start()
        print(f"Bot started.")
        webapp = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(webapp, bind_address, 5050).start()

    async def stop(self, *args):
        await super().stop()
        print(f"Bot stopped.")

app = Bot()
app.run()