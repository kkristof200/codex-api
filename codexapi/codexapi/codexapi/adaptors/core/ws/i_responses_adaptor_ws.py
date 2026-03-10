import abc
from typing import Any

from ..core import IResponsesAdaptor


class IResponsesAdaptorWS(IResponsesAdaptor):
    _response_id: str = ""
    _created_at: int = 0

    _model: str = ""
    _reasoning_effort: str = ""


    def translate(
        self,
        event: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            if event.get("type") == "response.created":
                response = event.get("response") or {}

                self._response_id = response.get("id") or self._response_id
                self._created_at = response.get("created_at") or self._created_at
                self._model = response.get("model") or self._model
                self._reasoning_effort = response.get("reasoning") or self._reasoning_effort
        except Exception as e:
            print(f"Error translating event: {e}")

        return self._translate(event, self._response_id, self._created_at, self._model, self._reasoning_effort)


    @abc.abstractmethod
    def _translate(
        self,
        event: dict[str, Any],

        response_id: str,
        created_at: int,

        model: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        pass
