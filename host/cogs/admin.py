import discord
from discord import app_commands
from discord.ext import commands

from application import (
    SetupServerCommand, SetupServerCommandRequest,
    GetServerQuery, GetServerQueryRequest,
    SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest,
    SetBalanceCommand, SetBalanceCommandRequest,
    AddBalanceCommand, AddBalanceCommandRequest,
    CreateBusinessStockCommand, CreateBusinessStockCommandRequest,
    SetExchangeRateCommand, SetExchangeRateCommandRequest,
    SetServerSettingCommand, SetServerSettingCommandRequest,
    PayDividendsCommand, PayDividendsCommandRequest,
    CreateResourceNodeCommand, CreateResourceNodeCommandRequest,
    UpdateResourceNodeCommand, UpdateResourceNodeCommandRequest,
    ToggleResourceNodeCommand, ToggleResourceNodeCommandRequest,
    DeleteResourceNodeCommand, DeleteResourceNodeCommandRequest,
    CreateRecipeCommand, CreateRecipeCommandRequest,
    UpdateRecipeCommand, UpdateRecipeCommandRequest,
    DeleteRecipeCommand, DeleteRecipeCommandRequest,
    CreateRecipeInputCommand, CreateRecipeInputCommandRequest,
    DeleteRecipeInputCommand, DeleteRecipeInputCommandRequest,
    CreateRecipeOutputCommand, CreateRecipeOutputCommandRequest,
    DeleteRecipeOutputCommand, DeleteRecipeOutputCommandRequest,
    CreateLocationPolicyCommand, CreateLocationPolicyCommandRequest,
    UpdateLocationPolicyCommand, UpdateLocationPolicyCommandRequest,
    DeleteLocationPolicyCommand, DeleteLocationPolicyCommandRequest,
)
from host.cogs.base_cog import BaseCog
from host.embeds.discord_admin_embed import DiscordAdminEmbed
from host.embeds.discord_economy_embed import DiscordEconomyEmbed
import typing

