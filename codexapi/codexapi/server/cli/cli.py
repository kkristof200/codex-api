import argparse
import os
import sys
import json


from ..server import read_auth_file, load_chatgpt_tokens, parse_jwt_claims
from .cli_login import cmd_login
from .cli_serve import cmd_serve


def main() -> None:
    parser = argparse.ArgumentParser(description="ChatGPT Local: login & OpenAI-compatible proxy")
    sub = parser.add_subparsers(dest="command", required=True)

    p_login = sub.add_parser("login", help="Authorize with ChatGPT and store tokens")
    p_login.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    p_login.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    p_serve = sub.add_parser("serve", help="Run local OpenAI-compatible server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    # p_serve.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    # p_serve.add_argument(
    #     "--verbose-obfuscation",
    #     action="store_true",
    #     help="Also dump raw SSE/obfuscation events (in addition to --verbose request/response logs).",
    # )
    # p_serve.add_argument(
    #     "--debug-model",
    #     dest="debug_model",
    #     default=os.getenv("CHATGPT_LOCAL_DEBUG_MODEL"),
    #     help="Forcibly override requested 'model' with this value",
    # )
    # p_serve.add_argument(
    #     "--reasoning-effort",
    #     choices=["minimal", "low", "medium", "high", "xhigh"],
    #     default=os.getenv("CHATGPT_LOCAL_REASONING_EFFORT", "medium").lower(),
    #     help="Reasoning effort level for Responses API (default: medium)",
    # )
    p_serve.add_argument(
        "--reasoning-summary",
        choices=["auto", "concise", "detailed", "none"],
        default=os.getenv("CHATGPT_LOCAL_REASONING_SUMMARY", "auto").lower(),
        help="Reasoning summary verbosity (default: auto)",
    )
    # p_serve.add_argument(
    #     "--reasoning-compat",
    #     choices=["legacy", "o3", "think-tags", "current"],
    #     default=os.getenv("CHATGPT_LOCAL_REASONING_COMPAT", "think-tags").lower(),
    #     help=(
    #         "Compatibility mode for exposing reasoning to clients (legacy|o3|think-tags). "
    #         "'current' is accepted as an alias for 'legacy'"
    #     ),
    # )
    # p_serve.add_argument(
    #     "--expose-reasoning-models",
    #     action="store_true",
    #     default=(os.getenv("CHATGPT_LOCAL_EXPOSE_REASONING_MODELS") or "").strip().lower() in ("1", "true", "yes", "on"),
    #     help=(
    #         "Expose GPT-5 family reasoning effort variants (minimal|low|medium|high|xhigh where supported) "
    #         "as separate models from /v1/models. This allows choosing effort via model selection in compatible UIs."
    #     ),
    # )
    p_serve.add_argument(
        "--enable-web-search",
        action=argparse.BooleanOptionalAction,
        default=(os.getenv("CHATGPT_LOCAL_ENABLE_WEB_SEARCH") or "").strip().lower() in ("1", "true", "yes", "on"),
        help=(
            "Enable default web_search tool when a request omits responses_tools (off by default). "
            "Also configurable via CHATGPT_LOCAL_ENABLE_WEB_SEARCH."
        ),
    )

    p_info = sub.add_parser("info", help="Print current stored tokens and derived account id")
    p_info.add_argument("--json", action="store_true", help="Output raw auth.json contents")

    args = parser.parse_args()

    if args.command == "login":
        sys.exit(cmd_login(no_browser=args.no_browser, verbose=args.verbose))
    elif args.command == "serve":
        sys.exit(
            cmd_serve(
                host=args.host,
                port=args.port,
                # verbose=args.verbose,
                # verbose_obfuscation=args.verbose_obfuscation,
                # reasoning_effort=args.reasoning_effort,
                reasoning_summary=args.reasoning_summary,
                # reasoning_compat=args.reasoning_compat,
                # debug_model=args.debug_model,
                # expose_reasoning_models=args.expose_reasoning_models,
                default_web_search=args.enable_web_search,
            )
        )
    elif args.command == "info":
        auth = read_auth_file()
        if getattr(args, "json", False):
            print(json.dumps(auth or {}, indent=2))
            sys.exit(0)
        access_token, account_id, id_token = load_chatgpt_tokens()
        if not access_token or not id_token:
            print("👤 Account")
            print("  • Not signed in")
            print("  • Run: codexapi login")
            print("")
            # _print_usage_limits_block()
            sys.exit(0)

        id_claims = parse_jwt_claims(id_token) or {}
        access_claims = parse_jwt_claims(access_token) or {}

        email = id_claims.get("email") or id_claims.get("preferred_username") or "<unknown>"
        plan_raw = (access_claims.get("https://api.openai.com/auth") or {}).get("chatgpt_plan_type") or "unknown"
        plan_map = {
            "plus": "Plus",
            "pro": "Pro",
            "free": "Free",
            "team": "Team",
            "enterprise": "Enterprise",
        }
        plan = plan_map.get(str(plan_raw).lower(), str(plan_raw).title() if isinstance(plan_raw, str) else "Unknown")

        print("👤 Account")
        print("  • Signed in with ChatGPT")
        print(f"  • Login: {email}")
        print(f"  • Plan: {plan}")
        if account_id:
            print(f"  • Account ID: {account_id}")
        print("")
        # _print_usage_limits_block()
        sys.exit(0)
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
