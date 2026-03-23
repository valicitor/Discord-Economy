import discord
from discord import app_commands
from discord.ext import commands
from domain import DiscordBalanceEmbed
from application import (
    PayCommand,
    GetBalanceQuery
)

class BalanceCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /balance ---
    @app_commands.command(name="balance", description="Show your current balance.")
    async def get_balance(self, interaction: discord.Interaction):
        query = GetBalanceQuery(interaction=interaction)
        balance = await query.execute(guild_id=str(interaction.guild_id), user_id=str(interaction.user.id))

        if balance is None:
            # Error messages are handled within the command, so we just return here to avoid sending a duplicate message.
            return

        embed = DiscordBalanceEmbed.get_balance_embed(interaction, bal=balance)
        await interaction.response.send_message(embed=embed)

    # --- /pay ---
    @app_commands.command(name="pay", description="Pay another user.")
    async def pay_user(self, interaction: discord.Interaction, user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        command = PayCommand(interaction=interaction)
        success = await command.execute(guild_id=str(interaction.guild_id), user_id=str(interaction.user.id), member_id=str(user.id), amount=amount)

        if success is None:
            # Error messages are handled within the command, so we just return here to avoid sending a duplicate message.
            return
        if not success:
            await interaction.response.send_message(f"Payment failed. Please ensure you have sufficient funds and try again.", ephemeral=True)
            return
        
        embed = DiscordBalanceEmbed.pay_balance_embed(interaction, user=interaction.user, member=user, amount=amount)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BalanceCog(bot))
