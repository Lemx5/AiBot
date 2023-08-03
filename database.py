import motor.motor_asyncio
from config import DATABASE_URL

DATABASE_NAME = "palmbot"
COLLECTION_NAME = "users"

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db[COLLECTION_NAME]

    def new_user(self, user_id):
        return {
            "user_id": user_id,
            "context": "",
        }

    async def add_user(self, user_id):
        user = self.new_user(user_id)
        await self.col.insert_one(user)

    async def is_user_exist(self, user_id):
        user = await self.col.find_one({"user_id": user_id})
        return True if user else False

    async def update_user_context(self, user_id, context):
        if not await self.is_user_exist(user_id):
            await self.add_user(user_id)

        if not isinstance(context, str):
            print("Error: context should be a string")
            return

        await self.col.update_one({"user_id": user_id}, {"$set": {"context": context}})

    async def get_user_context(self, user_id):
        user = await self.col.find_one({"user_id": user_id})
        if user is None or not user["context"]:
            return ""
        return user["context"]

db = Database(DATABASE_URL, DATABASE_NAME)
