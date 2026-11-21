#!/usr/bin/env bash
# 训练入口：bash scripts/train.sh configs/train_small.yaml [-- 额外 tyro 旗标透传]
# 示例：bash scripts/train.sh configs/train_smoke.yaml
#       bash scripts/train.sh configs/train_small.yaml -- --agent.resume True
set -euo pipefail

SIM2REAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RL_REPO="${MICRODUCK_RL_REPO:-C:/duck_work/microduck_rl}"
VENV_PY="${MICRODUCK_PYTHON:-$RL_REPO/.venv/Scripts/python.exe}"

CONFIG="${1:?用法: train.sh <configs/*.yaml> [-- extra-flags]}"
shift || true
EXTRA=()
if [[ "${1:-}" == "--" ]]; then
  shift
  EXTRA=("$@")
fi

read -r -a ARGS <<< "$("$VENV_PY" -I "$SIM2REAL_ROOT/scripts/yaml_to_flags.py" "$CONFIG")"

cd "$RL_REPO"
echo "[train.sh] config=$CONFIG"
echo "[train.sh] cd $RL_REPO && uv run train ${ARGS[*]} ${EXTRA[*]:+${EXTRA[*]}}"
exec uv run train "${ARGS[@]}" ${EXTRA[@]+"${EXTRA[@]}"}
