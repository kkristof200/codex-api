from typing import Dict, Literal, get_args


# Types

REASONING_EFFORT = Literal["none", "minimal", "low", "medium", "high", "xhigh"]

REASONING_SUMMARY = Literal["auto", "concise", "detailed"]

GPT_MODEL_NAME = Literal[
    # GPT
    "gpt-5",
    "gpt-5.1",
    "gpt-5.2",
    "gpt-5.4",

    # Codex
    "gpt-5-codex",
    "gpt-5.1-codex-mini",
    "gpt-5.1-codex",
    "gpt-5.1-codex-max",
    "gpt-5.2-codex",
    "gpt-5.3-codex",

    # Codex - Only API
    # "codex-mini"
]


# Data

# GPT_MODEL_NAME: (default_reasoning_effort, list_of_available_reasoning_efforts)
GPT_MODELS: dict[GPT_MODEL_NAME, tuple[REASONING_EFFORT, list[REASONING_EFFORT]]] = {
    "gpt-5": ("medium", ["high", "medium", "low", "minimal"]),
    "gpt-5.1": ("medium", ["high", "medium", "low", "none"]),
    "gpt-5.2": ("medium", ["xhigh", "high", "medium", "low", "minimal", "none"]),
    "gpt-5.4": ("medium", ["xhigh", "high", "medium", "low", "minimal", "none"]),
    "gpt-5.3-codex": ("medium", ["xhigh", "high", "medium", "low", "minimal", "none"]),
    "gpt-5-codex": ("medium", ["high", "medium", "low"]),
    "gpt-5.2-codex": ("medium", ["xhigh", "high", "medium", "low"]),
    "gpt-5.1-codex": ("medium", ["high", "medium", "low"]),
    "gpt-5.1-codex-max": ("medium", ["xhigh", "high", "medium", "low"]),
    "gpt-5.1-codex-mini": ("medium", ["high", "medium", "low"])
}


URL_CODEX_WSS = "wss://chatgpt.com/backend-api/codex/responses"

DEFAULT_CODEX_HEADERS: Dict[str, str] = {
    "Origin": "https://chatgpt.com",
    "originator": "codex_cli_rs",
    "version": "0.112.0",
    "openai-beta": "responses_websockets=2026-02-06",
}