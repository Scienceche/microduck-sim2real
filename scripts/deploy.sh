#!/usr/bin/env bash
# 实机部署入口（纯框架，实机阶段填）。
# 目标流程（对照 AGENTS.md 第 2 节部署自检）：
#   1) 打包 onnx + manifest（task、sha256、观测/动作契约）
#   2) scp 到鸭子 /opt/robot/feetech-ft5-r5/models/<sha256>/
#   3) 部署后必跑：C:\duck_work\deploy_verify.py（systemctl + 总线探针 + 哈希链）
#   4) 回退路径 = 上一版 models/<sha256> 目录仍在
# 任何一步没过，不算部署完成。
echo "deploy.sh：实机阶段才接线。现在调用 = 明确拒绝（防误触）。
流程见本文件注释与 AGENTS.md 第 2 节。" >&2
exit 3
