import json
from typing import Any, Dict, Iterator, List, Optional

from websocket import WebSocket, create_connection

from .adaptors import IResponsesAdaptorWS, IResponsesAdaptorHTTP
from .utils import ensure_session_id

from .constants import GPT_MODEL_NAME, REASONING_EFFORT, REASONING_SUMMARY, URL_CODEX_WSS, DEFAULT_CODEX_HEADERS


class CodexAPI:
    def request_ws(
        self,
        model_name: GPT_MODEL_NAME,
        reasoning_effort: REASONING_EFFORT,
        chatgpt_acc_id: str,
        auth_token: str,
        messages: List[Dict[str, Any]],
        adaptor: IResponsesAdaptorWS,
        web_search: bool = True,
        instructions: str | None = None,
        reasoning_summary: REASONING_SUMMARY = "auto",
        session_id: Optional[str] = None,
        timeout_s: float = 600.0
    ) -> Iterator[Dict[str, Any]]:
        for event in self._request(
            model_name=model_name,
            reasoning_effort=reasoning_effort,
            chatgpt_acc_id=chatgpt_acc_id,
            auth_token=auth_token,
            messages=messages,
            web_search=web_search,
            instructions=instructions,
            reasoning_summary=reasoning_summary,
            session_id=session_id,
            timeout_s=timeout_s,
        ):
            yield adaptor.translate(event)

    def request_http(
        self,
        model_name: GPT_MODEL_NAME,
        reasoning_effort: REASONING_EFFORT,
        chatgpt_acc_id: str,
        auth_token: str,
        messages: List[Dict[str, Any]],
        adaptor: IResponsesAdaptorHTTP,
        web_search: bool = True,
        instructions: str | None = None,
        reasoning_summary: REASONING_SUMMARY = "auto",
        session_id: Optional[str] = None,
        timeout_s: float = 600.0
    ) -> Dict[str, Any]:
        last_event = [
            event for event in self._request(
                model_name=model_name,
                reasoning_effort=reasoning_effort,
                chatgpt_acc_id=chatgpt_acc_id,
                auth_token=auth_token,
                messages=messages,
                web_search=web_search,
                instructions=instructions,
                reasoning_summary=reasoning_summary,
                session_id=session_id,
                timeout_s=timeout_s,
            )
        ][-1]

        return adaptor.translate(last_event)


    # Private

    def _request(
        self,
        model_name: GPT_MODEL_NAME,
        reasoning_effort: REASONING_EFFORT,
        chatgpt_acc_id: str,
        auth_token: str,
        messages: List[Dict[str, Any]],
        web_search: bool = True,
        instructions: str | None = None,
        reasoning_summary: REASONING_SUMMARY = "auto",
        session_id: Optional[str] = None,
        timeout_s: float = 600.0,
    ) -> Iterator[Dict[str, Any]]:
        sid = ensure_session_id(instructions, messages, client_supplied=session_id)
        turn_metadata = json.dumps({"turn_id": "", "sandbox": "seatbelt"}, separators=(",", ":"))

        headers: Dict[str, str] = DEFAULT_CODEX_HEADERS.copy()
        headers.update({
            "Authorization": f"Bearer {auth_token}",
            "chatgpt-account-id": chatgpt_acc_id,
            "session_id": sid,
            "x-codex-turn-metadata": turn_metadata,
        })

        filtered_messages: List[Dict[str, Any]] = []

        for message in messages:
            if message["role"] == "system":
                instructions = message["content"][0]["text"]
            else:
                filtered_messages.append(message)

        data = {
            "type": "response.create",
            "model": model_name,
            "reasoning": {
                "effort": reasoning_effort,
                "summary": reasoning_summary,
            },
            "instructions": instructions or "",
            "input": filtered_messages,
            # "store": False,
            "stream": True,
            "tool_choice": "auto",
            "parallel_tool_calls": True,
            "prompt_cache_key": sid,
            # "text": {
            #     "verbosity": "low"
            # },
        }

        if web_search:
            data["tools"] = [
                {
                    "type": "web_search",
                    "external_web_access": True,
                    "search_content_types": [
                        "text"
                    ]
                }
            ]

        if reasoning_summary != "none":
            data["include"] = [
                "reasoning.encrypted_content"
            ]

        ws: WebSocket = create_connection(URL_CODEX_WSS, header=headers, timeout=timeout_s)
        try:
            ws.send(
                json.dumps(
                    data,
                    separators=(",", ":"),
                )
            )

            while True:
                raw = ws.recv()
                if raw is None:
                    break

                event = json.loads(raw)
                yield event

                etype = event.get("type")
                if etype in ("response.completed", "response.failed", "response.cancelled"):
                    break

                if etype == "error":
                    raise Exception(event.get("error"))
        finally:
            try:
                ws.close()
            except Exception:
                pass
