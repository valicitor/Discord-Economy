import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    GetPlayerQuery, GetPlayerQueryRequest
)
from host.embeds.discord_player_embed import DiscordPlayerEmbed
import typing

class PlayerCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /register ---
    @app_commands.command(name="register", description="Register as a new player")
    @app_commands.guild_only()
    async def user_register(self, interaction: discord.Interaction):
        try:
            modal = await DiscordPlayerEmbed.new_player_modal(interaction)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /profile ---
    @app_commands.command(name="profile", description="View a player's profile.")
    @app_commands.guild_only()
    async def user_get_player_profile(self, interaction: discord.Interaction, target: typing.Optional[discord.User] = None):
        try:
            request=GetPlayerQueryRequest(
                discord_guild_id=interaction.guild_id,
                discord_user_id=target.id if target else interaction.user.id,
            )

            response = await GetPlayerQuery(request).execute()

            layout_view = await DiscordPlayerEmbed.get_player_profile_embed(interaction, response)
            await interaction.response.send_message(view=layout_view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCog(bot))
