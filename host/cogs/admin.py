import discord
from discord import app_commands
from discord.ext import commands
from domain import User, UserNotFoundException, GuildNotFoundException
from application import (
    SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest,
    SetBalanceCommand, SetBalanceCommandRequest,
    AddBalanceCommand, AddBalanceCommandRequest
)
from host.embeds.discord_admin_embed import DiscordAdminEmbed
import typing

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --- /set_currency_symbol ---
    @app_commands.command(name="set-currency-symbol", description="Set the currency symbol for the guild.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_currency_symbol(self, interaction: discord.Interaction, currency_symbol: str):
        try:
            request = SetCurrencySymbolCommandRequest(
                guild_id=interaction.guild_id, 
                currency_symbol=currency_symbol
            )

            response = SetCurrencySymbolCommand(request).execute()

            embed = DiscordAdminEmbed.set_currency_symbol_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /add-balance ---
    @app_commands.command(name="add-balance", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_add_balance_user(self, interaction: discord.Interaction, discord_user: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            request = AddBalanceCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id, 
                    username=discord_user.name,
                    avatar=str(discord_user.display_avatar)
                ), 
                account_type=account_type,
                amount=amount
            )

            response = AddBalanceCommand(request).execute()

            embed = DiscordAdminEmbed.add_balance_embed(interaction, discord_user, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /set-balance ---
    @app_commands.command(name="set-balance", description="Set a members current balance.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_balance_user(self, interaction: discord.Interaction, discord_user: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            request = SetBalanceCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id, 
                    username=discord_user.name,
                    avatar=str(discord_user.display_avatar)
                ), 
                account_type=account_type,
                amount=amount
            )

            response = SetBalanceCommand(request).execute()

            embed = DiscordAdminEmbed.set_balance_embed(interaction, discord_user, response)
            await interaction.response.send_message(embed=embed)
        except UserNotFoundException as e:
            await interaction.response.send_message(f"User not found: {str(e)}", ephemeral=True)
        except GuildNotFoundException as e:
            await interaction.response.send_message(f"Guild not found: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
