import string
import matplotlib.pyplot as plt
from dataclasses import dataclass
from shapely.geometry import Point, LineString
from shapely.ops import unary_union, split
from matplotlib.patches import Polygon as MplPolygon
from infrastructure import PointOfInterestRepository

# -------------------- Dataclasses --------------------
@dataclass
class POIMarker:
    marker: str
    color: str
    size: int
    font_size: int
    offset: int

# -------------------- Request & Response --------------------
@dataclass
class GenerateGalaxyMapCommandRequest:
    output_path: str = "starmap_full.png"
    show_grid: bool = True

@dataclass
class GenerateGalaxyMapCommandResponse:
    success: bool
    output_path: str

# -------------------- Main Command --------------------
class GenerateGalaxyMapCommand:

    POI_MARKERS = {
        "Capital World":    POIMarker("H", "white", 10, 6, 10),
        "Important World":  POIMarker("p", "white", 7, 5, 9),
        "Primary World":    POIMarker("o", "white", 4, 4, 8),
        "Secondary World":  POIMarker("s", "white", 2, 3, 6),
        "Tertiary World":   POIMarker("D", "gray", 2, 3, 5),
        "No Marker":        POIMarker(None, None, None, 4, 10),
    }

    def __init__(self, request: GenerateGalaxyMapCommandRequest):
        self.request = request
        self.MAP_MIN = 0
        self.MAP_MAX = 3200
        self.GRID_SIZE = 16
        self.map_size = self.MAP_MAX - self.MAP_MIN

    # -------------------- POI Rendering --------------------
    def _get_poi_marker(self, poi_type: str) -> POIMarker:
        return self.POI_MARKERS.get(poi_type, POIMarker("o", "white", 5, 6, 10))

    def _get_poi(self, ax: plt.Axes, poi):
        marker_info = self._get_poi_marker(poi.type)
        if marker_info.marker:
            ax.scatter(poi.x, poi.y, color=marker_info.color, s=marker_info.size, marker=marker_info.marker)
        ax.text(
            poi.x + 10,
            poi.y - (marker_info.offset or 0),
            poi.name,
            fontsize=marker_info.font_size,
            color="white",
            alpha=0.8
        )

    # -------------------- Territory Calculations --------------------
    def _poi_core_radius(self, poi) -> int:
        """Core radius for the POI territory"""
        factors = {
            "Capital World": 0.08,
            "Important World": 0.05,
            "Primary World": 0.03,
            "Secondary World": 0.015,
            "Tertiary World": 0.008,
        }
        return int(factors.get(poi.type, 0.02) * self.map_size)

    def _poi_influence_radius(self, poi) -> int:
        """Larger influence radius for POI"""
        factors = {
            "Capital World": 0.125,
            "Important World": 0.078,
            "Primary World": 0.0468,
            "Secondary World": 0.025,
            "Tertiary World": 0.0125,
        }
        return int(factors.get(poi.type, 0.03) * self.map_size)

    def _generate_poi_areas(self, pois):
        poi_areas = []
        for poi in pois:
            core_geom = Point(poi.x, poi.y).buffer(self._poi_core_radius(poi), quad_segs=8)
            influence_geom = Point(poi.x, poi.y).buffer(self._poi_influence_radius(poi), quad_segs=8)

            # Clip both against other POIs
            for other in pois:
                if other is poi or other.owner_player_id == poi.owner_player_id:
                    continue

                max_dist_core = self._poi_core_radius(poi) + self._poi_core_radius(other)
                max_dist_influence = self._poi_influence_radius(poi) + self._poi_influence_radius(other)
                
                dx, dy = poi.x - other.x, poi.y - other.y
                dist_sq = dx*dx + dy*dy

                if dist_sq <= max_dist_core*max_dist_core:
                    core_geom = self._clip_against(core_geom, poi, other)
                if dist_sq <= max_dist_influence*max_dist_influence:
                    influence_geom = self._clip_against(influence_geom, poi, other)

                if core_geom.is_empty and influence_geom.is_empty:
                    break

            if not core_geom.is_empty or not influence_geom.is_empty:
                poi_areas.append((poi, core_geom, influence_geom))
        return poi_areas

    def _bisector_line(self, p1, p2, extent=10000) -> LineString:
        mx, my = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
        dx, dy = p2.x - p1.x, p2.y - p1.y
        length = (dx**2 + dy**2) ** 0.5 or 1
        perp_dx, perp_dy = -dy/length, dx/length
        return LineString([
            (mx - perp_dx*extent, my - perp_dy*extent),
            (mx + perp_dx*extent, my + perp_dy*extent)
        ])

    def _clip_against(self, geom, poi_a, poi_b):
        try:
            parts = split(geom, self._bisector_line(poi_a, poi_b))
        except Exception:
            return geom

        geoms = [g for g in (getattr(parts, 'geoms', [parts])) 
                 if g.geom_type in ("Polygon", "MultiPolygon") and not g.is_empty]

        if len(geoms) <= 1:
            return geom

        # Keep the side where poi_a is closer
        for part in geoms:
            cx, cy = part.centroid.x, part.centroid.y
            if (cx - poi_a.x)**2 + (cy - poi_a.y)**2 <= (cx - poi_b.x)**2 + (cy - poi_b.y)**2:
                return part
        return geom

    def _merge_owner_polygons(self, poi_areas):
        owners = {}
        for poi, geom in poi_areas:
            owner = poi.owner_player_id or "Neutral"
            owners.setdefault(owner, []).append(geom)
        return owners

    def _draw_territories(self, ax, pois):
        poi_areas = self._generate_poi_areas(pois)

        # Separate merged polygons per owner
        owners_core = {}
        owners_influence = {}

        for poi, core, influence in poi_areas:
            owner = poi.owner_player_id or "Neutral"
            if core and not core.is_empty:
                owners_core.setdefault(owner, []).append(core)
            if influence and not influence.is_empty:
                owners_influence.setdefault(owner, []).append(influence)

        # Draw merged core territories
        for geoms in owners_core.values():
            merged = unary_union(geoms)
            polygons = [merged] if merged.geom_type == "Polygon" else list(merged.geoms)
            for poly in polygons:
                x, y = poly.exterior.coords.xy
                ax.add_patch(MplPolygon(
                    list(zip(x, y)),
                    closed=True,
                    facecolor=(1, 1, 1, 0.05),
                    edgecolor=(1, 1, 1, 0.1),
                    linewidth=0.5,
                    zorder=0
                ))

        # Draw merged influence areas
        for geoms in owners_influence.values():
            merged = unary_union(geoms)
            polygons = [merged] if merged.geom_type == "Polygon" else list(merged.geoms)
            for poly in polygons:
                x, y = poly.exterior.coords.xy
                ax.add_patch(MplPolygon(
                    list(zip(x, y)),
                    closed=True,
                    facecolor=(1, 1, 1, 0.025),
                    edgecolor=(1, 1, 1, 0.2),
                    linewidth=0.5,
                    linestyle='--',
                    zorder=0
                ))

    # -------------------- Map Rendering --------------------
    def _render_full_map(self, pois, output_path, show_grid=True):
        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('#131313')
        ax.set_facecolor('#131313')
        ax.set_aspect('equal')
        ax.set_xlim(self.MAP_MIN, self.MAP_MAX)
        ax.set_ylim(self.MAP_MIN, self.MAP_MAX)

        # Draw territories first
        self._draw_territories(ax, pois)

        # Draw POIs
        for poi in pois:
            self._get_poi(ax, poi)

        # Grid lines
        if show_grid:
            step = self.map_size / self.GRID_SIZE
            positions = [self.MAP_MIN + step*i for i in range(self.GRID_SIZE+1)]
            ax.hlines(positions, self.MAP_MIN, self.MAP_MAX, colors="#FFFFFF75", linestyles='--', linewidth=0.5)
            ax.vlines(positions, self.MAP_MIN, self.MAP_MAX, colors="#FFFFFF75", linestyles='--', linewidth=0.5)

            # Grid labels
            cols = list(string.ascii_uppercase[:self.GRID_SIZE])
            rows = list(range(1, self.GRID_SIZE+1))
            tick_pos = [self.MAP_MIN + step*(i+0.5) for i in range(self.GRID_SIZE)]
            ax.set_xticks(tick_pos)
            ax.set_xticklabels(cols)
            ax.set_yticks(tick_pos)
            ax.set_yticklabels(rows)
            ax.tick_params(axis='both', which='both', length=0, colors='#FFFFFF75')

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.savefig(output_path, dpi=600, bbox_inches='tight')
        plt.close()

    # -------------------- Execution --------------------
    def execute(self) -> GenerateGalaxyMapCommandResponse:
        repo = PointOfInterestRepository()
        pois = repo.get_all()
        self._render_full_map(pois, self.request.output_path, self.request.show_grid)
        return GenerateGalaxyMapCommandResponse(success=True, output_path=self.request.output_path)