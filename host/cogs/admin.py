import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    SetupServerCommand, SetupServerCommandRequest,
    GetServerQuery, GetServerQueryRequest,
    SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest,
    SetBalanceCommand, SetBalanceCommandRequest,
    AddBalanceCommand, AddBalanceCommandRequest,
    CreateBusinessStockCommand, CreateBusinessStockCommandRequest,
    SetExchangeRateCommand, SetExchangeRateCommandRequest,
    SetServerSettingCommand, SetServerSettingCommandRequest,
)
from host.embeds.discord_admin_embed import DiscordAdminEmbed
import typing

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    admin_group = app_commands.Group(name="admin", description="Admin commands")

    business_group = app_commands.Group(name="business", description="Business management", parent=admin_group)
    item_group     = app_commands.Group(name="item",     description="Shop item management",  parent=admin_group)
    economy_group  = app_commands.Group(name="economy",  description="Economy management",    parent=admin_group)
    world_group    = app_commands.Group(name="world",    description="World configuration",   parent=admin_group)

    # -------------------------------------------------------------------------
    # /admin setup
    # -------------------------------------------------------------------------
    @admin_group.command(name="setup", description="Initialize this server.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_setup_server(
        self,
        interaction: discord.Interaction,
        seed_data: typing.Optional[typing.Literal['True', 'False']] = "False",
        theme: typing.Optional[typing.Literal['star_wars', 'halo', 'none']] = "star_wars",
    ):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await SetupServerCommand(SetupServerCommandRequest(guild=guild, seed_data=(seed_data == "True"), theme=theme)).execute()
            view = await DiscordAdminEmbed.get_setup_server_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin server
    # -------------------------------------------------------------------------
    @admin_group.command(name="server", description="Show server configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_get_server(self, interaction: discord.Interaction):
        try:
            response = await GetServerQuery(GetServerQueryRequest(discord_guild_id=interaction.guild_id)).execute()
            view = await DiscordAdminEmbed.get_server_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin set-currency-symbol
    # -------------------------------------------------------------------------
    @admin_group.command(name="set-currency-symbol", description="Set the currency symbol.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_currency_symbol(self, interaction: discord.Interaction, currency_symbol: str):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await SetCurrencySymbolCommand(SetCurrencySymbolCommandRequest(guild=guild, currency_symbol=currency_symbol)).execute()
            view = await DiscordAdminEmbed.get_set_currency_symbol_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin add-balance  /admin set-balance
    # -------------------------------------------------------------------------
    @admin_group.command(name="add-balance", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_add_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=target.id, name=target.name, display_avatar=str(target.display_avatar))
            response = await AddBalanceCommand(AddBalanceCommandRequest(guild=guild, user=user, account_type=account_type, amount=amount)).execute()
            view = await DiscordAdminEmbed.get_add_balance_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @admin_group.command(name="set-balance", description="Set a member's balance.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            user = DiscordUser(user_id=target.id, name=target.name, display_avatar=str(target.display_avatar))
            response = await SetBalanceCommand(SetBalanceCommandRequest(guild=guild, user=user, account_type=account_type, amount=amount)).execute()
            view = await DiscordAdminEmbed.get_set_balance_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin business create  — opens a modal (name, type, x/y, description, range)
    # /admin business edit    — takes business_id, opens modal for optional fields
    # -------------------------------------------------------------------------
    @business_group.command(name="create", description="Create a new business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_create(self, interaction: discord.Interaction):
        try:
            modal = await DiscordAdminEmbed.get_create_business_modal(interaction)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @business_group.command(name="edit", description="Edit an existing business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_edit(self, interaction: discord.Interaction, business_id: int):
        try:
            modal = await DiscordAdminEmbed.get_edit_business_modal(interaction, business_id)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin item create  — opens modal (catalogue_id, name, price, stock, business_id)
    # /admin item edit    — takes item_id, opens modal for optional fields
    # -------------------------------------------------------------------------
    @item_group.command(name="create", description="Add an item to the shop.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_item_create(self, interaction: discord.Interaction):
        try:
            modal = await DiscordAdminEmbed.get_create_item_modal(interaction)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @item_group.command(name="edit", description="Edit a shop item.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_item_edit(self, interaction: discord.Interaction, item_id: int):
        try:
            modal = await DiscordAdminEmbed.get_edit_item_modal(interaction, item_id)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin economy stock-enable  /admin economy exchange-rate
    # -------------------------------------------------------------------------
    @economy_group.command(name="stock-enable", description="Enable stock trading for a business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_economy_stock_enable(
        self, interaction: discord.Interaction,
        business_id: int,
        base_price: int,
        dividend_rate: typing.Optional[float] = 0.05,
    ):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await CreateBusinessStockCommand(CreateBusinessStockCommandRequest(guild=guild, business_id=business_id, base_price=base_price, dividend_rate=dividend_rate)).execute()
            view = await DiscordAdminEmbed.get_create_business_stock_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @economy_group.command(name="exchange-rate", description="Set an exchange rate between two currencies.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_economy_exchange_rate(
        self, interaction: discord.Interaction,
        from_currency_id: int,
        to_currency_id: int,
        rate: float,
    ):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await SetExchangeRateCommand(SetExchangeRateCommandRequest(guild=guild, from_currency_id=from_currency_id, to_currency_id=to_currency_id, rate=rate)).execute()
            view = await DiscordAdminEmbed.get_set_exchange_rate_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # -------------------------------------------------------------------------
    # /admin world bank-create  — opens modal (name, interest_rate, x/y, range, max_accounts)
    # /admin world bank-edit    — takes bank_id, opens modal for optional fields
    # /admin world travel-speed  /admin world setting
    # -------------------------------------------------------------------------
    @world_group.command(name="bank-create", description="Create a new bank.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_bank_create(self, interaction: discord.Interaction):
        try:
            modal = await DiscordAdminEmbed.get_create_bank_modal(interaction)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @world_group.command(name="bank-edit", description="Edit an existing bank.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_bank_edit(self, interaction: discord.Interaction, bank_id: int):
        try:
            modal = await DiscordAdminEmbed.get_edit_bank_modal(interaction, bank_id)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @world_group.command(name="travel-speed", description="Set the travel speed (units per minute).")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_travel_speed(self, interaction: discord.Interaction, speed: app_commands.Range[int, 1, 1000]):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await SetServerSettingCommand(SetServerSettingCommandRequest(guild=guild, key="travel_speed", value=str(speed))).execute()
            view = await DiscordAdminEmbed.get_set_server_setting_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @world_group.command(name="setting", description="Set an arbitrary server setting key/value.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_setting(self, interaction: discord.Interaction, key: str, value: str):
        try:
            guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
            response = await SetServerSettingCommand(SetServerSettingCommandRequest(guild=guild, key=key, value=value)).execute()
            view = await DiscordAdminEmbed.get_set_server_setting_view(interaction, response)
            await interaction.response.send_message(view=view)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
