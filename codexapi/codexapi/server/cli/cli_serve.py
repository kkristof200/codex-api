import uvicorn

from ..server import create_app


def cmd_serve(
    host: str,
    port: int,

    reasoning_summary: str,
    default_web_search: bool,
) -> int:
    app = create_app(
        reasoning_summary=reasoning_summary, # type: ignore[arg-type]
        default_web_search=default_web_search,
    )

    uvicorn.run(app, host=host, port=port)

    return 0
