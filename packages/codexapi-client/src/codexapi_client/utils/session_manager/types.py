from typing import Any, Dict, List, Literal, TypeAlias


InputItem: TypeAlias = Dict[str, Any]
InputItems: TypeAlias = List[InputItem]
RequestContext: TypeAlias = Dict[str, Any]
SessionMatchSource: TypeAlias = Literal["client", "exact", "parent", "new"]
