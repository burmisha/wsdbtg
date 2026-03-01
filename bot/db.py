from dataclasses import dataclass
from typing import TYPE_CHECKING

import asyncpg

if TYPE_CHECKING:
    from bot.models import Activity


@dataclass
class BotContext:
    db: asyncpg.Pool | None = None
    admin_user_id: int | None = None


_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS messages (
    user_id    BIGINT NOT NULL,
    prefix     TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activities (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    filename    TEXT NOT NULL,
    recorded_at TIMESTAMPTZ,
    distance_m        FLOAT,
    source_distance_m FLOAT,
    duration_s        FLOAT,
    avg_hr      FLOAT,
    max_hr      INT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS track_points (
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    segment_id  INT NOT NULL,
    ts          TIMESTAMPTZ NOT NULL,
    lat         FLOAT NOT NULL,
    lon         FLOAT NOT NULL,
    elevation_m FLOAT,
    hr          INT
);
"""


async def create_pool(dsn: str) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(dsn)
    await pool.execute(_CREATE_TABLES)
    return pool


async def get_db_stats(pool: asyncpg.Pool) -> asyncpg.Record:
    return await pool.fetchrow(_SELECT_DB_STATS)


async def save_message(pool: asyncpg.Pool, user_id: int, text: str) -> None:
    await pool.execute(
        'INSERT INTO messages (user_id, prefix) VALUES ($1, $2)',
        user_id,
        text[:5],
    )


_SELECT_HISTORY = """
    SELECT prefix FROM messages
    WHERE user_id = $1
    ORDER BY created_at DESC
    LIMIT 7
"""

_INSERT_ACTIVITY = """
    INSERT INTO activities (
        user_id, filename, recorded_at,
        distance_m, source_distance_m, duration_s, avg_hr, max_hr
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING id
"""

_SELECT_DB_STATS = """
    SELECT
        pg_size_pretty(pg_database_size(current_database())) AS db_size,
        (SELECT count(*) FROM activities) AS activities,
        (SELECT count(*) FROM track_points) AS points
"""

_INSERT_TRACK_POINT = """
    INSERT INTO track_points (activity_id, segment_id, ts, lat, lon, elevation_m, hr)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
"""


async def get_history(pool: asyncpg.Pool, user_id: int) -> list[str]:
    rows = await pool.fetch(_SELECT_HISTORY, user_id)
    return [row['prefix'] for row in rows]


async def save_activity(pool: asyncpg.Pool, user_id: int, activity: 'Activity') -> int:
    async with pool.acquire() as conn:
        async with conn.transaction():
            activity_id = await conn.fetchval(
                _INSERT_ACTIVITY,
                user_id,
                activity.filename,
                activity.recorded_at,
                activity.distance_m,
                activity.source_distance_m,
                activity.duration_s,
                activity.avg_hr,
                activity.max_hr,
            )
            await conn.executemany(
                _INSERT_TRACK_POINT,
                [(activity_id, p.segment_id, p.timestamp, p.lat, p.lon, p.elevation_m, p.hr) for p in activity.points],
            )
    return activity_id
