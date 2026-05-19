import discord
from discord import app_commands
from discord.ext import commands

from application import (
    GetPlayerQuery, GetPlayerQueryRequest
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_player_embed import DiscordPlayerEmbed
import typing

class PlayerCog(BaseCog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /register ---
    @app_commands.command(name="register", description="Register as a new player")
    @app_commands.guild_only()
    async def user_register(self, interaction: discord.Interaction):
        modal = await DiscordPlayerEmbed.new_player_modal(interaction)
        await interaction.response.send_modal(modal)

    # --- /profile ---
    @app_commands.command(name="profile", description="View a player's profile.")
    @app_commands.guild_only()
    async def user_get_player_profile(self, interaction: discord.Interaction, target: typing.Optional[discord.User] = None):
        request = GetPlayerQueryRequest(
            discord_guild_id=interaction.guild_id,
            discord_user_id=target.id if target else interaction.user.id,
        )
        response = await GetPlayerQuery(request).execute()
        layout_view = await DiscordPlayerEmbed.get_player_profile_embed(interaction, response)
        await interaction.response.send_message(view=layout_view)

async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCog(bot))
