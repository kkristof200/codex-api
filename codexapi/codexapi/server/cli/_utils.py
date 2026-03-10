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
    """ANSI reset color code"""
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


# def _print_usage_limits_block() -> None:
#     stored = load_rate_limit_snapshot()

#     print("📊 Usage Limits")

#     if stored is None:
#         print("  No usage data available yet. Send a request through CodexAPI first.")
#         print()
#         return

#     update_time = _format_local_datetime(stored.captured_at)
#     print(f"Last updated: {update_time}")
#     print()

#     windows: list[tuple[str, str, RateLimitWindow]] = []
#     if stored.snapshot.primary is not None:
#         windows.append(("⚡", "5 hour limit", stored.snapshot.primary))
#     if stored.snapshot.secondary is not None:
#         windows.append(("📅", "Weekly limit", stored.snapshot.secondary))

#     if not windows:
#         print("  Usage data was captured but no limit windows were provided.")
#         print()
#         return

#     for i, (icon_label, desc, window) in enumerate(windows):
#         if i > 0:
#             print()

#         percent_used = _clamp_percent(window.used_percent)
#         remaining = max(0.0, 100.0 - percent_used)
#         color = _get_usage_color(percent_used)
#         reset = _reset_color()

#         progress = _render_progress_bar(percent_used)
#         usage_text = f"{percent_used:5.1f}% used"
#         remaining_text = f"{remaining:5.1f}% left"

#         print(f"{icon_label} {desc}")
#         print(f"{color}{progress}{reset} {color}{usage_text}{reset} | {remaining_text}")

#         reset_in = _format_reset_duration(window.resets_in_seconds)
#         reset_at = compute_reset_at(stored.captured_at, window)

#         if reset_in and reset_at:
#             reset_at_str = _format_local_datetime(reset_at)
#             print(f"    ⏳ Resets in: {reset_in} at {reset_at_str}")
#         elif reset_in:
#             print(f"    ⏳ Resets in: {reset_in}")
#         elif reset_at:
#             reset_at_str = _format_local_datetime(reset_at)
#             print(f"    ⏳ Resets at: {reset_at_str}")

#     print()
