import discord
from discord import Interaction

from application.helpers.helpers import Helpers
from application import (
    GetBalanceQueryResponse, 
    PayCommandResponse,
    WithdrawCommandResponse, 
    DepositCommandResponse,
    GetLeaderboardQueryResponse
)

class DiscordBalanceEmbed:

    @staticmethod
    async def get_balance_embed(interaction: Interaction, response: GetBalanceQueryResponse):
        currency = await response.server_config.get_default_currency_symbol()
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"### {response.player.player.name}",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )

        for balance in response.player.balances:
            embed.add_field(name=f"Balance", value=f"{currency}{Helpers.format_cash_amount(balance.balance)}", inline=True)
        for bank_account in response.player.bank_accounts:  
            embed.add_field(name="Bank", value=f"{currency}{Helpers.format_cash_amount(bank_account.balance)}", inline=True)
        return embed
    
    @staticmethod
    async def withdraw_embed(interaction: Interaction, response: WithdrawCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Withdrew {currency}{Helpers.format_cash_amount(response.amount)} from your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        return embed

    @staticmethod
    async def deposit_embed(interaction: Interaction, response: DepositCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Deposited {currency}{Helpers.format_cash_amount(response.amount)} into your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        return embed

    @staticmethod
    async def pay_balance_embed(interaction: discord.Interaction, target: discord.User, response: PayCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None
      
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{response.player.player.name}, you have paid {response.target_player.player.name} **{currency}{Helpers.format_cash_amount(response.amount)}**.",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        return embed
    
    @staticmethod
    async def get_leaderboard_embed(interaction: discord.Interaction, response: GetLeaderboardQueryResponse):
        currency = await response.server_config.get_default_currency_symbol()

        description=f"View the leaderboard here:\n"
        for player_profile in response.players:
            money = player_profile.balances.total_balance() if response.sort_by == "Cash" else player_profile.bank_accounts.total_bank_balance() if response.sort_by == "Bank" else player_profile.balances.total_balance() + player_profile.bank_accounts.total_bank_balance()
            description+=f"\n**{player_profile.player.rank}.** `{player_profile.player.name}` • {currency}{Helpers.format_cash_amount(money)}"
                
        embed=discord.Embed(
            title=f"Leaderboard [{response.sort_by}]", 
            description=description, 
            color=discord.Color.gold()
        )

        embed.set_footer(text=f"Page {response.page}/{response.max_pages}")

        return embed