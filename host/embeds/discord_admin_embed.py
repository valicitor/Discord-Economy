import discord
from discord import Interaction
from application import (
    AddBalanceCommandResponse, 
    SetBalanceCommandResponse, 
    SetCurrencySymbolCommandResponse
)
from host.helpers.currency import currency_symbol

class DiscordAdminEmbed:

    @staticmethod
    def set_currency_symbol_embed(interaction: Interaction, response: SetCurrencySymbolCommandResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )
                
        embed = discord.Embed(
            title=f"💱 Currency Symbol Updated",
            description=f"{interaction.user.mention}, set the currency symbol to **{currency}**.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def add_balance_embed(interaction: Interaction, target: discord.User, response: AddBalanceCommandResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )

        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{currency}{response.amount}** to {target.mention}'s {response.account_type} balance.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def set_balance_embed(interaction: Interaction, target: discord.User, response: SetBalanceCommandResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )
        
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, set {target.mention}'s {response.account_type} balance to **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed