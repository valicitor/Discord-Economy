import discord
from discord import app_commands
from discord.ext import commands

from application import (
    GetShopQuery, GetShopQueryRequest, GetShopQueryResponse,
    GetCatalogueQuery, GetCatalogueQueryRequest, GetCatalogueQueryResponse,
    SearchCatalogueQuery, SearchCatalogueQueryRequest,
    SellItemCommand, SellItemCommandRequest,
    CreateCustomUnitCommand, CreateCustomUnitCommandRequest,
    UnassignEquipmentCommand, UnassignEquipmentCommandRequest,
    AssignPlayerEquipmentCommand, AssignPlayerEquipmentCommandRequest,
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_shop_embed import DiscordShopEmbed
import typing

class ShopCog(BaseCog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    shop_group = app_commands.Group(name="shop", description="Shop and inventory")
    unit_group = app_commands.Group(name="unit", description="Unit and equipment management")

    # -------------------------------------------------------------------------
    # /shop browse  /shop info  /shop sell
    # -------------------------------------------------------------------------
    @shop_group.command(name="browse", description="Browse items available to buy.")
    @app_commands.guild_only()
    async def user_shop_browse(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cost', 'Name', 'Stock']] = "Cost"):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = GetShopQueryRequest(guild=guild, user=user, page=page, sort_by=sort, limit=10)
        response = await GetShopQuery(request).execute()
        layout_view = await DiscordShopEmbed.get_shop_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)

    @shop_group.command(name="info", description="Show the stats of a specific catalogue item.")
    @app_commands.guild_only()
    async def user_shop_info(self, interaction: discord.Interaction, name: str):
        guild = self._guild(interaction)
        request = GetCatalogueQueryRequest(guild=guild, name=name)
        response = await GetCatalogueQuery(request).execute()
        layout_view = await DiscordShopEmbed.get_catalogue_block_embed(interaction, response)
        await interaction.response.send_message(view=layout_view)

    @user_shop_info.autocomplete("name")
    async def shop_info_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self._catalogue_autocomplete(interaction, current)

    @shop_group.command(name="sell", description="Sell an item or unit from your inventory.")
    @app_commands.guild_only()
    async def user_shop_sell(self, interaction: discord.Interaction, name: str, quantity: typing.Optional[int] = 1):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = SellItemCommandRequest(guild=guild, user=user, item_id=None, item_name=name, quantity=quantity)
        response = await SellItemCommand(request).execute()
        layout_view = await DiscordShopEmbed.get_sell_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)

    @user_shop_sell.autocomplete("name")
    async def shop_sell_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self._catalogue_autocomplete(interaction, current)

    async def _catalogue_autocomplete(self, interaction: discord.Interaction, current: str):
        guild = self._guild(interaction)
        response = await SearchCatalogueQuery(SearchCatalogueQueryRequest(guild=guild, search=current)).execute()
        return [
            app_commands.Choice(name=f"{e.type}: {e.name}", value=e.name)
            for e in response.results
        ]

    # -------------------------------------------------------------------------
    # /unit create  /unit equip  /unit unequip  /unit unassign
    # -------------------------------------------------------------------------
    @unit_group.command(name="create", description="Create a custom unit from a race in your inventory.")
    @app_commands.guild_only()
    async def user_unit_create(self, interaction: discord.Interaction, unit_name: str, race_name: str):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = CreateCustomUnitCommandRequest(guild=guild, user=user, unit_name=unit_name, race_name=race_name, equipment={})
        response = await CreateCustomUnitCommand(request).execute()
        layout_view = await DiscordShopEmbed.get_create_unit_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)

    @unit_group.command(name="equip", description="Equip an item to your character from your inventory.")
    @app_commands.guild_only()
    async def user_unit_equip(self, interaction: discord.Interaction, name: str):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = AssignPlayerEquipmentCommandRequest(guild=guild, user=user, item_name=name, equip=True)
        response = await AssignPlayerEquipmentCommand(request).execute()
        layout_view = await DiscordShopEmbed.get_equip_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)

    @unit_group.command(name="unequip", description="Unequip an item from your character, returning it to your inventory.")
    @app_commands.guild_only()
    async def user_unit_unequip(self, interaction: discord.Interaction, name: str):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = AssignPlayerEquipmentCommandRequest(guild=guild, user=user, item_name=name, equip=False)
        response = await AssignPlayerEquipmentCommand(request).execute()
        layout_view = await DiscordShopEmbed.get_equip_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)

    @unit_group.command(name="unassign", description="Remove equipment from a unit's slot, returning it to your inventory.")
    @app_commands.guild_only()
    async def user_unit_unassign(self, interaction: discord.Interaction, unit_name: str, slot_name: str):
        guild = self._guild(interaction)
        user = self._user(interaction.user)
        request = UnassignEquipmentCommandRequest(guild=guild, user=user, unit_name=unit_name, slot_name=slot_name)
        response = await UnassignEquipmentCommand(request).execute()
        layout_view = await DiscordShopEmbed.get_unassign_equipment_view(interaction, response)
        await interaction.response.send_message(view=layout_view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ShopCog(bot))
