import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser


class BaseCog(commands.Cog):

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        original = getattr(error, 'original', error)
        if interaction.response.is_done():
            await interaction.followup.send(f"An error occurred: {str(original)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {str(original)}", ephemeral=True)

    @staticmethod
    def _guild(interaction: discord.Interaction) -> DiscordGuild:
        return DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)

    @staticmethod
    def _user(u: discord.User | discord.Member) -> DiscordUser:
        return DiscordUser(user_id=u.id, name=u.name, display_avatar=str(u.display_avatar))
