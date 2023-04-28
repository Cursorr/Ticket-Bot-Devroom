import discord
import json
import os

from discord.ext import commands

from cogs.tickets import TicketCreateButton
from cogs.mongo import Mongo

class DevRoomBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            command_prefix=None,
            intents=discord.Intents.all()
        )

        self.config = json.load(open("config.json", "r"))
        self.color = int(self.config["color"], 16) + 0x200

        self.DEV_GUILD = discord.Object(self.config["guild_id"])

    @property
    def mongo(self) -> Mongo:
        return self.get_cog("Mongo")

    async def setup_hook(self):
        self.add_view(TicketCreateButton())

    async def load_cogs(self):
        try:
            for file in os.listdir("cogs"):
                if file.endswith(".py"):
                    await self.load_extension(f"cogs.{file[:-3]}")
        except commands.ExtensionAlreadyLoaded:
            pass

    async def on_ready(self):
        await self.load_cogs()

        self.tree.copy_global_to(guild=self.DEV_GUILD)
        await self.tree.sync(guild=self.DEV_GUILD)

        print("[DevRoomBot] - Connected")

    def launch(self):
        self.run(self.config["token"])


DevRoomBot().launch()