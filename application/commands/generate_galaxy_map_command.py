from dataclasses import dataclass

from application import GalaxyMapGeneratorHandler
from infrastructure import PointOfInterestRepository

@dataclass
class GenerateGalaxyMapCommandRequest:
    output_path: str = "starmap_full.png"
    show_grid: bool = True

@dataclass
class GenerateGalaxyMapCommandResponse:
    success: bool
    output_path: str

class GenerateGalaxyMapCommand:
    def __init__(self, request: GenerateGalaxyMapCommandRequest):
        self.request = request
        return

    def execute(self) -> GenerateGalaxyMapCommandResponse:
        repo = PointOfInterestRepository()
        pois = repo.get_all()

        handler = GalaxyMapGeneratorHandler()
        handler.render_full_map(pois, self.request.output_path, self.request.show_grid)

        return GenerateGalaxyMapCommandResponse(success=True, output_path=self.request.output_path)