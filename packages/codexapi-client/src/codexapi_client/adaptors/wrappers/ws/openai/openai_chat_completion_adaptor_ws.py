import json
from typing import Any, Dict, Self

from ....core import IResponsesAdaptorWS


class OpenAIChatCompletionAdaptorWS(IResponsesAdaptorWS):
    def __init__(
        self,
        reasoning_compat: str = "think-tags"
    ) -> None:
        self.reasoning_compat = (reasoning_compat or "think-tags").strip().lower()

        # per-stream state
        self._think_open = False
        self._think_closed = False
        self._sent_stop_chunk = False
        self._saw_any_summary = False
        self._pending_summary_paragraph = False
        self._ws_state: Dict[str, Any] = {}
        self._ws_index: Dict[str, int] = {}
        self._ws_next_index: int = 0

    def copy(self) -> Self:
        return self.__class__(
            reasoning_compat=self.reasoning_compat,
        )

    # ------------------------------------------------------------------
    # IResponsesAdaptor implementation
    # ------------------------------------------------------------------

    def _translate(  # noqa: C901
        self,
        event: dict[str, Any],
        response_id: str,
        created_at: int,
        model: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        kind = event.get("type")
        compat = self.reasoning_compat

        def _chunk(delta: Any, finish_reason: Any = None) -> dict[str, Any]:
            return {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
            }

        # ── web search / tool calls ──────────────────────────────────────────
        if isinstance(kind, str) and "web_search_call" in kind:
            try:
                call_id = event.get("item_id") or "ws_call"
                item = event.get("item") if isinstance(event.get("item"), dict) else {}
                params: Dict[str, Any] = self._ws_state.setdefault(call_id, {})
                self._merge_ws_params(params, item)
                self._merge_ws_params(params, event)
                args_str = self._serialize_tool_args(self._ws_state.get(call_id) or {})
                if call_id not in self._ws_index:
                    self._ws_index[call_id] = self._ws_next_index
                    self._ws_next_index += 1
                idx = self._ws_index[call_id]
                return {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_at,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "tool_calls": [{
                                "index": idx,
                                "id": call_id,
                                "type": "function",
                                "function": {"name": "web_search", "arguments": args_str},
                            }]
                        },
                        "finish_reason": "tool_calls" if (kind.endswith(".completed") or kind.endswith(".done")) else None,
                    }],
                }
            except Exception:
                return {}

        # ── function / web-search item done ─────────────────────────────────
        if kind == "response.output_item.done":
            item = event.get("item") or {}
            if not isinstance(item, dict) or item.get("type") not in ("function_call", "web_search_call"):
                return {}
            call_id = item.get("call_id") or item.get("id") or ""
            name = item.get("name") or ("web_search" if item.get("type") == "web_search_call" else "")
            raw_args = item.get("arguments") or item.get("parameters")
            if isinstance(raw_args, dict):
                self._ws_state.setdefault(call_id, {}).update(raw_args)
            eff_args = self._ws_state.get(call_id, raw_args if isinstance(raw_args, (dict, list, str)) else {})
            args = self._serialize_tool_args(eff_args)
            if call_id not in self._ws_index:
                self._ws_index[call_id] = self._ws_next_index
                self._ws_next_index += 1
            idx = self._ws_index[call_id]
            return {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{
                    "index": 0,
                    "delta": {
                        "tool_calls": [{
                            "index": idx,
                            "id": call_id,
                            "type": "function",
                            "function": {"name": name, "arguments": args},
                        }]
                    },
                    "finish_reason": "tool_calls",
                }],
            }

        # ── text delta ───────────────────────────────────────────────────────
        if kind == "response.output_text.delta":
            content = ""
            if compat == "think-tags" and self._think_open and not self._think_closed:
                content = "</think>"
                self._think_open = False
                self._think_closed = True
            content += event.get("delta") or ""
            return _chunk({"content": content})

        # ── text done ────────────────────────────────────────────────────────
        if kind == "response.output_text.done":
            self._sent_stop_chunk = True
            return _chunk({}, "stop")

        # ── reasoning paragraph boundary ─────────────────────────────────────
        if kind == "response.reasoning_summary_part.added":
            if compat in ("think-tags", "o3"):
                if self._saw_any_summary:
                    self._pending_summary_paragraph = True
                else:
                    self._saw_any_summary = True
            return {}

        # ── reasoning text delta ─────────────────────────────────────────────
        if kind in ("response.reasoning_summary_text.delta", "response.reasoning_text.delta"):
            delta_txt = event.get("delta") or ""
            if compat == "o3":
                prefix = "\n" if (kind == "response.reasoning_summary_text.delta" and self._pending_summary_paragraph) else ""
                self._pending_summary_paragraph = False
                return _chunk({"reasoning": {"content": [{"type": "text", "text": prefix + delta_txt}]}})
            if compat == "think-tags":
                if not self._think_open and not self._think_closed:
                    self._think_open = True
                    delta_txt = "<think>" + delta_txt
                if self._think_open and not self._think_closed:
                    if kind == "response.reasoning_summary_text.delta" and self._pending_summary_paragraph:
                        delta_txt = "\n" + delta_txt
                        self._pending_summary_paragraph = False
                    return _chunk({"content": delta_txt})
            # plain-text compat
            key = "reasoning_summary" if kind == "response.reasoning_summary_text.delta" else "reasoning"
            return _chunk({key: delta_txt})

        # ── error ────────────────────────────────────────────────────────────
        if kind == "response.failed":
            err = (event.get("response") or {}).get("error", {}).get("message", "response.failed")
            return {"error": {"message": err}}

        # ── completed ────────────────────────────────────────────────────────
        if kind == "response.completed":
            usage = self._extract_usage(event)

            if compat == "think-tags" and self._think_open and not self._think_closed:
                self._think_open = False
                self._think_closed = True

            if usage:
                return {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_at,
                    "model": model,
                    "choices": [],
                    "usage": usage
                }

            if not self._sent_stop_chunk:
                self._sent_stop_chunk = True
                return _chunk({}, "stop")

            return {}

        return {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_tool_args(eff_args: Any) -> str:
        if isinstance(eff_args, (dict, list)):
            return json.dumps(eff_args)
        if isinstance(eff_args, str):
            try:
                parsed = json.loads(eff_args)
                if isinstance(parsed, (dict, list)):
                    return json.dumps(parsed)
                return json.dumps({"query": eff_args})
            except (json.JSONDecodeError, ValueError):
                return json.dumps({"query": eff_args})
        return "{}"

    def _merge_ws_params(self, params_dict: Dict[str, Any], src: Any) -> None:
        if not isinstance(src, dict):
            return
        for key in ("parameters", "args", "arguments", "input"):
            val = src.get(key)
            if isinstance(val, dict):
                params_dict.update(val)
        if isinstance(src.get("query"), str):
            params_dict.setdefault("query", src["query"])
        if isinstance(src.get("q"), str):
            params_dict.setdefault("query", src["q"])
        for k in ("recency", "time_range", "days"):
            if src.get(k) is not None and k not in params_dict:
                params_dict[k] = src[k]
        for k in ("domains", "include_domains", "include"):
            if isinstance(src.get(k), list) and "domains" not in params_dict:
                params_dict["domains"] = src[k]
        for k in ("max_results", "topn", "limit"):
            if src.get(k) is not None and "max_results" not in params_dict:
                params_dict["max_results"] = src[k]
