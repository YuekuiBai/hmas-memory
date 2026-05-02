import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from memory.hierarchy import HierarchicalMemory
from memory.adapter import HeterogeneousMemoryAdapter
from models.deepseek_router import DeepSeekDualRouter, ModelConfig
from eval.openclaw_bridge import OpenCLAWBridge
from utils.io import load_yaml, dump_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to pipeline yaml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)

    planner_cfg = cfg["models"]["planner"]
    syncer_cfg = cfg["models"]["syncer"]
    router = DeepSeekDualRouter(
        planner=ModelConfig(**planner_cfg),
        syncer=ModelConfig(**syncer_cfg),
    )

    # 读取 API key 环境变量（当前示例不实际调用远程 API）
    for c in (planner_cfg, syncer_cfg):
        _ = os.getenv(c["api_key_env"], "")

    mem_cfg = cfg["memory"]
    memory = HierarchicalMemory(
        short_max=mem_cfg["short_term"]["max_items"],
        retros_max=mem_cfg["retrospective"]["max_items"],
    )
    adapter = HeterogeneousMemoryAdapter(memory)

    # 1) 记忆写入/适配
    adapter.write("short", {"agent_id": "planner", "content": "任务拆解完成", "tags": ["plan"]})
    adapter.write("long", {"agent_id": "executor", "content": "长期策略：优先召回含任务关键词的记忆", "score": 1.2})
    adapter.write("retrospective", {"agent_id": "reviewer", "content": "上一轮遗漏了跨agent一致性检查"})

    # 2) 双模型协作
    reasoning_out = router.route("reasoning", "基于当前任务进行跨层记忆关联")
    sync_out = router.route("sync", "并发同步3个agent的最新记忆快照")
    recalls = adapter.read_long("任务关键词", top_k=mem_cfg["long_term"]["top_k"])

    # 3) OpenCLAW 基准评估（示例桥接）
    eval_cfg = cfg["evaluation"]
    openclaw = OpenCLAWBridge(
        openclaw_path=eval_cfg["openclaw_path"],
        metrics=eval_cfg["metrics"],
    )
    self_result = openclaw.evaluate(cfg["project"]["name"], cfg["experiment"]["tasks"])
    baseline_results = []
    for b in cfg.get("baselines", []):
        baseline_results.append(openclaw.evaluate(b["name"], cfg["experiment"]["tasks"]))

    report = {
        "project": cfg["project"]["name"],
        "reasoning_output": reasoning_out,
        "sync_output": sync_out,
        "retrieved_long_memories": [r.content for r in recalls],
        "self_eval": self_result,
        "baselines_eval": baseline_results,
    }

    out_path = ROOT / cfg["project"]["output_dir"] / "summary.json"
    dump_json(str(out_path), report)
    print(f"Pipeline finished. Report: {out_path}")


if __name__ == "__main__":
    main()

