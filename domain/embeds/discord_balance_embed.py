import discord
from discord import Interaction

class DiscordBalanceEmbed:

    @staticmethod
    def get_balance_embed(interaction: Interaction, bal: int):
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, you have **{bal} credits**.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def pay_balance_embed(interaction: discord.Interaction, user: discord.User, member: discord.User, amount: int):
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{interaction.user.mention}, you have paid {member.mention} **{amount} credits**.",
            color=discord.Color.blue()
        )
        return embed