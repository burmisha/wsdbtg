from datetime import datetime, timezone

import pytest

from bot.parsers import parse

_GPX = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><trkseg>
    <trkpt lat="55.7558" lon="37.6176">
      <ele>150.0</ele>
      <time>2024-03-15T10:00:00Z</time>
    </trkpt>
    <trkpt lat="55.7560" lon="37.6180">
      <ele>151.0</ele>
      <time>2024-03-15T10:01:00Z</time>
    </trkpt>
  </trkseg></trk>
</gpx>"""

_GPX_TWO_SEGMENTS = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <trkseg>
      <trkpt lat="55.7558" lon="37.6176"><time>2024-03-15T10:00:00Z</time></trkpt>
      <trkpt lat="55.7560" lon="37.6180"><time>2024-03-15T10:01:00Z</time></trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="55.7600" lon="37.6300"><time>2024-03-15T10:10:00Z</time></trkpt>
      <trkpt lat="55.7602" lon="37.6304"><time>2024-03-15T10:11:00Z</time></trkpt>
    </trkseg>
  </trk>
</gpx>"""


def test_parse_gpx():
    activity = parse('run.gpx', _GPX)
    assert len(activity.points) == 2
    assert activity.points[0].lat == pytest.approx(55.7558)
    assert activity.points[0].lon == pytest.approx(37.6176)
    assert activity.points[0].elevation_m == pytest.approx(150.0)
    assert activity.points[0].segment_id == 0
    assert activity.points[1].segment_id == 0
    assert activity.recorded_at == datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc)
    assert activity.duration_s == pytest.approx(60.0)
    assert activity.distance_m is not None and activity.distance_m > 0


def test_parse_gpx_two_segments():
    activity = parse('run.gpx', _GPX_TWO_SEGMENTS)
    assert len(activity.points) == 4
    assert activity.points[0].segment_id == 0
    assert activity.points[1].segment_id == 0
    assert activity.points[2].segment_id == 1
    assert activity.points[3].segment_id == 1
    # дистанция считается только внутри сегментов, не между ними
    assert activity.distance_m is not None
    assert activity.distance_m < 5000
