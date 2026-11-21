# 数据流图：观测 → 策略 → 动作 → robotd → 电机（Day 5 完成度：骨架 + 已实测事实）

> 本文档是部署与排障的"地图"。标 ✅ 的数字是 2026-11-21 实测/代码取证；
> 标 ⬜ 的等 Day 5 逐项打开代码补齐（补完把 ⬜ 改 ✅ 并注明出处 file:line）。

```
┌─ 仿真训练侧（mjlab，GPU mujoco-warp）────────────────────────────┐
│                                                                  │
│  物理 200 Hz (timestep 0.005 s)                                  │
│    └─ decimation 4 → 环境/控制步 50 Hz (0.02 s) ✅run14 日志       │
│                                                                  │
│  观测：actor 61 维 / critic 76 维（特权），具体分项 ⬜Day 5 逐项列   │
│  策略 MLP：61 → 512 → 256 → 128（ELU）→ 14 ✅（冒烟日志模型打印）   │
│    └─ 动作 = 14 个主动关节目标位置；归一化 obs_normalizer 在模型内   │
│      (EmpiricalNormalization)✅；passive_* 关节不进 ONNX ✅ Patch 4 │
│  动作 → BamActuator（Feetech HD1910 电机模型，含 backlash 编码器    │
│         反馈、电压跌落、摩擦）✅14/14 joints                       │
└──────────────────────────────────────────────────────────────────┘
                              │ ONNX 导出（scripts/export.py）
                              ▼
┌─ 实机部署侧（鸭子）──────────────────────────────────────────────┐
│  robotd @ 50 Hz ✅（与仿真控制频率一致——这是 sim2real 的地基）      │
│    观测组装 → ONNX 前向 → 关节目标 → Feetech 总线 → 电机           │
│    具体维度/裁剪/单位映射 ⬜ 实机阶段补（对照鸭子 /opt/robot/…）     │
└──────────────────────────────────────────────────────────────────┘
```

## 待 Day 5 补齐清单

- [ ] 观测张量逐项列表 + 每项维度（打印一次 `env.observation_space` 或
      `params/env.yaml` 的 obs 段落为证）
- [ ] 归一化（obs scale / clip）发生在 env 还是部署侧 runtime
- [ ] ONNX 输入输出名、shape、dtype（`onnxruntime` session 元数据为证）
- [ ] 实机 robotd 观测组装与仿真观测的一一对应表（部署排障时直接查表）
