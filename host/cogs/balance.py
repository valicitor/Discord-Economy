import discord
from discord import app_commands
from discord.ext import commands
from domain import (
    User, 
    GuildNotFoundException, 
    UserNotFoundException,
    InsufficientFundsException,
    OnCooldownException
)
from application import (
    GetBalanceQuery, GetBalanceQueryRequest,
    PayCommand, PayCommandRequest,
    GetTopBalancesQuery, GetTopBalancesQueryRequest,
    WithdrawCommand, WithdrawCommandRequest,
    DepositCommand, DepositCommandRequest,
    WorkCommand, WorkCommandRequest
)
from host.embeds.discord_balance_embed import DiscordBalanceEmbed
import typing

class BalanceCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /balance ---
    @app_commands.command(name="balance", description="Show your current balance.")
    @app_commands.guild_only()
    async def user_balance(self, interaction: discord.Interaction, discord_user: typing.Optional[discord.User] = None):
        try:
            request=GetBalanceQueryRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id if discord_user else interaction.user.id, 
                    username=discord_user.name if discord_user else interaction.user.name,
                    avatar=str(discord_user.display_avatar) if discord_user else str(interaction.user.display_avatar)
                ), 
            )

            response = GetBalanceQuery(request).execute()

            embed = DiscordBalanceEmbed.get_balance_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /pay ---
    @app_commands.command(name="pay", description="Pay another user.")
    @app_commands.guild_only()
    async def user_pay(self, interaction: discord.Interaction, discord_user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        try:
            request=PayCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=interaction.user.id, 
                    username=interaction.user.name,
                    avatar=str(interaction.user.display_avatar)
                ), 
                target=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id, 
                    username=discord_user.name,
                    avatar=str(discord_user.display_avatar)
                ), 
                amount=amount
            )

            response = PayCommand(request).execute()
            
            embed = DiscordBalanceEmbed.pay_balance_embed(interaction, discord_user, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except InsufficientFundsException as e:
            await interaction.response.send_message(f"Insufficient funds: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /withdraw ---
    @app_commands.command(name="withdraw", description="Withdraw money from your bank.")
    @app_commands.guild_only()
    async def user_withdraw(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            request=WithdrawCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=interaction.user.id, 
                    username=interaction.user.name,
                    avatar=str(interaction.user.display_avatar)
                ), 
                amount=amount
            )

            response = WithdrawCommand(request).execute()

            embed = DiscordBalanceEmbed.withdraw_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except InsufficientFundsException as e:
            await interaction.response.send_message(f"Insufficient funds: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /deposit ---
    @app_commands.command(name="deposit", description="Deposit money into your bank.")
    @app_commands.guild_only()
    async def user_deposit(self, interaction: discord.Interaction, amount: typing.Optional[app_commands.Range[int, 1, 100000000]] = None):
        try:
            request=DepositCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=interaction.user.id, 
                    username=interaction.user.name,
                    avatar=str(interaction.user.display_avatar)
                ), 
                amount=amount
            )

            response = DepositCommand(request).execute()

            embed = DiscordBalanceEmbed.deposit_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except InsufficientFundsException as e:
            await interaction.response.send_message(f"Insufficient funds: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /leaderboard ---
    @app_commands.command(name="leaderboard", description="Show the top users by balance.")
    @app_commands.guild_only()
    async def user_leaderboard(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cash', 'Bank', 'Total']] = "Cash"):
        try:
            request=GetTopBalancesQueryRequest(
                guild_id=interaction.guild_id, 
                page=page, 
                sort_by=sort
            )

            response = GetTopBalancesQuery(request).execute()

            if not response.users:
                await interaction.response.send_message("No users found.", ephemeral=True)
                return

            embed = DiscordBalanceEmbed.get_leaderboard_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /work ---
    @app_commands.command(name="work", description="Work to earn money.")
    @app_commands.guild_only()
    async def user_work(self, interaction: discord.Interaction):
        try:
            request=WorkCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=interaction.user.id, 
                    username=interaction.user.name,
                    avatar=str(interaction.user.display_avatar)
                )
            )

            response = WorkCommand(request).execute()

            embed = DiscordBalanceEmbed.work_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except OnCooldownException as e:
            await interaction.response.send_message(f"On cooldown: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(BalanceCog(bot))
