from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...models import OpenAIChatCompletionRequest, OpenAITextCompletionRequest, OpenAIResponseCompletionRequest
from ...vars import ALL_GPT_MODELS

from codexapi_client import (
    OpenAIChatCompletionAdaptorWS, OpenAIChatCompletionAdaptorHTTP,
    OpenAITextCompletionAdaptorWS, OpenAITextCompletionAdaptorHTTP,
    OpenAIResponsesAdaptorWS, OpenAIResponsesAdaptorHTTP
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
                        "type": "output_text" if m["role"] == "assistant" else "input_text",
                        "text": m["content"] if isinstance(m["content"], str) else list(m["content"])[0]["text"]  # type: ignore[index]
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
                "role": "user",
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
# POST /v1/responses
# ---------------------------------------------------------------------------

@router.post("/responses")
def responses(req: OpenAIResponseCompletionRequest, request: Request) -> Any:
    if isinstance(req.input, str):
        messages = [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": req.input}]
            }
        ]
    else:
        messages = [
            {
                "type": "message",
                "role": msg.role,
                "content": [
                    {
                        "type": "output_text" if msg.role == "assistant" else "input_text",
                        "text": msg.content if isinstance(msg.content, str) else msg.content[0]["text"] # type: ignore[index]
                    }
                ]
            } for msg in req.input
        ]

    return solve_req(
        req,
        request,
        messages=messages,
        adaptor_ws=OpenAIResponsesAdaptorWS,
        adaptor_http=OpenAIResponsesAdaptorHTTP
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
