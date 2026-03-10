from __future__ import annotations

import abc
from typing import Any, Dict, Self


class IResponsesAdaptor(abc.ABC):

    @abc.abstractmethod
    def translate(
        self,
        event: dict[str, Any]
    ) -> dict[str, Any]:
        pass

    def copy(self) -> Self:
        return self.__class__()

    def _extract_usage(
        self,
        evt: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        try:
            usage = (evt.get("response") or {}).get("usage")

            if not isinstance(usage, dict):
                return None

            input_tokens = int(usage.get("input_tokens") or 0)
            output_tokens = int(usage.get("output_tokens") or 0)
            total_tokens = int(usage.get("total_tokens") or (input_tokens + output_tokens))
            cached_tokens = int((usage.get("input_tokens_details") or {}).get("cached_tokens") or 0)
            reasoning_tokens = int((usage.get("output_tokens_details") or {}).get("reasoning_tokens") or 0)

            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
                "prompt_tokens_details": {"cached_tokens": cached_tokens},
                "cache_read_tokens": cached_tokens,
                "cache_creation_tokens": 0,
                "reasoning_tokens": reasoning_tokens,
                "reasoning_tokens_details": {"reasoning_tokens": reasoning_tokens},
                "completion_tokens_details": {"completion_tokens": output_tokens},
            }
        except Exception:
            return None
