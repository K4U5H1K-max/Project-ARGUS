from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import cos, pi, sin
from typing import Any

from app.risk.models import RiskAssessment


@dataclass(frozen=True)
class PlantBlueprint:
    plant_id: str
    zones: list[dict[str, Any]]
    workers: list[dict[str, Any]]
    equipment: list[dict[str, Any]]
    hazards: list[dict[str, Any]]


class GeoSpatialProjectionService:
    def __init__(self, graph_query_service: Any) -> None:
        self.graph_query_service = graph_query_service

    async def project_assessment(self, assessment: RiskAssessment) -> dict[str, Any]:
        blueprint = await self._blueprint(assessment.plant_id, assessment.zone_id)
        heat_intensity = self._heat_intensity(assessment.risk_score, assessment.confidence)
        features: list[dict[str, Any]] = []
        features.extend(self._layer_features("zone", blueprint.zones, assessment, heat_intensity, geometry_type="Polygon"))
        features.extend(self._layer_features("worker", blueprint.workers, assessment, heat_intensity * 0.75, geometry_type="Point"))
        features.extend(self._layer_features("equipment", blueprint.equipment, assessment, heat_intensity * 0.85, geometry_type="Point"))
        features.extend(self._layer_features("hazard", blueprint.hazards, assessment, heat_intensity, geometry_type="Point", radius_meters=max(assessment.risk_score, 10)))
        if not features:
            features.append(self._fallback_feature(assessment, heat_intensity))
        return {
            "type": "FeatureCollection",
            "features": features,
            "summary": {
                "plant_id": assessment.plant_id,
                "zone_id": assessment.zone_id,
                "risk_id": str(assessment.risk_id),
                "score": assessment.risk_score,
                "level": assessment.risk_level,
                "heat_intensity": heat_intensity,
                "clusters": self._cluster_count(features),
            },
        }

    async def zones(self, assessment: RiskAssessment) -> list[dict[str, Any]]:
        projection = await self.project_assessment(assessment)
        return [feature for feature in projection["features"] if feature["properties"].get("layer") == "zone"]

    async def workers(self, assessment: RiskAssessment) -> list[dict[str, Any]]:
        projection = await self.project_assessment(assessment)
        return [feature for feature in projection["features"] if feature["properties"].get("layer") == "worker"]

    async def equipment(self, assessment: RiskAssessment) -> list[dict[str, Any]]:
        projection = await self.project_assessment(assessment)
        return [feature for feature in projection["features"] if feature["properties"].get("layer") == "equipment"]

    async def hotspots(self, assessment: RiskAssessment) -> list[dict[str, Any]]:
        projection = await self.project_assessment(assessment)
        return [feature for feature in projection["features"] if feature["properties"].get("heat_intensity", 0) >= 0.5]

    async def _blueprint(self, plant_id: str, zone_id: str) -> PlantBlueprint:
        zone_nodes = await self._safe_query("node", "Zone", zone_id)
        worker_nodes = await self._safe_query("worker_exposure", zone_id)
        equipment_nodes = await self._safe_query("impact", zone_id)
        hazard_nodes = await self._safe_query("zone_graph", zone_id)
        return PlantBlueprint(
            plant_id=plant_id,
            zones=self._as_entities(zone_nodes, "zone"),
            workers=self._as_entities(worker_nodes, "worker"),
            equipment=self._as_entities(equipment_nodes, "equipment"),
            hazards=self._as_entities(hazard_nodes, "hazard"),
        )

    async def _safe_query(self, method_name: str, *args: Any) -> list[dict[str, Any]]:
        method = getattr(self.graph_query_service, method_name, None)
        if method is None:
            return []
        try:
            result = await method(*args)
        except Exception:
            return []
        return list(result or [])

    def _as_entities(self, records: list[dict[str, Any]], layer: str) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for record in records:
            entity = self._extract_entity(record)
            if entity is not None:
                entity["layer"] = layer
                entities.append(entity)
        return entities

    def _extract_entity(self, record: dict[str, Any]) -> dict[str, Any] | None:
        candidate = None
        for value in record.values():
            if isinstance(value, dict) and value.get("node_id"):
                candidate = value
                break
        if candidate is None:
            return None
        coordinates = self._extract_coordinates(candidate)
        if coordinates is None:
            coordinates = self._anchor(candidate.get("node_id", "unknown"))
        return {
            "id": candidate.get("node_id"),
            "node_type": candidate.get("node_type"),
            "properties": candidate.get("properties", candidate),
            "coordinates": coordinates,
        }

    def _layer_features(
        self,
        layer: str,
        entities: list[dict[str, Any]],
        assessment: RiskAssessment,
        heat_intensity: float,
        *,
        geometry_type: str,
        radius_meters: float | None = None,
    ) -> list[dict[str, Any]]:
        features: list[dict[str, Any]] = []
        for entity in entities:
            coordinates = entity.get("coordinates") or self._anchor(str(entity.get("id", assessment.zone_id)))
            geometry = self._geometry(geometry_type, coordinates, radius_meters or assessment.risk_score)
            features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "layer": layer,
                        "id": entity.get("id"),
                        "node_type": entity.get("node_type"),
                        "plant_id": assessment.plant_id,
                        "zone_id": assessment.zone_id,
                        "risk_id": str(assessment.risk_id),
                        "risk_score": assessment.risk_score,
                        "risk_level": assessment.risk_level,
                        "heat_intensity": round(heat_intensity, 3),
                        "radius_meters": radius_meters or self._radius_from_score(assessment.risk_score),
                        "properties": entity.get("properties", {}),
                    },
                }
            )
        return features

    def _fallback_feature(self, assessment: RiskAssessment, heat_intensity: float) -> dict[str, Any]:
        coordinates = self._anchor(assessment.zone_id)
        return {
            "type": "Feature",
            "geometry": self._geometry("Point", coordinates, assessment.risk_score),
            "properties": {
                "layer": "zone",
                "zone_id": assessment.zone_id,
                "plant_id": assessment.plant_id,
                "risk_id": str(assessment.risk_id),
                "risk_score": assessment.risk_score,
                "risk_level": assessment.risk_level,
                "heat_intensity": round(heat_intensity, 3),
                "radius_meters": self._radius_from_score(assessment.risk_score),
            },
        }

    def _geometry(self, geometry_type: str, coordinates: tuple[float, float], radius_meters: float) -> dict[str, Any]:
        if geometry_type == "Polygon":
            return {"type": "Polygon", "coordinates": [self._circle(coordinates, radius_meters)]}
        return {"type": "Point", "coordinates": [round(coordinates[0], 6), round(coordinates[1], 6)]}

    def _circle(self, coordinates: tuple[float, float], radius_meters: float, segments: int = 12) -> list[list[float]]:
        longitude, latitude = coordinates
        radius_degrees = max(radius_meters, 1) / 111_000.0
        ring: list[list[float]] = []
        for index in range(segments + 1):
            angle = 2 * pi * (index / segments)
            ring.append([round(longitude + radius_degrees * cos(angle), 6), round(latitude + radius_degrees * sin(angle), 6)])
        return ring

    def _extract_coordinates(self, entity: dict[str, Any]) -> tuple[float, float] | None:
        properties = entity.get("properties", {})
        for latitude_key, longitude_key in (("latitude", "longitude"), ("lat", "lon"), ("y", "x")):
            if latitude_key in properties and longitude_key in properties:
                return float(properties[longitude_key]), float(properties[latitude_key])
        if "coordinates" in properties and isinstance(properties["coordinates"], (list, tuple)) and len(properties["coordinates"]) >= 2:
            lon, lat = properties["coordinates"][0], properties["coordinates"][1]
            return float(lon), float(lat)
        if "geometry" in properties and isinstance(properties["geometry"], dict):
            geometry = properties["geometry"]
            if geometry.get("type") == "Point":
                lon, lat = geometry.get("coordinates", [0, 0])[:2]
                return float(lon), float(lat)
        return None

    def _anchor(self, value: str) -> tuple[float, float]:
        digest = sha256(value.encode("utf-8")).digest()
        longitude = ((int.from_bytes(digest[:4], "big") % 360000) / 1000.0) - 180.0
        latitude = ((int.from_bytes(digest[4:8], "big") % 180000) / 1000.0) - 90.0
        return round(longitude, 6), round(latitude, 6)

    def _heat_intensity(self, score: float, confidence: float) -> float:
        return min(1.0, max(0.05, (score / 100.0) * (0.5 + confidence / 2.0)))

    def _radius_from_score(self, score: float) -> float:
        return max(15.0, min(150.0, score * 1.5))

    def _cluster_count(self, features: list[dict[str, Any]]) -> int:
        return len({feature["properties"].get("layer") for feature in features if feature.get("properties")})