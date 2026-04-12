import math
import random
from typing import List, Dict, Tuple, Optional, Any, Set
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import string

from application.handlers.territory.claimability_map import ClaimabilityMap
from application.handlers.territory.territory_flood_fill import TerritoryFloodFill
from application.handlers.territory.simple_noise_generator import SimpleNoiseGenerator
from application.handlers.territory.light_weight_barrier_generator import LightweightBarrierGenerator

from config import BASE_DIR
from domain import PointOfInterest, Location, Faction, FactionMember
from infrastructure import FactionRepository, FactionMemberRepository

class LightweightGalaxyMapGenerator:
    def __init__(self, claimability_map: Optional[ClaimabilityMap] = None, 
                 territory_resolution: int = 100):  # NEW: Lower resolution for flood fill
        self.MAP_MIN = 0
        self.MAP_MAX = 6400
        self.GRID_SIZE = 16
        self.map_size = self.MAP_MAX - self.MAP_MIN
        
        # Territory radii factors
        self.RADIUS_FACTORS = {
            "Capital World": (0.08, 0.125),
            "Important World": (0.05, 0.078),
            "Primary World": (0.03, 0.0468),
            "Secondary World": (0.015, 0.025),
            "Tertiary World": (0.008, 0.0125),
        }
        
        self._faction_color_cache = {}
        
        self.VORONOI_MAX_DISTANCE = 2000
        self.VORONOI_LINE_COLOR = (255, 255, 255, 60)
        self.VORONOI_LINE_WIDTH = 2
        
        self.claimability_map = claimability_map or ClaimabilityMap()
        self.territory_resolution = territory_resolution  # Lower = faster, more pixelated

    async def _get_territory_radius(self, poi_type: str, radius_type: str = "core") -> int:
        """Get core or influence radius for a POI type in world coordinates"""
        factors = self.RADIUS_FACTORS.get(poi_type, (0.02, 0.03))
        idx = 0 if radius_type == "core" else 1
        return int(factors[idx] * self.map_size)
        
    async def _get_faction_color(self, owner_player_id: int) -> Optional[Tuple[int, int, int]]:
        if not owner_player_id:
            return None

        if owner_player_id in self._faction_color_cache:
            return self._faction_color_cache[owner_player_id]
        
        faction_member_repo = await FactionMemberRepository().get_instance()
        member = await faction_member_repo.get_by_player_id(owner_player_id)
        if member:
            faction_repo = await FactionRepository().get_instance()
            faction = await faction_repo.get_by_id(member.faction_id)
            if faction:
                if isinstance(faction.color, str) and faction.color.startswith('#'):
                    hex_color = faction.color.lstrip('#')
                    color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                else:
                    color = faction.color
                self._faction_color_cache[owner_player_id] = color
                return color
        
        self._faction_color_cache[owner_player_id] = None
        return None
    
    async def _draw_circle_alpha(self, img: Image.Image, x: float, y: float, radius: int, 
                        color: Tuple[int, int, int], alpha: int):
        img_width, img_height = img.size
        
        left = int(x - radius)
        top = int(y - radius)
        right = int(x + radius)
        bottom = int(y + radius)
        
        if right <= 0 or left >= img_width or bottom <= 0 or top >= img_height:
            return
        
        circle_img = Image.new('RGBA', (radius * 2, radius * 2), (0, 0, 0, 0))
        circle_draw = ImageDraw.Draw(circle_img)
        circle_draw.ellipse([0, 0, radius * 2, radius * 2], 
                        fill=(color[0], color[1], color[2], alpha))
        
        src_left = max(0, -left)
        src_top = max(0, -top)
        src_right = radius * 2 - max(0, right - img_width)
        src_bottom = radius * 2 - max(0, bottom - img_height)
        
        dst_left = max(0, left)
        dst_top = max(0, top)
        
        if src_left < src_right and src_top < src_bottom:
            cropped_circle = circle_img.crop((src_left, src_top, src_right, src_bottom))
            img.paste(cropped_circle, (dst_left, dst_top), cropped_circle)
    
    async def _draw_circle_border(self, img: Image.Image, x: float, y: float, radius: int, 
                        color: Tuple[int, int, int]):
        img_width, img_height = img.size
        
        left = int(x - radius)
        top = int(y - radius)
        right = int(x + radius)
        bottom = int(y + radius)
        
        if right <= 0 or left >= img_width or bottom <= 0 or top >= img_height:
            return
        
        border_img = Image.new('RGBA', (radius * 2, radius * 2), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_img)
        border_draw.ellipse([0, 0, radius * 2, radius * 2], 
                        outline=(color[0], color[1], color[2], 200), 
                        width=3)
        
        src_left = max(0, -left)
        src_top = max(0, -top)
        src_right = radius * 2 - max(0, right - img_width)
        src_bottom = radius * 2 - max(0, bottom - img_height)
        
        dst_left = max(0, left)
        dst_top = max(0, top)
        
        if src_left < src_right and src_top < src_bottom:
            cropped_border = border_img.crop((src_left, src_top, src_right, src_bottom))
            img.paste(cropped_border, (dst_left, dst_top), cropped_border)
    
    async def _draw_flood_fill_territories(self, img: Image.Image, 
                                    locations: List[Location], 
                                    scale: float):
        """Draw territories using flood fill with connectivity guaranteed"""
        
        if not self.claimability_map:
            await self._draw_territories(img, locations, scale)
            return
        
        # Group locations by faction
        locations_by_faction = defaultdict(list)
        for location in locations:
            if location.owner_player_id:
                locations_by_faction[location.owner_player_id].append(location)
        
        if not locations_by_faction:
            return
        
        # Calculate territory size at lower resolution
        territory_img_size = self.territory_resolution
        territory_scale = territory_img_size / self.map_size
        
        print(f"Generating territories at {territory_img_size}x{territory_img_size} resolution...")
        
        # Create a low-resolution claimability map for faster processing
        low_res_claim_map = await self._create_low_res_claimability_map(territory_img_size)
        
        # Initialize flood fill with low-res map
        flood_fill = TerritoryFloodFill(low_res_claim_map, self.map_size)
        
        # Use priority-based flood fill (strongest factions expand first)
        print("Using priority-based flood fill with connectivity...")
        all_territories = flood_fill.flood_fill_with_priority(locations_by_faction)
        
        # Resolve conflicts with connectivity check
        print("Resolving territory conflicts with connectivity...")
        resolved_territories = flood_fill.resolve_contested_cells(all_territories, locations_by_faction)
        
        # Create low-resolution territory image
        low_res_territory = Image.new('RGBA', (territory_img_size, territory_img_size), (0, 0, 0, 0))
        
        for faction_id, territory_cells in resolved_territories.items():
            color = await self._get_faction_color(faction_id)
            if not color:
                continue
            
            # Draw each territory cell on low-res image
            draw = ImageDraw.Draw(low_res_territory, 'RGBA')
            for cell_x, cell_y in territory_cells:
                draw.rectangle([cell_x, cell_y, cell_x + 1, cell_y + 1],
                            fill=(color[0], color[1], color[2], 100))
        
        # Scale up to full resolution
        print(f"Scaling territories from {territory_img_size} to {img.size[0]}...")
        scaled_territory = low_res_territory.resize(img.size, Image.Resampling.NEAREST)
        
        # Draw barrier overlay at full resolution
        if self.claimability_map and self.claimability_map.barriers:
            barrier_layer = await self._draw_barrier_overlay(img.size, scale)
            scaled_territory = Image.alpha_composite(scaled_territory, barrier_layer)
        
        # Composite onto main image
        img.alpha_composite(scaled_territory)

    async def _create_low_res_claimability_map(self, target_resolution: int) -> ClaimabilityMap:
        """Create a lower resolution version of the claimability map for faster processing"""
        
        low_res_map = ClaimabilityMap(size=self.map_size, resolution=target_resolution)
        
        # Sample the original claimability map at lower resolution
        for cell_x in range(target_resolution):
            for cell_y in range(target_resolution):
                # Get world coordinates for this low-res cell
                world_x = (cell_x + 0.5) * low_res_map.cell_size
                world_y = (cell_y + 0.5) * low_res_map.cell_size
                
                # Sample claimability from original map
                claimability = self.claimability_map.get_claimability(world_x, world_y)
                
                # Store in low-res map
                low_res_map.barriers[(cell_x, cell_y)] = claimability
        
        return low_res_map

    async def _draw_barrier_overlay(self, img_size: Tuple[int, int], 
                              scale: float) -> Image.Image:
        """Draw visual representation of unclaimable areas"""
        barrier_img = Image.new('RGBA', img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(barrier_img, 'RGBA')
        
        for cell, claimability in self.claimability_map.barriers.items():
            if claimability >= 0.7:
                continue
            
            world_x = (cell[0] + 0.5) * self.claimability_map.cell_size
            world_y = (cell[1] + 0.5) * self.claimability_map.cell_size
            
            px = int(world_x * scale)
            py = int(world_y * scale)
            cell_px_size = max(2, int(self.claimability_map.cell_size * scale))
            
            if 0 <= px < img_size[0] and 0 <= py < img_size[1]:
                if claimability < 0.2:
                    # Black hole core
                    alpha = int(180 * (1 - claimability))
                    draw.rectangle([px - cell_px_size, py - cell_px_size,
                                   px + cell_px_size, py + cell_px_size],
                                  fill=(255, 0, 0, alpha))
                elif claimability < 0.4:
                    # Hazard zone
                    alpha = int(120 * (1 - claimability))
                    draw.rectangle([px - cell_px_size, py - cell_px_size,
                                   px + cell_px_size, py + cell_px_size],
                                  fill=(150, 0, 0, alpha))
                elif claimability < 0.7:
                    # Nebula
                    alpha = int(60 * (1 - claimability))
                    draw.rectangle([px - cell_px_size, py - cell_px_size,
                                   px + cell_px_size, py + cell_px_size],
                                  fill=(100, 0, 150, alpha))
        
        return barrier_img
    
    async def _draw_territories(self, img: Image.Image, locations: List[Location], scale: float):
        """Fallback territory drawing method"""
        for location in locations:
            if not location.owner_player_id:
                continue
                
            color = await self._get_faction_color(location.owner_player_id)
            if not color:
                continue

            poi_type = location.type or "Secondary World"
            radius_world = await self._get_territory_radius(poi_type, "core")
            
            if radius_world > 0:
                px = location.x * scale
                py = location.y * scale
                radius_px = max(1, int(radius_world * scale))
                
                await self._draw_circle_alpha(img, px, py, radius_px, color, 80)
                await self._draw_circle_border(img, px, py, radius_px, color)
    
    async def _draw_grid(self, draw: ImageDraw, img_size: int, scale: float):
        step = self.map_size / self.GRID_SIZE
        positions = [self.MAP_MIN + step * i for i in range(self.GRID_SIZE + 1)]
        pixel_positions = [pos * scale for pos in positions]
        
        for pos in pixel_positions:
            if 0 <= pos <= img_size:
                draw.line([(pos, 0), (pos, img_size)], fill=(255, 255, 255, 40), width=1)
                draw.line([(0, pos), (img_size, pos)], fill=(255, 255, 255, 40), width=1)
        
        try:
            grid_font = ImageFont.truetype(f"{BASE_DIR}/shared/assets/fonts/DejaVuSans.ttf", 48)
        except:
            grid_font = ImageFont.load_default()
        
        cols = list(string.ascii_uppercase[:self.GRID_SIZE])
        rows = list(range(1, self.GRID_SIZE + 1))
        
        tick_pos = [self.MAP_MIN + step * (i + 0.5) for i in range(self.GRID_SIZE)]
        pixel_ticks = [pos * scale for pos in tick_pos]
        
        for i, col in enumerate(cols):
            x_pos = pixel_ticks[i] - 10
            if 0 <= x_pos <= img_size - 20:
                draw.text((x_pos, 25), col, fill=(255, 255, 255, 100), font=grid_font)
        
        for i, row in enumerate(rows):
            y_pos = pixel_ticks[i] - 10
            if 0 <= y_pos <= img_size - 20:
                draw.text((25, y_pos), str(row), fill=(255, 255, 255, 100), font=grid_font)

    async def _draw_pois(self, draw: ImageDraw, pois: List[PointOfInterest], locations: List[Location], scale: float):
        def to_pixel(x: float, y: float) -> Tuple[float, float]:
            return (x * scale, y * scale)

        img_width, img_height = draw.im.size
        
        for poi in pois:
            locations_for_poi = [loc for loc in locations if loc.poi_id == poi.poi_id]

            try:
                poi_font = ImageFont.truetype(f"{BASE_DIR}/shared/assets/fonts/DejaVuSans.ttf", poi.size)
            except:
                poi_font = ImageFont.load_default()

            for location in locations_for_poi:
                px, py = to_pixel(float(location.x), float(location.y))
                
                margin = max(poi.size, 50)
                if (px + margin < 0 or px - margin >= img_width or
                    py + margin < 0 or py - margin >= img_height):
                    continue

                color = None
                if location.owner_player_id:
                    color = await self._get_faction_color(location.owner_player_id)
                
                text_color = color if color else (255, 255, 255, 255)
                
                icon_x = px - poi.size//2
                icon_y = py - poi.size//2
                
                if -poi.size <= icon_x < img_width and -poi.size <= icon_y < img_height:
                    draw.text((icon_x + 1, icon_y + 1), poi.icon, 
                                fill=(0, 0, 0, 100), font=poi_font)
                    draw.text((icon_x, icon_y), poi.icon, 
                                fill=text_color, font=poi_font)
                
                name_offset = poi.size + 5
                name_x = px + name_offset
                name_y = py - 10
                
                if name_x < img_width and name_y > -20:
                    try:
                        bbox = draw.textbbox((name_x, name_y), location.name, font=poi_font)
                        bbox_left = max(0, bbox[0])
                        bbox_top = max(0, bbox[1])
                        bbox_right = min(img_width, bbox[2])
                        bbox_bottom = min(img_height, bbox[3])
                        
                        if bbox_left < bbox_right and bbox_top < bbox_bottom:
                            draw.rectangle([bbox_left, bbox_top, bbox_right, bbox_bottom], 
                                        fill=(0, 0, 0, 100))
                            draw.text((name_x, name_y), location.name, 
                                        fill=(255, 255, 255, 255), font=poi_font)
                    except:
                        draw.text((name_x, name_y), location.name, 
                                    fill=(255, 255, 255, 255), font=poi_font)
                    
    async def render_full_map(self, pois: List[PointOfInterest], locations: List[Location], output_path: str, 
                    show_grid: bool = True, show_territories: bool = True, 
                    show_voronoi: bool = False, weighted_voronoi: bool = False,
                    include_barriers: bool = True, use_flood_fill: bool = True,
                    territory_resolution: int = None):  # NEW: Allow override per render
        """Render the complete galaxy map with configurable territory resolution"""
        
        # Override territory resolution if provided
        if territory_resolution:
            self.territory_resolution = territory_resolution
        
        print(f"Rendering map with include_barriers={include_barriers}, "
              f"use_flood_fill={use_flood_fill}, "
              f"territory_resolution={self.territory_resolution}")
        
        # Create image
        img_size = 4096
        scale = img_size / self.map_size
        img = Image.new('RGBA', (img_size, img_size), '#131313')
        
        # Draw territories
        if show_territories:
            if include_barriers and use_flood_fill and self.claimability_map:
                print("Using optimized flood fill territory generation...")
                await self._draw_flood_fill_territories(img, locations, scale)
            elif include_barriers and self.claimability_map:
                print("Using circle-based territories with barriers...")
                await self._draw_territories_with_barriers(img, locations, scale)
            else:
                print("Using basic circle territories...")
                await self._draw_territories(img, locations, scale)
        
        # Draw Voronoi boundaries
        if show_voronoi:
            draw = ImageDraw.Draw(img, 'RGBA')
            if weighted_voronoi:
                await self._draw_weighted_voronoi(draw, locations, scale)
            else:
                await self._draw_voronoi_boundaries(draw, locations, scale)
        
        # Draw grid
        if show_grid:
            draw = ImageDraw.Draw(img, 'RGBA')
            await self._draw_grid(draw, img_size, scale)
        
        # Draw POIs (at full resolution)
        draw = ImageDraw.Draw(img, 'RGBA')
        await self._draw_pois(draw, pois, locations, scale)
        
        # Save image
        img.save(output_path, 'PNG', optimize=True)
        print(f"Map saved to {output_path}")
    
    async def _draw_territories_with_barriers(self, img: Image.Image, locations: List[Location], scale: float):
        """Fallback territory drawing with simple barrier influence"""
        territory_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        
        for location in locations:
            if not location.owner_player_id:
                continue
                
            color = await self._get_faction_color(location.owner_player_id)
            if not color:
                continue

            poi_type = location.type or "Secondary World"
            base_radius_world = await self._get_territory_radius(poi_type, "core")
            
            # Simple barrier influence
            if self.claimability_map:
                claimability = self.claimability_map.get_claimability(location.x, location.y)
                radius_world = int(base_radius_world * claimability)
            else:
                radius_world = base_radius_world
            
            if radius_world > 0:
                px = location.x * scale
                py = location.y * scale
                radius_px = max(5, int(radius_world * scale))
                
                await self._draw_circle_alpha(territory_layer, px, py, radius_px, color, 80)
                await self._draw_circle_border(territory_layer, px, py, radius_px, color)
        
        if self.claimability_map and self.claimability_map.barriers:
            barrier_layer = await self._draw_barrier_overlay(img.size, scale)
            territory_layer = Image.alpha_composite(territory_layer, barrier_layer)
        
        img.alpha_composite(territory_layer)
    
    async def _draw_voronoi_boundaries(self, draw: ImageDraw, locations: List[Location], scale: float):
        owned_locations = [loc for loc in locations if loc.owner_player_id]
        
        if len(owned_locations) < 2:
            return
        
        boundaries = []
        
        for i, loc1 in enumerate(owned_locations):
            for loc2 in owned_locations[i+1:]:
                dist = math.hypot(loc1.x - loc2.x, loc1.y - loc2.y)
                
                if dist < self.VORONOI_MAX_DISTANCE:
                    line_start, line_end = self._calculate_bisector_line(loc1, loc2)
                    
                    px1, py1 = line_start[0] * scale, line_start[1] * scale
                    px2, py2 = line_end[0] * scale, line_end[1] * scale
                    
                    boundaries.append(((px1, py1), (px2, py2)))
        
        for start, end in boundaries:
            draw.line([start, end], fill=self.VORONOI_LINE_COLOR, width=self.VORONOI_LINE_WIDTH)
    
    async def _calculate_bisector_line(self, loc1: Location, loc2: Location, extent: float = None):
        if extent is None:
            extent = self.map_size * 0.3
        
        mx = (loc1.x + loc2.x) / 2
        my = (loc1.y + loc2.y) / 2
        
        dx = loc2.x - loc1.x
        dy = loc2.y - loc1.y
        
        length = math.hypot(dx, dy)
        if length < 0.001:
            return ((mx, my), (mx, my))
        
        perp_dx = -dy / length
        perp_dy = dx / length
        
        x1 = mx - perp_dx * extent
        y1 = my - perp_dy * extent
        x2 = mx + perp_dx * extent
        y2 = my + perp_dy * extent
        
        return ((x1, y1), (x2, y2))
    
    async def _draw_weighted_voronoi(self, draw: ImageDraw, locations: List[Location], scale: float):
        owned_locations = [loc for loc in locations if loc.owner_player_id]
        
        if len(owned_locations) < 2:
            return
        
        for i, loc1 in enumerate(owned_locations):
            for loc2 in owned_locations[i+1:]:
                dist = math.hypot(loc1.x - loc2.x, loc1.y - loc2.y)
                
                if dist < self.VORONOI_MAX_DISTANCE:
                    poi_type1 = loc1.type or "Secondary World"
                    poi_type2 = loc2.type or "Secondary World"
                    
                    radius1 = await self._get_territory_radius(poi_type1, "core")
                    radius2 = await self._get_territory_radius(poi_type2, "core")
                    
                    total_radius = radius1 + radius2
                    if total_radius > 0:
                        weight1 = radius2 / total_radius
                        weight2 = radius1 / total_radius
                    else:
                        weight1 = weight2 = 0.5
                    
                    mx = (loc1.x * weight2 + loc2.x * weight1)
                    my = (loc1.y * weight2 + loc2.y * weight1)
                    
                    dx = loc2.x - loc1.x
                    dy = loc2.y - loc1.y
                    
                    length = math.hypot(dx, dy)
                    if length > 0.001:
                        perp_dx = -dy / length
                        perp_dy = dx / length
                        
                        extent = self.map_size * 0.3
                        x1 = mx - perp_dx * extent
                        y1 = my - perp_dy * extent
                        x2 = mx + perp_dx * extent
                        y2 = my + perp_dy * extent
                        
                        px1, py1 = x1 * scale, y1 * scale
                        px2, py2 = x2 * scale, y2 * scale
                        
                        draw.line([(px1, py1), (px2, py2)], 
                                 fill=(255, 255, 255, 80), 
                                 width=2, 
                                 joint='curve')


async def create_default_claimability_map(map_size: int = 6400, resolution: int = 200) -> ClaimabilityMap:
    """Create a default claimability map with interesting features"""
    print(f"Creating claimability map with size={map_size}, resolution={resolution}")
    claim_map = ClaimabilityMap(size=map_size, resolution=resolution)
    barrier_gen = LightweightBarrierGenerator(map_size=map_size, resolution=resolution)
    
    # Add central supermassive black hole
    center = map_size / 2
    #claim_map.add_circle_barrier(1950, 2265, radius=400, strength=0.1, falloff=True)
    #claim_map.add_circle_barrier(center, center, radius=800, strength=0.4, falloff=True)
    
    # Generate noise-based barriers
    claim_map = barrier_gen.generate_perlin_like_barriers(claim_map, scale=0.03, octaves=3)
    
    # Add spiral arm patterns
    claim_map = barrier_gen.add_spiral_arms(claim_map, num_arms=4, tightness=0.6)
    
    # Add some random nebulae
    random.seed(42)
    for _ in range(12):
        x = random.randint(500, map_size - 500)
        y = random.randint(500, map_size - 500)
        dist_from_center = math.hypot(x - center, y - center)
        if dist_from_center > 800:
            radius = random.randint(150, 300)
            strength = random.uniform(0.3, 0.6)
            claim_map.add_circle_barrier(x, y, radius, strength, falloff=True)
    
    print(f"Created claimability map with {len(claim_map.barriers)} barrier cells")
    return claim_map