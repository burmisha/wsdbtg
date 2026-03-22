from dataclasses import dataclass

from bot.models import Activity
from bot.parsers.common import _haversine


@dataclass
class PointMetrics:
    elapsed_s: float
    distance_km: float  # cumulative from activity start, within segment
    pace_min_km: float | None  # None for first point, stops (>20 min/km), and segment breaks
    hr: int | None
    elevation_m: float | None


def compute(activity: Activity) -> list[PointMetrics]:
    """Compute per-point derived metrics (pace, cumulative distance) from an Activity."""
    if not activity.points:
        return []

    start = activity.points[0].timestamp
    dist_m = 0.0
    result = []

    for i, p in enumerate(activity.points):
        elapsed_s = (p.timestamp - start).total_seconds()

        pace: float | None = None
        if i > 0:
            prev = activity.points[i - 1]
            if p.segment_id == prev.segment_id:
                d = _haversine(prev.lat, prev.lon, p.lat, p.lon)
                dist_m += d
                dt = (p.timestamp - prev.timestamp).total_seconds()
                if dt > 0 and d > 0:
                    pace_raw = 1000 / (d / dt) / 60  # min/km
                    if pace_raw < 20:  # cap: ignore stops and GPS glitches
                        pace = pace_raw

        result.append(
            PointMetrics(
                elapsed_s=elapsed_s,
                distance_km=dist_m / 1000,
                pace_min_km=pace,
                hr=p.hr,
                elevation_m=p.elevation_m,
            )
        )

    return result
