import discord
from discord import Interaction

from application import DiscordGuild, DiscordUser
from application import (
    CreateFactionCommand, CreateFactionCommandRequest,
    CreateFactionCommandResponse,
    JoinFactionCommandResponse,
    LeaveFactionCommandResponse,
    GetFactionQueryResponse,
)


class DiscordFactionEmbed:

    class CreateFactionModal(discord.ui.Modal, title="Create Faction"):
        name = None
        description = None
        color = None

        def __init__(self):
            super().__init__()

        @classmethod
        async def create(cls):
            modal = cls()
            await modal._build()
            return modal

        async def _build(self):
            self.name = discord.ui.Label(
                text="Faction Name:",
                component=discord.ui.TextInput(
                    placeholder="e.g. Clan Wren",
                    required=True,
                    max_length=100
                )
            )
            self.add_item(self.name)

            self.description = discord.ui.Label(
                text="Description:",
                component=discord.ui.TextInput(
                    placeholder="A brief description of your faction...",
                    style=discord.TextStyle.paragraph,
                    required=False,
                    max_length=1000
                )
            )
            self.add_item(self.description)

            self.color = discord.ui.Label(
                text="Color (hex, e.g. #FF6600):",
                component=discord.ui.TextInput(
                    placeholder="#FFFFFF",
                    required=False,
                    max_length=7
                )
            )
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                guild = DiscordGuild(guild_id=interaction.guild_id, name=interaction.guild.name)
                user = DiscordUser(
                    user_id=interaction.user.id,
                    name=interaction.user.name,
                    display_avatar=str(interaction.user.display_avatar)
                )
                response = await CreateFactionCommand(CreateFactionCommandRequest(
                    guild=guild,
                    user=user,
                    name=self.name.component.value,
                    description=self.description.component.value or '',
                    color=self.color.component.value or '#FFFFFF'
                )).execute()
                view = await DiscordFactionEmbed.CreateFactionLayoutView.create(response)
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


    class CreateFactionLayoutView(discord.ui.LayoutView):
        def __init__(self, response: CreateFactionCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: CreateFactionCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            faction = self.response.faction
            hex_color = faction.color if faction.color else None
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## ⚔️ Faction Created"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**{faction.name}**"),
                    discord.ui.TextDisplay(content=faction.description or "No description."),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"-# You are now the owner of {faction.name}."),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.default(),
                    spoiler=False
                )
            )


    class JoinFactionLayoutView(discord.ui.LayoutView):
        def __init__(self, response: JoinFactionCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: JoinFactionCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## ⚔️ Joined Faction"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"{self.user_mention} has joined **{self.response.faction.name}**!"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class LeaveFactionLayoutView(discord.ui.LayoutView):
        def __init__(self, response: LeaveFactionCommandResponse | None = None, user_mention: str = ""):
            self.response = response
            self.user_mention = user_mention
            super().__init__()

        @classmethod
        async def create(cls, response: LeaveFactionCommandResponse, user_mention: str):
            view = cls(response, user_mention)
            await view._build()
            return view

        async def _build(self):
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## ⚔️ Left Faction"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"{self.user_mention} has left their faction."),
                    accent_color=discord.Color.orange(),
                    spoiler=False
                )
            )


    class FactionInfoLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetFactionQueryResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetFactionQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            faction = self.response.faction
            if not faction:
                self.add_item(
                    discord.ui.Container(
                        discord.ui.TextDisplay(content="## ⚔️ Faction Not Found"),
                        discord.ui.TextDisplay(content="No faction found."),
                        accent_color=discord.Color.red(),
                        spoiler=False
                    )
                )
                return

            hex_color = faction.color if faction.color else None
            member_lines = []
            if self.response.members:
                for member, player in self.response.members:
                    role_tag = " 👑" if member.role in ("owner", "Leader") else ""
                    member_lines.append(f"**{player.name}**{role_tag} — {member.role}")

            members_text = "\n".join(member_lines) if member_lines else "No members."

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"## ⚔️ {faction.name}"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=faction.description or "No description."),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"### Members ({len(member_lines)})\n{members_text}"),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.default(),
                    spoiler=False
                )
            )


    @staticmethod
    async def get_create_faction_modal(interaction: discord.Interaction):
        return await DiscordFactionEmbed.CreateFactionModal.create()

    @staticmethod
    async def get_join_faction_view(interaction: discord.Interaction, response: JoinFactionCommandResponse):
        return await DiscordFactionEmbed.JoinFactionLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_leave_faction_view(interaction: discord.Interaction, response: LeaveFactionCommandResponse):
        return await DiscordFactionEmbed.LeaveFactionLayoutView.create(response, interaction.user.mention)

    @staticmethod
    async def get_faction_info_view(interaction: discord.Interaction, response: GetFactionQueryResponse):
        return await DiscordFactionEmbed.FactionInfoLayoutView.create(response)
