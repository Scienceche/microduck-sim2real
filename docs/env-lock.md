# 环境版本锁定表（env-lock）

> 生成日期：2026-11-21。所有数值均为**当日在本机实测**，非记忆或文档抄录。
> 复现探针：`scripts/probes/env_probe_sim2real.py`、`scripts/probes/task_defaults_probe.py`
> （用 `C:/duck_work/microduck_rl/.venv/Scripts/python.exe -I` 运行）。

## 硬件 / 驱动

| 项 | 值 | 证据 |
|---|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti（Blackwell，sm_120） | nvidia-smi 2026-11-21 13:41 |
| 显存 | 16311 MiB（torch 可见 15.9 GiB）；WDDM 模式，桌面常驻占用 ~3.3 GiB | nvidia-smi / torch 探针 |
| 驱动 | KMD 610.88，CUDA UMD 13.3 | nvidia-smi 头部 |
| CUDA 运行时 | torch 自带 cu128；warp 报 "CUDA Toolkit 12.9, Driver 13.3" | run14_train.log:18 |
| OS | Windows 11 10.0.26200 x64 + Git Bash | winver / shell |

**注意：sm_120 必须 CUDA ≥ 12.8**（`microduck_rl/pyproject.toml` cu128 source 注释），
Windows 上 PyPI 的 torch 是 CPU-only，pyproject 已用 `tool.uv.sources` 路由到
`pytorch-cu128` index——换机器复现时不要手改。

## Python / 工具链

| 项 | 值 |
|---|---|
| Python | 3.12.14（uv 托管；约束 `>=3.12,<3.13`，bam 钉死上限） |
| uv | 0.12.10 |
| venv 位置 | `C:\duck_work\microduck_rl\.venv` |

## 训练栈（`pip` 实测版本）

| 包 | 版本 | 备注 |
|---|---|---|
| mjlab | 1.3.0 | RL 框架（manager-based env + mujoco-warp GPU 物理） |
| rsl_rl_lib | 5.0.1 | PPO 实现。**发行名是 `rsl_rl_lib`**，查 `rsl-rl`/`rsl_rl` 会报不存在 |
| torch | 2.9.1+cu128 | cuda_available=True，本机直跑 GPU |
| mujoco | 3.10.0 | 被 mjlab 的 mujoco-warp 兼容性锁定，**勿 override**（见 troubleshooting #3） |
| warp-lang | 1.12.0 | GPU 内核层 |
| better-actuator-models | 1.0.1 | **本地 editable `C:\duck_work\bam`**（Feetech HD1910 实测参数），不在 PyPI |
| onnxruntime / onnx | 1.24.4 / 1.22.0 | 导出/验证 |
| scipy / tensorboard / matplotlib | 1.18.0 / 2.20.0 / 3.10.9 | |

## 关键默认值（注册表实测，不是猜的）

- **所有 MicroDuck 任务注册的 `scene.num_envs` 默认 = 1**。忘传 `--env.scene.num-envs`
  就会像 run14 那样单环境空转（`BamActuator ... envs=1`，run14_train.log:44）。
- 仓库约定（`microduck_rl/AGENTS.md:15-16`）：全量 `4096`，冒烟 `64 env × 5 iter`。
- 上游口径：4096 env 训出可用步态约 **1–2 小时**（`microduck_rl/README.md:39`）。
- 控制频率（run14 日志表格实测）：物理步 0.005 s（200 Hz）× decimation 4 = 环境步
  0.02 s（**50 Hz，与实机 robotd 50 Hz 一致**）。
- 活动关节 14 个（BamActuator joints=14，backlash 编码器反馈 14/14）；ONNX 导出会
  过滤 `passive_*` 关节（mdp Patch 4）。

## 吞吐 / 耗时（2026-11-21 实测）

| 口径 | 值 | 证据 |
|---|---|---|
| 64 env 冒烟（5 iter） | 稳态 ~820 steps/s（1.85 s/iter，首 iter 3.4 s 预热）；训练段 10 s，含启动全程 ~2.5 min | `logs/smoke_w1_evidence.log` |
| run14 参照（1 env 微调） | 22–34 steps/s，0.70 s/iter，2000 iter = 22 min | run14_train.log（单环境无并行意义，仅作对照） |
| 1024 env 基线（train_small，50 iter） | 稳态 **~11.5k steps/s**（2.09 s/iter）；1.23M 步全程 **107 s**；checkpoint model_0…49 + tfevents 齐全 | `logs/baseline_w1.log`、上游 `logs/rsl_rl/velocity/2026-11-21_13-58-09_week1_small_baseline` |
| 显存峰值（各档 num_envs） | ⬜ 下次训练时 `nvidia-smi --query-gpu=memory.used --format=csv -l 5` 旁挂记录 | |

> 网络维度（冒烟日志取证）：actor 观测 61 维 → MLP 512/256/128（ELU）→ 动作 14 维；
> critic 观测 76 维（特权）。

## Docker（✅ 2026-11-22 全链路验证通过）

| 项 | 值 |
|---|---|
| Docker Desktop | 4.99.0（winget 装），引擎 29.9.3，WSL2 后端 |
| **数据盘位置** | `E:\docker-wsl\DockerDesktopWSL`（GUI 迁移；C 盘只剩系统盘空间，且一次 CUDA 镜像构建在 containerd 存储里要 ~25GB 峰值三份拷贝，C 盘根本放不下） |
| 镜像 microduck-train | 内容 6.86GB / 磁盘 19.2GB；`imports OK`（build 内验证）+ GPU 冒烟 64×5 通过（~280 steps/s，比宿主机 820 慢，WSL2 直通 + warp 首编开销） |
| 代理 | Docker Desktop 手动代理 → Clash `127.0.0.1:7897`（settings-store.json `OverrideProxyHTTP`）。**注意 BuildKit 解析器不走 daemon 代理**：`docker pull` 通不代表 `docker build` 拉 FROM 通——先预拉基础镜像（troubleshooting #9） |
| apt 源 | 清华 TUNA（国内直连 archive.ubuntu.com 部分 .deb 502） |
| 构建命令 | `docker build -f microduck-sim2real/docker/Dockerfile -t microduck-train C:/duck_work`（上下文必须是 duck_work；**C:\duck_work\.dockerignore 必须在位**，否则 .venv/日志全进上下文） |
| GPU 冒烟 | `docker run --rm --gpus all microduck-train`（CMD 自带 64×5 + tensorboard logger） |
