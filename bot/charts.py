import io

import matplotlib
import numpy as np

matplotlib.use('Agg')  # non-interactive backend, must be set before pyplot import
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from bot.models import Activity
from bot.parsers.common import _haversine

# ── Catppuccin Mocha palette ─────────────────────────────────────────────────

_BG = '#1e1e2e'  # base
_AX_BG = '#181825'  # crust (slightly darker for plot area)
_GRID = '#313244'  # surface0
_SPINE = '#45475a'  # surface1
_TEXT = '#cdd6f4'  # text
_SUBTEXT = '#a6adc8'  # subtext0
_BLUE = '#89b4fa'  # blue
_RED = '#f38ba8'  # red

matplotlib.rcParams.update(
    {
        'figure.facecolor': _BG,
        'axes.facecolor': _AX_BG,
        'axes.edgecolor': _SPINE,
        'axes.labelcolor': _SUBTEXT,
        'axes.labelsize': 10,
        'text.color': _TEXT,
        'xtick.color': _SUBTEXT,
        'ytick.color': _SUBTEXT,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'grid.color': _GRID,
        'grid.alpha': 1.0,
        'grid.linewidth': 0.8,
        'lines.linewidth': 2.0,
        'savefig.facecolor': _BG,
        'font.family': 'sans-serif',
    }
)

# ── helpers ───────────────────────────────────────────────────────────────────


def _fig_to_bytes(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _smooth(values: np.ndarray, window: int) -> np.ndarray:
    """Rolling mean over valid (non-NaN) values; NaN gaps are preserved."""
    result = np.full_like(values, np.nan)
    valid = ~np.isnan(values)
    if valid.sum() < 2:
        return result
    kernel = np.ones(window) / window
    result[valid] = np.convolve(values[valid], kernel, mode='same')
    return result


def _clean_spines(ax: plt.Axes, keep_right: bool = False) -> None:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(keep_right)
    if not keep_right:
        ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)


# ── charts ────────────────────────────────────────────────────────────────────


def elevation_chart(activity: Activity) -> bytes | None:
    """Elevation profile: filled area of elevation (m) vs cumulative distance (km)."""
    pts = [p for p in activity.points if p.elevation_m is not None]
    if len(pts) < 2:
        return None

    dist_m = 0.0
    distances_km = [0.0]
    for i in range(1, len(pts)):
        if pts[i].segment_id == pts[i - 1].segment_id:
            dist_m += _haversine(pts[i - 1].lat, pts[i - 1].lon, pts[i].lat, pts[i].lon)
        distances_km.append(dist_m / 1000)

    elevations = [p.elevation_m for p in pts]
    baseline = min(elevations)

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.fill_between(distances_km, elevations, baseline, alpha=0.2, color=_BLUE)
    ax.plot(distances_km, elevations, color=_BLUE, linewidth=2.0)
    ax.set_xlabel('Дистанция, км')
    ax.set_ylabel('Высота, м')
    ax.set_title('Профиль высот', color=_TEXT, fontsize=11, pad=6)
    ax.set_xlim(distances_km[0], distances_km[-1])
    ax.grid(axis='y')
    _clean_spines(ax)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def pace_hr_chart(activity: Activity) -> bytes | None:
    """Pace (min/km) and HR (bpm) vs elapsed time on a dual-axis chart."""
    pts = activity.points
    if len(pts) < 2:
        return None

    start = pts[0].timestamp
    elapsed_s = np.array([(p.timestamp - start).total_seconds() for p in pts])

    # Instantaneous pace between consecutive same-segment points.
    raw_pace = np.full(len(pts), np.nan)
    for i in range(1, len(pts)):
        p, q = pts[i - 1], pts[i]
        if p.segment_id != q.segment_id:
            continue
        dt = (q.timestamp - p.timestamp).total_seconds()
        d = _haversine(p.lat, p.lon, q.lat, q.lon)
        if dt > 0 and d > 0:
            pace = 1000 / (d / dt) / 60  # min/km
            if pace < 20:  # cap: ignore stops and GPS glitches
                raw_pace[i] = pace

    hrs = np.array([p.hr if p.hr is not None else np.nan for p in pts])

    has_pace = not np.all(np.isnan(raw_pace))
    has_hr = not np.all(np.isnan(hrs))
    if not has_pace and not has_hr:
        return None

    fig, ax1 = plt.subplots(figsize=(10, 3))

    def fmt_elapsed(s, _):
        s = int(s)
        h, m = divmod(s // 60, 60)
        return f'{h}:{m:02d}' if h else str(m)

    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_elapsed))
    ax1.set_xlabel('Время, мин')
    ax1.grid(axis='x')

    if has_pace:
        window = min(30, int(np.sum(~np.isnan(raw_pace))))
        pace = _smooth(raw_pace, window)
        ax1.plot(elapsed_s, pace, color=_BLUE, linewidth=2.0)
        ax1.fill_between(elapsed_s, pace, np.nanmax(pace), alpha=0.15, color=_BLUE)
        ax1.set_ylabel('Темп, мин/км', color=_BLUE)
        ax1.tick_params(axis='y', labelcolor=_BLUE)
        ax1.invert_yaxis()  # lower value = faster pace
        _clean_spines(ax1, keep_right=has_hr)
    else:
        _clean_spines(ax1, keep_right=True)

    if has_hr:
        ax2 = ax1.twinx()
        ax2.plot(elapsed_s, hrs, color=_RED, linewidth=1.5, alpha=0.85)
        ax2.set_ylabel('HR, уд/мин', color=_RED)
        ax2.tick_params(axis='y', labelcolor=_RED)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['right'].set_color(_RED)
        ax2.spines['right'].set_linewidth(0.8)

    title = 'Темп и пульс' if has_pace and has_hr else ('Темп' if has_pace else 'Пульс')
    ax1.set_title(title, color=_TEXT, fontsize=11, pad=6)
    fig.tight_layout()
    return _fig_to_bytes(fig)
