from datetime import datetime
# from ..server import load_rate_limit_snapshot

_STATUS_LIMIT_BAR_SEGMENTS = 30
_STATUS_LIMIT_BAR_FILLED = "█"
_STATUS_LIMIT_BAR_EMPTY = "░"
_STATUS_LIMIT_BAR_PARTIAL = "▓"


def _clamp_percent(value: float) -> float:
    try:
        percent = float(value)
    except Exception:
        return 0.0
    if percent != percent:
        return 0.0
    if percent < 0.0:
        return 0.0
    if percent > 100.0:
        return 100.0
    return percent


def _render_progress_bar(percent_used: float) -> str:
    ratio = max(0.0, min(1.0, percent_used / 100.0))
    filled_exact = ratio * _STATUS_LIMIT_BAR_SEGMENTS
    filled = int(filled_exact)
    partial = filled_exact - filled

    has_partial = partial > 0.5
    if has_partial:
        filled += 1

    filled = max(0, min(_STATUS_LIMIT_BAR_SEGMENTS, filled))
    empty = _STATUS_LIMIT_BAR_SEGMENTS - filled

    if has_partial and filled > 0:
        bar = _STATUS_LIMIT_BAR_FILLED * (filled - 1) + _STATUS_LIMIT_BAR_PARTIAL + _STATUS_LIMIT_BAR_EMPTY * empty
    else:
        bar = _STATUS_LIMIT_BAR_FILLED * filled + _STATUS_LIMIT_BAR_EMPTY * empty

    return f"[{bar}]"


def _get_usage_color(percent_used: float) -> str:
    if percent_used >= 90:
        return "\033[91m"
    elif percent_used >= 75:
        return "\033[93m"
    elif percent_used >= 50:
        return "\033[94m"
    else:
        return "\033[92m"


def _reset_color() -> str:
    return "\033[0m"


def _format_reset_duration(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    try:
        value = int(seconds)
    except Exception:
        return None
    if value < 0:
        value = 0
    days, remainder = divmod(value, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts and remainder:
        parts.append("under 1m")
    if not parts:
        parts.append("0m")
    return " ".join(parts)


def _format_local_datetime(dt: datetime) -> str:
    local = dt.astimezone()
    tz_name = local.tzname() or "local"
    return f"{local.strftime('%b %d, %Y %H:%M')} {tz_name}"
