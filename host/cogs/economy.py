import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    BuyStockCommand, BuyStockCommandRequest,
    GetStocksQuery, GetStocksQueryRequest,
    PayDividendsCommand, PayDividendsCommandRequest,
    TakeLoanCommand, TakeLoanCommandRequest,
    RepayLoanCommand, RepayLoanCommandRequest,
    ExchangeCommand, ExchangeCommandRequest,
)
from host.embeds.discord_economy_embed import DiscordEconomyEmbed
import typing


class EconomyCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stocks", description="View your stock portfolio.")
    @app_commands.guild_only()
    async def user_stocks(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await GetStocksQuery(GetStocksQueryRequest(guild=guild, user=user)).execute()
            view = await DiscordEconomyEmbed.get_stocks_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="buy-stock", description="Buy shares of a business.")
    @app_commands.guild_only()
    async def user_buy_stock(self, interaction: discord.Interaction, business_id: int, quantity: app_commands.Range[int, 1, 10000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await BuyStockCommand(BuyStockCommandRequest(guild=guild, user=user, business_id=business_id, quantity=quantity)).execute()
            view = await DiscordEconomyEmbed.get_buy_stock_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="pay-dividends", description="Pay dividends to all shareholders of a business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_pay_dividends(self, interaction: discord.Interaction, business_id: int):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await PayDividendsCommand(PayDividendsCommandRequest(guild=guild, business_id=business_id)).execute()
            view = await DiscordEconomyEmbed.get_pay_dividends_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    loan_group = app_commands.Group(name="loan", description="Loan management")

    @loan_group.command(name="take", description="Take out a loan from the bank.")
    @app_commands.guild_only()
    async def user_take_loan(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10000000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await TakeLoanCommand(TakeLoanCommandRequest(guild=guild, user=user, amount=amount)).execute()
            view = await DiscordEconomyEmbed.get_take_loan_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @loan_group.command(name="repay", description="Repay your outstanding loan.")
    @app_commands.guild_only()
    async def user_repay_loan(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10000000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await RepayLoanCommand(RepayLoanCommandRequest(guild=guild, user=user, amount=amount)).execute()
            view = await DiscordEconomyEmbed.get_repay_loan_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="exchange", description="Exchange one currency for another.")
    @app_commands.guild_only()
    async def user_exchange(self, interaction: discord.Interaction, from_currency_id: int, to_currency_id: int, amount: app_commands.Range[int, 1, 10000000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await ExchangeCommand(ExchangeCommandRequest(guild=guild, user=user, from_currency_id=from_currency_id, to_currency_id=to_currency_id, amount=amount)).execute()
            view = await DiscordEconomyEmbed.get_exchange_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
