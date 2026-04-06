import math

from application.handlers.territory.claimability_map import ClaimabilityMap
from application.handlers.territory.territory_flood_fill import TerritoryFloodFill
from application.handlers.territory.simple_noise_generator import SimpleNoiseGenerator

class LightweightBarrierGenerator:
    """Generate claimability barriers without heavy dependencies"""
    
    def __init__(self, map_size: int = 6400, resolution: int = 200):
        self.map_size = map_size
        self.resolution = resolution
        self.noise = SimpleNoiseGenerator()
        
    def generate_perlin_like_barriers(self, claim_map: ClaimabilityMap,
                                      scale: float = 0.05,
                                      octaves: int = 3) -> ClaimabilityMap:
        """Generate noise-based barriers"""
        for cell_x in range(claim_map.resolution):
            for cell_y in range(claim_map.resolution):
                world_x = (cell_x + 0.5) * claim_map.cell_size
                world_y = (cell_y + 0.5) * claim_map.cell_size
                
                noise_value = self.noise.fractal_noise(
                    world_x * scale, world_y * scale, octaves
                )
                
                # Gentle barrier mapping for natural look
                if noise_value < 0.2:
                    claimability = 0.3
                elif noise_value < 0.4:
                    claimability = 0.5
                elif noise_value < 0.6:
                    claimability = 0.7
                else:
                    claimability = 1.0
                
                current = claim_map.barriers.get((cell_x, cell_y), 1.0)
                claim_map.barriers[(cell_x, cell_y)] = min(current, claimability)
        
        return claim_map
    
    def add_spiral_arms(self, claim_map: ClaimabilityMap,
                       num_arms: int = 4,
                       tightness: float = 0.5) -> ClaimabilityMap:
        """Add spiral arm patterns"""
        center_x = self.map_size / 2
        center_y = self.map_size / 2
        
        for cell_x in range(claim_map.resolution):
            for cell_y in range(claim_map.resolution):
                world_x = (cell_x + 0.5) * claim_map.cell_size
                world_y = (cell_y + 0.5) * claim_map.cell_size
                
                dx = world_x - center_x
                dy = world_y - center_y
                radius = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)
                
                arm_nearby = False
                for arm in range(num_arms):
                    arm_angle = (2 * math.pi * arm / num_arms) + (tightness * math.log(radius + 1))
                    angle_diff = abs(angle - arm_angle)
                    angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
                    
                    arm_width = 0.4 * (1 - radius / self.map_size) + 0.15
                    if angle_diff < arm_width:
                        arm_nearby = True
                        break
                
                if arm_nearby and radius > 300:
                    current = claim_map.barriers.get((cell_x, cell_y), 1.0)
                    claim_map.barriers[(cell_x, cell_y)] = min(1.0, current * 1.3)
        
        return claim_map

