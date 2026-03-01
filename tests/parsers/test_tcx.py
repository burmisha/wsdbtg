from datetime import datetime, timezone

import pytest

from bot.parsers import parse

_TCX = b"""<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
  <Activities><Activity Sport="Running"><Lap>
    <Track>
      <Trackpoint>
        <Time>2024-03-15T10:00:00Z</Time>
        <Position>
          <LatitudeDegrees>55.7558</LatitudeDegrees>
          <LongitudeDegrees>37.6176</LongitudeDegrees>
        </Position>
        <AltitudeMeters>150.0</AltitudeMeters>
        <HeartRateBpm><Value>140</Value></HeartRateBpm>
        <DistanceMeters>0.0</DistanceMeters>
      </Trackpoint>
      <Trackpoint>
        <Time>2024-03-15T10:01:00Z</Time>
        <Position>
          <LatitudeDegrees>55.7560</LatitudeDegrees>
          <LongitudeDegrees>37.6180</LongitudeDegrees>
        </Position>
        <AltitudeMeters>151.0</AltitudeMeters>
        <HeartRateBpm><Value>150</Value></HeartRateBpm>
        <DistanceMeters>1000.0</DistanceMeters>
      </Trackpoint>
    </Track>
  </Lap></Activity></Activities>
</TrainingCenterDatabase>"""


def test_parse_tcx():
    activity = parse('run.tcx', _TCX)
    assert len(activity.points) == 2
    assert activity.points[0].lat == pytest.approx(55.7558)
    assert activity.points[0].hr == 140
    assert activity.points[0].segment_id == 0
    assert activity.points[1].segment_id == 0
    assert activity.recorded_at == datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc)
    assert activity.duration_s == pytest.approx(60.0)
    assert activity.distance_m == pytest.approx(33.4, abs=1.0)
    assert activity.source_distance_m == pytest.approx(1000.0)
    assert activity.avg_hr == pytest.approx(145.0)
    assert activity.max_hr == 150
