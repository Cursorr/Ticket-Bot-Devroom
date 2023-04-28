import discord



class TicketCreateButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()

        bot = interaction.client
        user = interaction.user
        user_data = await bot.mongo.get_user_ticket(user.id)

        bypass_roles = bot.config["tickets"]["bypass_limit_roles"]
        bypass = any(role.id in bypass_roles for role in user.roles)

        max_tickets = bot.config["tickets"]["max_tickets"]
        if len(user_data["tickets"]) >= max_tickets and not bypass:
            return await interaction.followup.send(embed=discord.Embed(
                description=f"You can't have more than {bot.config['tickets']['max_tickets']} tickets.",
                color=bot.color
            ), ephemeral=True)

        category = bot.get_channel(bot.config["tickets"]["category"])
        channel = await category.create_text_channel(name=f"ticket-{user.name}")
        
        automatic_added_role = discord.utils.get(interaction.guild.roles, id=bot.config["tickets"]["automatic_added_role"])
        await channel.set_permissions(automatic_added_role, read_messages=True)
        
        await bot.mongo.update_user_data(user.id, {"$push": {"tickets": channel.id}})

        await interaction.followup.send(embed=discord.Embed(
            description=f"Your ticket have been created. {channel.mention}",
            color=bot.color
        ), ephemeral=True)

        await channel.send(user.mention, embed=discord.Embed(
            description="Please describe your problem.",
            color=bot.color
        ))
