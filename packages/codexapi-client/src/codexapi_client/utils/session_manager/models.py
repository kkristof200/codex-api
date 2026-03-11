from dataclasses import dataclass

from pydantic import BaseModel

from .types import SessionMatchSource


class Session(BaseModel):
    session_id: str
    prompt_cache_key: str
    match_source: SessionMatchSource


@dataclass(frozen=True)
class ConversationState:
    session_id: str
    parent_full_fp: str | None
