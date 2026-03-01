from io import BytesIO

from fitparse import FitFile

from bot.models import TrackPoint

_SEMICIRCLE_TO_DEGREES = 180 / 2**31


def parse_fit(data: bytes) -> tuple[list[TrackPoint], float | None]:
    fitfile = FitFile(BytesIO(data))

    points = []
    for record in fitfile.get_messages('record'):
        lat = record.get_value('position_lat')
        lon = record.get_value('position_long')
        ts = record.get_value('timestamp')
        if lat is None or lon is None or ts is None:
            continue
        points.append(
            TrackPoint(
                timestamp=ts,
                lat=lat * _SEMICIRCLE_TO_DEGREES,
                lon=lon * _SEMICIRCLE_TO_DEGREES,
                elevation_m=record.get_value('altitude'),
                hr=record.get_value('heart_rate'),
            )
        )

    source_distance_m = None
    for session in fitfile.get_messages('session'):
        source_distance_m = session.get_value('total_distance')
        break

    return points, source_distance_m
