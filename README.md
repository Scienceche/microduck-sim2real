# microduck-sim2real

第一周工程资产层：把"脚本跑通了"固化成**可复现、可观测、可交接**的训练资产。
训练本体在 `C:\duck_work\microduck_rl`（mjlab + rsl_rl_lib PPO + mujoco-warp GPU 物理），
本仓库只做环境锁定、配置、脚本、文档、周报。环境实测值见 `docs/env-lock.md`。

## 怎么跑（1 小时复现口径）

```bash
# 冒烟（~分钟级，上游既定口径 64 env × 5 iter）
bash scripts/train.sh configs/train_smoke.yaml

# 小规模基线（第一周主线，~1.2M env-steps）
bash scripts/train.sh configs/train_small.yaml
```

前置：`C:\duck_work\microduck_rl` 已 `uv sync`、`C:\duck_work\bam` 在位（见 env-lock）。
曲线：`uv run tensorboard --logdir C:/duck_work/microduck_rl/logs/rsl_rl`。

## 进度

- [x] Day 1–2 环境固化：env-lock.md 全实测落盘
- [x] Docker 全链路（2026-11-22）：Desktop 4.99 装好（数据盘迁 E:\docker-wsl，代理 Clash 7897），镜像 build 成功（imports OK），GPU 容器冒烟 64×5 通过
- [x] Day 3 小规模基线：1024 env × 50 iter 跑通（~11.5k steps/s，1.23M 步 @107 s，checkpoint 齐全）；显存峰值待下次旁挂记录
- [ ] Day 4 读懂配置：train-repro.md 逐项标注
- [ ] Day 5 数据流图：dataflow.md ⬜ 项补齐
- [ ] Day 6–7 复盘：reports/week1.md

**成功标准：另一个人拿到本仓库，按 README 在 1 小时内复现出小规模训练曲线。**
