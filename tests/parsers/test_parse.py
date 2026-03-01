import pytest

from bot.parsers import parse


def test_parse_unsupported_raises():
    with pytest.raises(ValueError):
        parse('file.kml', b'data')
