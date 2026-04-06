import math
from typing import Dict, Tuple

class ClaimabilityMap:
    """Lightweight 2D map with sparse storage for performance"""
    size: int
    resolution: int
    barriers: Dict[Tuple[int, int], float]
    
    def __init__(self, size: int = 6400, resolution: int = 200):
        self.size = size
        self.resolution = resolution
        self.cell_size = size / resolution
        self.barriers = {}
        
    def _world_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        cell_x = int(x / self.cell_size)
        cell_y = int(y / self.cell_size)
        cell_x = max(0, min(cell_x, self.resolution - 1))
        cell_y = max(0, min(cell_y, self.resolution - 1))
        return (cell_x, cell_y)
    
    def get_claimability(self, x: float, y: float) -> float:
        cell = self._world_to_cell(x, y)
        return self.barriers.get(cell, 1.0)
    
    def get_claimability_cell(self, cell_x: int, cell_y: int) -> float:
        """Get claimability directly by cell coordinates"""
        if 0 <= cell_x < self.resolution and 0 <= cell_y < self.resolution:
            return self.barriers.get((cell_x, cell_y), 1.0)
        return 0.0
    
    def set_barrier(self, x: float, y: float, claimability: float):
        cell = self._world_to_cell(x, y)
        self.barriers[cell] = max(0.0, min(1.0, claimability))
    
    def add_circle_barrier(self, center_x: float, center_y: float, 
                           radius: float, strength: float = 0.0,
                           falloff: bool = True):
        min_cell_x = max(0, int((center_x - radius) / self.cell_size))
        max_cell_x = min(self.resolution, int((center_x + radius) / self.cell_size) + 1)
        min_cell_y = max(0, int((center_y - radius) / self.cell_size))
        max_cell_y = min(self.resolution, int((center_y + radius) / self.cell_size) + 1)
        
        for cell_x in range(min_cell_x, max_cell_x):
            for cell_y in range(min_cell_y, max_cell_y):
                world_x = (cell_x + 0.5) * self.cell_size
                world_y = (cell_y + 0.5) * self.cell_size
                
                distance = math.hypot(world_x - center_x, world_y - center_y)
                
                if distance < radius:
                    if falloff:
                        factor = 1 - (distance / radius)
                        new_value = strength + (1 - strength) * factor
                    else:
                        new_value = strength
                    
                    current = self.barriers.get((cell_x, cell_y), 1.0)
                    self.barriers[(cell_x, cell_y)] = min(current, new_value)

