from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class SemanticType:
    name: str
    display_name: str
    category: str
    description: str = ""
    default_importance: float = 0.5
    priority: int = 100
    aliases: List[str] = field(default_factory=list)

class SemanticTypeRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SemanticTypeRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._types: Dict[str, SemanticType] = {}
        self._alias_map: Dict[str, str] = {}
        self._initialized = True
        self._register_defaults()

    def _register_defaults(self):
        # Register standard semantic types
        defaults = [
            SemanticType("paragraph", "Paragraph", "text", "Standard block of text", 0.50, 1000),
            SemanticType("definition", "Definition", "concept", "Explanation of a term or concept", 0.85, 10, ["def", "term_explanation"]),
            SemanticType("example", "Example", "reference", "Illustrative sample or code snippet example", 0.60, 50, ["eg", "illustration", "sample"]),
            SemanticType("algorithm", "Algorithm", "procedure", "Sequence of steps or pseudo-code", 0.85, 20, ["step_list", "procedure", "pseudo_code"]),
            SemanticType("warning", "Warning", "callout", "Cautionary information or critical alert", 0.90, 5, ["caution", "danger", "alert"]),
            SemanticType("tip", "Tip", "callout", "Best practice, advice, or tip", 0.85, 15, ["note", "hint", "best_practice"]),
            SemanticType("summary", "Summary", "text", "Recap or key takeaways of preceding information", 0.75, 40, ["conclusion", "recap", "takeaways"]),
            SemanticType("code", "Code Block", "technical", "Code block or raw code", 0.70, 30, ["code_block", "source_code"]),
            SemanticType("table", "Table", "structured", "Tabular data presentation", 0.70, 30, ["tabular", "grid"]),
            SemanticType("formula", "Formula", "technical", "Mathematical expression or equation", 0.80, 25, ["equation", "math"]),
            SemanticType("question", "Question", "interaction", "A question or inquiry", 0.65, 35, ["q", "inquiry"]),
            SemanticType("answer", "Answer", "interaction", "An answer or solution to a question", 0.65, 35, ["a", "response", "solution"])
        ]
        for t in defaults:
            self.register(t)

    def register(self, sem_type: SemanticType) -> None:
        self._types[sem_type.name] = sem_type
        # Add primary name to alias map
        self._alias_map[sem_type.name] = sem_type.name
        for alias in sem_type.aliases:
            self._alias_map[alias] = sem_type.name

    def unregister(self, name: str) -> None:
        if name in self._types:
            sem_type = self._types.pop(name)
            # Remove aliases
            self._alias_map.pop(name, None)
            for alias in sem_type.aliases:
                self._alias_map.pop(alias, None)

    def exists(self, name: str) -> bool:
        resolved = self.resolve_alias(name)
        return resolved in self._types

    def get(self, name: str) -> Optional[SemanticType]:
        resolved = self.resolve_alias(name)
        return self._types.get(resolved) if resolved else None

    def list_types(self) -> List[SemanticType]:
        # Return sorted by priority
        return sorted(self._types.values(), key=lambda x: x.priority)

    def resolve_alias(self, alias: str) -> Optional[str]:
        return self._alias_map.get(alias)
