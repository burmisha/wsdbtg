import logging


def setup_logging(level: str = 'INFO') -> None:
    valid_levels = logging.getLevelNamesMapping()
    if level.upper() not in valid_levels:
        raise ValueError(f'invalid logging level {level!r}, valid values: {", ".join(sorted(valid_levels))}')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=valid_levels[level.upper()],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
