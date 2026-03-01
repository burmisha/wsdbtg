import math

from bot.models import Activity, TrackPoint


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def build_activity(filename: str, points: list[TrackPoint], source_distance_m: float | None) -> Activity:
    recorded_at = points[0].timestamp if points else None
    duration_s = (points[-1].timestamp - points[0].timestamp).total_seconds() if points else None
    hr_values = [p.hr for p in points if p.hr is not None]
    distance_m = (
        sum(
            _haversine(points[i].lat, points[i].lon, points[i + 1].lat, points[i + 1].lon)
            for i in range(len(points) - 1)
            if points[i].segment_id == points[i + 1].segment_id
        )
        if len(points) >= 2
        else None
    )
    return Activity(
        filename=filename,
        recorded_at=recorded_at,
        distance_m=distance_m,
        source_distance_m=source_distance_m,
        duration_s=duration_s,
        avg_hr=sum(hr_values) / len(hr_values) if hr_values else None,
        max_hr=max(hr_values) if hr_values else None,
        points=points,
    )
