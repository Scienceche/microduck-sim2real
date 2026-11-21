#!/usr/bin/env bash
# ONNX 导出入口（上游命令，见 microduck_rl/README.md:46）：
#   uv run scripts/export.py <TASK> --wandb-run-path <entity/project/run_id>
# 导出后自检（AGENTS.md 第 2 节）：onnx 输入输出 shape 与 dataflow.md 对表。
set -euo pipefail

RL_REPO="${MICRODUCK_RL_REPO:-C:/duck_work/microduck_rl}"
TASK="${1:-Mjlab-Velocity-Flat-MicroDuck}"
RUN_PATH="${2:?用法: export_onnx.sh [task] <wandb-run-path>}"

cd "$RL_REPO"
exec uv run scripts/export.py "$TASK" --wandb-run-path "$RUN_PATH"
