from dataclasses import dataclass, field
from typing import Any, Dict, List
import time


@dataclass
class MemoryRecord:
    agent_id: str
    content: str
    tags: List[str] = field(default_factory=list)
    score: float = 1.0
    timestamp: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)


class HierarchicalMemory:
    def __init__(self, short_max: int = 50, retros_max: int = 30):
        self.short_term: List[MemoryRecord] = []
        self.long_term: List[MemoryRecord] = []
        self.retrospective: List[MemoryRecord] = []
        self.short_max = short_max
        self.retros_max = retros_max

    def write_short(self, record: MemoryRecord) -> None:
        self.short_term.append(record)
        if len(self.short_term) > self.short_max:
            self.short_term.pop(0)

    def write_long(self, record: MemoryRecord) -> None:
        self.long_term.append(record)

    def write_retrospective(self, record: MemoryRecord) -> None:
        self.retrospective.append(record)
        if len(self.retrospective) > self.retros_max:
            self.retrospective.pop(0)

    def retrieve_long(self, query: str, top_k: int = 8) -> List[MemoryRecord]:
        q = query.lower()
        ranked = sorted(
            self.long_term,
            key=lambda r: (q in r.content.lower(), r.score, r.timestamp),
            reverse=True,
        )
        return ranked[:top_k]

