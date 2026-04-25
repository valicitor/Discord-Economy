import discord
from discord import Interaction

from application import (
    SetupServerCommandResponse,
    GetServerQueryResponse,
    AddBalanceCommandResponse, 
    SetBalanceCommandResponse, 
    SetCurrencySymbolCommandResponse
)

class DiscordAdminEmbed:

    @staticmethod
    async def setup_server_embed(interaction: Interaction, response: SetupServerCommandResponse):
        message = f"{interaction.user.mention}, setup the server successfully." if response.success else f"Server has already been setup."
        embed = discord.Embed(
            title=f"💿 Server Setup",
            description=message,
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    async def get_server_embed(interaction: Interaction, response: GetServerQueryResponse):
        description=f"### Server:\n"

        server = response.server_config.server
        description+=f"**Server Id:** " + str(server.server_id) + f"\n"
        description+=f"**Server Name:** " + server.name + f"\n"

        description+=f"### Server Settings:\n"
        currency = await response.server_config.get_default_currency()
        if currency:
            currency_symbol = await response.server_config.get_default_currency_symbol()
            description+=f"**Default Currency:** " + currency.name + f"\n"
            description+=f"-# **Symbol:** " + currency_symbol + f"\n\n"
        
        bank = await response.server_config.get_default_bank()
        if bank:
            description+=f"**Default Bank:** " + bank.name + f"\n"
        
        faction = await response.server_config.get_default_faction()
        if faction:
            description+=f"**Default Faction:** " + faction.name + f"\n"

        embed=discord.Embed(
            title=f"Server Configuration", 
            description=description, 
            color=discord.Color.blue()
        )

        return embed

    @staticmethod
    async def set_currency_symbol_embed(interaction: Interaction, response: SetCurrencySymbolCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
                
        embed = discord.Embed(
            title=f"💱 Currency Symbol Updated",
            description=f"{interaction.user.mention}, set the currency symbol to **{currency}**.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    async def add_balance_embed(interaction: Interaction, target: discord.User, response: AddBalanceCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()

        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{currency}{response.amount}** to {target.mention}'s {response.account_type} balance.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    async def set_balance_embed(interaction: Interaction, target: discord.User, response: SetBalanceCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, set {target.mention}'s {response.account_type} balance to **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed