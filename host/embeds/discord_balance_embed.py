import discord
from discord import Interaction
from application import GetBalanceQueryResponse, PayCommandResponse, GetTopBalancesQueryResponse
from host.helpers.currency import currency_symbol

class DiscordBalanceEmbed:

    @staticmethod
    def get_balance_embed(interaction: Interaction, response: GetBalanceQueryResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )

        embed=discord.Embed(
            description=f"Leaderboard Rank: **#{response.user.rank}**",
            color=discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.user.username}", icon_url=f"{response.user.avatar}")
        embed.add_field(name="Cash", value=f"{currency}{response.user.cash_balance}", inline=True)
        embed.add_field(name="Bank", value=f"{currency}{response.user.bank_balance}", inline=True)
        embed.add_field(name="Total", value=f"{currency}{response.user.cash_balance + response.user.bank_balance}", inline=True)
        return embed

    @staticmethod
    def pay_balance_embed(interaction: discord.Interaction, target: discord.User, response: PayCommandResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )
                
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{interaction.user.mention}, you have paid {target.mention} **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed
    
    @staticmethod
    def get_leaderboard_embed(interaction: discord.Interaction, response: GetTopBalancesQueryResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )

        description=f"View the leaderboard here:\n"
        for idx, record in enumerate(response.users, start=1):
            description+=f"\n**{idx}.** `{record.username}` • {currency}{record.cash_balance}"
                
        embed=discord.Embed(
            title="🏆 Leaderboard", 
            description=description, 
            color=discord.Color.gold()
        )

        embed.set_footer(text=f"Page {response.page}/{response.max_pages}")

        return embed