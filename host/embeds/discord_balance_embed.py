import discord
from discord import Interaction
from domain import User

class DiscordBalanceEmbed:

    @staticmethod
    def get_balance_embed(interaction: Interaction, user: User):
        embed=discord.Embed(
            description=f"Leaderboard Rank: **#{user.rank}**",
            color=discord.Color.blue()
        )
        embed.set_author(name=f"{user.username}")
        embed.add_field(name="Cash", value=f"{user.cash_balance}", inline=True)
        embed.add_field(name="Bank", value=f"{user.bank_balance}", inline=True)
        embed.add_field(name="Total", value=f"{user.cash_balance + user.bank_balance}", inline=True)
        return embed

    @staticmethod
    def pay_balance_embed(interaction: discord.Interaction, user: discord.User, target: discord.User, amount: int):
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{interaction.user.mention}, you have paid {target.mention} **{amount} credits**.",
            color=discord.Color.blue()
        )
        return embed
    
    @staticmethod
    def get_leaderboard_embed(interaction: discord.Interaction, top_balances: list[User]):
        embed=discord.Embed(
            title="🏆 Leaderboard", 
            description="View the leaderboard here:", 
            color=discord.Color.gold()
        )
        for idx, record in enumerate(top_balances, start=1):
            embed.add_field(name=f"{idx}. `{record.username}` • {record.cash_balance}", value=f"", inline=False)
        
        embed.add_field(name="1. Someone . sdgsg", value="", inline=True)
        embed.set_footer(text="Page 1/1")

        return embed