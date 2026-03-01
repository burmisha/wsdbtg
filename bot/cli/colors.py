from rich.console import Console

console = Console()


def hr_colored(text: str, hr: int) -> str:
    if hr > 170:
        return f'[red]{text}[/red]'
    if hr >= 160:
        return f'[yellow]{text}[/yellow]'
    if hr >= 130:
        return f'[green]{text}[/green]'
    return text


def elevation_colored(text: str, delta: float) -> str:
    if delta > 0.2:
        return f'[yellow]{text}[/yellow]'
    if delta < -0.2:
        return f'[green]{text}[/green]'
    return text
