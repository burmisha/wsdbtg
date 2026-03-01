import gpxpy

from bot.models import TrackPoint


def _extract_hr(point: gpxpy.gpx.GPXTrackPoint) -> int | None:
    for ext in point.extensions:
        for child in ext:
            if child.tag.endswith('}hr') or child.tag == 'hr':
                try:
                    return int(child.text)
                except (ValueError, TypeError):
                    pass
    return None


def parse_gpx(data: bytes) -> tuple[list[TrackPoint], float | None]:
    gpx = gpxpy.parse(data.decode('utf-8'))

    points = []
    segment_id = 0
    for track in gpx.tracks:
        for segment in track.segments:
            for p in segment.points:
                if p.time is None:
                    continue
                points.append(
                    TrackPoint(
                        timestamp=p.time,
                        lat=p.latitude,
                        lon=p.longitude,
                        segment_id=segment_id,
                        elevation_m=p.elevation,
                        hr=_extract_hr(p),
                    )
                )
            segment_id += 1

    return points, gpx.length_2d() or None
