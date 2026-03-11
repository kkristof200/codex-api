import hashlib
import threading
import uuid
from typing import Dict, List

from ._canonicalization import canonicalize_cache_prefix, canonicalize_conversation
from .models import ConversationState, Session
from .types import InputItems, RequestContext, SessionMatchSource


class SessionManager:
    def __init__(
        self,
        max_entries: int = 10000
    ) -> None:
        self._lock = threading.Lock()
        self._full_to_state: Dict[str, ConversationState] = {}
        self._full_order: List[str] = []
        self._max_entries = max_entries

    # Public

    def create(
        self,
        instructions: str | None,
        input_items: InputItems,
        client_supplied: str | None = None,
        request_context: RequestContext | None = None,
    ) -> Session:
        session_id, match_source = self._ensure_session_id(
            instructions=instructions,
            input_items=input_items,
            client_supplied=client_supplied,
            request_context=request_context,
        )
        prompt_cache_key = self._build_prompt_cache_key(
            instructions=instructions,
            input_items=input_items,
            request_context=request_context,
        )
        return Session(
            session_id=session_id,
            prompt_cache_key=prompt_cache_key,
            match_source=match_source,
        )

    # Private

    def _build_prompt_cache_key(
        self,
        instructions: str | None,
        input_items: InputItems,
        request_context: RequestContext | None,
    ) -> str:
        return self._fingerprint(
            canonicalize_cache_prefix(
                instructions=instructions,
                input_items=input_items,
                request_context=request_context,
            )
        )

    def _ensure_session_id(
        self,
        instructions: str | None,
        input_items: InputItems,
        client_supplied: str | None,
        request_context: RequestContext | None,
    ) -> tuple[str, SessionMatchSource]:
        if isinstance(client_supplied, str) and client_supplied.strip():
            return client_supplied.strip(), "client"

        full_fp = self._build_full_fingerprint(instructions, input_items, request_context)
        parent_full_fp = self._build_parent_fingerprint(instructions, input_items, request_context)

        with self._lock:
            existing = self._full_to_state.get(full_fp)
            if existing is not None:
                return existing.session_id, "exact"

            session_id = self._find_parent_session(parent_full_fp)
            match_source: SessionMatchSource = "parent"
            if session_id is None:
                session_id = str(uuid.uuid4())
                match_source = "new"

            self._remember_full(
                full_fp=full_fp,
                state=ConversationState(session_id=session_id, parent_full_fp=parent_full_fp),
            )
            return session_id, match_source

    def _build_full_fingerprint(
        self,
        instructions: str | None,
        input_items: InputItems,
        request_context: RequestContext | None,
    ) -> str:
        return self._fingerprint(
            canonicalize_conversation(
                instructions=instructions,
                input_items=input_items,
                request_context=request_context,
            )
        )

    def _build_parent_fingerprint(
        self,
        instructions: str | None,
        input_items: InputItems,
        request_context: RequestContext | None,
    ) -> str | None:
        if not input_items:
            return None
        return self._build_full_fingerprint(
            instructions=instructions,
            input_items=input_items[:-1],
            request_context=request_context,
        )

    def _find_parent_session(self, parent_full_fp: str | None) -> str | None:
        if parent_full_fp is None:
            return None
        parent_state = self._full_to_state.get(parent_full_fp)
        if parent_state is None:
            return None
        return parent_state.session_id

    def _fingerprint(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _remember_full(self, full_fp: str, state: ConversationState) -> None:
        if full_fp in self._full_to_state:
            return
        self._full_to_state[full_fp] = state
        self._full_order.append(full_fp)
        if len(self._full_order) > self._max_entries:
            oldest = self._full_order.pop(0)
            self._full_to_state.pop(oldest, None)
