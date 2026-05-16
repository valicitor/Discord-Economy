import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    AssignGarrisonCommand, AssignGarrisonCommandRequest,
    GetGarrisonQuery, GetGarrisonQueryRequest,
    PayMaintenanceCommand, PayMaintenanceCommandRequest,
    StartTransportCommand, StartTransportCommandRequest,
    CompleteTransportCommand, CompleteTransportCommandRequest,
)
from host.embeds.discord_logistics_embed import DiscordLogisticsEmbed


class LogisticsCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    garrison_group = app_commands.Group(name="garrison", description="Garrison management")

    @garrison_group.command(name="assign", description="Assign a unit to garrison a location.")
    @app_commands.guild_only()
    async def user_garrison_assign(self, interaction: discord.Interaction, unit_name: str, poi_name: str):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await AssignGarrisonCommand(AssignGarrisonCommandRequest(guild=guild, user=user, unit_name=unit_name, poi_name=poi_name)).execute()
            view = await DiscordLogisticsEmbed.get_garrison_assign_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @garrison_group.command(name="view", description="View your garrisoned units.")
    @app_commands.guild_only()
    async def user_garrison_view(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await GetGarrisonQuery(GetGarrisonQueryRequest(guild=guild, user=user)).execute()
            view = await DiscordLogisticsEmbed.get_garrison_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    maintenance_group = app_commands.Group(name="maintenance", description="Maintenance management")

    @maintenance_group.command(name="pay", description="Pay maintenance costs for all your units.")
    @app_commands.guild_only()
    async def user_maintenance_pay(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await PayMaintenanceCommand(PayMaintenanceCommandRequest(guild=guild, user=user)).execute()
            view = await DiscordLogisticsEmbed.get_maintenance_pay_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    transport_group = app_commands.Group(name="transport", description="Resource transport")

    @transport_group.command(name="start", description="Start transporting a resource between two businesses.")
    @app_commands.guild_only()
    async def user_transport_start(
        self, interaction: discord.Interaction,
        from_business_id: int,
        to_business_id: int,
        resource_type: str,
        quantity: app_commands.Range[int, 1, 1000],
    ):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await StartTransportCommand(StartTransportCommandRequest(guild=guild, user=user, from_business_id=from_business_id, to_business_id=to_business_id, resource_type=resource_type, quantity=quantity)).execute()
            view = await DiscordLogisticsEmbed.get_transport_start_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @transport_group.command(name="complete", description="Collect all arrived transports.")
    @app_commands.guild_only()
    async def user_transport_complete(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=interaction.user.id, name=interaction.user.name, display_avatar=str(interaction.user.display_avatar))
            response = await CompleteTransportCommand(CompleteTransportCommandRequest(guild=guild, user=user)).execute()
            view = await DiscordLogisticsEmbed.get_transport_complete_view(interaction, response)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LogisticsCog(bot))
