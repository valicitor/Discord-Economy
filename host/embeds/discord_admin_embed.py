import discord
from discord import Interaction

from application import get_default_currency
from application import (
    AddBalanceCommandResponse, 
    SetBalanceCommandResponse, 
    SetCurrencySymbolCommandResponse
)

class DiscordAdminEmbed:

    @staticmethod
    async def set_currency_symbol_embed(interaction: Interaction, response: SetCurrencySymbolCommandResponse):
        currency = await get_default_currency(response.server_config)
                
        embed = discord.Embed(
            title=f"💱 Currency Symbol Updated",
            description=f"{interaction.user.mention}, set the currency symbol to **{currency}**.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    async def add_balance_embed(interaction: Interaction, target: discord.User, response: AddBalanceCommandResponse):
        currency = await get_default_currency(response.server_config)

        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{currency}{response.amount}** to {target.mention}'s {response.account_type} balance.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    async def set_balance_embed(interaction: Interaction, target: discord.User, response: SetBalanceCommandResponse):
        currency = await get_default_currency(response.server_config)
        
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, set {target.mention}'s {response.account_type} balance to **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed