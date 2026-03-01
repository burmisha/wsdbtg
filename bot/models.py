from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackPoint:
    timestamp: datetime
    lat: float
    lon: float
    segment_id: int = 0
    elevation_m: float | None = None
    hr: int | None = None


@dataclass
class Activity:
    filename: str
    recorded_at: datetime | None
    distance_m: float | None
    source_distance_m: float | None
    duration_s: float | None
    avg_hr: float | None
    max_hr: int | None
    points: list[TrackPoint] = field(default_factory=list)

    @property
    def min_elevation_m(self) -> float | None:
        elevations = [p.elevation_m for p in self.points if p.elevation_m is not None]
        return min(elevations) if elevations else None
