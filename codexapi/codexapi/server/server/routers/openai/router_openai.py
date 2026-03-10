from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...models import OpenAIChatCompletionRequest, OpenAITextCompletionRequest
from ...vars import ALL_GPT_MODELS

from .....codexapi import (
    OpenAIChatCompletionAdaptorWS, OpenAIChatCompletionAdaptorHTTP,
    OpenAITextCompletionAdaptorWS, OpenAITextCompletionAdaptorHTTP
)
from ._utils import solve_req


router = APIRouter(prefix="/v1")


# ---------------------------------------------------------------------------
# POST /v1/chat/completions
# ---------------------------------------------------------------------------

@router.post("/chat/completions")
def chat_completions(req: OpenAIChatCompletionRequest, request: Request) -> Any:
    return solve_req(
        req,
        request,
        messages=[
            {
                "type": "message",
                "role": m["role"],
                "content": [
                    {
                        "type": "input_text",
                        "text": m["content"] if isinstance(m["content"], str) else m["content"][0]["text"]  # type: ignore[index]
                    }
                ]
            }
            for m in req.messages
        ],
        adaptor_ws=OpenAIChatCompletionAdaptorWS,
        adaptor_http=OpenAIChatCompletionAdaptorHTTP
    )


# ---------------------------------------------------------------------------
# POST /v1/completions
# ---------------------------------------------------------------------------

@router.post("/completions")
def completions(req: OpenAITextCompletionRequest, request: Request) -> Any:
    return solve_req(
        req,
        request,
        messages=[
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "input_text",
                        "text": req.prompt
                    }
                ]
            }
        ],
        adaptor_ws=OpenAITextCompletionAdaptorWS,
        adaptor_http=OpenAITextCompletionAdaptorHTTP
    )


# ---------------------------------------------------------------------------
# GET /v1/models
# ---------------------------------------------------------------------------

@router.get("/models")
def list_models() -> Any:
    return JSONResponse(content={
        "object": "list",
        "data": [
            {
                "id": model_id,
                "object": "model",
                "owned_by": "openai",
            }
            for model_id in sorted(ALL_GPT_MODELS)
        ],
    })
