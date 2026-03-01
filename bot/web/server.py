from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from bot.models import Activity
from bot.parsers.common import _haversine

app = FastAPI()

_activity: Activity | None = None

_STATIC = Path(__file__).parent / 'static'


def set_activity(activity: Activity) -> None:
    global _activity
    _activity = activity


def _activity_to_dict(activity: Activity) -> dict:
    start = activity.points[0].timestamp if activity.points else None

    speeds: list[float | None] = [None] * len(activity.points)
    for i in range(1, len(activity.points)):
        p_prev = activity.points[i - 1]
        p_curr = activity.points[i]
        if p_prev.segment_id == p_curr.segment_id:
            dt = (p_curr.timestamp - p_prev.timestamp).total_seconds()
            if dt > 0:
                dist = _haversine(p_prev.lat, p_prev.lon, p_curr.lat, p_curr.lon)
                speeds[i] = dist / dt

    points = []
    for i, p in enumerate(activity.points):
        points.append(
            {
                'id': i,
                'lat': p.lat,
                'lon': p.lon,
                'timestamp': p.timestamp.isoformat(),
                'elapsed_s': int((p.timestamp - start).total_seconds()) if start else 0,
                'elevation_m': p.elevation_m,
                'hr': p.hr,
                'segment_id': p.segment_id,
                'speed_ms': speeds[i],
            }
        )

    return {
        'filename': activity.filename,
        'recorded_at': activity.recorded_at.isoformat() if activity.recorded_at else None,
        'distance_m': activity.distance_m,
        'duration_s': activity.duration_s,
        'points': points,
    }


@app.get('/')
def index() -> FileResponse:
    # Serve the single-page map application.
    return FileResponse(_STATIC / 'index.html')


@app.get('/api/activity')
def get_activity() -> JSONResponse:
    # Return the loaded activity as JSON, including per-point speed derived from GPS coordinates
    # and timestamps. Returns 503 if no activity has been set yet (race condition on slow start).
    if _activity is None:
        return JSONResponse({'error': 'no activity loaded'}, status_code=503)
    return JSONResponse(_activity_to_dict(_activity))
