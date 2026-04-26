import discord

from domain import Catalogue
from application import DiscordGuild, DiscordUser
from application import (
    BuyItemCommand,
    BuyItemCommandRequest,
    GetShopQueryResponse,
    GetCatalogueQueryResponse
)
import json

class DiscordShopEmbed:

    class GetShopLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetShopQueryResponse|None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetShopQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()

            shop_item_components = []
            for item in self.response.shop_items:
                if len(shop_item_components) > 0:
                    shop_item_components.append(discord.ui.Separator())

                components = []
                item_icon = item.icon + " " if item.icon else ""
                item_name = item.name if item.name else "Unnamed Item"
                components.append(discord.ui.TextDisplay(content=f"**{item_icon}{item_name}**"))
                if item.description:
                    components.append(discord.ui.TextDisplay(content=f"-# {item.description}"))
                
                disabled = (item.stock == 0) or (item.price > self.response.player.balances.total_balance())
                button = discord.ui.Button(
                    custom_id=f"{item.item_id}", 
                    label=f"{item.price}", 
                    emoji=f"{currency}", 
                    disabled=disabled, 
                    style=discord.ButtonStyle.success if not disabled else discord.ButtonStyle.secondary
                )

                async def callback(interaction: discord.Interaction, item=item):
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
                    
                        request=BuyItemCommandRequest(
                            guild=guild,
                            user=user,
                            item_id=item.item_id,
                            item_name=None
                        )

                        response = await BuyItemCommand(request).execute()

                        await interaction.response.send_message(f"You bought {response.shop_item.name}", ephemeral=True)
                    except Exception as e:
                        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


                button.callback = callback

                label = discord.ui.Section(
                    *components,
                    accessory=button
                )

                shop_item_components.append(label)

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## Store"),
                    discord.ui.TextDisplay(content="Click a button below to instantly buy an item, or use the /item buy command.\nFor more details before purchasing, use the /item info command."),
                    discord.ui.Separator(),
                    *shop_item_components,
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"-# Page {self.response.page}/{self.response.max_pages}"),
                    accent_color=discord.Color.light_grey(),
                    spoiler=False
                )
            )

    @staticmethod
    async def get_shop_view(interaction: discord.Interaction, response: GetShopQueryResponse):
        view = DiscordShopEmbed.GetShopLayoutView()
        view = await view.create(response=response)
        return view
    

    class GetCatalogueLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetCatalogueQueryResponse|None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetCatalogueQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            slots_subtitle = None
            keywords_explanation_components = []
            related_items_components = []
            if self.response.keywords:
                keywords_explanation_components.append(discord.ui.Separator())
                for keyword in self.response.keywords:
                    keywords_explanation_components.append(discord.ui.TextDisplay(content=f"-# **{keyword.name}:** {keyword.description}"))
            
            if not self.response.catalogue_item.type == "Race":
                slots_subtitle = None
            else:
                race_metadata = None

                if isinstance(self.response.catalogue_item.metadata, str):
                    race_metadata = json.loads(self.response.catalogue_item.metadata)
                elif isinstance(self.response.catalogue_item.metadata, dict):
                    race_metadata = self.response.catalogue_item.metadata

                if isinstance(race_metadata, dict):
                    available_slots = race_metadata.get("slots", {})

                    if isinstance(available_slots, dict):
                        # Use keys explicitly
                        slots = "*] [*".join(available_slots.keys()) if available_slots else ""
                        slots_subtitle=f"\n-# [*{slots}*]"


            if self.response.related_items:
                related_items_components.append(discord.ui.Separator())
                related_items_components.append(discord.ui.TextDisplay(content=f"## Related Items"))
                related_slots_subtitle = None
                for item in self.response.related_items:
                    if not item.type == "Race":
                        related_slots_subtitle = None
                    else:
                        race_metadata = None

                        if isinstance(item.metadata, str):
                            race_metadata = json.loads(item.metadata)
                        elif isinstance(item.metadata, dict):
                            race_metadata = item.metadata

                        if isinstance(race_metadata, dict):
                            available_slots = race_metadata.get("slots", {})

                            if isinstance(available_slots, dict):
                                # Use keys explicitly
                                slots = "*] [*".join(available_slots.keys()) if available_slots else ""
                                related_slots_subtitle=f"\n-# [*{slots}*]"

                    related_items_components.append(discord.ui.TextDisplay(content=f"### {item.type} - {item.name}{related_slots_subtitle if related_slots_subtitle else ""}"))
                    related_items_components.append(discord.ui.TextDisplay(content=f"{item.description}"))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## Catalogue"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"# {self.response.catalogue_item.type} - {self.response.catalogue_item.name}{slots_subtitle if slots_subtitle else ""}"),
                    discord.ui.TextDisplay(content=f"{self.response.catalogue_item.description}"),
                    discord.ui.Separator(),
                    *self._get_stat_block(self.response.catalogue_item, self.response.related_items),
                    *related_items_components,
                    *keywords_explanation_components,
                    accent_color=discord.Color.light_grey(),
                    spoiler=False
                )
            )
        
        def _get_stat_block(self, item: Catalogue, related_items: list[Catalogue]):
            stats = {}
            metadata = json.loads(item.metadata)
            item_stats = metadata.get("stats", {})
            if item_stats and isinstance(item_stats, dict):
                stats.update(item_stats)
            else:
                # Order related_items by type so that Race base stats are overridden by Weapon and Armor stats
                priority = {"Race": 0, "Weapon": 1, "Armor": 2}
                related_items = sorted(related_items, key=lambda x: priority.get(x.type, 99))
                for related_item in related_items:
                    related_metadata = json.loads(related_item.metadata)
                    related_item_stats = related_metadata.get("stats", {})
                    if isinstance(related_item_stats, dict):
                        stats.update(related_item_stats)


            has_weapon = any(item.type == "Weapon" for item in related_items + [item])
            has_armor = any(item.type == "Armor" for item in related_items + [item])

            weapon_label = "Weapon" if has_weapon else "Unarmed"
            armor_label = "Armor" if has_armor else "Unarmored"
            categories = {
                "Stats": ["WS", "BS", "T", "W"],
                weapon_label: ["Attacks", "S", "AP", "D", "Range"],
                armor_label: ["Sv"]
            }
            stat_blocks = {}
            for category, keys in categories.items():
                header_row = []
                separator_row = []
                stat_row = []
                for key in keys:
                    if key in stats:
                        value = stats[key]
                        width = max(len(key), len(str(value)))

                        header_row.append(f"{key:^{width}}")
                        stat_row.append(f"{value:^{width}}")
                        separator_row.append("━" * width)

                if not header_row:
                    continue

                stat_blocks[category] = (
                    "```\n"
                    "┃ " + " ┃ ".join(header_row) + " ┃\n"
                    "┣━" + "━╋━".join(separator_row) + "━┫\n"
                    "┃ " + " ┃ ".join(stat_row) + " ┃\n```"
                )

            result = []
            for category, block in stat_blocks.items():
                result.append(discord.ui.TextDisplay(content=f"### {category}\n{block}"))
            return result

    @staticmethod
    async def get_catalogue_block_embed(interaction: discord.Interaction, response: GetCatalogueQueryResponse):
        view = DiscordShopEmbed.GetCatalogueLayoutView()
        view = await view.create(response=response)
        return view