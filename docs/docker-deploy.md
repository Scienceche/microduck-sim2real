# Docker 部署手册（新人跟跑版）

> 本文每一步都在 2026-11-21/22 于本机**真实执行并验证过**（证据：`logs/docker_smoke_w1.log`）。
> 跟跑原则：**每做完一步，先看"✅ 验证"过没过，再走下一步**。不过就查"⚠️ 常见失败"。
> 全程约 1.5 小时（含 25–50 分钟镜像构建）。

## 0. 前置条件自查（缺一样都先补齐）

| 项 | 要求 | 自查命令 | 期望 |
|---|---|---|---|
| 系统 | Windows 10/11 x64 + Git Bash | — | — |
| GPU | NVIDIA + 驱动（CUDA ≥12.8，RTX 50 系必须 12.8+） | `nvidia-smi` | 显示 RTX … 与驱动版本 |
| 磁盘 | **非系统盘**（如 E:）≥ 60GB 空闲 | `df -h /e` | Avail ≥ 60G |
| 代码 | `C:\duck_work\microduck_rl`（已能本机跑）+ `C:\duck_work\bam` | `ls C:/duck_work/microduck_rl/pyproject.toml C:/duck_work/bam` | 两个路径都存在 |
| 代理 | Clash 等本地代理在跑 | `netstat -ano \| findstr 7897`（端口按实际改） | LISTENING |

**为什么磁盘必须是非系统盘**：一次 CUDA 镜像构建在 Docker 内部要产生约**3 份层拷贝、峰值 ~25GB**，系统盘塞不下会把整个 Docker 引擎打死（troubleshooting #10，真实事故两回）。

## 1. 安装 Docker Desktop

```bash
winget install --id Docker.DockerDesktop --silent --accept-package-agreements --accept-source-agreements
```

- 安装器可能弹 **UAC 管理员确认，点"是"**；下载几百 MB，等 `Successfully installed`。
- 装完启动：`cmd //c start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"`
- 首次启动若弹条款页，点 Accept。

**✅ 验证**（注意：老终端的 PATH 不含新装的 docker，**开新终端**或用全路径）：

```bash
DOCKER="C:/Program Files/Docker/Docker/resources/bin/docker.exe"
"$DOCKER" info --format '{{.ServerVersion}}'     # 期望: 29.x.x
```

## 2. 配置代理（国内网络必做）

不做这步：拉镜像时 `auth.docker.io` 解析到污染 IP，直连超时。

**先备份，再写入**（端口换成你自己代理的；本机 Clash 是 7897）：

```bash
S="$APPDATA/Docker/settings-store.json"
cp "$S" "$S.bak"    # 回退就还原这个文件
```

在 `$S` 的 JSON 里加入（注意大小写，`HTTP` 全大写）：

```json
"ProxyHTTPMode": "manual",
"OverrideProxyHTTP": "http://127.0.0.1:7897",
"OverrideProxyHTTPS": "http://127.0.0.1:7897",
"OverrideProxyExclude": "localhost,127.0.0.1"
```

然后重启 Docker（强杀防退出回写旧配置）：

