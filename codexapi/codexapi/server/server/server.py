from fastapi import FastAPI

from ...codexapi import REASONING_SUMMARY

from .routers import router_openai


def create_app(
    reasoning_summary: REASONING_SUMMARY,
    default_web_search: bool,
) -> FastAPI:
    app = FastAPI(
        title="CodexAPI",
        version="0.1.0"
    )

    app.state.reasoning_summary = reasoning_summary
    app.state.default_web_search = default_web_search

    app.include_router(router_openai)

    return app
