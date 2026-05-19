import discord
from discord import Interaction

from application import WorkCommandResponse
from application.services.helpers import Helpers


class DiscordWorkEmbed:

    class WorkLayoutView(discord.ui.LayoutView):
        def __init__(self, response: WorkCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: WorkCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            color = discord.Color.green() if self.response.action_success else discord.Color.red()

            business_name = self.response.business.name if self.response.business and self.response.business.name else "Unknown Business"
            action_name = self.response.action.name if self.response.action and self.response.action.name else "Unknown Action"
            outcome_msg = self.response.action.success_message if self.response.action_success else self.response.action.failure_message
            balance_msg = f"You were paid {currency}{self.response.wage}!" if self.response.action_success else f"You were fined {currency}{self.response.fine}!"

            extra_lines = []
            if self.response.discovered_node:
                node = self.response.discovered_node
                extra_lines.append(f"You discovered a **{node.resource_type}** node! ({node.quantity}/{node.max_quantity} remaining)")
            elif self.response.extracted_resource:
                inv = self.response.extracted_resource
                extra_lines.append(f"Extracted **1** catalogue item #{inv.catalogue_id} — business stock: {inv.quantity}")
            elif self.response.processed_output:
                recipe, outputs = self.response.processed_output
                produced = ", ".join(f"{o.quantity}× #{o.catalogue_id}" for o in outputs)
                extra_lines.append(f"Processed **{recipe.name}** — produced {produced}")
            elif self.response.hauled_transfer:
                catalogue_id, dest = self.response.hauled_transfer
                extra_lines.append(f"Hauled **1** catalogue item #{catalogue_id} to {dest.name}")
            elif self.response.restocked_item:
                _, item = self.response.restocked_item
                extra_lines.append(f"Restocked **{item.name}** — shop stock now {item.stock}")

            items = [
                discord.ui.TextDisplay(content=f"### {self.response.player.player.name}"),
                discord.ui.TextDisplay(content=f"**{business_name} — {action_name}**"),
                discord.ui.Separator(),
                discord.ui.TextDisplay(content=outcome_msg),
                discord.ui.TextDisplay(content=balance_msg),
            ]
            for line in extra_lines:
                items.append(discord.ui.TextDisplay(content=line))
            items.append(discord.ui.Separator())
            items.append(discord.ui.TextDisplay(content=f"-# Cooldown: {Helpers.format_countdown(self.response.action.cooldown_seconds)}"))

            self.add_item(discord.ui.Container(*items, accent_color=color, spoiler=False))


    @staticmethod
    async def get_work_view(interaction: Interaction, response: WorkCommandResponse):
        return await DiscordWorkEmbed.WorkLayoutView.create(response)

    @staticmethod
    async def get_crime_view(interaction: Interaction, response: WorkCommandResponse):
        return await DiscordWorkEmbed.WorkLayoutView.create(response)
