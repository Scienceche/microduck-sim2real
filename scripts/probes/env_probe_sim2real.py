"""环境探针：环境版本锁定表（docs/env-lock.md）的数据来源。

用法：C:/duck_work/microduck_rl/.venv/Scripts/python.exe -I env_probe_sim2real.py
"""
import importlib.metadata as m
import sys

print("python", sys.version.replace("\n", " "))
import torch

print("torch", torch.__version__, "| cuda build:", torch.version.cuda,
      "| cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print("gpu:", p.name, "| sm_", f"{p.major}{p.minor}",
          "| vram GiB:", round(p.total_memory / 1024**3, 1))

import mujoco

print("mujoco", mujoco.__version__)

import warp

print("warp-lang", m.version("warp-lang"))

# 注意 rsl_rl 的发行名是 rsl_rl_lib（查 rsl-rl / rsl_rl 会误报未安装）
for dist in ["mjlab", "rsl_rl_lib", "better-actuator-models", "onnxruntime",
             "scipy", "tensorboard", "matplotlib", "onnx"]:
    try:
        print(dist, m.version(dist))
    except m.PackageNotFoundError:
        print(dist, "NOT INSTALLED")
