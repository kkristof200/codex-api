from typing import Any

from ....core import IResponsesAdaptorHTTP


class OpenAITextCompletionAdaptorHTTP(IResponsesAdaptorHTTP):
    """Translate a single Responses API event into an OpenAI Text Completions chunk.

    Emitted ``object`` field: ``"text_completion.chunk"``.
    Choices carry a ``text`` field rather than ``delta``.
    Returns an empty dict ``{}`` for events that produce no output chunk.
    """

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
            "object": "text_completion",
            "created": response.get("created_at") or 0,
            "model": response.get("model") or "",
            "choices": [
                {
                    "text": output_text,
                    "index": 0,
                    "finish_reason": "stop",
                    "logprobs": None
                }
            ],
            "usage": self._extract_usage(event),
            "system_fingerprint": ""
        }
