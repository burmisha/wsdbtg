from datetime import datetime

from lxml import etree

from bot.models import TrackPoint

_NS = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}


def parse_tcx(data: bytes) -> tuple[list[TrackPoint], float | None]:
    root = etree.fromstring(data)

    points = []
    for segment_id, lap in enumerate(root.findall('.//tcx:Lap', _NS)):
        for tp in lap.findall('.//tcx:Trackpoint', _NS):
            time_el = tp.find('tcx:Time', _NS)
            lat_el = tp.find('tcx:Position/tcx:LatitudeDegrees', _NS)
            lon_el = tp.find('tcx:Position/tcx:LongitudeDegrees', _NS)
            if time_el is None or lat_el is None or lon_el is None:
                continue

            alt_el = tp.find('tcx:AltitudeMeters', _NS)
            hr_el = tp.find('tcx:HeartRateBpm/tcx:Value', _NS)

            points.append(
                TrackPoint(
                    timestamp=datetime.fromisoformat(time_el.text.replace('Z', '+00:00')),
                    lat=float(lat_el.text),
                    lon=float(lon_el.text),
                    segment_id=segment_id,
                    elevation_m=float(alt_el.text) if alt_el is not None else None,
                    hr=int(hr_el.text) if hr_el is not None else None,
                )
            )

    source_distance_m = None
    dist_els = root.findall('.//tcx:Trackpoint/tcx:DistanceMeters', _NS)
    if dist_els:
        try:
            source_distance_m = float(dist_els[-1].text)
        except (ValueError, TypeError):
            pass

    return points, source_distance_m
