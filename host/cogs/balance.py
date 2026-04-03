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

    # --- /balance ---
    @app_commands.command(name="balance", description="Show your current balance.")
    @app_commands.guild_only()
    async def user_balance(self, interaction: discord.Interaction, target: typing.Optional[discord.User] = None):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=target.id if target else interaction.user.id,
                name=target.name if target else interaction.user.name,
                display_avatar=str(target.display_avatar) if target else str(interaction.user.display_avatar)
            )
        
            request=GetBalanceQueryRequest(
                guild=guild, 
                user=user, 
            )

            response = GetBalanceQuery(request).execute()

            embed = DiscordBalanceEmbed.get_balance_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    balance_group = app_commands.Group(
        name="bal",
        description="Balance management commands"
    )

    # --- /pay ---
    @balance_group.command(name="pay", description="Pay another user.")
    @app_commands.guild_only()
    async def user_pay(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=interaction.user.id,
                name=interaction.user.name,
                display_avatar=str(interaction.user.display_avatar)
            )
            target = DiscordUser(
                user_id=target.id,
                name=target.name,
                display_avatar=str(target.display_avatar)
            )
        
            request=PayCommandRequest(
                guild=guild, 
                user=user, 
                target=target, 
                amount=amount
            )

            response = PayCommand(request).execute()
            
            embed = DiscordBalanceEmbed.pay_balance_embed(interaction, target, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    bank_group = app_commands.Group(
        name="bank",
        description="Bank management commands"
    )


    # --- /withdraw ---
    @bank_group.command(name="withdraw", description="Withdraw money from your bank.")
    @app_commands.guild_only()
    async def user_withdraw(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=interaction.user.id,
                name=interaction.user.name,
                display_avatar=str(interaction.user.display_avatar)
            )
        
            request=WithdrawCommandRequest(
                guild=guild, 
                user=user, 
                amount=amount
            )

            response = WithdrawCommand(request).execute()

            embed = DiscordBalanceEmbed.withdraw_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /deposit ---
    @bank_group.command(name="deposit", description="Deposit money into your bank.")
    @app_commands.guild_only()
    async def user_deposit(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=interaction.user.id,
                name=interaction.user.name,
                display_avatar=str(interaction.user.display_avatar)
            )
        
            request=DepositCommandRequest(
                guild=guild, 
                user=user, 
                amount=amount
            )

            response = DepositCommand(request).execute()

            embed = DiscordBalanceEmbed.deposit_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /leaderboard ---
    @app_commands.command(name="leaderboard", description="Show the top users by balance.")
    @app_commands.guild_only()
    async def user_leaderboard(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cash', 'Bank', 'Total']] = "Cash"):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )

            request=GetLeaderboardQueryRequest(
                guild=guild, 
                page=page, 
                sort_by=sort
            )

            response = GetLeaderboardQuery(request).execute()

            if not response.players:
                await interaction.response.send_message("No players found.", ephemeral=True)
                return

            embed = DiscordBalanceEmbed.get_leaderboard_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /work ---
    # @app_commands.command(name="work", description="Work to earn money.")
    # @app_commands.guild_only()
    # async def user_work(self, interaction: discord.Interaction):
    #     try:
    #         request=WorkCommandRequest(
    #             guild_id=interaction.guild_id, 
    #             user=User(
    #                 guild_id=interaction.guild_id, 
    #                 user_id=interaction.user.id, 
    #                 username=interaction.user.name,
    #                 avatar=str(interaction.user.display_avatar)
    #             )
    #         )

    #         response = WorkCommand(request).execute()

    #         embed = DiscordBalanceEmbed.work_embed(interaction, response)
    #         await interaction.response.send_message(embed=embed)
    #     except Exception as e:
    #         await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(BalanceCog(bot))
