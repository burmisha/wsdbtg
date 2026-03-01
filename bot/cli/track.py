import argparse
import sys
from datetime import datetime
from pathlib import Path

from bot.cli import colors
from bot.logging import get_logger
from bot.models import Activity, TrackPoint
from bot.parsers import parse

logger = get_logger(__name__)


def _format_activity(activity: Activity) -> str:
    parts = [f'Файл: {activity.filename}']
    if activity.recorded_at:
        parts.append(f'Дата: {activity.recorded_at.strftime("%Y-%m-%d %H:%M")}')
    if activity.distance_m:
        parts.append(f'Дистанция: {activity.distance_m / 1000:.2f} км')
    if activity.source_distance_m:
        parts.append(f'Дистанция (файл): {activity.source_distance_m / 1000:.2f} км')
    if activity.duration_s:
        m, s = divmod(int(activity.duration_s), 60)
        parts.append(f'Время: {m}:{s:02d}')
    if activity.avg_hr:
        parts.append(f'Пульс: {activity.avg_hr:.0f} уд/мин (макс {activity.max_hr})')
    parts.append(f'Точек: {len(activity.points)}')
    if activity.points:
        p = activity.points[0]
        parts.append(f'Старт: https://yandex.ru/maps/?pt={p.lon},{p.lat}&z=14')
    return '\n'.join(parts)


def _format_elapsed(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'


def _elevation_icon(delta: float) -> str:
    if delta > 0.1:
        return '↑'
    if delta < -0.1:
        return '↓'
    return '→'


def _format_point(
    point: TrackPoint,
    start_time: datetime,
    min_elevation: float,
    prev_elevation: float | None,
) -> str:
    elapsed = int((point.timestamp - start_time).total_seconds())
    elapsed_str = f'(+{_format_elapsed(elapsed)})'
    parts = [
        f'{point.timestamp.strftime("%H:%M:%S")} {elapsed_str}',
        f'seg={point.segment_id}',
        f'lat={point.lat:9.6f} lon={point.lon:9.6f}',
    ]
    if point.elevation_m is not None:
        rel = point.elevation_m - min_elevation
        delta = point.elevation_m - prev_elevation if prev_elevation is not None else 0.0
        icon = _elevation_icon(delta)
        rel_str = colors.elevation_colored(f'+{rel:5.1f}m {icon}', delta)
        parts.append(f'ele={point.elevation_m:6.1f}m ({rel_str})')
    if point.hr is not None:
        parts.append(f'hr={colors.hr_colored(f"{point.hr:3d}", point.hr)}')
    return ' | '.join(parts)


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser('track', help='Статистика трека из файла')
    p.add_argument(
        '--track',
        type=Path,
        action='append',
        required=True,
        metavar='FILE',
        dest='tracks',
        help='Путь к файлу (.fit, .gpx, .tcx), можно указать несколько раз',
    )
    p.add_argument('--points', action='store_true', help='Вывести все точки трека')
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    has_errors = False
    for path in args.tracks:
        if not path.exists():
            logger.error('Файл не найден: %s', path)
            has_errors = True
            continue

        try:
            activity = parse(path.name, path.read_bytes())
        except ValueError as e:
            logger.error('Ошибка в %s: %s', path, e)
            has_errors = True
            continue

        logger.info(_format_activity(activity))
        if args.points and activity.points:
            start_time = activity.points[0].timestamp
            elevations = [p.elevation_m for p in activity.points if p.elevation_m is not None]
            min_elevation = min(elevations) if elevations else 0.0
            prev_elevation: float | None = None
            for point in activity.points:
                logger.info(_format_point(point, start_time, min_elevation, prev_elevation))
                if point.elevation_m is not None:
                    prev_elevation = point.elevation_m

    if has_errors:
        sys.exit(1)
