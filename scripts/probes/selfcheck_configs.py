"""交付自检：configs 三个 yaml 可解析 + yaml_to_flags 映射输出正确 + typo 必须被拒绝。

用法：C:/duck_work/microduck_rl/.venv/Scripts/python.exe -I selfcheck_configs.py
"""
import os
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENV_PY = r"C:\duck_work\microduck_rl\.venv\Scripts\python.exe"

for name in ["train_smoke", "train_small", "train_full"]:
    path = os.path.join(ROOT, "configs", f"{name}.yaml")
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    assert cfg["task"] and cfg["num_envs"] >= 64 and cfg["max_iterations"] >= 5, (name, cfg)
    out = subprocess.run(
        [VENV_PY, "-I", os.path.join(ROOT, "scripts", "yaml_to_flags.py"), path],
        capture_output=True, text=True, check=True).stdout.strip()
    print(f"{name}: {out}")

# 冒烟配置必须等于上游 AGENTS.md 既定口径 64×5
smoke = yaml.safe_load(open(os.path.join(ROOT, "configs", "train_smoke.yaml"), encoding="utf-8"))
assert (smoke["num_envs"], smoke["max_iterations"]) == (64, 5), smoke

# 拼错字段必须被拒绝（防 typo 静默失效 → num_envs 默认=1 事故，troubleshooting #6）
typo = os.path.join(ROOT, "configs", "_typo_test.yaml")
open(typo, "w", encoding="utf-8").write("task: X\nnum_envss: 64\n")
bad = subprocess.run(
    [VENV_PY, "-I", os.path.join(ROOT, "scripts", "yaml_to_flags.py"), typo],
    capture_output=True, text=True)
assert bad.returncode != 0 and "未知字段" in bad.stderr, bad.stderr
os.remove(typo)
print("ALL SELF-CHECKS PASSED")
