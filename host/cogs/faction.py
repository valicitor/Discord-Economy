import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    JoinFactionCommand, JoinFactionCommandRequest,
    LeaveFactionCommand, LeaveFactionCommandRequest,
    GetFactionQuery, GetFactionQueryRequest,
)
from host.embeds.discord_faction_embed import DiscordFactionEmbed
import typing


class FactionCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    faction_group = app_commands.Group(name="faction", description="Faction commands")

    # -------------------------------------------------------------------------
    # /faction create — opens a modal to collect name, description, color
    # -------------------------------------------------------------------------
    @faction_group.command(name="create", description="Create a new faction.")
    @app_commands.guild_only()
    async def user_faction_create(self, interaction: discord.Interaction):
        try:
            modal = await DiscordFactionEmbed.get_create_faction_modal(interaction)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /faction join
    # -------------------------------------------------------------------------
    @faction_group.command(name="join", description="Join an existing faction.")
    @app_commands.guild_only()
    async def user_faction_join(self, interaction: discord.Interaction, faction_name: str):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await JoinFactionCommand(JoinFactionCommandRequest(guild=guild, user=user, faction_name=faction_name)).execute()
            view = await DiscordFactionEmbed.get_join_faction_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /faction leave
    # -------------------------------------------------------------------------
    @faction_group.command(name="leave", description="Leave your current faction.")
    @app_commands.guild_only()
    async def user_faction_leave(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await LeaveFactionCommand(LeaveFactionCommandRequest(guild=guild, user=user)).execute()
            view = await DiscordFactionEmbed.get_leave_faction_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /faction info
    # -------------------------------------------------------------------------
    @faction_group.command(name="info", description="View information about a faction.")
    @app_commands.guild_only()
    async def user_faction_info(self, interaction: discord.Interaction, faction_name: typing.Optional[str] = None):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await GetFactionQuery(GetFactionQueryRequest(guild=guild, faction_name=faction_name)).execute()
            view = await DiscordFactionEmbed.get_faction_info_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FactionCog(bot))
