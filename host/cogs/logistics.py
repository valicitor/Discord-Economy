import discord
from discord import app_commands
from discord.ext import commands

from application import (
    AssignGarrisonCommand, AssignGarrisonCommandRequest,
    GetGarrisonQuery, GetGarrisonQueryRequest,
    PayMaintenanceCommand, PayMaintenanceCommandRequest,
    StartTransportCommand, StartTransportCommandRequest,
    CompleteTransportCommand, CompleteTransportCommandRequest,
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_logistics_embed import DiscordLogisticsEmbed


class LogisticsCog(BaseCog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    logistics_group   = app_commands.Group(name="logistics",    description="Logistics management")
    garrison_group    = app_commands.Group(name="garrison",     description="Garrison management",   parent=logistics_group)
    maintenance_group = app_commands.Group(name="maintenance",  description="Maintenance management", parent=logistics_group)
    transport_group   = app_commands.Group(name="transport",    description="Resource transport",     parent=logistics_group)

    # -------------------------------------------------------------------------
    # /logistics garrison assign  /logistics garrison view
    # -------------------------------------------------------------------------
    @garrison_group.command(name="assign", description="Assign a unit to garrison a location.")
    @app_commands.guild_only()
    async def user_garrison_assign(self, interaction: discord.Interaction, unit_name: str, poi_name: str):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await AssignGarrisonCommand(AssignGarrisonCommandRequest(guild=guild, user=user, unit_name=unit_name, poi_name=poi_name)).execute()
        view = await DiscordLogisticsEmbed.get_garrison_assign_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    @garrison_group.command(name="view", description="View your garrisoned units.")
    @app_commands.guild_only()
    async def user_garrison_view(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await GetGarrisonQuery(GetGarrisonQueryRequest(guild=guild, user=user)).execute()
        view = await DiscordLogisticsEmbed.get_garrison_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    # -------------------------------------------------------------------------
    # /logistics maintenance pay
    # -------------------------------------------------------------------------
    @maintenance_group.command(name="pay", description="Pay maintenance costs for all your units.")
    @app_commands.guild_only()
    async def user_maintenance_pay(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await PayMaintenanceCommand(PayMaintenanceCommandRequest(guild=guild, user=user)).execute()
        view = await DiscordLogisticsEmbed.get_maintenance_pay_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    # -------------------------------------------------------------------------
    # /logistics transport start  /logistics transport complete
    # -------------------------------------------------------------------------
    @transport_group.command(name="start", description="Start transporting a resource between two businesses.")
    @app_commands.guild_only()
    async def user_transport_start(
        self, interaction: discord.Interaction,
        from_business_id: int,
        to_business_id: int,
        catalogue_id: int,
        quantity: app_commands.Range[int, 1, 1000],
    ):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await StartTransportCommand(StartTransportCommandRequest(guild=guild, user=user, from_business_id=from_business_id, to_business_id=to_business_id, catalogue_id=catalogue_id, quantity=quantity)).execute()
        view = await DiscordLogisticsEmbed.get_transport_start_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)

    @transport_group.command(name="complete", description="Collect all arrived transports.")
    @app_commands.guild_only()
    async def user_transport_complete(self, interaction: discord.Interaction):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        response = await CompleteTransportCommand(CompleteTransportCommandRequest(guild=guild, user=user)).execute()
        view = await DiscordLogisticsEmbed.get_transport_complete_view(interaction, response)
        await interaction.response.send_message(view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LogisticsCog(bot))
