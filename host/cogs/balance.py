import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    GetBalanceQuery, GetBalanceQueryRequest,
    PayCommand, PayCommandRequest,
    WithdrawCommand, WithdrawCommandRequest,
    DepositCommand, DepositCommandRequest,
    GetLeaderboardQuery, GetLeaderboardQueryRequest
)
from host.embeds.discord_balance_embed import DiscordBalanceEmbed
import typing

class BalanceCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Show your current balance.")
    @app_commands.guild_only()
    async def user_balance(self, interaction: discord.Interaction, target: typing.Optional[discord.User] = None):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(
                user_id=target.id if target else interaction.user.id,
                name=target.name if target else interaction.user.name,
                display_avatar=str(target.display_avatar) if target else str(interaction.user.display_avatar)
            )
            response = await GetBalanceQuery(GetBalanceQueryRequest(guild=guild, user=user)).execute()
            view = await DiscordBalanceEmbed.get_balance_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    balance_group = app_commands.Group(name="bal", description="Balance management commands")

    @balance_group.command(name="pay", description="Pay another user.")
    @app_commands.guild_only()
    async def user_pay(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            target_user = DiscordUser(user_id=target.id, name=target.name, display_avatar=str(target.display_avatar))
            response = await PayCommand(PayCommandRequest(guild=guild, user=user, target=target_user, amount=amount)).execute()
            view = await DiscordBalanceEmbed.get_pay_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    bank_group = app_commands.Group(name="bank", description="Bank management commands")

    @bank_group.command(name="withdraw", description="Withdraw money from your bank.")
    @app_commands.guild_only()
    async def user_withdraw(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await WithdrawCommand(WithdrawCommandRequest(guild=guild, user=user, amount=amount)).execute()
            view = await DiscordBalanceEmbed.get_withdraw_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @bank_group.command(name="deposit", description="Deposit money into your bank.")
    @app_commands.guild_only()
    async def user_deposit(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await DepositCommand(DepositCommandRequest(guild=guild, user=user, amount=amount)).execute()
            view = await DiscordBalanceEmbed.get_deposit_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="leaderboard", description="Show the top users by balance.")
    @app_commands.guild_only()
    async def user_leaderboard(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cash', 'Bank', 'Total']] = "Cash"):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await GetLeaderboardQuery(GetLeaderboardQueryRequest(guild=guild, page=page, sort_by=sort, limit=10)).execute()
            if not response.players:
                await interaction.response.send_message("No players found.", ephemeral=True)
                return
            view = await DiscordBalanceEmbed.get_leaderboard_view(interaction, response, guild)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(BalanceCog(bot))
