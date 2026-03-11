import json
from typing import Any, Dict, Self

from ....core import IResponsesAdaptorHTTP


class OpenAIChatCompletionAdaptorHTTP(IResponsesAdaptorHTTP):
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

    def translate(  # noqa: C901
        self,
        event: dict[str, Any]
    ) -> dict[str, Any]:
        response = event.get("response") or {}

        # reasoning = response.get("reasoning") or {}
        # effort = reasoning.get("effort") or "none"

        output_text = (response.get("output") or [])[-1]["content"][0]["text"]

        return {
            "id": response.get("id") or "",
            "object": "chat.completion",
            "created": response.get("created_at") or 0,
            "model": response.get("model") or "",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "logprobs": None,
                    "message": {
                        "role": "assistant",
                        "content": output_text,
                        "refusal": None
                    }
                }
            ],
            "usage": self._extract_usage(event),
            "service_tier": "default",
            "system_fingerprint": ""
        }
