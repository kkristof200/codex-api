import json
from typing import Any, Dict, Iterator


def sse_stream(events: Iterator[Dict[str, Any]]) -> Iterator[str]:
    for event in events:
        if event:
            yield f"data: {json.dumps(event)}\n\n"
    yield "data: [DONE]\n\n"