class AdminCog(BaseCog):

    def __init__(self, bot):
        self.bot = bot

    admin_group         = app_commands.Group(name="admin",         description="Admin commands")
    balance_group       = app_commands.Group(name="balance",       description="Player balance management",  parent=admin_group)
    currency_group      = app_commands.Group(name="currency",      description="Currency configuration",     parent=admin_group)
    business_group      = app_commands.Group(name="business",      description="Business management",        parent=admin_group)
    item_group          = app_commands.Group(name="item",          description="Shop item management",       parent=admin_group)
    world_group         = app_commands.Group(name="world",         description="World configuration",        parent=admin_group)
    resource_node_group = app_commands.Group(name="resource-node", description="Resource node management",   parent=admin_group)
    recipe_group        = app_commands.Group(name="recipe",        description="Recipe management",          parent=admin_group)
    policy_group        = app_commands.Group(name="policy",        description="Location policy management", parent=admin_group)

    # -------------------------------------------------------------------------
    # /admin setup
    # -------------------------------------------------------------------------
    @admin_group.command(name="setup", description="Initialize this server.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_setup_server(
        self,
        interaction: discord.Interaction,
        theme: typing.Optional[typing.Literal['star_wars', 'halo', 'none']] = "star_wars",
    ):
        guild = self._guild(interaction)
        response = await SetupServerCommand(SetupServerCommandRequest(guild=guild, theme=theme)).execute()
        view = await DiscordAdminEmbed.get_setup_server_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin server
    # -------------------------------------------------------------------------
    @admin_group.command(name="server", description="Show server configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_get_server(self, interaction: discord.Interaction):
        response = await GetServerQuery(GetServerQueryRequest(discord_guild_id=interaction.guild_id)).execute()
        view = await DiscordAdminEmbed.get_server_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin balance add  /admin balance set
    # -------------------------------------------------------------------------
    @balance_group.command(name="add", description="Add balance to a member.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_add_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        guild = self._guild(interaction)
        user = self._user(target)
        response = await AddBalanceCommand(AddBalanceCommandRequest(guild=guild, user=user, account_type=account_type, amount=amount)).execute()
        view = await DiscordAdminEmbed.get_add_balance_view(interaction, response)
        await interaction.response.send_message(view=view)

    @balance_group.command(name="set", description="Set a member's balance.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_balance_user(self, interaction: discord.Interaction, target: discord.User, amount: app_commands.Range[int, 1, 100000000], account_type: typing.Optional[typing.Literal['Cash', 'Bank']] = "Cash"):
        guild = self._guild(interaction)
        user = self._user(target)
        response = await SetBalanceCommand(SetBalanceCommandRequest(guild=guild, user=user, account_type=account_type, amount=amount)).execute()
        view = await DiscordAdminEmbed.get_set_balance_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin currency symbol  /admin currency exchange-rate
    # -------------------------------------------------------------------------
    @currency_group.command(name="symbol", description="Set the currency symbol.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_currency_symbol(self, interaction: discord.Interaction, currency_symbol: str):
        guild = self._guild(interaction)
        response = await SetCurrencySymbolCommand(SetCurrencySymbolCommandRequest(guild=guild, currency_symbol=currency_symbol)).execute()
        view = await DiscordAdminEmbed.get_set_currency_symbol_view(interaction, response)
        await interaction.response.send_message(view=view)

    @currency_group.command(name="exchange-rate", description="Set an exchange rate between two currencies.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_set_exchange_rate(
        self, interaction: discord.Interaction,
        from_currency_id: int,
        to_currency_id: int,
        rate: float,
    ):
        guild = self._guild(interaction)
        response = await SetExchangeRateCommand(SetExchangeRateCommandRequest(guild=guild, from_currency_id=from_currency_id, to_currency_id=to_currency_id, rate=rate)).execute()
        view = await DiscordAdminEmbed.get_set_exchange_rate_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin business create  /admin business edit
    # /admin business stock-enable  /admin business pay-dividends
    # -------------------------------------------------------------------------
    @business_group.command(name="create", description="Create a new business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_create(self, interaction: discord.Interaction):
        modal = await DiscordAdminEmbed.get_create_business_modal(interaction)
        await interaction.response.send_modal(modal)

    @business_group.command(name="edit", description="Edit an existing business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_edit(self, interaction: discord.Interaction, business_id: int):
        modal = await DiscordAdminEmbed.get_edit_business_modal(interaction, business_id)
        await interaction.response.send_modal(modal)

    @business_group.command(name="stock-enable", description="Enable stock trading for a business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_stock_enable(
        self, interaction: discord.Interaction,
        business_id: int,
        base_price: int,
        dividend_rate: typing.Optional[float] = 0.05,
    ):
        guild = self._guild(interaction)
        response = await CreateBusinessStockCommand(CreateBusinessStockCommandRequest(guild=guild, business_id=business_id, base_price=base_price, dividend_rate=dividend_rate)).execute()
        view = await DiscordAdminEmbed.get_create_business_stock_view(interaction, response)
        await interaction.response.send_message(view=view)

    @business_group.command(name="pay-dividends", description="Pay dividends to all shareholders of a business.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_business_pay_dividends(self, interaction: discord.Interaction, business_id: int):
        guild = self._guild(interaction)
        response = await PayDividendsCommand(PayDividendsCommandRequest(guild=guild, business_id=business_id)).execute()
        view = await DiscordEconomyEmbed.get_pay_dividends_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin item create  /admin item edit
    # -------------------------------------------------------------------------
    @item_group.command(name="create", description="Add an item to the shop.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_item_create(self, interaction: discord.Interaction):
        modal = await DiscordAdminEmbed.get_create_item_modal(interaction)
        await interaction.response.send_modal(modal)

    @item_group.command(name="edit", description="Edit a shop item.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_item_edit(self, interaction: discord.Interaction, item_id: int):
        modal = await DiscordAdminEmbed.get_edit_item_modal(interaction, item_id)
        await interaction.response.send_modal(modal)

    # -------------------------------------------------------------------------
    # /admin world bank-create  /admin world bank-edit
    # /admin world travel-speed  /admin world setting
    # -------------------------------------------------------------------------
    @world_group.command(name="bank-create", description="Create a new bank.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_bank_create(self, interaction: discord.Interaction):
        modal = await DiscordAdminEmbed.get_create_bank_modal(interaction)
        await interaction.response.send_modal(modal)

    @world_group.command(name="bank-edit", description="Edit an existing bank.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_bank_edit(self, interaction: discord.Interaction, bank_id: int):
        modal = await DiscordAdminEmbed.get_edit_bank_modal(interaction, bank_id)
        await interaction.response.send_modal(modal)

    @world_group.command(name="travel-speed", description="Set the travel speed (units per minute).")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_travel_speed(self, interaction: discord.Interaction, speed: app_commands.Range[int, 1, 1000]):
        guild = self._guild(interaction)
        response = await SetServerSettingCommand(SetServerSettingCommandRequest(guild=guild, key="travel_speed", value=str(speed))).execute()
        view = await DiscordAdminEmbed.get_set_server_setting_view(interaction, response)
        await interaction.response.send_message(view=view)

    @world_group.command(name="setting", description="Set an arbitrary server setting key/value.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_world_setting(self, interaction: discord.Interaction, key: str, value: str):
        guild = self._guild(interaction)
        response = await SetServerSettingCommand(SetServerSettingCommandRequest(guild=guild, key=key, value=value)).execute()
        view = await DiscordAdminEmbed.get_set_server_setting_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin resource-node create  edit  toggle  delete
    # -------------------------------------------------------------------------
    @resource_node_group.command(name="create", description="Create a resource node at a location.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_resource_node_create(
        self, interaction: discord.Interaction,
        location_id: int,
        resource_type: str,
        max_quantity: int,
        regen_rate: int,
        discovered: typing.Optional[bool] = False,
    ):
        guild = self._guild(interaction)
        response = await CreateResourceNodeCommand(CreateResourceNodeCommandRequest(
            guild=guild, location_id=location_id, resource_type=resource_type,
            max_quantity=max_quantity, regen_rate=regen_rate, discovered=discovered,
        )).execute()
        view = await DiscordAdminEmbed.get_resource_node_view(interaction, response)
        await interaction.response.send_message(view=view)

    @resource_node_group.command(name="edit", description="Edit a resource node's properties.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_resource_node_edit(
        self, interaction: discord.Interaction,
        node_id: int,
        resource_type: typing.Optional[str] = None,
        max_quantity: typing.Optional[int] = None,
        regen_rate: typing.Optional[int] = None,
    ):
        response = await UpdateResourceNodeCommand(UpdateResourceNodeCommandRequest(
            node_id=node_id, resource_type=resource_type,
            max_quantity=max_quantity, regen_rate=regen_rate,
        )).execute()
        view = await DiscordAdminEmbed.get_resource_node_view(interaction, response)
        await interaction.response.send_message(view=view)

    @resource_node_group.command(name="toggle", description="Toggle a resource node between discoverable and available.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_resource_node_toggle(self, interaction: discord.Interaction, node_id: int):
        response = await ToggleResourceNodeCommand(ToggleResourceNodeCommandRequest(node_id=node_id)).execute()
        view = await DiscordAdminEmbed.get_resource_node_view(interaction, response)
        await interaction.response.send_message(view=view)

    @resource_node_group.command(name="delete", description="Delete a resource node.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_resource_node_delete(self, interaction: discord.Interaction, node_id: int):
        response = await DeleteResourceNodeCommand(DeleteResourceNodeCommandRequest(node_id=node_id)).execute()
        view = await DiscordAdminEmbed.get_resource_node_delete_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin recipe create  edit  delete  input-add  input-remove  output-add  output-remove
    # -------------------------------------------------------------------------
    @recipe_group.command(name="create", description="Create a server-level recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_create(self, interaction: discord.Interaction, name: str):
        guild = self._guild(interaction)
        response = await CreateRecipeCommand(CreateRecipeCommandRequest(guild=guild, name=name)).execute()
        view = await DiscordAdminEmbed.get_recipe_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="edit", description="Rename a recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_edit(
        self, interaction: discord.Interaction,
        recipe_id: int,
        name: typing.Optional[str] = None,
    ):
        response = await UpdateRecipeCommand(UpdateRecipeCommandRequest(recipe_id=recipe_id, name=name)).execute()
        view = await DiscordAdminEmbed.get_recipe_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="delete", description="Delete a recipe and all its inputs/outputs.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_delete(self, interaction: discord.Interaction, recipe_id: int):
        response = await DeleteRecipeCommand(DeleteRecipeCommandRequest(recipe_id=recipe_id)).execute()
        view = await DiscordAdminEmbed.get_recipe_delete_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="input-add", description="Add a catalogue input to a recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_input_add(
        self, interaction: discord.Interaction,
        recipe_id: int,
        catalogue_id: int,
        quantity: int,
    ):
        response = await CreateRecipeInputCommand(CreateRecipeInputCommandRequest(
            recipe_id=recipe_id, catalogue_id=catalogue_id, quantity=quantity,
        )).execute()
        view = await DiscordAdminEmbed.get_recipe_input_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="input-remove", description="Remove a catalogue input from a recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_input_remove(
        self, interaction: discord.Interaction,
        recipe_id: int,
        catalogue_id: int,
    ):
        response = await DeleteRecipeInputCommand(DeleteRecipeInputCommandRequest(
            recipe_id=recipe_id, catalogue_id=catalogue_id,
        )).execute()
        view = await DiscordAdminEmbed.get_recipe_input_delete_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="output-add", description="Add a catalogue output to a recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_output_add(
        self, interaction: discord.Interaction,
        recipe_id: int,
        catalogue_id: int,
        quantity: int,
    ):
        response = await CreateRecipeOutputCommand(CreateRecipeOutputCommandRequest(
            recipe_id=recipe_id, catalogue_id=catalogue_id, quantity=quantity,
        )).execute()
        view = await DiscordAdminEmbed.get_recipe_output_view(interaction, response)
        await interaction.response.send_message(view=view)

    @recipe_group.command(name="output-remove", description="Remove a catalogue output from a recipe.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_recipe_output_remove(
        self, interaction: discord.Interaction,
        recipe_id: int,
        catalogue_id: int,
    ):
        response = await DeleteRecipeOutputCommand(DeleteRecipeOutputCommandRequest(
            recipe_id=recipe_id, catalogue_id=catalogue_id,
        )).execute()
        view = await DiscordAdminEmbed.get_recipe_output_delete_view(interaction, response)
        await interaction.response.send_message(view=view)

    # -------------------------------------------------------------------------
    # /admin policy create  edit  delete
    # -------------------------------------------------------------------------
    @policy_group.command(name="create", description="Set a governance policy for a location.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_policy_create(
        self, interaction: discord.Interaction,
        location_id: int,
        tax_rate: typing.Optional[float] = 0.0,
        trade_tariff: typing.Optional[float] = 0.0,
        import_restricted: typing.Optional[bool] = False,
        export_restricted: typing.Optional[bool] = False,
        interest_rate_modifier: typing.Optional[float] = 1.0,
        smuggling_risk_modifier: typing.Optional[float] = 1.0,
    ):
        response = await CreateLocationPolicyCommand(CreateLocationPolicyCommandRequest(
            location_id=location_id, tax_rate=tax_rate, trade_tariff=trade_tariff,
            import_restricted=import_restricted, export_restricted=export_restricted,
            interest_rate_modifier=interest_rate_modifier, smuggling_risk_modifier=smuggling_risk_modifier,
        )).execute()
        view = await DiscordAdminEmbed.get_location_policy_view(interaction, response)
        await interaction.response.send_message(view=view)

    @policy_group.command(name="edit", description="Update a location's governance policy.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_policy_edit(
        self, interaction: discord.Interaction,
        location_id: int,
        tax_rate: typing.Optional[float] = None,
        trade_tariff: typing.Optional[float] = None,
        import_restricted: typing.Optional[bool] = None,
        export_restricted: typing.Optional[bool] = None,
        interest_rate_modifier: typing.Optional[float] = None,
        smuggling_risk_modifier: typing.Optional[float] = None,
    ):
        response = await UpdateLocationPolicyCommand(UpdateLocationPolicyCommandRequest(
            location_id=location_id, tax_rate=tax_rate, trade_tariff=trade_tariff,
            import_restricted=import_restricted, export_restricted=export_restricted,
            interest_rate_modifier=interest_rate_modifier, smuggling_risk_modifier=smuggling_risk_modifier,
        )).execute()
        view = await DiscordAdminEmbed.get_location_policy_view(interaction, response)
        await interaction.response.send_message(view=view)

    @policy_group.command(name="delete", description="Remove the governance policy from a location.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_policy_delete(self, interaction: discord.Interaction, location_id: int):
        response = await DeleteLocationPolicyCommand(DeleteLocationPolicyCommandRequest(location_id=location_id)).execute()
        view = await DiscordAdminEmbed.get_location_policy_delete_view(interaction, response)
        await interaction.response.send_message(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