```bash
taskkill //IM "Docker Desktop.exe" //F; sleep 3
cmd //c start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

**✅ 验证**：`"$DOCKER" pull hello-world` → 期望 `Status: Downloaded newer image`。

**⚠️ 常见失败**：`docker pull` 通了但后面 `docker build` 拉 `FROM` 超时——BuildKit 不走 daemon 代理，见第 5 步的预拉解法（troubleshooting #9）。

## 3. 迁移数据盘到大盘（GUI 操作）

**手改配置文件里的 `wslDataFolder` 键无效**（实测被引擎无视），必须走 GUI：

Docker Desktop → 右上齿轮 **Settings** → **Resources** → **VM resources** →
**Disk image location** → **Browse…** → 在弹窗底部"文件夹"输入框填 `E:\docker-wsl` →
点"选择文件夹" → **Apply & Restart Engine** → 弹"Move disk image?"点 **Yes, move it**。

**✅ 验证**：

```bash
ls -lh /e/docker-wsl/DockerDesktopWSL/disk/*.vhdx   # 期望: docker_data.vhdx 在此
ls "$LOCALAPPDATA/Docker/wsl/disk/"                  # 期望: 空（C 盘已无 vhdx）
```

## 4. 写 .dockerignore（不做=构建上下文爆炸）

构建上下文是整个 `C:\duck_work`，不排除的话 `.venv`（GB 级）、训练日志、
工具链全会被打进上下文。新建 **`C:\duck_work\.dockerignore`**：

```
*
!bam/**
!microduck_rl/**

microduck_rl/.venv
microduck_rl/logs
microduck_rl/wandb
microduck_rl/.git
microduck_rl/output.onnx
microduck_rl/**/__pycache__
microduck_rl/**/*.pyc
bam/.git
bam/**/__pycache__
```

## 5. 预拉基础镜像（绕过 BuildKit 代理盲区）

```bash
"$DOCKER" pull nvidia/cuda:12.8.1-runtime-ubuntu22.04
"$DOCKER" pull ghcr.io/astral-sh/uv:latest
```

**✅ 验证**：两条都 `Status: Downloaded`。第 6 步 build 就不会再撞 registry。

## 6. 构建镜像

```bash
"$DOCKER" build --progress=plain \
  -f C:/duck_work/microduck-sim2real/docker/Dockerfile \
  -t microduck-train C:/duck_work
```

- 构建上下文必须是 `C:/duck_work`（pyproject 用相对路径 `../bam` 找电机模型）。
- 耗时 25–50 分钟（大头是容器内 `uv sync` 下载 CUDA 版 torch，~3GB）。
- Dockerfile 已内置：apt 清华源、`UV_NO_CACHE=1`、构建末尾 `imports OK` 自检。

**✅ 验证**：日志末尾出现 `imports OK` 与 `naming to docker.io/library/microduck-train:latest`：

```bash
"$DOCKER" images microduck-train   # 期望看到 6.9GB 内容 / ~19GB 磁盘
```

**⚠️ 常见失败**：
- `read-only file system` 死在 exporting/unpacking → 数据盘没在大盘，回第 3 步（#10）
- apt `502 Bad Gateway` → Dockerfile 的清华源被改掉了，恢复它
- 网络超时 → 重跑即可（层缓存续命）；确认代理在跑

## 7. GPU 冒烟（最终验收）

```bash
"$DOCKER" run --rm --gpus all --name smoke microduck-train
```

镜像 CMD 自带 64 env × 5 iter 冒烟（含 `--agent.logger tensorboard`——容器里
没有 wandb 凭据，不带必崩，troubleshooting #8）。

**✅ 验证**：退出码 0，输出含：

```
| Number of environments | 64     |
... Steps per second: ~2xx-4xx ...
... Time elapsed: ... （共 5 个 Learning iteration）
```

参考值：本机容器内 ~280 steps/s（宿主机直跑 820；WSL2 直通 + warp 首编开销，正常）。

## 8. 之后怎么用（日常操作）

```bash
# 完整训练（挂载日志卷，宿主机直接看 tensorboard）
"$DOCKER" run --rm --gpus all \
  -v C:/duck_work/microduck_rl/logs:/opt/microduck_rl/logs \
  microduck-train \
  uv run train Mjlab-Velocity-Flat-MicroDuck \
    --env.scene.num-envs 1024 --agent.max-iterations 50 \
    --agent.logger tensorboard

# 宿主机看曲线
cd C:/duck_work/microduck_rl && uv run tensorboard --logdir logs/rsl_rl

# 或用 compose（docker/docker-compose.yml）
"$DOCKER" compose -f C:/duck_work/microduck-sim2real/docker/docker-compose.yml run --rm train
```

## 故障速查表

| 症状 | 去处 |
|---|---|
| wandb `No API key configured` | troubleshooting #8：加 `--agent.logger tensorboard` |
| build 拉 FROM 超时但 pull 正常 | troubleshooting #9：预拉基础镜像 |
| exporting/unpacking `read-only file system` | troubleshooting #10：数据盘迁大盘 |
| apt 下载 502 | Dockerfile 里清华 TUNA 源必须在位 |
| 引擎 unable to start | 先 `df -h /c` 查是不是 0 字节；清 vhdx 或迁盘后重启 |
| 命令找不到 docker | 开新终端，或用全路径 `C:/Program Files/Docker/Docker/resources/bin/docker.exe` |
