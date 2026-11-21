# 踩坑日志（从第一天就记）

> 每条 = 症状 + 根因 + 修复 + 证据。新坑追加在末尾，别删旧记录。

## 1. Git Bash 内联多行 python 必炸（两次实锤）

- **症状**：把 `2>/dev/null` 写进 python 源码导致 SyntaxError；历史上 `\d` 被打进
  正则、替换静默失败（AGENTS.md 案例）。
- **根因**：Git Bash 对内联 heredoc/引号的转义不可靠。
- **修复**：任何 python 一律落盘 .py 再 `python -I xxx.py`。本日探针即此做法。
- **证据**：2026-11-21 会话 env probe 第一次内联运行即翻车，改落盘后通过。

## 2. Windows 上 PyPI torch 是 CPU-only

- **症状**：`torch.cuda.is_available() == False`，mjlab select_gpus 抛 IndexError。
- **根因**：PyPI Windows wheel 不带 CUDA。
- **修复**：`microduck_rl/pyproject.toml` 的 `[tool.uv.sources]` 已把 win32 路由到
  `pytorch-cu128` index（RTX 5060 Ti sm_120 需 CUDA ≥ 12.8）。**别手动 `pip install torch`。**

## 3. mujoco 版本不可随意 override

- **症状**：override 到 3.4.0 后 import 崩（缺 `mjDSBL_MULTICCD`）。
- **根因**：mjlab 1.3.0 的 mujoco-warp 需要 mujoco 3.10.x。
- **修复**：不 override，让 mjlab 自己钉（pyproject 注释，2026 会话事故）。

## 4. bam 连锁拖垮 protobuf / onnx / zmq

- **症状**：fresh `uv sync` 失败或 onnx 被拖到无 wheel 的 1.17.0。
- **修复**：`[tool.uv] override-dependencies` 三条（protobuf 4–6、onnx≥1.20.1、
  假 marker 踢掉 zmq）——已在 pyproject，原理见其注释。

## 5. `train` 命令名冲突（liblinear 事故，2026-08-31）

- **症状**：`uv run train` 报 `can't open input file Mjlab-Velocity-Flat-MicroDuck`。
- **根因**：删掉 pyproject 里的 train script 声明会让 `uv sync` 卸载 shim 而 mjlab
  不重装，PATH 落到 liblinear 的 train 上。
- **修复**：保留同名声明（见 pyproject 长注释）。**永远不要"清理"那条声明。**

## 6. num_envs 默认是 1 的陷阱（2026-11-21 实测确认）

- **症状**：训练照常跑、曲线照常出，但慢得毫无意义。
- **根因**：注册表里所有 MicroDuck 任务 `scene.num_envs` 默认=1；run14 就是 1 env
  跑完 2000 iter（22 分钟，~34 steps/s）。
- **修复**：起训练必带 `--env.scene.num-envs`；本仓库 `configs/*.yaml` 强制该字段。

## 7. mjlab 1.3.0 忘声明 scipy 依赖

- **修复**：microduck_rl pyproject 已直接依赖 `scipy>=1.16`（fresh uv sync 需要）。

## 8. rsl_rl 默认 logger=wandb，未登录即崩（2026-11-21 实锤）

- **症状**：模型打印完后立刻退出 1，`wandb.errors.errors.UsageError: No API key
  configured`；且经重定向时 traceback 可能被缓冲吞掉，看起来像"无声死掉"。
- **修复**：`--agent.logger tensorboard`（configs/*.yaml 已带 `logger: tensorboard`；
  Dockerfile CMD 也带），或先 `wandb login` 再用 wandb。排障时加
  `PYTHONUNBUFFERED=1` 保证 traceback 可见。
- **复发记录**：2026-11-22 容器冒烟第一次退出 1——Dockerfile CMD 忘带该旗标，
  同一坑在不同环境咬人，配置必须随环境走（不能只靠肌肉记忆）。

## 9. `docker pull` 通、`docker build` 拉 FROM 却超时（2026-11-22）

- **症状**：daemon 配好代理后 `docker pull hello-world` 正常，但 build 解析
  `FROM docker.io/nvidia/cuda...` 时直连 auth.docker.io 超时（DNS 污染 IP）。
- **根因**：BuildKit（containerd 存储）的 registry 解析不走 daemon 的 HTTP 代理。
- **修复**：先用 daemon 路径预拉基础镜像（`docker pull nvidia/cuda:... `），
  build 命中本地层即不再撞 registry。

## 10. C 盘爆盘事故：一次 CUDA 镜像构建 ≈ 25GB 峰值（2026-11-22）

- **症状**：构建本体全部成功（imports OK），死在"exporting/unpacking layers"：
  `read-only file system`；C 盘 0 字节可用，docker_data.vhdx 涨到 26GB。
- **根因**：containerd 导出+解包期间层内容存在约三份拷贝（buildkit 层 + tar 导出
  + snapshot 解包），CUDA torch 镜像单层 ~8GB → 峰值 ~25GB；VHDX 只涨不缩。
- **修复**：Docker Desktop → Settings → Resources → VM resources → Disk image
  location 迁到 `E:\docker-wsl`（E 盘 245G 空闲）。附带教训：`UV_NO_CACHE=1` 让
  uv 缓存不进层（层体积近半）；settings-store.json 手写 `wslDataFolder` 键无效，
  只有 GUI 写的键才被引擎认。
