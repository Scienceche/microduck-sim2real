# 训练复现记录（train-repro）

> Day 4 任务：逐项标注训练配置。原则——**每项都用自己的话解释 + 给出处**，
> 不确定就写"不确定"，不编。

## 复现命令（冒烟，3 分钟级）

```bash
cd C:/duck_work/microduck_rl
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max_iterations 5
```

## 小规模基线（Day 3 回填）

- 命令：`scripts/train.sh configs/train_small.yaml`
- 结果：⬜（曲线截图进 `reports/`，数值回填 env-lock 吞吐表）

## 配置逐项标注（Day 4 待办，现在先钉住已实测的）

| 项 | 值（实测） | 出处 |
|---|---|---|
| 物理 timestep | 0.005 s（200 Hz） | run14 日志表 |
| decimation | 4 | 注册表探针 |
| 控制步 | 0.02 s（50 Hz） | run14 日志表 |
| 主动关节 | 14（BamActuator，Feetech HD1910 参数来自本地 bam） | run14 日志:44 |
| num_envs（默认/全量/冒烟） | 1（注册默认，必传）/ 4096 / 64 | 探针 + 上游 AGENTS.md |
| rollout 长度 num_steps_per_env | 24 | 注册表探针 |
| save_interval 默认 | 250 | 注册表探针 |

## 待 Day 4 逐项标注（打开 `microduck_velocity_env_cfg.py`）

- [ ] 观测维度与各项含义
- [ ] reward 每一项：名字 / 权重 / 物理含义
- [ ] 域随机化：哪些参数、各自范围
- [ ] curriculum：阶段划分与门槛
- [ ] PPO 超参（lr、entropy、minibatch…）来自 `MicroduckRlCfg`

## 冒烟实测补充（2026-11-21，logs/smoke_w1_evidence.log）

- 网络：actor 61→512→256→128→14；critic 76→…→1；obs_normalizer 在模型内。
- Velocity 任务 reward 分项（冒烟日志 18 项）：track_linear/angular_velocity、
  upright、pose、body_ang_vel、angular_momentum、dof_pos_limits、action_rate_l2、
  air_time、foot_clearance、foot_swing_height、foot_slip、self_collisions、
  head_pose_tracking、body_pose_tracking、head_pose_bias 等——Day 4 逐项标权重。
