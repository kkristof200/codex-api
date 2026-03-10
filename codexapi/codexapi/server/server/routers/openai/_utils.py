import json
from typing import Iterator, List, Dict, Any

from fastapi import Request
from fastapi.responses import StreamingResponse, JSONResponse

from ...auth import get_effective_chatgpt_auth
from ...utils import parse_model_config
from ...models import OpenAIChatCompletionRequest, OpenAITextCompletionRequest, OpenAIResponseCompletionRequest
from ...vars import REASONING_SUMMARY_VALUES

from .....codexapi import (
    CodexAPI,
    IResponsesAdaptorWS, IResponsesAdaptorHTTP
)


def solve_req(
    req: OpenAIChatCompletionRequest | OpenAITextCompletionRequest | OpenAIResponseCompletionRequest,
    request: Request,
    messages: List[Dict[str, Any]],
    adaptor_ws: type[IResponsesAdaptorWS],
    adaptor_http: type[IResponsesAdaptorHTTP]
):
    model = parse_model_config(req.model)
    auth_token, chatgpt_acc_id = get_effective_chatgpt_auth()

    web_search = str(request.app.state.default_web_search).lower() == "true"

    reasoning_summary = str(request.app.state.reasoning_summary).lower()
    if reasoning_summary not in REASONING_SUMMARY_VALUES:
        reasoning_summary = "auto"

    codex = CodexAPI()
    kwargs = {
        "model_name": model.model,
        "reasoning_effort": model.reasoning_effort,
        "chatgpt_acc_id": chatgpt_acc_id,
        "auth_token": auth_token,
        "messages": messages,
        "web_search": model.web_search if model.web_search is not None else web_search,
        "reasoning_summary": model.reasoning_summary if model.reasoning_summary is not None else reasoning_summary
    }

    if req.stream:
        events = codex.request_ws(adaptor=adaptor_ws(), **kwargs)

        return StreamingResponse(
            _sse_stream(events),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no"},
        )

    result = codex.request_http(adaptor=adaptor_http(), **kwargs)
    return JSONResponse(content=result)

def _sse_stream(events: Iterator[Dict[str, Any]]) -> Iterator[str]:
    for event in events:
        if event:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"
