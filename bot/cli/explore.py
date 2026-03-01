import argparse
import threading
import webbrowser
from pathlib import Path

import uvicorn

from bot.logging import get_logger
from bot.parsers import parse

logger = get_logger(__name__)


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser('explore', help='Открыть трек в браузере')
    p.add_argument(
        '--track',
        type=Path,
        required=False,
        default=None,
        metavar='FILE',
        help='Путь к файлу трека (если не указан — ожидает drag-and-drop в браузере)',
    )
    p.add_argument('--port', type=int, default=8765, metavar='PORT', help='Порт локального сервера (по умолчанию 8765)')
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    from bot.web import server

    if args.track is not None:
        if not args.track.exists():
            logger.error('Файл не найден: %s', args.track)
            return
        try:
            activity = parse(args.track.name, args.track.read_bytes())
        except ValueError as e:
            logger.error('Ошибка в %s: %s', args.track, e)
            return
        server.set_activity(activity)

    url = f'http://127.0.0.1:{args.port}'
    logger.info('Сервер запущен: %s  (Ctrl+C для остановки)', url)
    threading.Timer(0.5, webbrowser.open, args=[url]).start()

    uvicorn.run(server.app, host='127.0.0.1', port=args.port, log_level='warning')
