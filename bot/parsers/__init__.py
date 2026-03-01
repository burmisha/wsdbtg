from typing import Callable

from bot.models import Activity, TrackPoint
from bot.parsers.common import build_activity
from bot.parsers.fit import parse_fit
from bot.parsers.gpx import parse_gpx
from bot.parsers.tcx import parse_tcx

_PARSERS: dict[str, Callable[[bytes], tuple[list[TrackPoint], float | None]]] = {
    'fit': parse_fit,
    'gpx': parse_gpx,
    'tcx': parse_tcx,
}

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(f'.{ext}' for ext in _PARSERS)


def parse(filename: str, data: bytes) -> Activity:
    ext = filename.rsplit('.', 1)[-1].lower()
    parser = _PARSERS.get(ext)
    if parser is None:
        raise ValueError(f'Unsupported format: {ext}')
    points, source_distance_m = parser(data)
    return build_activity(filename, points, source_distance_m)
