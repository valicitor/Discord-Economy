import discord

from application import (
    DiscordUser,
    GetServerQuery, GetServerQueryRequest,
    SetupPlayerCommand, SetupPlayerCommandRequest,
    GetPlayerQueryResponse
)
from infrastructure import (
    ServerRepository,
    CatalogueRepository,
    PointOfInterestRepository,
    LocationRepository
)

class DiscordPlayerEmbed:

    class NewPlayerRegistrationModal(discord.ui.Modal, title="New Player Registration"):
        name = None
        race = None
        backstory = None
        location = None

        def __init__(self, discord_guild_id: int|None = None):
            self.discord_guild_id = discord_guild_id
            super().__init__()

        async def on_submit(self, interaction: discord.Interaction):
            try:
                self.discord_guild_id
                request = GetServerQueryRequest(discord_guild_id=self.discord_guild_id)
                response = await GetServerQuery(request).execute()

                location_repo = await LocationRepository().get_instance()
                location_rec = await location_repo.get_by_name(self.location.component.values[0], response.server_config.server.server_id)

                request = SetupPlayerCommandRequest(
                    server_config=response.server_config,
                    discord_user=DiscordUser(
                        user_id=interaction.user.id,
                        name=interaction.user.name,
                        display_avatar=str(interaction.user.display_avatar)
                    ),
                    name=self.name.component.value,
                    race=self.race.component.values[0],
                    backstory=self.backstory.component.value,
                    x=location_rec.x,
                    y=location_rec.y,
                )
                response = await SetupPlayerCommand(request).execute()
                
                if response.success:
                    await interaction.response.send_message(f"{request.name} was successfully registered", ephemeral=True)
                else:
                    await interaction.response.send_message(f"You already have a registered character", ephemeral=True)

            except Exception as e:
                await interaction.response.send_message(f"Error: {e}", ephemeral=True)

        @classmethod
        async def create(cls, discord_guild_id: int):
            modal = cls(discord_guild_id)
            await modal._build()
            return modal

        async def _build(self):
            server_repo = await ServerRepository().get_instance()
            catalogue_repo = await CatalogueRepository().get_instance()
            poi_repo = await PointOfInterestRepository().get_instance()
            location_repo = await LocationRepository().get_instance()

            self.name = discord.ui.Label(
                text="Name:",
                component=discord.ui.TextInput(
                    placeholder="Your character's name",
                    required=True
                )
            )
            self.add_item(self.name)

            catalogue_race_items = [
                discord.SelectOption(label="default", value="default")
            ]
            server = await server_repo.get_by_guild_id(self.discord_guild_id)
            if server:
                race_items = await catalogue_repo.get_all_by_type("Race", server.server_id)
                if race_items:
                    catalogue_race_items = [
                        discord.SelectOption(label=e.name, value=e.name, description=e.description)
                        for e in race_items
                    ]

            self.race = discord.ui.Label(
                text="Race:",
                description="For more information use `/catalogue`",
                component=discord.ui.Select(
                    placeholder="Your character's race",
                    options=catalogue_race_items,
                    required=True
                )
            )
            self.add_item(self.race)

            location_items = [
                discord.SelectOption(label="default", value="default")
            ]
            if server:
                poi = await poi_repo.get_by_name("Capital World", server.server_id)
                if poi:
                    locations = await location_repo.get_all(poi.poi_id)
                    if locations:
                        location_items = [
                            discord.SelectOption(label=e.name, value=e.name)
                            for e in locations
                        ]

            self.location = discord.ui.Label(
                text="Location:",
                component=discord.ui.Select(
                    placeholder="Your starting location",
                    options=location_items,
                    required=True
                )
            )
            self.add_item(self.location)

            self.backstory = discord.ui.Label(
                text="Backstory:",
                description="Please provide at least two paragraphs",
                component=discord.ui.TextInput(
                    placeholder="Your character's backstory...",
                    style=discord.TextStyle.paragraph,
                    min_length=10,
                    max_length=4000,
                    required=True
                )
            )
            self.add_item(self.backstory)


    @staticmethod
    async def new_player_modal(interaction: discord.Interaction):
        modal = DiscordPlayerEmbed.NewPlayerRegistrationModal()
        modal = await modal.create(discord_guild_id=interaction.guild_id)
        return modal


    class GetPlayerProfileLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetPlayerQueryResponse|None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetPlayerQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            hex_color = self.response.player.faction.color if self.response.player.faction and self.response.player.faction.color else None
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {self.response.player.player.name}"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Rank:** #{self.response.player.player.rank}"),
                    discord.ui.TextDisplay(content=f"**Faction:** {self.response.player.faction.name if self.response.player.faction else 'None'}"),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue(),
                    spoiler=False
                )
            )

    @staticmethod
    async def get_player_profile_embed(interaction: discord.Interaction, response: GetPlayerQueryResponse):
        view = DiscordPlayerEmbed.GetPlayerProfileLayoutView()
        view = await view.create(response=response)
        return view