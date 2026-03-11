from typing import Any

from ....core import IResponsesAdaptorHTTP


class OpenAIResponsesAdaptorHTTP(IResponsesAdaptorHTTP):
    """Pass-through adaptor for the OpenAI Responses API SSE format.

    The upstream already speaks the Responses API event format, so each event
    is re-serialised and forwarded verbatim.  ``response.completed`` is used
    solely as the end-of-stream signal and also yields ``[DONE]``.
    """

    def translate(
        self,
        event: dict[str, Any]
    ) -> dict[str, Any]:
        return event["response"]
