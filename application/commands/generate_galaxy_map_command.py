from dataclasses import dataclass

from application import DiscordGuild
from application.helpers.ensure_user import ensure_guild

from application import LightweightGalaxyMapGenerator, create_default_claimability_map
from infrastructure import PointOfInterestRepository, LocationRepository

@dataclass
class GenerateGalaxyMapCommandRequest:
    guild: DiscordGuild
    output_path: str = "starmap_full.png"
    show_grid: bool = True
    show_territories: bool = True
    show_voronoi: bool = True
    weighted_voronoi: bool = True
    use_barriers: bool = True
    use_flood_fill: bool = True
    territory_resolution: int = 150  # NEW: Control territory detail (50-200, lower = faster)

@dataclass
class GenerateGalaxyMapCommandResponse:
    success: bool
    output_path: str

class GenerateGalaxyMapCommand:
    def __init__(self, request: GenerateGalaxyMapCommandRequest):
        self.request = request
        return
    
    async def execute(self) -> GenerateGalaxyMapCommandResponse:
        self.point_of_interest_repo = await PointOfInterestRepository().get_instance()
        self.location_repo = await LocationRepository().get_instance()

        server_config = await ensure_guild(self.request.guild)

        pois = await self.point_of_interest_repo.get_all(server_config.server.server_id)
        locations = []
        for poi in pois:
            locs = await self.location_repo.get_all(poi.poi_id)
            locations.extend(locs)

        # Create generator with or without barriers
        if self.request.use_barriers:
            print("Creating map WITH barriers using flood fill...")
            claimability_map = await create_default_claimability_map(map_size=6400, resolution=150)  # Lower resolution for faster flood fill
            generator = LightweightGalaxyMapGenerator(claimability_map=claimability_map)
        else:
            print("Creating map WITHOUT barriers...")
            generator = LightweightGalaxyMapGenerator()
        
        # Render the map
        await generator.render_full_map(
            pois=pois,
            locations=locations,
            output_path=self.request.output_path,
            show_grid=self.request.show_grid,
            show_territories=self.request.show_territories,
            show_voronoi=self.request.show_voronoi,
            weighted_voronoi=self.request.weighted_voronoi,
            include_barriers=self.request.use_barriers,  # This tells render_full_map to use barriers
            use_flood_fill=self.request.use_flood_fill,
            territory_resolution=self.request.territory_resolution,  # Pass to render method
        )

        return GenerateGalaxyMapCommandResponse(success=True, output_path=self.request.output_path)