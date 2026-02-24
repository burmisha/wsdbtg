import sys
from pathlib import Path


def parse_keys(path: Path) -> set[str]:
    keys = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key = line.split('=', 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def main() -> None:
    root = Path(__file__).parent.parent
    env_file = root / '.env'
    example_file = root / '.env.example'

    if not env_file.exists():
        print(f'error: {env_file} not found')
        sys.exit(1)

    env_keys = parse_keys(env_file)
    example_keys = parse_keys(example_file)

    missing_in_env = example_keys - env_keys
    extra_in_env = env_keys - example_keys

    if missing_in_env:
        print(f'missing in .env: {", ".join(sorted(missing_in_env))}')
    if extra_in_env:
        print(f'missing in .env.example: {", ".join(sorted(extra_in_env))}')

    if missing_in_env or extra_in_env:
        sys.exit(1)

    print('.env and .env.example are in sync')


if __name__ == '__main__':
    main()
