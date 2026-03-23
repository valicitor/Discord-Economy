import discord
from discord import app_commands
from discord.ext import commands
from domain import DiscordHelpEmbed

class HelpCog(commands.Cog):
    HELP_COMMANDS = [
        # app_commands.Choice(name="General Help", value="general_help"),
    ]
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /version ---
    @app_commands.command(name="version", description="Show the bot's current version.")
    async def version(self, interaction: discord.Interaction):
        embed = DiscordHelpEmbed.version_embed()
        await interaction.response.send_message(embed=embed)

    # --- /help ---
    @app_commands.command(name="help", description="Show the help menu or info about a specific command.")
    @app_commands.describe(command_name="Choose one")
    @app_commands.choices(command_name=HELP_COMMANDS)
    async def help(self, interaction: discord.Interaction, command_name: app_commands.Choice[str] | None = None):
        # If no command specified, show the general help embed
        if not command_name:
            embed = DiscordHelpEmbed.help_embed()
            await interaction.response.send_message(embed=embed)
            return
        
        embed = DiscordHelpEmbed.command_help(command_name.value)
        await interaction.response.send_message(embed=embed)

    # --- /faq ---
    @app_commands.command(name="faq", description="Display frequently asked questions about the bot.")
    async def faq(self, interaction: discord.Interaction):
        embed = DiscordHelpEmbed.command_faq()
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
