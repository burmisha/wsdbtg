import colorama
from colorama import Fore, Style


def init() -> None:
    colorama.init()


def green(text: str) -> str:
    return f'{Style.NORMAL}{Fore.GREEN}{text}{Style.RESET_ALL}'


def yellow(text: str) -> str:
    return f'{Style.NORMAL}{Fore.YELLOW}{text}{Style.RESET_ALL}'


def red(text: str) -> str:
    return f'{Fore.RED}{text}{Style.RESET_ALL}'


def hr_colored(text: str, hr: int) -> str:
    if hr > 170:
        return red(text)
    if hr >= 160:
        return yellow(text)
    if hr >= 130:
        return green(text)
    return text


def elevation_colored(text: str, delta: float) -> str:
    if delta > 0.2:
        return yellow(text)
    if delta < -0.2:
        return green(text)
    return text
