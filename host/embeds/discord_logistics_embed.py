import discord
from discord import Interaction

from application import (
    AssignGarrisonCommandResponse,
    GetGarrisonQueryResponse,
    PayMaintenanceCommandResponse,
    StartTransportCommandResponse,
    CompleteTransportCommandResponse,
)
from application.services.helpers import Helpers


class DiscordLogisticsEmbed:

    class GarrisonAssignLayoutView(discord.ui.LayoutView):
        def __init__(self, response: AssignGarrisonCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: AssignGarrisonCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏰 Unit Garrisoned"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Unit:** {self.response.unit.name}"),
                    discord.ui.TextDisplay(content=f"**Location:** {self.response.poi.name}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class GarrisonViewLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetGarrisonQueryResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetGarrisonQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            if not self.response.garrisons:
                self.add_item(
                    discord.ui.Container(
                        discord.ui.TextDisplay(content="## 🏰 Your Garrisons"),
                        discord.ui.Separator(),
                        discord.ui.TextDisplay(content="You have no units garrisoned anywhere."),
                        accent_color=discord.Color.blue(),
                        spoiler=False
                    )
                )
                return

            garrison_items = []
            for unit, garrison, poi in self.response.garrisons:
                if garrison_items:
                    garrison_items.append(discord.ui.Separator())
                garrison_items.append(discord.ui.TextDisplay(content=f"**{unit.name}**"))
                garrison_items.append(discord.ui.TextDisplay(
                    content=f"Location: **{poi.name}** | Qty: **{unit.quantity}**"
                ))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏰 Your Garrisons"),
                    discord.ui.Separator(),
                    *garrison_items,
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class MaintenancePayLayoutView(discord.ui.LayoutView):
        def __init__(self, response: PayMaintenanceCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: PayMaintenanceCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            items = [
                discord.ui.TextDisplay(content="## 🔧 Maintenance Paid"),
                discord.ui.Separator(),
                discord.ui.TextDisplay(content=f"**Total Cost:** {currency}{Helpers.format_cash_amount(self.response.total_cost)}"),
            ]
            if self.response.total_cost == 0:
                items.append(discord.ui.TextDisplay(content="-# No units require maintenance right now."))
            self.add_item(
                discord.ui.Container(
                    *items,
                    accent_color=discord.Color.orange(),
                    spoiler=False
                )
            )


    class TransportStartLayoutView(discord.ui.LayoutView):
        def __init__(self, response: StartTransportCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: StartTransportCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            transport = self.response.transport
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🚚 Transport Started"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Catalogue ID:** {transport.catalogue_id}"),
                    discord.ui.TextDisplay(content=f"**Quantity:** {transport.quantity}"),
                    discord.ui.TextDisplay(content=f"**Arrives At:** {transport.arrive_at}"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content="-# Use `/transport complete` when it arrives to collect your resources."),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class TransportCompleteLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CompleteTransportCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CompleteTransportCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            if not self.response.completed:
                self.add_item(
                    discord.ui.Container(
                        discord.ui.TextDisplay(content="## 🚚 Transports Collected"),
                        discord.ui.Separator(),
                        discord.ui.TextDisplay(content="No transports have arrived yet."),
                        accent_color=discord.Color.green(),
                        spoiler=False
                    )
                )
                return

            transport_items = []
            for transport in self.response.completed:
                if transport_items:
                    transport_items.append(discord.ui.Separator())
                transport_items.append(discord.ui.TextDisplay(content=f"**Catalogue ID {transport.catalogue_id}**"))
                transport_items.append(discord.ui.TextDisplay(
                    content=f"Qty: **{transport.quantity}** → Business ID {transport.to_business_id}"
                ))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🚚 Transports Collected"),
                    discord.ui.Separator(),
                    *transport_items,
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    @staticmethod
    async def get_garrison_assign_view(interaction: Interaction, response: AssignGarrisonCommandResponse):
        return await DiscordLogisticsEmbed.GarrisonAssignLayoutView.create(response)

    @staticmethod
    async def get_garrison_view(interaction: Interaction, response: GetGarrisonQueryResponse):
        return await DiscordLogisticsEmbed.GarrisonViewLayoutView.create(response)

    @staticmethod
    async def get_maintenance_pay_view(interaction: Interaction, response: PayMaintenanceCommandResponse):
        return await DiscordLogisticsEmbed.MaintenancePayLayoutView.create(response)

    @staticmethod
    async def get_transport_start_view(interaction: Interaction, response: StartTransportCommandResponse):
        return await DiscordLogisticsEmbed.TransportStartLayoutView.create(response)

    @staticmethod
    async def get_transport_complete_view(interaction: Interaction, response: CompleteTransportCommandResponse):
        return await DiscordLogisticsEmbed.TransportCompleteLayoutView.create(response)
