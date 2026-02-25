import os
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent


def _parse_keys(path: Path) -> set[str]:
    keys = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key = line.split('=', 1)[0].strip()
        if key:
            keys.add(key)
    return keys


@pytest.mark.skipif(os.getenv('CI') == 'true', reason='no .env in CI')
def test_env_in_sync_with_example():
    env_keys = _parse_keys(_ROOT / '.env')
    example_keys = _parse_keys(_ROOT / '.env.example')

    missing_in_env = example_keys - env_keys
    extra_in_env = env_keys - example_keys

    assert not missing_in_env, f'missing in .env: {", ".join(sorted(missing_in_env))}'
    assert not extra_in_env, f'missing in .env.example: {", ".join(sorted(extra_in_env))}'
