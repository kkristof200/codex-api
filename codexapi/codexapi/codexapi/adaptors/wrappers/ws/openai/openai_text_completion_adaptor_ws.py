from typing import Any

from ....core import IResponsesAdaptorWS


class OpenAITextCompletionAdaptorWS(IResponsesAdaptorWS):
    """Translate a single Responses API event into an OpenAI Text Completions chunk.

    Emitted ``object`` field: ``"text_completion.chunk"``.
    Choices carry a ``text`` field rather than ``delta``.
    Returns an empty dict ``{}`` for events that produce no output chunk.
    """

    def _translate(
        self,
        event: dict[str, Any],
        response_id: str,
        created_at: int,
        model: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        kind = event.get("type")

        if kind == "response.output_text.delta":
            return {
                "id": response_id,
                "object": "text_completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{"index": 0, "text": event.get("delta") or "", "finish_reason": None}],
            }

        if kind == "response.output_text.done":
            return {
                "id": response_id,
                "object": "text_completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{"index": 0, "text": "", "finish_reason": "stop"}],
            }

        if kind == "response.completed":
            return {
                "id": response_id,
                "object": "text_completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{"index": 0, "text": "", "finish_reason": None}],
                "usage": self._extract_usage(event),
            }

        return {}
