from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import atan2, cos, radians, sin, sqrt
from typing import Any

from app.context.schemas import ContextObject
from app.graph.service import GraphQueryService
from app.risk.models import RiskAssessment
from app.risk.projection import GeoSpatialProjectionService
from app.risk.service import RiskService


@dataclass(frozen=True, slots=True)
class GeometryEntity:
    entity_id: str
    layer: str
    geometry_type: str
    coordinates: Any
    properties: dict[str, Any]


class GeoIntelligenceService:
    def __init__(self, graph_query_service: GraphQueryService, risk_service: RiskService, projection_service: GeoSpatialProjectionService | None = None) -> None:
        self.graph_query_service = graph_query_service
        self.risk_service = risk_service
        self.projection_service = projection_service or GeoSpatialProjectionService(graph_query_service)

    async def layout(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("layout")
        blueprint = await self._blueprint(latest)
        features = blueprint["features"]
        return {
            "type": "FeatureCollection",
            "features": features,
            "summary": {
                "plant_id": latest.plant_id,
                "zone_id": latest.zone_id,
                "layout_type": "plant-blueprint",
                "feature_count": len(features),
                "risk_id": str(latest.risk_id),
            },
        }

    async def heatmap(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("heatmap")
        projection = await self.projection_service.project_assessment(latest)
        heat_features = [feature for feature in projection["features"] if feature["properties"].get("heat_intensity", 0) > 0]
        return {"type": "FeatureCollection", "features": heat_features, "summary": {**projection["summary"], "feature_count": len(heat_features)}}

    async def hazards(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("hazards")
        blueprint = await self._blueprint(latest)
        hazard_features = [feature for feature in blueprint["features"] if feature["properties"].get("layer") == "hazard"]
        return {"type": "FeatureCollection", "features": hazard_features, "summary": {"count": len(hazard_features), "risk_id": str(latest.risk_id)}}

    async def routes(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("routes")
        blueprint = await self._blueprint(latest)
        routes = self._evacuation_routes(latest, blueprint["entities"])
        return {"type": "FeatureCollection", "features": routes, "summary": {"count": len(routes), "risk_id": str(latest.risk_id)}}

    async def evacuation(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("evacuation")
        blueprint = await self._blueprint(latest)
        routes = self._evacuation_routes(latest, blueprint["entities"])
        assembly_points = [entity for entity in blueprint["entities"] if entity.layer == "assembly_point"]
        return {
            "type": "FeatureCollection",
            "features": routes,
            "summary": {
                "risk_id": str(latest.risk_id),
                "safe_assembly_points": [self._serialize_entity(entity) for entity in assembly_points],
                "route_count": len(routes),
            },
        }

    async def exposure(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("exposure")
        blueprint = await self._blueprint(latest)
        exposure_features = [feature for feature in blueprint["features"] if feature["properties"].get("layer") in {"worker", "equipment", "hazard"}]
        for feature in exposure_features:
            feature["properties"]["exposure_radius_meters"] = self._exposure_radius(feature["properties"].get("risk_score", latest.risk_score), feature["properties"].get("layer"))
        return {"type": "FeatureCollection", "features": exposure_features, "summary": {"count": len(exposure_features), "risk_id": str(latest.risk_id)}}

    async def clusters(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("clusters")
        projection = await self.projection_service.project_assessment(latest)
        clusters = self._cluster_features(projection["features"])
        return {"type": "FeatureCollection", "features": clusters, "summary": {"count": len(clusters), "risk_id": str(latest.risk_id)}}

    async def resources(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return self._empty_collection("resources")
        blueprint = await self._blueprint(latest)
        resources = [feature for feature in blueprint["features"] if feature["properties"].get("layer") in {"emergency_exit", "assembly_point", "road", "walkway"}]
        return {"type": "FeatureCollection", "features": resources, "summary": {"count": len(resources), "risk_id": str(latest.risk_id)}}

    async def nearest_safe_zone(self, session, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        latest = await self.risk_service.latest(session, plant_id=plant_id, zone_id=zone_id)
        if latest is None:
            return {"safe_zone": None, "distance_meters": 0, "reason": "no-risk-assessment"}
        blueprint = await self._blueprint(latest)
        zone_entities = [entity for entity in blueprint["entities"] if entity.layer == "assembly_point"]
        if not zone_entities:
            return {"safe_zone": None, "distance_meters": 0, "reason": "no-assembly-point"}
        hazard_anchor = self._anchor(f"{latest.plant_id}:{latest.zone_id}:{latest.risk_id}")
        nearest = min(zone_entities, key=lambda entity: self._distance_meters(hazard_anchor, entity.coordinates))
        return {
            "safe_zone": self._serialize_entity(nearest),
            "distance_meters": round(self._distance_meters(hazard_anchor, nearest.coordinates), 2),
            "risk_id": str(latest.risk_id),
        }

    async def _blueprint(self, assessment: RiskAssessment) -> dict[str, Any]:
        nodes = await self.graph_query_service.zone_graph(assessment.zone_id)
        entities: list[GeometryEntity] = [
            GeometryEntity(entity_id=f"zone:{assessment.zone_id}", layer="zone", geometry_type="Polygon", coordinates=self._polygon(self._anchor(assessment.zone_id), assessment.risk_score), properties={"plant_id": assessment.plant_id, "zone_id": assessment.zone_id, "risk_id": str(assessment.risk_id), "layer": "zone"}),
            GeometryEntity(entity_id=f"building:{assessment.plant_id}:main", layer="building", geometry_type="Polygon", coordinates=self._polygon(self._anchor(f"{assessment.plant_id}:building"), 60), properties={"plant_id": assessment.plant_id, "layer": "building"}),
            GeometryEntity(entity_id=f"exit:{assessment.zone_id}:north", layer="emergency_exit", geometry_type="Point", coordinates=self._offset(self._anchor(assessment.zone_id), 0.002, 0.001), properties={"plant_id": assessment.plant_id, "layer": "emergency_exit"}),
            GeometryEntity(entity_id=f"assembly:{assessment.plant_id}:alpha", layer="assembly_point", geometry_type="Point", coordinates=self._offset(self._anchor(assessment.zone_id), 0.006, -0.004), properties={"plant_id": assessment.plant_id, "layer": "assembly_point"}),
            GeometryEntity(entity_id=f"road:{assessment.plant_id}:primary", layer="road", geometry_type="LineString", coordinates=[self._offset(self._anchor(assessment.zone_id), -0.01, -0.004), self._offset(self._anchor(assessment.zone_id), 0.01, 0.004)], properties={"plant_id": assessment.plant_id, "layer": "road"}),
            GeometryEntity(entity_id=f"walkway:{assessment.zone_id}:1", layer="walkway", geometry_type="LineString", coordinates=[self._offset(self._anchor(assessment.zone_id), -0.004, 0.006), self._offset(self._anchor(assessment.zone_id), 0.003, -0.006)], properties={"plant_id": assessment.plant_id, "layer": "walkway"}),
            GeometryEntity(entity_id=f"utility:{assessment.zone_id}:corridor", layer="utility_corridor", geometry_type="LineString", coordinates=[self._offset(self._anchor(assessment.zone_id), -0.006, 0.002), self._offset(self._anchor(assessment.zone_id), 0.006, 0.002)], properties={"plant_id": assessment.plant_id, "layer": "utility_corridor"}),
            GeometryEntity(entity_id=f"pipeline:{assessment.zone_id}:feed", layer="pipeline", geometry_type="LineString", coordinates=[self._offset(self._anchor(assessment.zone_id), -0.005, -0.003), self._offset(self._anchor(assessment.zone_id), 0.005, 0.003)], properties={"plant_id": assessment.plant_id, "layer": "pipeline"}),
            GeometryEntity(entity_id=f"tank:{assessment.zone_id}:storage", layer="storage_tank", geometry_type="Point", coordinates=self._offset(self._anchor(assessment.zone_id), 0.008, 0.005), properties={"plant_id": assessment.plant_id, "layer": "storage_tank"}),
        ]
        for node in nodes:
            entity = self._entity_from_record(node, default_layer="hazard")
            if entity is not None:
                entities.append(entity)
        features = [self._feature_from_entity(entity, assessment) for entity in entities]
        return {"entities": entities, "features": features}

    def _entity_from_record(self, record: dict[str, Any], default_layer: str) -> GeometryEntity | None:
        candidate = None
        for value in record.values():
            if isinstance(value, dict) and value.get("node_id"):
                candidate = value
                break
        if candidate is None:
            return None
        node_id = str(candidate.get("node_id"))
        coordinates = self._extract_coordinates(candidate) or self._anchor(node_id)
        return GeometryEntity(
            entity_id=node_id,
            layer=default_layer,
            geometry_type="Point",
            coordinates=coordinates,
            properties={"node_type": candidate.get("node_type"), "properties": candidate.get("properties", candidate), "layer": default_layer},
        )

    def _feature_from_entity(self, entity: GeometryEntity, assessment: RiskAssessment) -> dict[str, Any]:
        geometry = self._geometry(entity.geometry_type, entity.coordinates, assessment.risk_score)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                **entity.properties,
                "id": entity.entity_id,
                "layer": entity.layer,
                "plant_id": assessment.plant_id,
                "zone_id": assessment.zone_id,
                "risk_id": str(assessment.risk_id),
                "risk_score": assessment.risk_score,
                "risk_level": assessment.risk_level,
                "confidence": assessment.confidence,
                "heat_intensity": round(self._heat_intensity(assessment.risk_score, assessment.confidence), 3),
                "radius_meters": self._radius_from_score(assessment.risk_score),
            },
        }

    def _evacuation_routes(self, assessment: RiskAssessment, entities: list[GeometryEntity]) -> list[dict[str, Any]]:
        hazard_anchor = self._anchor(f"{assessment.plant_id}:{assessment.zone_id}:{assessment.risk_id}")
        exits = [entity for entity in entities if entity.layer == "emergency_exit"] or [GeometryEntity("fallback-exit", "emergency_exit", "Point", self._offset(hazard_anchor, 0.004, 0.004), {"layer": "emergency_exit"})]
        routes: list[dict[str, Any]] = []
        for index, exit_entity in enumerate(exits):
            route_geometry = {
                "type": "LineString",
                "coordinates": [list(hazard_anchor), list(exit_entity.coordinates)],
            }
            routes.append(
                {
                    "type": "Feature",
                    "geometry": route_geometry,
                    "properties": {
                        "layer": "route",
                        "route_type": "evacuation",
                        "route_index": index,
                        "risk_id": str(assessment.risk_id),
                        "plant_id": assessment.plant_id,
                        "zone_id": assessment.zone_id,
                        "distance_meters": round(self._distance_meters(hazard_anchor, exit_entity.coordinates), 2),
                        "safe_zone_id": exit_entity.entity_id,
                    },
                }
            )
        return routes

    def _cluster_features(self, features: list[dict[str, Any]]) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        by_layer: dict[str, list[dict[str, Any]]] = {}
        for feature in features:
            by_layer.setdefault(feature["properties"].get("layer", "unknown"), []).append(feature)
        for index, (layer, items) in enumerate(by_layer.items()):
            coordinates = self._cluster_center(items)
            clusters.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": list(coordinates)},
                    "properties": {"layer": "cluster", "cluster_index": index, "cluster_type": layer, "feature_count": len(items), "heat_intensity": max(item["properties"].get("heat_intensity", 0) for item in items)},
                }
            )
        return clusters

    def _cluster_center(self, features: list[dict[str, Any]]) -> tuple[float, float]:
        coordinates = [feature["geometry"]["coordinates"] for feature in features if feature.get("geometry")]
        if not coordinates:
            return 0.0, 0.0
        longitudes = [coord[0] for coord in coordinates if coord]
        latitudes = [coord[1] for coord in coordinates if coord]
        if not longitudes or not latitudes:
            return 0.0, 0.0
        return round(sum(longitudes) / len(longitudes), 6), round(sum(latitudes) / len(latitudes), 6)

    def _geometry(self, geometry_type: str, coordinates: Any, radius_meters: float) -> dict[str, Any]:
        if geometry_type == "Polygon":
            return {"type": "Polygon", "coordinates": [self._circle(tuple(coordinates), radius_meters)]}
        if geometry_type == "LineString":
            return {"type": "LineString", "coordinates": [list(point) for point in coordinates]}
        if geometry_type == "MultiLineString":
            return {"type": "MultiLineString", "coordinates": coordinates}
        return {"type": "Point", "coordinates": [round(coordinates[0], 6), round(coordinates[1], 6)]}

    def _circle(self, coordinates: tuple[float, float], radius_meters: float, segments: int = 16) -> list[list[float]]:
        longitude, latitude = coordinates
        radius_degrees = max(radius_meters, 1) / 111_000.0
        points: list[list[float]] = []
        for index in range(segments + 1):
            angle = 2 * 3.141592653589793 * (index / segments)
            points.append([round(longitude + radius_degrees * cos(angle), 6), round(latitude + radius_degrees * sin(angle), 6)])
        return points

    def _polygon(self, coordinates: tuple[float, float], radius_meters: float) -> list[list[float]]:
        return self._circle(coordinates, radius_meters)

    def _offset(self, coordinates: tuple[float, float], dx: float, dy: float) -> tuple[float, float]:
        return round(coordinates[0] + dx, 6), round(coordinates[1] + dy, 6)

    def _anchor(self, value: str) -> tuple[float, float]:
        digest = sha256(value.encode("utf-8")).digest()
        longitude = ((int.from_bytes(digest[:4], "big") % 360000) / 1000.0) - 180.0
        latitude = ((int.from_bytes(digest[4:8], "big") % 180000) / 1000.0) - 90.0
        return round(longitude, 6), round(latitude, 6)

    def _extract_coordinates(self, entity: dict[str, Any]) -> tuple[float, float] | None:
        properties = entity.get("properties", {})
        for latitude_key, longitude_key in (("latitude", "longitude"), ("lat", "lon"), ("y", "x")):
            if latitude_key in properties and longitude_key in properties:
                return float(properties[longitude_key]), float(properties[latitude_key])
        if "coordinates" in properties and isinstance(properties["coordinates"], (list, tuple)) and len(properties["coordinates"]) >= 2:
            lon, lat = properties["coordinates"][0], properties["coordinates"][1]
            return float(lon), float(lat)
        return None

    def _distance_meters(self, left: tuple[float, float], right: tuple[float, float]) -> float:
        earth_radius = 6_371_000.0
        lon1, lat1 = radians(left[0]), radians(left[1])
        lon2, lat2 = radians(right[0]), radians(right[1])
        delta_lon = lon2 - lon1
        delta_lat = lat2 - lat1
        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        return 2 * earth_radius * atan2(sqrt(a), sqrt(1 - a))

    def _heat_intensity(self, score: float, confidence: float) -> float:
        return min(1.0, max(0.05, (score / 100.0) * (0.5 + confidence / 2.0)))

    def _radius_from_score(self, score: float) -> float:
        return max(15.0, min(150.0, score * 1.5))

    def _exposure_radius(self, score: float, layer: str) -> float:
        multipliers = {"worker": 1.0, "equipment": 1.3, "hazard": 1.6}
        return round(self._radius_from_score(score) * multipliers.get(layer, 1.0), 2)

    def _empty_collection(self, name: str) -> dict[str, Any]:
        return {"type": "FeatureCollection", "features": [], "summary": {"count": 0, "layer": name}}

    def _serialize_entity(self, entity: GeometryEntity) -> dict[str, Any]:
        return {
            "id": entity.entity_id,
            "layer": entity.layer,
            "geometry_type": entity.geometry_type,
            "coordinates": entity.coordinates,
            "properties": entity.properties,
        }
