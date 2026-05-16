import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import WorkCommand, WorkCommandRequest
from host.embeds.discord_work_embed import DiscordWorkEmbed

class WorkCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="work", description="Work to earn money.")
    @app_commands.guild_only()
    async def user_work(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await WorkCommand(WorkCommandRequest(guild=guild, user=user, work_type="Work")).execute()
            view = await DiscordWorkEmbed.get_work_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="crime", description="Attempt a crime to earn money.")
    @app_commands.guild_only()
    async def user_crime(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await WorkCommand(WorkCommandRequest(guild=guild, user=user, work_type="Crime")).execute()
            view = await DiscordWorkEmbed.get_crime_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WorkCog(bot))
