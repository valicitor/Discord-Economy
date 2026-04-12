import math
import heapq
from collections import defaultdict
from typing import Set, Tuple, Dict, List, Optional
from .claimability_map import ClaimabilityMap
from domain import Location

class TerritoryFloodFill:
    """Handles flood fill territory expansion with influence weights and connectivity"""
    
    def __init__(self, claimability_map: ClaimabilityMap, map_size: int = 6400):
        self.claimability_map = claimability_map
        self.map_size = map_size
        self.cell_size = claimability_map.cell_size
        self.resolution = claimability_map.resolution
        
    def calculate_influence(self, location: Location) -> float:
        """Calculate the influence value of a POI based on its type"""
        influence_map = {
            "Capital World": 1.0,
            "Important World": 0.7,
            "Primary World": 0.5,
            "Secondary World": 0.3,
            "Tertiary World": 0.15,
        }
        poi_type = location.type or "Secondary World"
        return influence_map.get(poi_type, 0.3)
    
    def get_max_territory_radius(self, location: Location) -> float:
        """Get the maximum territory radius in world units based on POI type"""
        radius_map = {
            "Capital World": 1200,
            "Important World": 900,
            "Primary World": 650,
            "Secondary World": 400,
            "Tertiary World": 250,
        }
        poi_type = location.type or "Secondary World"
        return radius_map.get(poi_type, 400)
    
    def flood_fill_territory(self, location: Location, 
                            contested_cells: Optional[Set[Tuple[int, int]]] = None) -> Set[Tuple[int, int]]:
        """Perform flood fill to determine territory cells with connectivity guaranteed"""
        
        start_cell = self.claimability_map._world_to_cell(location.x, location.y)
        max_radius_cells = int(self.get_max_territory_radius(location) / self.cell_size)
        influence = self.calculate_influence(location)
        
        # Priority queue for Dijkstra-like expansion
        priority_queue = []
        heapq.heappush(priority_queue, (0, start_cell))
        
        # Track visited cells and their costs
        visited = {}
        territory_cells = set()
        
        # Cost multipliers
        BARRIER_COST_MULTIPLIER = 3.0
        DISTANCE_FALLOFF = 0.8
        
        while priority_queue:
            cost, (cell_x, cell_y) = heapq.heappop(priority_queue)
            
            # Skip if already visited with lower cost
            if (cell_x, cell_y) in visited and visited[(cell_x, cell_y)] <= cost:
                continue
            
            visited[(cell_x, cell_y)] = cost
            
            # Calculate effective influence at this cell
            distance_factor = 1 - (cost / (max_radius_cells * DISTANCE_FALLOFF))
            if distance_factor <= 0:
                continue
            
            # Get claimability at this cell
            claimability = self.claimability_map.get_claimability_cell(cell_x, cell_y)
            
            # Check if this cell is contested and should be excluded
            if contested_cells and (cell_x, cell_y) in contested_cells:
                # Skip contested cells - they'll be resolved later
                pass
            else:
                # Calculate if this cell can be claimed
                claim_threshold = 0.3
                if claimability >= claim_threshold:
                    cell_influence = influence * distance_factor * claimability
                    
                    if cell_influence > 0.15:
                        territory_cells.add((cell_x, cell_y))
            
            # Stop expanding if we've reached max radius
            if cost >= max_radius_cells:
                continue
            
            # Explore neighbors (8-directional for better connectivity)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    nx, ny = cell_x + dx, cell_y + dy
                    
                    # Check bounds
                    if not (0 <= nx < self.resolution and 0 <= ny < self.resolution):
                        continue
                    
                    # Calculate step cost (diagonal moves cost more)
                    step_cost = math.sqrt(dx*dx + dy*dy)
                    
                    # Add barrier cost
                    neighbor_claimability = self.claimability_map.get_claimability_cell(nx, ny)
                    if neighbor_claimability < 0.3:
                        step_cost *= BARRIER_COST_MULTIPLIER
                    elif neighbor_claimability < 0.6:
                        step_cost *= 1.5
                    
                    new_cost = cost + step_cost
                    
                    # Only add if better than previously found
                    if (nx, ny) not in visited or visited[(nx, ny)] > new_cost:
                        heapq.heappush(priority_queue, (new_cost, (nx, ny)))
        
        return territory_cells
    
    def flood_fill_with_priority(self, all_locations: Dict[int, List[Location]]) -> Dict[int, Set[Tuple[int, int]]]:
        """Flood fill with priority ordering to prevent disconnection"""
        
        # Sort factions by total influence (higher influence expands first)
        faction_influence = {}
        for faction_id, locations in all_locations.items():
            total_influence = sum(self.calculate_influence(loc) for loc in locations)
            faction_influence[faction_id] = total_influence
        
        sorted_factions = sorted(faction_influence.items(), key=lambda x: x[1], reverse=True)
        
        all_territories = {}
        occupied_cells = set()
        
        # Expand territories in order of influence (strongest first)
        for faction_id, _ in sorted_factions:
            faction_locations = all_locations[faction_id]
            faction_territory = set()
            
            # Collect cells already occupied by stronger factions
            for location in faction_locations:
                territory_cells = self.flood_fill_territory(location, occupied_cells)
                faction_territory.update(territory_cells)
            
            # Remove any cells that were taken by stronger factions during expansion
            faction_territory -= occupied_cells
            all_territories[faction_id] = faction_territory
            occupied_cells.update(faction_territory)
        
        return all_territories
    
    def resolve_contested_cells(self, all_territories: Dict[int, Set[Tuple[int, int]]], 
                                locations_by_faction: Dict[int, List[Location]]) -> Dict[int, Set[Tuple[int, int]]]:
        """Resolve conflicts while maintaining connectivity to parent POIs"""
        
        # First, ensure each territory remains connected to its POIs
        connected_territories = {}
        
        for faction_id, territory_cells in all_territories.items():
            # Get all POI cells for this faction
            poi_cells = set()
            for location in locations_by_faction.get(faction_id, []):
                poi_cells.add(self.claimability_map._world_to_cell(location.x, location.y))
            
            # Find connected components that include POIs
            if poi_cells:
                connected_cells = self._get_connected_to_pois(territory_cells, poi_cells)
                connected_territories[faction_id] = connected_cells
            else:
                connected_territories[faction_id] = territory_cells
        
        # Now resolve conflicts between factions with weighted influence
        cell_faction_influence = defaultdict(lambda: defaultdict(float))
        
        for faction_id, territory_cells in connected_territories.items():
            for cell in territory_cells:
                # Calculate max influence from this faction's POIs to this cell
                max_influence = 0
                for location in locations_by_faction.get(faction_id, []):
                    cell_center_x = (cell[0] + 0.5) * self.cell_size
                    cell_center_y = (cell[1] + 0.5) * self.cell_size
                    distance = math.hypot(cell_center_x - location.x, cell_center_y - location.y)
                    
                    influence = self.calculate_influence(location)
                    max_radius = self.get_max_territory_radius(location)
                    
                    if distance < max_radius:
                        influence_factor = influence * (1 - (distance / max_radius))
                        # Add small bonus for cells closer to any POI
                        if distance < max_radius * 0.3:
                            influence_factor *= 1.2
                        max_influence = max(max_influence, influence_factor)
                
                cell_faction_influence[cell][faction_id] = max_influence
        
        # Resolve conflicts with connectivity preference
        resolved_territories = defaultdict(set)
        
        # First pass: assign cells that are clearly dominated
        for cell, influences in cell_faction_influence.items():
            if influences:
                # Sort factions by influence
                sorted_influences = sorted(influences.items(), key=lambda x: x[1], reverse=True)
                top_faction, top_influence = sorted_influences[0]
                
                # If influence difference is significant (>30%), assign immediately
                if len(sorted_influences) == 1 or (top_influence - sorted_influences[1][1]) > 0.15:
                    resolved_territories[top_faction].add(cell)
                else:
                    # Contested cell - needs connectivity check
                    pass
        
        # Second pass: handle contested cells with connectivity
        contested_cells = set(cell for cell in cell_faction_influence 
                             if cell not in resolved_territories)
        
        if contested_cells:
            # Grow territories from assigned cells into contested areas
            for faction_id in connected_territories.keys():
                frontier = resolved_territories[faction_id].copy()
                visited = frontier.copy()
                
                while frontier:
                    current = frontier.pop()
                    
                    # Check neighbors
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            
                            nx, ny = current[0] + dx, current[1] + dy
                            neighbor = (nx, ny)
                            
                            if (neighbor in contested_cells and 
                                neighbor not in visited and
                                neighbor in cell_faction_influence):
                                
                                # Check if this faction has influence here
                                if faction_id in cell_faction_influence[neighbor]:
                                    resolved_territories[faction_id].add(neighbor)
                                    visited.add(neighbor)
                                    frontier.add(neighbor)
        
        return resolved_territories
    
    def _get_connected_to_pois(self, territory_cells: Set[Tuple[int, int]], 
                               poi_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Get only the cells that are connected to any POI cell"""
        
        if not territory_cells or not poi_cells:
            return set()
        
        # BFS from POI cells through territory cells
        connected = set()
        queue = list(poi_cells)
        
        while queue:
            current = queue.pop(0)
            if current in connected:
                continue
            
            if current in territory_cells:
                connected.add(current)
                
                # Add neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        neighbor = (current[0] + dx, current[1] + dy)
                        if neighbor in territory_cells and neighbor not in connected:
                            queue.append(neighbor)
        
        return connected