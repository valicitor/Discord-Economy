import discord
from discord import Interaction

class DiscordAdminEmbed:

    @staticmethod
    def add_balance_embed(interaction: Interaction, member: discord.User, amount: int):
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, added **{amount} credits** to {member.mention} account.",
            color=discord.Color.blue()
        )
        return embed

    @staticmethod
    def set_balance_embed(interaction: Interaction, member: discord.User, amount: int):
        embed = discord.Embed(
            title=f"💳 Bank Account Summary",
            description=f"{interaction.user.mention}, set {member.mention}'s balance to **{amount} credits**.",
            color=discord.Color.blue()
        )
        return embed