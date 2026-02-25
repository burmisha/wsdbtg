import asyncpg

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    user_id    BIGINT NOT NULL,
    prefix     TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


async def create_pool(dsn: str) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(dsn)
    await pool.execute(_CREATE_TABLE)
    return pool


async def save_message(pool: asyncpg.Pool, user_id: int, text: str) -> None:
    await pool.execute(
        'INSERT INTO messages (user_id, prefix) VALUES ($1, $2)',
        user_id,
        text[:5],
    )


async def get_history(pool: asyncpg.Pool, user_id: int) -> list[str]:
    rows = await pool.fetch(
        'SELECT prefix FROM messages WHERE user_id = $1 ORDER BY created_at DESC LIMIT 7',
        user_id,
    )
    return [row['prefix'] for row in rows]
