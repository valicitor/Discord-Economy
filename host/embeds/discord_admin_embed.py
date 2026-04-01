import discord
from discord import Interaction

from application import get_default_currenncy
from application import (
    AddBalanceCommandResponse, 
    SetBalanceCommandResponse, 
    SetCurrencySymbolCommandResponse
)

class DiscordAdminEmbed:

    @staticmethod
    def set_currency_symbol_embed(interaction: Interaction, response: SetCurrencySymbolCommandResponse):
        currency = get_default_currenncy(response.server_config)
                
        embed = discord.Embed(
            title=f"💱 Currency Symbol Updated",
            description=f"{interaction.user.mention}, set the currency symbol to **{currency}**.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def add_balance_embed(interaction: Interaction, target: discord.User, response: AddBalanceCommandResponse):
        currency = get_default_currenncy(response.server_config)

        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{currency}{response.amount}** to {target.mention}'s {response.account_type} balance.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def set_balance_embed(interaction: Interaction, target: discord.User, response: SetBalanceCommandResponse):
        currency = get_default_currenncy(response.server_config)
        
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, set {target.mention}'s {response.account_type} balance to **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed
    
    # @staticmethod
    # def create_item_embed(interaction: Interaction, response: CreateItemCommandResponse):
    #     currency = get_default_currenncy(response.server_config)
                
    #     embed = discord.Embed(
    #         color=discord.Color.green()
    #     )
    #     embed.set_author(name=f"{interaction.user.name}", icon_url=f"{interaction.user.display_avatar}")

    #     if response.item.icon != '':
    #         embed.set_thumbnail(url=response.item.icon)
    #     embed.add_field(name="Name", value=f"{response.item.name}", inline=True)
    #     embed.add_field(name="Price", value=f"{currency}{response.item.price}", inline=True)
    #     embed.add_field(name="Description", value=response.item.description if response.item.description else "None provided", inline=False)
    #     embed.add_field(name="Inventory", value="Yes" if response.item.inventory else "No", inline=True)
    #     embed.add_field(name="Usable", value="Yes" if response.item.usable else "No", inline=True)
    #     embed.add_field(name="Sellable", value="Yes" if response.item.sellable else "No", inline=True)
    #     if response.item.category != 'default':
    #         embed.add_field(name="Category", value=response.item.category, inline=False)

    #     embed.add_field(name="Stock", value=f"{'Unlimited' if response.item.stock == -1 else response.item.stock}", inline=False)
    #     return embed