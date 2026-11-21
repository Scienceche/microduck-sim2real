#!/usr/bin/env bash
# 评测入口（框架）：仿真回放 + 电池行为评测，实机 acceptance_pipeline 见 AGENTS.md。
# 原则（AGENTS.md 第 4 节）：奖励 ≠ 行为，一切判定以行为评测为准；判据先校准。
#
# 用法（仿真回放训练出的策略）:
#   bash scripts/eval.sh <wandb-run-path 或 本地 logs/rsl_rl/<exp>/<run> 目录>
set -euo pipefail

RL_REPO="${MICRODUCK_RL_REPO:-C:/duck_work/microduck_rl}"
RUN="${1:?用法: eval.sh <run-path-or-wandb-run-path> [task]}"
TASK="${2:-Mjlab-Velocity-Flat-MicroDuck}"

cd "$RL_REPO"
if [[ -d "$RUN" ]]; then
  echo "[eval.sh] 本地 run 目录模式尚未接线——Day 3 基线后按实际产物补齐" >&2
  exit 2
fi
exec uv run play "$TASK" --wandb-run-path "$RUN"
