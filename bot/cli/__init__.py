import argparse

from bot.cli import track
from bot.logging import setup_logging


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(prog='wsdbtg')
    subparsers = parser.add_subparsers(dest='command', required=True)
    track.add_subparser(subparsers)
    args = parser.parse_args()
    args.func(args)
