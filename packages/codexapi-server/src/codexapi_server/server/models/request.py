from typing import List

from pydantic import BaseModel
from openai.types.responses import EasyInputMessage
from openai.types.chat import ChatCompletionMessageParam


class OpenAIChatCompletionRequest(BaseModel):
    model: str
    stream: bool = False
    messages: List[ChatCompletionMessageParam]
    temperature: float = 1.0
    max_completion_tokens: int | None = None

class OpenAITextCompletionRequest(BaseModel):
    model: str
    stream: bool = False
    temperature: float = 1.0

    prompt: str
    max_tokens: int | None = None

class OpenAIResponseCompletionRequest(BaseModel):
    model: str
    stream: bool = False
    temperature: float = 1.0

    input: str | List[EasyInputMessage]
    max_output_tokens: int | None = None
