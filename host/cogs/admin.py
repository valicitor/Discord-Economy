import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest,
    SetBalanceCommand, SetBalanceCommandRequest,
    AddBalanceCommand, AddBalanceCommandRequest,
)
from host.embeds.discord_admin_embed import DiscordAdminEmbed
import typing

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    admin_group = app_commands.Group(
        name="admin",
        description="Admin commands"
    )

    # --- /set_currency_symbol ---
    @admin_group.command(name="set-currency-symbol", description="Set the currency symbol for the guild.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_currency_symbol(self, interaction: discord.Interaction, currency_symbol: str):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )

            request = SetCurrencySymbolCommandRequest(
                guild=guild, 
                currency_symbol=currency_symbol
            )

            response = await SetCurrencySymbolCommand(request).execute()

            embed = await DiscordAdminEmbed.set_currency_symbol_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /add-balance ---
    @admin_group.command(name="add-balance", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_add_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=target.id,
                name=target.name,
                display_avatar=str(target.display_avatar)
            )
        
            request = AddBalanceCommandRequest(
                guild=guild, 
                user=user, 
                account_type=account_type,
                amount=amount
            )

            response = await AddBalanceCommand(request).execute()

            embed = await DiscordAdminEmbed.add_balance_embed(interaction, target, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # --- /set-balance ---
    @admin_group.command(name="set-balance", description="Set a members current balance.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=target.id,
                name=target.name,
                display_avatar=str(target.display_avatar)
            )
        
            request = SetBalanceCommandRequest(
                guild=guild, 
                user=user, 
                account_type=account_type,
                amount=amount
            )

            response = await SetBalanceCommand(request).execute()

            embed = await DiscordAdminEmbed.set_balance_embed(interaction, target, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    
     # --- /item-setup-create ---
    # item_setup_group = app_commands.Group(
    #     name="item-setup",
    #     description="Item setup commands"
    # )
    
    # @item_setup_group.command(name="create", description="Create a new item.")
    # @app_commands.checks.has_permissions(administrator=True)
    # @app_commands.guild_only()
    # async def admin_create_item(
    #     self, interaction: discord.Interaction, 
    #     name: str, 
    #     price: typing.Optional[int] = 0, 
    #     icon: typing.Optional[str] = "", 
    #     description: typing.Optional[str] = "", 
    #     stock_remaining: typing.Optional[int] = -1, 
    #     category: typing.Optional[str] = "default", 
    #     inventory: typing.Optional[bool] = True, 
    #     usable: typing.Optional[bool] = True, 
    #     sellable: typing.Optional[bool] = True
    # ):
    #     try:
    #         request = CreateItemCommandRequest(
    #             guild_id=interaction.guild_id, 
    #             item=Item(
    #                 guild_id=interaction.guild_id, 
    #                 name=name,
    #                 price=price,
    #                 icon=icon,
    #                 description=description,
    #                 stock=stock_remaining,
    #                 category=category,
    #                 inventory=inventory,
    #                 usable=usable,
    #                 sellable=sellable
    #             )
    #         )

    #         response = await CreateItemCommand(request).execute()

    #         embed = DiscordAdminEmbed.create_item_embed(interaction, response)
    #         await interaction.response.send_message(embed=embed)
    #     except Exception as e:
    #         await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
