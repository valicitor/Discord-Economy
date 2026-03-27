import discord
from discord import app_commands
from discord.ext import commands
from domain import User, UserNotFoundException, GuildNotFoundException
from application import (
    SetBalanceCommand, SetBalanceCommandRequest,
    AddBalanceCommand, AddBalanceCommandRequest
)
from host.embeds.discord_admin_embed import DiscordAdminEmbed

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --- /add-balance ---
    @app_commands.command(name="add-balance", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_add_balance_user(self, interaction: discord.Interaction, discord_user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        try:
            request = AddBalanceCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id, 
                    username=discord_user.name,
                    avatar=str(discord_user.display_avatar)
                ), 
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
    async def admin_set_balance_user(self, interaction: discord.Interaction, discord_user: discord.User, amount: app_commands.Range[int, 1, 100000000]):
        try:
            request = SetBalanceCommandRequest(
                guild_id=interaction.guild_id, 
                user=User(
                    guild_id=interaction.guild_id, 
                    user_id=discord_user.id, 
                    username=discord_user.name,
                    avatar=str(discord_user.display_avatar)
                ), 
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
