import discord
from discord import app_commands
from discord.ext import commands

from infrastructure import ServerRepository, RaceRepository, EquipmentRepository

from application import DiscordGuild, DiscordUser
from application import (
    GetEquipmentQuery, GetEquipmentQueryRequest,
    GetRaceQuery, GetRaceQueryRequest
)
from host.embeds.discord_units_embed import DiscordUnitsEmbed

class UnitsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    stat_block_group = app_commands.Group(
        name="stat-block",
        description="Stat Block commands"
    )

    # --- /stat-block equipment ---
    @stat_block_group.command(name="equipment", description="Show the stats of a specific equipment.")
    @app_commands.guild_only()
    async def user_equipment_stat_block(self, interaction: discord.Interaction, name: str):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )

            request=GetEquipmentQueryRequest(
                guild=guild, 
                name=name
            )

            response = await GetEquipmentQuery(request).execute()

            if not response.equipment:
                await interaction.response.send_message("No equipment found.", ephemeral=True)
                return

            embed = await DiscordUnitsEmbed.get_equipment_stat_block_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        
    @user_equipment_stat_block.autocomplete("name")
    async def equipment_autocomplete(self, interaction: discord.Interaction, current: str):
        server_repo = await ServerRepository().get_instance()
        equipment_repo = await EquipmentRepository().get_instance()
        
        server = await server_repo.get_by_guild_id(interaction.guild_id)
        if server is None:
             return []
        equipment = await equipment_repo.search_by_name(current, server.server_id, 25)

        matches = sorted((e.name for e in equipment), key=str.lower)[:25]

        return [
            app_commands.Choice(
                name=match,
                value=match
            )
            for match in matches
        ]


    # --- /stat-block race ---
    @stat_block_group.command(name="race", description="Show the stats of a specific race.")
    @app_commands.guild_only()
    async def user_race_stat_block(self, interaction: discord.Interaction, name: str):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )

            request=GetRaceQueryRequest(
                guild=guild, 
                name=name
            )

            response = await GetRaceQuery(request).execute()

            if not response.race:
                await interaction.response.send_message("No race found.", ephemeral=True)
                return

            embed = await DiscordUnitsEmbed.get_race_stat_block_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    
    @user_race_stat_block.autocomplete("name")
    async def race_autocomplete(self, interaction: discord.Interaction, current: str):
        server_repo = await ServerRepository().get_instance()
        race_repo = await RaceRepository().get_instance()
        
        server = await server_repo.get_by_guild_id(interaction.guild_id)
        if server is None:
            return []
        races = await race_repo.search_by_name(current, server.server_id, 25)

        matches = sorted((e.name for e in races), key=str.lower)[:25]

        return [
            app_commands.Choice(
                name=match,
                value=match
            )
            for match in matches
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(UnitsCog(bot))
