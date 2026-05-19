import discord
from discord import app_commands
from discord.ext import commands

from application import (
    BuyStockCommand, BuyStockCommandRequest,
    GetStocksQuery, GetStocksQueryRequest,
    TakeLoanCommand, TakeLoanCommandRequest,
    RepayLoanCommand, RepayLoanCommandRequest,
    ExchangeCommand, ExchangeCommandRequest,
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_economy_embed import DiscordEconomyEmbed
import typing


class EconomyCog(BaseCog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    market_group = app_commands.Group(name="market", description="Market and trading")

    # -------------------------------------------------------------------------
    # /market stocks  /market buy  /market exchange
    # -------------------------------------------------------------------------
    @market_group.command(name="stocks", description="View your stock portfolio.")
    @app_commands.guild_only()
    async def user_market_stocks(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await GetStocksQuery(GetStocksQueryRequest(guild=guild, user=user)).execute()
        view = await DiscordEconomyEmbed.get_stocks_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    @market_group.command(name="buy", description="Buy shares of a business.")
    @app_commands.guild_only()
    async def user_market_buy(self, interaction: discord.Interaction, business_id: int, quantity: app_commands.Range[int, 1, 10000]):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await BuyStockCommand(BuyStockCommandRequest(guild=guild, user=user, business_id=business_id, quantity=quantity)).execute()
        view = await DiscordEconomyEmbed.get_buy_stock_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    @market_group.command(name="exchange", description="Exchange one currency for another.")
    @app_commands.guild_only()
    async def user_market_exchange(self, interaction: discord.Interaction, from_currency_id: int, to_currency_id: int, amount: app_commands.Range[int, 1, 10000000]):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await ExchangeCommand(ExchangeCommandRequest(guild=guild, user=user, from_currency_id=from_currency_id, to_currency_id=to_currency_id, amount=amount)).execute()
        view = await DiscordEconomyEmbed.get_exchange_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    # -------------------------------------------------------------------------
    # /loan take  /loan repay
    # -------------------------------------------------------------------------
    loan_group = app_commands.Group(name="loan", description="Loan management")

    @loan_group.command(name="take", description="Take out a loan from the bank.")
    @app_commands.guild_only()
    async def user_take_loan(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10000000]):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await TakeLoanCommand(TakeLoanCommandRequest(guild=guild, user=user, amount=amount)).execute()
        view = await DiscordEconomyEmbed.get_take_loan_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    @loan_group.command(name="repay", description="Repay your outstanding loan.")
    @app_commands.guild_only()
    async def user_repay_loan(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10000000]):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await RepayLoanCommand(RepayLoanCommandRequest(guild=guild, user=user, amount=amount)).execute()
        view = await DiscordEconomyEmbed.get_repay_loan_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
