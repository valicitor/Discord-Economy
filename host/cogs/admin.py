import discord
from discord import app_commands
from discord.ext import commands
from domain import DiscordAdminEmbed
from application import (
    SetBalanceCommand,
    AddBalanceCommand
)

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --- /add-balance ---
    @app_commands.command(name="add-balance", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_balance(self, interaction: discord.Interaction, user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        query = AddBalanceCommand(interaction=interaction)
        success = await query.execute(guild_id=str(interaction.guild_id), member_id=str(user.id), amount=amount)

        if success is None:
            # Error messages are handled within the command, so we just return here to avoid sending a duplicate message.
            return

        embed = DiscordAdminEmbed.add_balance_embed(interaction, amount)
        await interaction.response.send_message(embed=embed)

    # --- /set-balance ---
    @app_commands.command(name="set-balance", description="Set a members current balance.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_balance(self, interaction: discord.Interaction, user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        query = SetBalanceCommand(interaction=interaction)
        success = await query.execute(guild_id=str(interaction.guild_id), member_id=str(user.id), amount=amount)

        if success is None:
            # Error messages are handled within the command, so we just return here to avoid sending a duplicate message.
            return

        embed = DiscordAdminEmbed.set_balance_embed(interaction, amount)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
