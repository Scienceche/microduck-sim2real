# 第一周周报（Day 6–7 填完）

## 环境版本
见 `docs/env-lock.md`（全部 2026-11-21 实测）。

## 训练曲线
⬜ Day 3：贴 train_small 基线曲线截图 + reward 分项表。

## 显存/耗时
| 口径 | 值 |
|---|---|
| 64 env 冒烟 | ~820 steps/s 稳态；全程 ~2.5 min（含启动）✅2026-11-21 |
| 1024 env 基线 | ~11.5k steps/s；50 iter=1.23M 步 @107 s ✅2026-11-21（`logs/baseline_w1.log`）|

## 训练曲线
- tfevents：`C:\duck_work\microduck_rl\logs\rsl_rl\velocity\2026-11-21_13-58-09_week1_small_baseline`
- 查看：`uv run tensorboard --logdir C:/duck_work/microduck_rl/logs/rsl_rl`
- ⬜ Day 6–7：曲线截图 + 关键指标表贴进来

## 遇到的问题
见 `docs/troubleshooting.md`（已记 7 条，含本日两次内联 python 事故）。

## 下周计划
⬜（候选：完整训练 train_full 定稿、评测口径校准、ONNX 导出对表、实机部署管线接线）
