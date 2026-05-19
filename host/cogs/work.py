import discord
from discord import app_commands
from discord.ext import commands

from application import WorkCommand, WorkCommandRequest
from host.cogs.base_cog import BaseCog
from host.embeds.discord_work_embed import DiscordWorkEmbed

class WorkCog(BaseCog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="work", description="Work to earn money.")
    @app_commands.guild_only()
    async def user_work(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await WorkCommand(WorkCommandRequest(guild=guild, user=user, work_type="Work")).execute()
        view = await DiscordWorkEmbed.get_work_view(interaction, response)
        await interaction.response.send_message(view=view)

    @app_commands.command(name="crime", description="Attempt a crime to earn money.")
    @app_commands.guild_only()
    async def user_crime(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await WorkCommand(WorkCommandRequest(guild=guild, user=user, work_type="Crime")).execute()
        view = await DiscordWorkEmbed.get_crime_view(interaction, response)
        await interaction.response.send_message(view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(WorkCog(bot))
