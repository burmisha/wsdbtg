import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.table import Table

from bot.cli import colors
from bot.logging import get_logger
from bot.models import Activity, TrackPoint
from bot.parsers import SUPPORTED_EXTENSIONS, parse

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


@dataclass
class _PointRow:
    point: TrackPoint
    elapsed_s: int
    rel_elevation_m: float | None
    delta_elevation_m: float | None


def _prepare_rows(activity: Activity) -> list[_PointRow]:
    min_ele = activity.min_elevation_m
    prev_elevation: float | None = None
    rows = []
    for point in activity.points:
        elapsed_s = int((point.timestamp - activity.recorded_at).total_seconds()) if activity.recorded_at else 0
        rel = (point.elevation_m - min_ele) if (point.elevation_m is not None and min_ele is not None) else None
        delta = (
            (point.elevation_m - prev_elevation)
            if (point.elevation_m is not None and prev_elevation is not None)
            else None
        )
        rows.append(_PointRow(point=point, elapsed_s=elapsed_s, rel_elevation_m=rel, delta_elevation_m=delta))
        if point.elevation_m is not None:
            prev_elevation = point.elevation_m
    return rows


def _row_cells(row: _PointRow) -> tuple[str, str, str, str, str]:
    elapsed_str = f'+{_format_elapsed(row.elapsed_s)}'
    time_cell = f'[{row.point.timestamp.strftime("%H:%M:%S")}] {elapsed_str}'
    seg_cell = f'{row.point.segment_id}'
    coords_cell = f'lat={row.point.lat:9.6f} lon={row.point.lon:9.6f}'

    if row.rel_elevation_m is not None:
        delta = row.delta_elevation_m or 0.0
        icon = _elevation_icon(delta)
        rel_str = colors.elevation_colored(f'+{row.rel_elevation_m:5.1f}m {icon}', delta)
        ele_cell = f'{row.point.elevation_m:6.1f}m ({rel_str})'
    else:
        ele_cell = ''

    hr_cell = f'{colors.hr_colored(f"{row.point.hr:3d}", row.point.hr)}' if row.point.hr is not None else ''

    return time_cell, seg_cell, coords_cell, ele_cell, hr_cell


def _build_points_table(activity: Activity) -> Table:
    table = Table(box=None, show_header=True, padding=(0, 1))
    table.add_column('time', no_wrap=True)
    table.add_column('seg', no_wrap=True)
    table.add_column('coordinates', no_wrap=True)
    table.add_column('elevation', no_wrap=True)
    table.add_column('HR', no_wrap=True)
    for row in _prepare_rows(activity):
        table.add_row(*_row_cells(row))
    return table


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser('track', help='Статистика трека из файла')
    p.add_argument(
        '--track',
        type=Path,
        action='append',
        required=True,
        metavar='FILE',
        dest='tracks',
        help=f'Путь к файлу ({", ".join(sorted(SUPPORTED_EXTENSIONS))}), можно указать несколько раз',
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

        colors.console.print(_format_activity(activity))
        if args.points and activity.points:
            colors.console.print(_build_points_table(activity))

    if has_errors:
        sys.exit(1)
