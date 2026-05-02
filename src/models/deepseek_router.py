from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ModelConfig:
    provider: str
    model: str
    api_key_env: str


class DeepSeekDualRouter:
    def __init__(self, planner: ModelConfig, syncer: ModelConfig):
        self.planner = planner
        self.syncer = syncer

    def route(self, task_type: str, prompt: str) -> Dict[str, Any]:
        if task_type in {"reasoning", "association", "planning"}:
            chosen = self.planner
        else:
            chosen = self.syncer
        # 这里预留真实 API 调用，当前返回可观测模拟结果用于工作流调试
        return {
            "provider": chosen.provider,
            "model": chosen.model,
            "task_type": task_type,
            "output": f"[mocked:{chosen.model}] {prompt[:120]}",
        }

