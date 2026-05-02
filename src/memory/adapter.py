from typing import Dict, Any
from .hierarchy import HierarchicalMemory, MemoryRecord


class HeterogeneousMemoryAdapter:
    """
    统一异构 agent 的记忆读写协议：
    输入任意结构 -> 规范化为统一 schema -> 写入分层记忆
    """

    def __init__(self, memory: HierarchicalMemory):
        self.memory = memory

    def normalize(self, payload: Dict[str, Any]) -> MemoryRecord:
        return MemoryRecord(
            agent_id=str(payload.get("agent_id", "unknown")),
            content=str(payload.get("content", "")),
            tags=list(payload.get("tags", [])),
            score=float(payload.get("score", 1.0)),
            meta=dict(payload.get("meta", {})),
        )

    def write(self, layer: str, payload: Dict[str, Any]) -> None:
        record = self.normalize(payload)
        if layer == "short":
            self.memory.write_short(record)
        elif layer == "long":
            self.memory.write_long(record)
        elif layer == "retrospective":
            self.memory.write_retrospective(record)
        else:
            raise ValueError(f"unknown layer: {layer}")

    def read_long(self, query: str, top_k: int = 8):
        return self.memory.retrieve_long(query, top_k=top_k)

