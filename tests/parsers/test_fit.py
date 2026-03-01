from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from bot.parsers import parse


def test_parse_fit():
    _SEMICIRCLE = 180 / 2**31
    ts = datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc)

    mock_record = MagicMock()
    mock_record.get_value.side_effect = lambda f: {
        'position_lat': int(55.7558 / _SEMICIRCLE),
        'position_long': int(37.6176 / _SEMICIRCLE),
        'timestamp': ts,
        'altitude': 150.0,
        'heart_rate': 140,
    }.get(f)

    mock_session = MagicMock()
    mock_session.get_value.return_value = 5000.0

    def get_messages(msg_type):
        return [mock_record] if msg_type == 'record' else [mock_session]

    with patch('bot.parsers.fit.FitFile') as MockFitFile:
        MockFitFile.return_value.get_messages.side_effect = get_messages
        activity = parse('activity.fit', b'fake')

    assert len(activity.points) == 1
    assert activity.points[0].segment_id == 0
    assert activity.points[0].lat == pytest.approx(55.7558, abs=0.001)
    assert activity.points[0].elevation_m == pytest.approx(150.0)
    assert activity.distance_m is None
    assert activity.source_distance_m == pytest.approx(5000.0)
