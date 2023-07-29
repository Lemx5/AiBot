import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id):
        return {
            "user_id": id,
            "context": "chatbot",
        }

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"user_id": id})
        return True if user else False

    async def update_user_context(self, id, context):
        await self.col.update_one({"user_id": id}, {"$set": {"context": context}})

    async def get_user_context(self, id):
        user = await self.col.find_one({"user_id": id})
        return user["context"] if user and "context" in user else None



    
db = Database(DATABASE_URL, DATABASE_NAME)