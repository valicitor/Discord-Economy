import discord
from discord import app_commands
from discord.ext import commands

from host.embeds.discord_help_embed import DiscordHelpEmbed
import typing


class HelpCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all commands or get details on a specific command.")
    @app_commands.guild_only()
    async def user_help(self, interaction: discord.Interaction, command: typing.Optional[str] = None):
        if command:
            embed = DiscordHelpEmbed.command_help(command)
        else:
            embed = DiscordHelpEmbed.help_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="version", description="Show the bot version.")
    @app_commands.guild_only()
    async def user_version(self, interaction: discord.Interaction):
        embed = DiscordHelpEmbed.version_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
