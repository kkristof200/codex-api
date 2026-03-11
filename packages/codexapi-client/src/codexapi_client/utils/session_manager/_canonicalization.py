import json
from typing import Any, Dict

from .types import InputItems, RequestContext


def canonicalize_conversation(
    instructions: str | None,
    input_items: InputItems,
    request_context: RequestContext | None = None,
) -> str:
    payload: Dict[str, Any] = {
        "input": _normalize_value(input_items),
    }
    if isinstance(instructions, str) and instructions.strip():
        payload["instructions"] = instructions.strip()
    if request_context:
        payload["request_context"] = _normalize_value(request_context)
    return _canonical_json(payload)


def canonicalize_cache_prefix(
    instructions: str | None,
    input_items: InputItems,
    request_context: RequestContext | None = None,
) -> str:
    last_user_idx = _last_user_message_index(input_items)
    if last_user_idx is None:
        prefix_items = input_items
    else:
        prefix_items = input_items[:last_user_idx]
    return canonicalize_conversation(instructions, prefix_items, request_context)


def _canonical_json(value: Any) -> str:
    return json.dumps(_normalize_value(value), sort_keys=True, separators=(",", ":"))


def _last_user_message_index(input_items: InputItems) -> int | None:
    for idx in range(len(input_items) - 1, -1, -1):
        item = input_items[idx]
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue
        if item.get("role") == "user":
            return idx
    return None


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_value(value[key])
            for key in sorted(value)
            if value[key] is not None
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    return value
