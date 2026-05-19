import discord
from discord import Interaction

from application.services.helpers import Helpers
from application import DiscordGuild
from application import (
    CreateBusinessCommand, CreateBusinessCommandRequest,
    UpdateBusinessCommand, UpdateBusinessCommandRequest,
    CreateItemCommand, CreateItemCommandRequest,
    UpdateItemCommand, UpdateItemCommandRequest,
    CreateBankCommand, CreateBankCommandRequest,
    UpdateBankCommand, UpdateBankCommandRequest,
    SetupServerCommandResponse,
    GetServerQueryResponse,
    AddBalanceCommandResponse,
    SetBalanceCommandResponse,
    SetCurrencySymbolCommandResponse,
    CreateBusinessCommandResponse,
    UpdateBusinessCommandResponse,
    CreateItemCommandResponse,
    UpdateItemCommandResponse,
    CreateBankCommandResponse,
    UpdateBankCommandResponse,
    CreateBusinessStockCommandResponse,
    SetExchangeRateCommandResponse,
    SetServerSettingCommandResponse,
)

_BUSINESS_TYPES = [
    'Manufacturing', 'Military', 'Research', 'Commerce',
    'Entertainment', 'Mining', 'Education', 'Construction',
]


class DiscordAdminEmbed:

    # =========================================================================
    # Modals
    # =========================================================================

    class CreateBusinessModal(discord.ui.Modal, title="Create Business"):
        name = None
        type = None
        coordinates = None
        description = None
        range = None

        def __init__(self):
            super().__init__()

        @classmethod
        async def create(cls):
            modal = cls()
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Name:",
                component=discord.ui.TextInput(placeholder="Business name", required=True, max_length=100)
            )
            self.add_item(self.name)

            self.type = discord.ui.Label(
                text="Type:",
                component=discord.ui.Select(
                    placeholder="Select business type",
                    options=[discord.SelectOption(label=t, value=t) for t in _BUSINESS_TYPES],
                    required=True
                )
            )
            self.add_item(self.type)

            self.coordinates = discord.ui.Label(
                text="Coordinates (X,Y):",
                component=discord.ui.TextInput(placeholder="e.g. 100,200", required=True)
            )
            self.add_item(self.coordinates)

            self.description = discord.ui.Label(
                text="Description:",
                component=discord.ui.TextInput(
                    placeholder="Optional description...",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=500
                )
            )
            self.add_item(self.description)

            self.range = discord.ui.Label(
                text="Range (blank = unlimited):",
                component=discord.ui.TextInput(placeholder="e.g. 500", required=False)
            )
            self.add_item(self.range)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                coords = self.coordinates.component.value.strip().split(",")
                if len(coords) != 2:
                    raise ValueError("Coordinates must be in format X,Y (e.g. 100,200)")
                x, y = int(coords[0].strip()), int(coords[1].strip())
                range_str = self.range.component.value.strip()
                range_val = int(range_str) if range_str else None

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await CreateBusinessCommand(CreateBusinessCommandRequest(
                    guild=guild,
                    name=self.name.component.value,
                    type=self.type.component.values[0],
                    x=x, y=y,
                    description=self.description.component.value or '',
                    range=range_val
                )).execute()
                view = await DiscordAdminEmbed.CreateBusinessLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class EditBusinessModal(discord.ui.Modal, title="Edit Business"):
        name = None
        coordinates = None
        description = None
        range = None

        def __init__(self, business_id: int):
            self.business_id = business_id
            super().__init__()

        @classmethod
        async def create(cls, business_id: int):
            modal = cls(business_id)
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Name (blank = no change):",
                component=discord.ui.TextInput(placeholder="New business name", required=False, max_length=100)
            )
            self.add_item(self.name)

            self.coordinates = discord.ui.Label(
                text="Coordinates X,Y (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 100,200", required=False)
            )
            self.add_item(self.coordinates)

            self.description = discord.ui.Label(
                text="Description (blank = no change):",
                component=discord.ui.TextInput(
                    placeholder="New description...",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=500
                )
            )
            self.add_item(self.description)

            self.range = discord.ui.Label(
                text="Range (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 500", required=False)
            )
            self.add_item(self.range)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                name_val = self.name.component.value.strip() or None
                description_val = self.description.component.value.strip() or None
                range_str = self.range.component.value.strip()
                range_val = int(range_str) if range_str else None

                x_val, y_val = None, None
                coords_str = self.coordinates.component.value.strip()
                if coords_str:
                    coords = coords_str.split(",")
                    if len(coords) != 2:
                        raise ValueError("Coordinates must be in format X,Y (e.g. 100,200)")
                    x_val, y_val = int(coords[0].strip()), int(coords[1].strip())

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await UpdateBusinessCommand(UpdateBusinessCommandRequest(
                    guild=guild,
                    business_id=self.business_id,
                    name=name_val,
                    description=description_val,
                    x=x_val, y=y_val,
                    range=range_val
                )).execute()
                view = await DiscordAdminEmbed.UpdateBusinessLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class CreateItemModal(discord.ui.Modal, title="Create Shop Item"):
        catalogue_id = None
        name = None
        price = None
        stock = None
        business_id = None

        def __init__(self):
            super().__init__()

        @classmethod
        async def create(cls):
            modal = cls()
            await modal._build()
            return modal

        async def _build(self):
            self.catalogue_id = discord.ui.Label(
                text="Catalogue ID:",
                component=discord.ui.TextInput(placeholder="e.g. 3", required=True)
            )
            self.add_item(self.catalogue_id)

            self.name = discord.ui.Label(
                text="Name:",
                component=discord.ui.TextInput(placeholder="Display name in shop", required=True, max_length=100)
            )
            self.add_item(self.name)

            self.price = discord.ui.Label(
                text="Price:",
                component=discord.ui.TextInput(placeholder="e.g. 1000", required=True)
            )
            self.add_item(self.price)

            self.stock = discord.ui.Label(
                text="Stock (blank = unlimited):",
                component=discord.ui.TextInput(placeholder="e.g. 50", required=False)
            )
            self.add_item(self.stock)

            self.business_id = discord.ui.Label(
                text="Business ID (blank = any location):",
                component=discord.ui.TextInput(placeholder="e.g. 2", required=False)
            )
            self.add_item(self.business_id)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                catalogue_id_val = int(self.catalogue_id.component.value.strip())
                price_val = int(self.price.component.value.strip())
                stock_str = self.stock.component.value.strip()
                stock_val = int(stock_str) if stock_str else None
                biz_str = self.business_id.component.value.strip()
                business_id_val = int(biz_str) if biz_str else None

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await CreateItemCommand(CreateItemCommandRequest(
                    guild=guild,
                    catalogue_id=catalogue_id_val,
                    name=self.name.component.value,
                    price=price_val,
                    description='',
                    icon='',
                    stock=stock_val,
                    business_id=business_id_val,
                    sellable=True
                )).execute()
                view = await DiscordAdminEmbed.CreateItemLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class EditItemModal(discord.ui.Modal, title="Edit Shop Item"):
        name = None
        price = None
        stock = None
        description = None
        sellable = None

        def __init__(self, item_id: int):
            self.item_id = item_id
            super().__init__()

        @classmethod
        async def create(cls, item_id: int):
            modal = cls(item_id)
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Name (blank = no change):",
                component=discord.ui.TextInput(placeholder="New display name", required=False, max_length=100)
            )
            self.add_item(self.name)

            self.price = discord.ui.Label(
                text="Price (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 1500", required=False)
            )
            self.add_item(self.price)

            self.stock = discord.ui.Label(
                text="Stock (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 20", required=False)
            )
            self.add_item(self.stock)

            self.description = discord.ui.Label(
                text="Description (blank = no change):",
                component=discord.ui.TextInput(
                    placeholder="Item description...",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=500
                )
            )
            self.add_item(self.description)

            self.sellable = discord.ui.Label(
                text="Sellable:",
                component=discord.ui.Select(
                    placeholder="Keep current setting",
                    options=[
                        discord.SelectOption(label="No change", value=""),
                        discord.SelectOption(label="Yes", value="True"),
                        discord.SelectOption(label="No", value="False"),
                    ],
                    required=False
                )
            )
            self.add_item(self.sellable)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                name_val = self.name.component.value.strip() or None
                price_str = self.price.component.value.strip()
                price_val = int(price_str) if price_str else None
                stock_str = self.stock.component.value.strip()
                stock_val = int(stock_str) if stock_str else None
                description_val = self.description.component.value.strip() or None
                sellable_raw = self.sellable.component.values[0] if self.sellable.component.values else ""
                if sellable_raw == "True":
                    sellable_val = True
                elif sellable_raw == "False":
                    sellable_val = False
                else:
                    sellable_val = None

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await UpdateItemCommand(UpdateItemCommandRequest(
                    guild=guild,
                    item_id=self.item_id,
                    name=name_val,
                    price=price_val,
                    description=description_val,
                    icon=None,
                    stock=stock_val,
                    business_id=None,
                    sellable=sellable_val
                )).execute()
                view = await DiscordAdminEmbed.UpdateItemLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class CreateBankModal(discord.ui.Modal, title="Create Bank"):
        name = None
        interest_rate = None
        coordinates = None
        range = None
        max_accounts = None

        def __init__(self):
            super().__init__()

        @classmethod
        async def create(cls):
            modal = cls()
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Name:",
                component=discord.ui.TextInput(placeholder="e.g. Central Bank", required=True, max_length=100)
            )
            self.add_item(self.name)

            self.interest_rate = discord.ui.Label(
                text="Interest Rate (e.g. 0.02 for 2%):",
                component=discord.ui.TextInput(placeholder="0.02", required=True)
            )
            self.add_item(self.interest_rate)

            self.coordinates = discord.ui.Label(
                text="Coordinates (X,Y):",
                component=discord.ui.TextInput(placeholder="e.g. 0,0", required=True)
            )
            self.add_item(self.coordinates)

            self.range = discord.ui.Label(
                text="Range (blank = unlimited):",
                component=discord.ui.TextInput(placeholder="e.g. 300", required=False)
            )
            self.add_item(self.range)

            self.max_accounts = discord.ui.Label(
                text="Max Accounts (blank = unlimited):",
                component=discord.ui.TextInput(placeholder="e.g. 100", required=False)
            )
            self.add_item(self.max_accounts)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                interest_rate_val = float(self.interest_rate.component.value.strip())
                coords = self.coordinates.component.value.strip().split(",")
                if len(coords) != 2:
                    raise ValueError("Coordinates must be in format X,Y (e.g. 0,0)")
                x, y = int(coords[0].strip()), int(coords[1].strip())
                range_str = self.range.component.value.strip()
                range_val = int(range_str) if range_str else None
                max_str = self.max_accounts.component.value.strip()
                max_accounts_val = int(max_str) if max_str else None

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await CreateBankCommand(CreateBankCommandRequest(
                    guild=guild,
                    name=self.name.component.value,
                    interest_rate=interest_rate_val,
                    x=x, y=y,
                    range=range_val,
                    max_accounts=max_accounts_val
                )).execute()
                view = await DiscordAdminEmbed.CreateBankLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class EditBankModal(discord.ui.Modal, title="Edit Bank"):
        name = None
        interest_rate = None
        coordinates = None
        range = None

        def __init__(self, bank_id: int):
            self.bank_id = bank_id
            super().__init__()

        @classmethod
        async def create(cls, bank_id: int):
            modal = cls(bank_id)
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Name (blank = no change):",
                component=discord.ui.TextInput(placeholder="New bank name", required=False, max_length=100)
            )
            self.add_item(self.name)

            self.interest_rate = discord.ui.Label(
                text="Interest Rate (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 0.03", required=False)
            )
            self.add_item(self.interest_rate)

            self.coordinates = discord.ui.Label(
                text="Coordinates X,Y (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 100,200", required=False)
            )
            self.add_item(self.coordinates)

            self.range = discord.ui.Label(
                text="Range (blank = no change):",
                component=discord.ui.TextInput(placeholder="e.g. 300", required=False)
            )
            self.add_item(self.range)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                name_val = self.name.component.value.strip() or None
                rate_str = self.interest_rate.component.value.strip()
                rate_val = float(rate_str) if rate_str else None
                range_str = self.range.component.value.strip()
                range_val = int(range_str) if range_str else None

                x_val, y_val = None, None
                coords_str = self.coordinates.component.value.strip()
                if coords_str:
                    coords = coords_str.split(",")
                    if len(coords) != 2:
                        raise ValueError("Coordinates must be in format X,Y")
                    x_val, y_val = int(coords[0].strip()), int(coords[1].strip())

                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                response = await UpdateBankCommand(UpdateBankCommandRequest(
                    guild=guild,
                    bank_id=self.bank_id,
                    name=name_val,
                    interest_rate=rate_val,
                    x=x_val, y=y_val,
                    range=range_val
                )).execute()
                view = await DiscordAdminEmbed.UpdateBankLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    # =========================================================================
    # LayoutViews
    # =========================================================================

    class SetupServerLayoutView(discord.ui.LayoutView):
        def __init__(self, response: SetupServerCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: SetupServerCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            if self.response.success:
                content = f"{self.user_mention}, server initialized successfully."
                color = discord.Color.green()
            else:
                content = "Server has already been set up."
                color = discord.Color.orange()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💿 Server Setup"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=content),
                    accent_color=color,
                    spoiler=False
                )
            )


    class GetServerLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetServerQueryResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetServerQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            server = self.response.server_config.server
            lines = [
                f"**Server ID:** {server.server_id}",
                f"**Server Name:** {server.name}",
            ]
            currency = await self.response.server_config.get_default_currency()
            if currency:
                symbol = await self.response.server_config.get_default_currency_symbol()
                lines.append(f"**Default Currency:** {currency.name} ({symbol})")
            bank = await self.response.server_config.get_default_bank()
            if bank:
                lines.append(f"**Default Bank:** {bank.name}")
            faction = await self.response.server_config.get_default_faction()
            if faction:
                lines.append(f"**Default Faction:** {faction.name}")
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## Server Configuration"),
                    discord.ui.Separator(),
                    *[discord.ui.TextDisplay(content=l) for l in lines],
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class SetCurrencySymbolLayoutView(discord.ui.LayoutView):
        def __init__(self, response: SetCurrencySymbolCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: SetCurrencySymbolCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            symbol = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💱 Currency Symbol Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"{self.user_mention}, set the currency symbol to **{symbol}**."),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class AddBalanceLayoutView(discord.ui.LayoutView):
        def __init__(self, response: AddBalanceCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: AddBalanceCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💳 Balance Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(
                        content=f"{self.user_mention} added **{currency}{Helpers.format_cash_amount(self.response.amount)}** "
                                f"to **{self.response.player.player.name}**'s {self.response.account_type} balance."
                    ),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class SetBalanceLayoutView(discord.ui.LayoutView):
        def __init__(self, response: SetBalanceCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: SetBalanceCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💳 Balance Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(
                        content=f"{self.user_mention} set **{self.response.player.player.name}**'s "
                                f"{self.response.account_type} balance to **{currency}{Helpers.format_cash_amount(self.response.amount)}**."
                    ),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class CreateBusinessLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CreateBusinessCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CreateBusinessCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            b = self.response.business
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏢 Business Created"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{b.name}** (ID: {b.business_id})"),
                    discord.ui.TextDisplay(content=f"**Type:** {b.type}"),
                    discord.ui.TextDisplay(content=f"**Location:** ({b.x}, {b.y})"),
                    discord.ui.TextDisplay(content=f"**Range:** {b.range if b.range else 'Unlimited'}"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class UpdateBusinessLayoutView(discord.ui.LayoutView):
        def __init__(self, response: UpdateBusinessCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: UpdateBusinessCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            b = self.response.business
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏢 Business Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{b.name}** has been updated."),
                    discord.ui.TextDisplay(content=f"**Location:** ({b.x}, {b.y})"),
                    discord.ui.TextDisplay(content=f"**Range:** {b.range if b.range else 'Unlimited'}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class CreateItemLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CreateItemCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CreateItemCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            item = self.response.item
            currency = await self.response.server_config.get_default_currency_symbol()
            lines = [
                f"**{item.name}** (ID: {item.item_id})",
                f"**Price:** {currency}{Helpers.format_cash_amount(item.price)}",
                f"**Catalogue ID:** {item.catalogue_id}",
            ]
            if item.business_id:
                lines.append(f"**Business ID:** {item.business_id}")
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🛒 Shop Item Created"),
                    discord.ui.Separator(),
                    *[discord.ui.TextDisplay(content=l) for l in lines],
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class UpdateItemLayoutView(discord.ui.LayoutView):
        def __init__(self, response: UpdateItemCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: UpdateItemCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            item = self.response.item
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🛒 Shop Item Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{item.name}** has been updated."),
                    discord.ui.TextDisplay(content=f"**Price:** {currency}{Helpers.format_cash_amount(item.price)}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class CreateBankLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CreateBankCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CreateBankCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            bank = self.response.bank
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏦 Bank Created"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{bank.name}** (ID: {bank.bank_id})"),
                    discord.ui.TextDisplay(content=f"**Interest Rate:** {bank.interest_rate * 100:.1f}%"),
                    discord.ui.TextDisplay(content=f"**Location:** ({bank.x}, {bank.y})"),
                    discord.ui.TextDisplay(content=f"**Range:** {bank.range if bank.range else 'Unlimited'}"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class UpdateBankLayoutView(discord.ui.LayoutView):
        def __init__(self, response: UpdateBankCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: UpdateBankCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            bank = self.response.bank
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏦 Bank Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{bank.name}** has been updated."),
                    discord.ui.TextDisplay(content=f"**Interest Rate:** {bank.interest_rate * 100:.1f}%"),
                    discord.ui.TextDisplay(content=f"**Location:** ({bank.x}, {bank.y})"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class CreateBusinessStockLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CreateBusinessStockCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CreateBusinessStockCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            stock = self.response.stock
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📈 Stock Listing Enabled"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Business ID:** {stock.business_id}"),
                    discord.ui.TextDisplay(content=f"**Base Price:** {stock.base_price}"),
                    discord.ui.TextDisplay(content=f"**Current Price:** {stock.current_price}"),
                    discord.ui.TextDisplay(content=f"**Dividend Rate:** {stock.dividend_rate * 100:.1f}%"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class SetExchangeRateLayoutView(discord.ui.LayoutView):
        def __init__(self, response: SetExchangeRateCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: SetExchangeRateCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            rate = self.response.exchange_rate
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💱 Exchange Rate Set"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**From Currency ID:** {rate.from_currency_id}"),
                    discord.ui.TextDisplay(content=f"**To Currency ID:** {rate.to_currency_id}"),
                    discord.ui.TextDisplay(content=f"**Rate:** {rate.rate:.4f}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class SetServerSettingLayoutView(discord.ui.LayoutView):
        def __init__(self, response: SetServerSettingCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: SetServerSettingCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            setting = self.response.setting
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## ⚙️ Setting Updated"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{setting.key}** = `{setting.value}`"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    # =========================================================================
    # Resource node views
    # =========================================================================

    class ResourceNodeLayoutView(discord.ui.LayoutView):
        def __init__(self, node=None):
            self.node = node
            super().__init__()

        @classmethod
        async def create(cls, node):
            view = cls(node)
            await view._build()
            return view

        async def _build(self):
            status = "🔍 Discoverable" if not self.node.discovered else "✅ Available"
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🪨 Resource Node"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Node ID:** {self.node.node_id}"),
                    discord.ui.TextDisplay(content=f"**Location ID:** {self.node.location_id}"),
                    discord.ui.TextDisplay(content=f"**Resource:** {self.node.resource_type}"),
                    discord.ui.TextDisplay(content=f"**Max Quantity:** {self.node.max_quantity}"),
                    discord.ui.TextDisplay(content=f"**Regen Rate:** {self.node.regen_rate}/tick"),
                    discord.ui.TextDisplay(content=f"**Status:** {status}"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )

    class ResourceNodeDeleteLayoutView(discord.ui.LayoutView):
        def __init__(self, node_id=None):
            self.node_id = node_id
            super().__init__()

        @classmethod
        async def create(cls, node_id):
            view = cls(node_id)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🗑️ Resource Node Deleted"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Node ID {self.node_id}** has been removed."),
                    accent_color=discord.Color.red(),
                    spoiler=False
                )
            )

    # =========================================================================
    # Recipe views
    # =========================================================================

    class RecipeLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe=None):
            self.recipe = recipe
            super().__init__()

        @classmethod
        async def create(cls, recipe):
            view = cls(recipe)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📋 Recipe"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Recipe ID:** {self.recipe.recipe_id}"),
                    discord.ui.TextDisplay(content=f"**Server ID:** {self.recipe.server_id}"),
                    discord.ui.TextDisplay(content=f"**Name:** {self.recipe.name}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )

    class RecipeDeleteLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe_id=None):
            self.recipe_id = recipe_id
            super().__init__()

        @classmethod
        async def create(cls, recipe_id):
            view = cls(recipe_id)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🗑️ Recipe Deleted"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Recipe ID {self.recipe_id}** and all its inputs/outputs have been removed."),
                    accent_color=discord.Color.red(),
                    spoiler=False
                )
            )

    class RecipeInputLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe_input=None):
            self.recipe_input = recipe_input
            super().__init__()

        @classmethod
        async def create(cls, recipe_input):
            view = cls(recipe_input)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🧪 Recipe Input"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Recipe ID:** {self.recipe_input.recipe_id}"),
                    discord.ui.TextDisplay(content=f"**Catalogue ID:** {self.recipe_input.catalogue_id}"),
                    discord.ui.TextDisplay(content=f"**Quantity:** {self.recipe_input.quantity}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )

    class RecipeInputDeleteLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe_id=None, catalogue_id=None):
            self.recipe_id = recipe_id
            self.catalogue_id = catalogue_id
            super().__init__()

        @classmethod
        async def create(cls, recipe_id, catalogue_id):
            view = cls(recipe_id, catalogue_id)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🗑️ Recipe Input Removed"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"Catalogue ID **{self.catalogue_id}** removed from recipe **{self.recipe_id}**."),
                    accent_color=discord.Color.red(),
                    spoiler=False
                )
            )

    class RecipeOutputLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe_output=None):
            self.recipe_output = recipe_output
            super().__init__()

        @classmethod
        async def create(cls, recipe_output):
            view = cls(recipe_output)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📦 Recipe Output"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Recipe ID:** {self.recipe_output.recipe_id}"),
                    discord.ui.TextDisplay(content=f"**Catalogue ID:** {self.recipe_output.catalogue_id}"),
                    discord.ui.TextDisplay(content=f"**Quantity:** {self.recipe_output.quantity}"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )

    class RecipeOutputDeleteLayoutView(discord.ui.LayoutView):
        def __init__(self, recipe_id=None, catalogue_id=None):
            self.recipe_id = recipe_id
            self.catalogue_id = catalogue_id
            super().__init__()

        @classmethod
        async def create(cls, recipe_id, catalogue_id):
            view = cls(recipe_id, catalogue_id)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🗑️ Recipe Output Removed"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"Catalogue ID **{self.catalogue_id}** removed from recipe **{self.recipe_id}**."),
                    accent_color=discord.Color.red(),
                    spoiler=False
                )
            )

    # =========================================================================
    # Location policy views
    # =========================================================================

    class LocationPolicyLayoutView(discord.ui.LayoutView):
        def __init__(self, policy=None):
            self.policy = policy
            super().__init__()

        @classmethod
        async def create(cls, policy):
            view = cls(policy)
            await view._build()
            return view

        async def _build(self):
            p = self.policy
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📜 Location Policy"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Location ID:** {p.location_id}"),
                    discord.ui.TextDisplay(content=f"**Tax Rate:** {p.tax_rate:.1%}"),
                    discord.ui.TextDisplay(content=f"**Trade Tariff:** {p.trade_tariff:.1%}"),
                    discord.ui.TextDisplay(content=f"**Imports:** {'🔒 Restricted' if p.import_restricted else '✅ Open'}"),
                    discord.ui.TextDisplay(content=f"**Exports:** {'🔒 Restricted' if p.export_restricted else '✅ Open'}"),
                    discord.ui.TextDisplay(content=f"**Interest Rate Modifier:** ×{p.interest_rate_modifier:.2f}"),
                    discord.ui.TextDisplay(content=f"**Smuggling Risk Modifier:** ×{p.smuggling_risk_modifier:.2f}"),
                    accent_color=discord.Color.gold(),
                    spoiler=False
                )
            )

    class LocationPolicyDeleteLayoutView(discord.ui.LayoutView):
        def __init__(self, location_id=None):
            self.location_id = location_id
            super().__init__()

        @classmethod
        async def create(cls, location_id):
            view = cls(location_id)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🗑️ Location Policy Removed"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"Policy for **Location ID {self.location_id}** has been removed."),
                    accent_color=discord.Color.red(),
                    spoiler=False
                )
            )

    # =========================================================================
    # Factory methods
    # =========================================================================

    @staticmethod
    async def get_create_business_modal(interaction: Interaction):
        return await DiscordAdminEmbed.CreateBusinessModal.create()

    @staticmethod
    async def get_edit_business_modal(interaction: Interaction, business_id: int):
        return await DiscordAdminEmbed.EditBusinessModal.create(business_id)

    @staticmethod
    async def get_create_item_modal(interaction: Interaction):
        return await DiscordAdminEmbed.CreateItemModal.create()

    @staticmethod
    async def get_edit_item_modal(interaction: Interaction, item_id: int):
        return await DiscordAdminEmbed.EditItemModal.create(item_id)

    @staticmethod
    async def get_create_bank_modal(interaction: Interaction):
        return await DiscordAdminEmbed.CreateBankModal.create()

    @staticmethod
    async def get_edit_bank_modal(interaction: Interaction, bank_id: int):
        return await DiscordAdminEmbed.EditBankModal.create(bank_id)

    @staticmethod
    async def get_setup_server_view(interaction: Interaction, response: SetupServerCommandResponse):
        return await DiscordAdminEmbed.SetupServerLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_server_view(interaction: Interaction, response: GetServerQueryResponse):
        return await DiscordAdminEmbed.GetServerLayoutView.create(response)

    @staticmethod
    async def get_set_currency_symbol_view(interaction: Interaction, response: SetCurrencySymbolCommandResponse):
        return await DiscordAdminEmbed.SetCurrencySymbolLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_add_balance_view(interaction: Interaction, response: AddBalanceCommandResponse):
        return await DiscordAdminEmbed.AddBalanceLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_set_balance_view(interaction: Interaction, response: SetBalanceCommandResponse):
        return await DiscordAdminEmbed.SetBalanceLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_create_business_stock_view(interaction: Interaction, response: CreateBusinessStockCommandResponse):
        return await DiscordAdminEmbed.CreateBusinessStockLayoutView.create(response)

    @staticmethod
    async def get_set_exchange_rate_view(interaction: Interaction, response: SetExchangeRateCommandResponse):
        return await DiscordAdminEmbed.SetExchangeRateLayoutView.create(response)

    @staticmethod
    async def get_set_server_setting_view(interaction: Interaction, response: SetServerSettingCommandResponse):
        return await DiscordAdminEmbed.SetServerSettingLayoutView.create(response)

    @staticmethod
    async def get_resource_node_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.ResourceNodeLayoutView.create(response.node)

    @staticmethod
    async def get_resource_node_delete_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.ResourceNodeDeleteLayoutView.create(response.node_id)

    @staticmethod
    async def get_recipe_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeLayoutView.create(response.recipe)

    @staticmethod
    async def get_recipe_delete_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeDeleteLayoutView.create(response.recipe_id)

    @staticmethod
    async def get_recipe_input_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeInputLayoutView.create(response.recipe_input)

    @staticmethod
    async def get_recipe_input_delete_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeInputDeleteLayoutView.create(response.recipe_id, response.catalogue_id)

    @staticmethod
    async def get_recipe_output_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeOutputLayoutView.create(response.recipe_output)

    @staticmethod
    async def get_recipe_output_delete_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.RecipeOutputDeleteLayoutView.create(response.recipe_id, response.catalogue_id)

    @staticmethod
    async def get_location_policy_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.LocationPolicyLayoutView.create(response.policy)

    @staticmethod
    async def get_location_policy_delete_view(interaction: Interaction, response):
        return await DiscordAdminEmbed.LocationPolicyDeleteLayoutView.create(response.location_id)
