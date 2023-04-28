from motor import motor_asyncio as motor
from discord.ext import commands


class Mongo(commands.Cog):

    USER_DATA = {
        "user_id": None,
        "tickets": []
    }

    def __init__(self, bot):
        self.bot = bot
        self.db = motor.AsyncIOMotorClient()["devrooms"]

    async def get_all_users(self):
        data = self.db["tickets"].find({})
        return data

    async def get_user_ticket(self, user_id):
        data = await self.db["tickets"].find_one({"user_id": user_id})

        if not data:
            data = self.USER_DATA.copy()
            data["user_id"] = user_id

        return data

    async def update_user_data(self, user_id, query):
        await self.db["tickets"].update_one({"user_id": user_id}, query, upsert=True)
        

async def setup(bot):
    await bot.add_cog(Mongo(bot))