# HMAS 研究闭环实验工作流

本项目用于落地异构多智能体系统（HMAS）记忆研究，聚焦三类痛点：
- 异构架构下记忆格式不兼容
- 长时记忆召回效率低
- 缺乏标准化测评流程

## 目标方案

- 以 `Claude Code` + `Codex` 作为开发协作环境
- 使用 `deepseek-v4-pro` 执行长链推理与记忆关联决策
- 使用 `deepseek-v4-flash` 处理高并发记忆同步、快速调试与迭代
- 基于 `OpenCLAW` 对自研模块与开源基线（如 cognee / hindsight）做对照测评

## 项目结构

```text
hmas研究/
  configs/
    pipeline.yaml
  scripts/
    run_pipeline.py
  src/
    memory/
      hierarchy.py
      adapter.py
    models/
      deepseek_router.py
    eval/
      openclaw_bridge.py
    utils/
      io.py
  data/
  results/
```

## 快速开始

1. 创建环境并安装依赖（示例）
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install pyyaml
```

2. 配置 `configs/pipeline.yaml`
- 填写 DeepSeek API Key（可通过环境变量注入）
- 设置 OpenCLAW 路径与基线项目路径

3. 运行闭环流程
```bash
python scripts/run_pipeline.py --config configs/pipeline.yaml
```

## 流程说明

1. 记忆适配阶段：
- 统一写入短期记忆、长期记忆、复盘记忆
- 以统一 schema 适配多智能体读写协议

2. 双模型协同阶段：
- `v4-pro`：复杂记忆关联与长链推理
- `v4-flash`：并发同步、错误定位与快速反馈

3. 基准测评阶段：
- 调用 OpenCLAW 对自研模块与基线进行统一输入、统一指标评估
- 输出结果到 `results/summary.json`

## 下一步扩展建议

- 接入向量数据库（Milvus / FAISS）优化长期记忆检索
- 增加召回延迟、命中率、跨 agent 一致性等指标
- 引入自动化 ablation（关闭某层记忆或关闭某模型）做消融评估

