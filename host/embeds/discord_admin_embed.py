import discord
from discord import Interaction
from application import AddBalanceCommandResponse, SetBalanceCommandResponse
from host.helpers.currency import currency_symbol

class DiscordAdminEmbed:

    @staticmethod
    def add_balance_embed(interaction: Interaction, target: discord.User, response: AddBalanceCommandResponse):
        currency = currency_symbol(
            response.guild_config.currency_emoji, 
            response.guild_config.currency_symbol
        )

        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{currency}{response.amount}** to {target.mention} account.",
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
            description=f"{interaction.user.mention}, set {target.mention}'s balance to **{currency}{response.amount}**.",
            color=discord.Color.blue()
        )
        return embed