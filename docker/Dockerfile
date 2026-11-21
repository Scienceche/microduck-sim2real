# microduck 训练镜像（CUDA ≥12.8，RTX 5060 Ti sm_120 兼容）
#
# ⚠️ 状态：未验证 —— 本机 2026-11-21 尚未安装 Docker（docker: command not found）。
# 装好 Docker Desktop 后第一件事执行下面的 build 并把结果记进 docs/env-lock.md。
#
# 构建上下文必须是 C:\duck_work（pyproject 以 ../bam 引用本地电机模型），
# 且 C:\duck_work\.dockerignore 必须在位（否则 .venv/日志/工具链全进上下文）：
#   docker build -f microduck-sim2real/docker/Dockerfile -t microduck-train C:/duck_work
# 冒烟（需 NVIDIA Container Toolkit / Docker Desktop GPU 支持）：
#   docker run --rm --gpus all microduck-train
#   → 容器内跑 64 env × 5 iter 冒烟，退出码 0 即通过

FROM nvidia/cuda:12.8.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    MUJOCO_GL=egl \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_HTTP_TIMEOUT=600 \
    # 2026-11-21 教训：不关缓存时 uv cache+venv 双份进层(~13GB)，导出阶段直接撑爆
    # 系统盘（C 盘 0 可用→containerd 只读）。关缓存层体积近半。
    UV_NO_CACHE=1

# apt 走清华 TUNA 镜像（2026-11-21 实测：国内直连 archive.ubuntu.com 部分 .deb 502）
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g; s|http://security.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git libegl1 libgl1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 本地 bam（better-actuator-models，Feetech HD1910 参数）必须与训练仓库同层放置，
# pyproject 的 [tool.uv.sources] 用相对路径 ../bam 找它 → /opt/bam、/opt/microduck_rl
COPY bam /opt/bam
COPY microduck_rl /opt/microduck_rl

RUN uv python install 3.12 \
    && cd /opt/microduck_rl \
    && uv sync --locked \
    # 冒烟即验证：装完立刻证明 import + GPU 前向都活着（build 阶段无 GPU，
    # 真正的 GPU 冒烟靠运行期那条 docker run）
    && uv run python -c "import mujoco, torch, warp, mjlab, rsl_rl; print('imports OK')"

WORKDIR /opt/microduck_rl
# 运行期默认冒烟；完整训练请挂载配置/日志卷并覆盖 CMD
# --agent.logger tensorboard：容器里没有 wandb 凭据，默认 wandb 会直接崩（troubleshooting #8）
CMD ["uv", "run", "train", "Mjlab-Velocity-Flat-MicroDuck", \
     "--env.scene.num-envs", "64", "--agent.max_iterations", "5", \
     "--agent.run-name", "docker_smoke", "--agent.logger", "tensorboard"]
