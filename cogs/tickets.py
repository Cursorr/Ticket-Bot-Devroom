import discord
import io

from discord.ext import commands
from discord import app_commands

from views.open_button import TicketCreateButton

from chat_exporter.construct.transcript import Transcript


class Ticket(commands.GroupCog):

    async def ticket_add_remove(self, interaction, user, parameter):
        await interaction.response.defer()

        author = interaction.user
        bot = interaction.client
        channel = interaction.channel

        command_access_roles = bot.config["tickets"]["add_remove_roles"]
        access = any(role.id in command_access_roles for role in author.roles)

        # Check if user has role
        if not access:
            return await interaction.followup.send(
                "You can't execute this command.",
                ephemeral=True
            )

        # Check if the channel is a ticket
        documents = await bot.mongo.get_all_users()
        async for doc in documents:
            if channel.id in doc["tickets"]:
                add = True if parameter == "add" else False # add = True, remove = False
                await channel.set_permissions(user, read_messages=add)
                return await interaction.followup.send(f"You sucessfully {f'added {user} to' if add else f'removed {user} from'} this ticket.")

        return await interaction.followup.send("This channel is not a ticket.", ephemeral=True)

    @app_commands.command(description="To setup the ticket message")
    @app_commands.default_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed = discord.Embed(
            title="Tickets",
            description="To create a ticket, react with 📩",
            color=interaction.client.color
        ), view=TicketCreateButton())

    @app_commands.command(description="To add a user to a ticket")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        await self.ticket_add_remove(interaction, user, 'add')

    @app_commands.command(description="To remove a user from a ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        await self.ticket_add_remove(interaction, user, 'remove')

    @app_commands.command(description="To close a ticket")
    async def close(self, interaction: discord.Interaction):
        await interaction.response.defer()

        bot = interaction.client
        channel: discord.TextChannel = interaction.channel
        user = interaction.user

        command_access_roles = bot.config["tickets"]["close_roles"]
        command_access = any(role.id in command_access_roles for role in user.roles)

        if not command_access:
            return await interaction.followup.send(
                "You can't execute this command.",
                ephemeral=True
            )

        # Check if the channel is a ticket
        documents = await bot.mongo.get_all_users()
        async for doc in documents:
            if channel.id in doc["tickets"]:
                await interaction.followup.send("A transcript is being created, this ticket will be closed in few seconds...")

                transcript_channel = bot.get_channel(bot.config["tickets"]["transcript_channel"])

                transcript = (
                    await Transcript(
                        channel=channel,
                        limit=None,
                        messages=None,
                        pytz_timezone="UTC",
                        military_time=True,
                        fancy_times=True,
                        before=None,
                        after=None,
                        support_dev=True,
                        bot=bot,
                        ).export()
                    ).html

                transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html")

                embed = discord.Embed(color=bot.color, title="Transcript")
                embed.add_field(name="Ticket name", value=channel.name)
                embed.add_field(name="Closed by", value=user.mention)

                await transcript_channel.send(embed=embed, file=transcript_file)
                await channel.delete()

                await bot.mongo.update_user_data(user.id, {"$pull": {"tickets": channel.id}})


async def setup(bot):
    await bot.add_cog(Ticket())