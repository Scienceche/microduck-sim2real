"""configs/*.yaml → mjlab train CLI 旗标。

train CLI 是 tyro 风格（不吃 yaml），本脚本把人类可读的 yaml 单一事实源翻译成
CLI 参数。白名单映射：写错字段名直接报错（防 typo 静默失效——num_envs 默认=1 的
事故教训，docs/troubleshooting.md #6）。

用法：python -I yaml_to_flags.py configs/train_small.yaml
输出：单行 "<TASK> --flag val ..."，供 train.sh 展开为参数组。
"""
import sys

import yaml

# yaml 键 → (tyro 旗标, 值转换)。None 值表示直接透传字符串。
FLAG_MAP = {
    "num_envs": "--env.scene.num-envs",
    "max_iterations": "--agent.max-iterations",
    "save_interval": "--agent.save-interval",
    "run_name": "--agent.run-name",
    "seed": "--agent.seed",
    "load_run": "--agent.load-run",
    "load_checkpoint": "--agent.load-checkpoint",
    "resume": "--agent.resume",
    "logger": "--agent.logger",
}


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert isinstance(cfg, dict), f"{path} 顶层必须是映射"

    task = cfg.pop("task", None)
    assert task, f"{path} 缺必填字段 task（如 Mjlab-Velocity-Flat-MicroDuck）"

    flags = [task]
    for key, value in cfg.items():
        assert key in FLAG_MAP, (
            f"未知字段 {key!r}（可用：{sorted(FLAG_MAP)}）——拼错就拒绝，不猜"
        )
        if isinstance(value, bool):  # tyro FlagConversionOff：布尔用 True/False 字面量
            value = str(value)
        flags.extend([FLAG_MAP[key], str(value)])
    print(" ".join(flags))


if __name__ == "__main__":
    main(sys.argv[1])
