from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class BoundaryType:
    name: str
    priority: int
    aliases: List[str] = field(default_factory=list)
    description: str = ""

class BoundaryTypeRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BoundaryTypeRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._types: Dict[str, BoundaryType] = {}
        self._alias_map: Dict[str, str] = {}
        self._initialized = True
        self._register_defaults()

    def _register_defaults(self):
        defaults = [
            BoundaryType("DOCUMENT_END", 100, ["end", "doc_end"], "Reached the end of the document structure"),
            BoundaryType("HEADING_BREAK", 95, ["heading_change", "heading"], "Transition to a new heading block"),
            BoundaryType("SECTION_BREAK", 90, ["section_change", "section"], "Transition to a new section boundary"),
            BoundaryType("CODE_START", 88, ["code_begin"], "Beginning of a code block"),
            BoundaryType("CODE_END", 88, ["code_exit"], "End of a code block"),
            BoundaryType("TABLE_START", 85, ["table_begin"], "Beginning of a table block"),
            BoundaryType("TABLE_END", 85, ["table_exit"], "End of a table block"),
            BoundaryType("FORMULA_START", 80, ["formula_begin"], "Beginning of a formula block"),
            BoundaryType("FORMULA_END", 80, ["formula_exit"], "End of a formula block"),
            BoundaryType("WARNING_START", 75, ["warning_begin"], "Beginning of a warning block"),
            BoundaryType("WARNING_END", 75, ["warning_exit"], "End of a warning block"),
            BoundaryType("LIST_START", 70, ["list_begin"], "Beginning of a bullet or numbered list block"),
            BoundaryType("LIST_END", 70, ["list_exit"], "End of a list block"),
            BoundaryType("TOPIC_SHIFT", 60, ["topic_change"], "High semantic distance or defined topic transitions"),
            BoundaryType("FALLBACK_BOUNDARY", 20, ["paragraph_boundary", "fallback"], "Default fallback boundary between adjacent blocks")
        ]
        for t in defaults:
            self.register(t)

    def register(self, boundary_type: BoundaryType) -> None:
        self._types[boundary_type.name] = boundary_type
        self._alias_map[boundary_type.name] = boundary_type.name
        for alias in boundary_type.aliases:
            self._alias_map[alias] = boundary_type.name

    def unregister(self, name: str) -> None:
        if name in self._types:
            bt = self._types.pop(name)
            self._alias_map.pop(name, None)
            for alias in bt.aliases:
                self._alias_map.pop(alias, None)

    def exists(self, name: str) -> bool:
        resolved = self.resolve_alias(name)
        return resolved in self._types

    def get(self, name: str) -> Optional[BoundaryType]:
        resolved = self.resolve_alias(name)
        return self._types.get(resolved) if resolved else None

    def priority(self, name: str) -> int:
        bt = self.get(name)
        return bt.priority if bt else 20

    def resolve_alias(self, alias: str) -> Optional[str]:
        return self._alias_map.get(alias)

    def list_types(self) -> List[BoundaryType]:
        return sorted(self._types.values(), key=lambda x: x.priority, reverse=True)
