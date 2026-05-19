import discord
from discord import app_commands
from discord.ext import commands

from application import (
    GetBalanceQuery, GetBalanceQueryRequest,
    PayCommand, PayCommandRequest,
    WithdrawCommand, WithdrawCommandRequest,
    DepositCommand, DepositCommandRequest,
    GetLeaderboardQuery, GetLeaderboardQueryRequest
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_balance_embed import DiscordBalanceEmbed
import typing

class BalanceCog(BaseCog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------------------------------------------------
    # /balance  /leaderboard
    # -------------------------------------------------------------------------
    @app_commands.command(name="balance", description="Show your current balance.")
    @app_commands.guild_only()
    async def user_balance(self, interaction: discord.Interaction, target: typing.Optional[discord.User] = None):
        guild = self._guild(interaction)
        user = self._user(target if target else interaction.user)
        response = await GetBalanceQuery(GetBalanceQueryRequest(guild=guild, user=user)).execute()
        view = await DiscordBalanceEmbed.get_balance_view(interaction, response)
        await interaction.response.send_message(view=view)

    @app_commands.command(name="leaderboard", description="Show the top users by balance.")
    @app_commands.guild_only()
    async def user_leaderboard(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cash', 'Bank', 'Total']] = "Cash"):
        guild = self._guild(interaction)
        response = await GetLeaderboardQuery(GetLeaderboardQueryRequest(guild=guild, page=page, sort_by=sort, limit=10)).execute()
        view = await DiscordBalanceEmbed.get_leaderboard_view(interaction, response, guild)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /pay
    # -------------------------------------------------------------------------
    @app_commands.command(name="pay", description="Pay another user.")
    @app_commands.guild_only()
    async def user_pay(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        target_user = self._user(target)
        response = await PayCommand(PayCommandRequest(guild=guild, user=user, target=target_user, amount=amount)).execute()
        view = await DiscordBalanceEmbed.get_pay_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /bank deposit  /bank withdraw
    # -------------------------------------------------------------------------
    bank_group = app_commands.Group(name="bank", description="Bank management commands")

    @bank_group.command(name="withdraw", description="Withdraw money from your bank.")
    @app_commands.guild_only()
    async def user_withdraw(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await WithdrawCommand(WithdrawCommandRequest(guild=guild, user=user, amount=amount)).execute()
        view = await DiscordBalanceEmbed.get_withdraw_view(interaction, response)
        await interaction.response.send_message(view=view)

    @bank_group.command(name="deposit", description="Deposit money into your bank.")
    @app_commands.guild_only()
    async def user_deposit(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await DepositCommand(DepositCommandRequest(guild=guild, user=user, amount=amount)).execute()
        view = await DiscordBalanceEmbed.get_deposit_view(interaction, response)
        await interaction.response.send_message(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(BalanceCog(bot))
