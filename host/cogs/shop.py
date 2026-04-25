import discord
from discord import app_commands
from discord.ext import commands

from infrastructure import ServerRepository, CatalogueRepository
from application import DiscordGuild, DiscordUser
from application import (
    GetShopQuery, GetShopQueryRequest, GetShopQueryResponse,
    GetCatalogueQuery, GetCatalogueQueryRequest, GetCatalogueQueryResponse
)
from host.embeds.discord_shop_embed import DiscordShopEmbed
import typing

class ShopCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /shop ---
    @app_commands.command(name="shop", description="View the shop.")
    @app_commands.guild_only()
    async def user_shop(self, interaction: discord.Interaction, page: typing.Optional[int] = 1, sort: typing.Optional[typing.Literal['Cost', 'Name', 'Stock']] = "Cost"):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=interaction.user.id,
                name=interaction.user.name,
                display_avatar=str(interaction.user.display_avatar)
            )
        
            request=GetShopQueryRequest(
                guild=guild,
                user=user,
                page=page,
                sort_by=sort,
                limit=10
            )

            response = await GetShopQuery(request).execute()

            layout_view = await DiscordShopEmbed.get_shop_view(interaction, response)
            await interaction.response.send_message(view=layout_view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /catalogue ---
    @app_commands.command(name="catalogue", description="Show the stats of a specific catalogue item.")
    @app_commands.guild_only()
    async def user_catalogue_block(self, interaction: discord.Interaction, name: str):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )

            request=GetCatalogueQueryRequest(
                guild=guild, 
                name=name
            )

            response = await GetCatalogueQuery(request).execute()

            if not response.catalogue_item:
                await interaction.response.send_message("No catalogue item found.", ephemeral=True)
                return

            layout_view = await DiscordShopEmbed.get_catalogue_block_embed(interaction, response)
            await interaction.response.send_message(view=layout_view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        
    @user_catalogue_block.autocomplete("name")
    async def catalogue_autocomplete(self, interaction: discord.Interaction, current: str):
        server_repo = await ServerRepository().get_instance()
        catalogue_repo = await CatalogueRepository().get_instance()
        
        server = await server_repo.get_by_guild_id(interaction.guild_id)
        if server is None:
            return []

        catalogue_items = await catalogue_repo.search_by_name(
            current, server.server_id, ['active'], 25
        )

        return [
            app_commands.Choice(
                name=f"{e.type}: {e.name}",
                value=e.name
            )
            for e in catalogue_items
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(ShopCog(bot))
