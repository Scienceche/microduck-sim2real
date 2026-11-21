"""任务注册表探针：打印各 MicroDuck 任务注册默认值（num_envs/迭代数/rollout）。

用途：验证 "注册默认 num_envs=1"（docs/env-lock.md、troubleshooting.md #6），
以及给 configs/*.yaml 定 max_iterations 提供注册默认参照。

用法：C:/duck_work/microduck_rl/.venv/Scripts/python.exe -I task_defaults_probe.py
"""
import mjlab.tasks  # noqa: F401 - 导入即经插件入口点填充注册表

from mjlab.tasks.registry import _REGISTRY  # noqa: 保护访问，探针用途可接受


def g(obj, *names, default="?"):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


for task_id, entry in sorted(_REGISTRY.items()):
    if "MicroDuck" not in task_id:
        continue
    env_cfg, agent_cfg = entry.env_cfg, entry.rl_cfg
    print(f"== {task_id}")
    print(f"   scene.num_envs = {env_cfg.scene.num_envs}")
    print(f"   decimation = {g(env_cfg, 'decimation')}")
    print(f"   max_iterations = {g(agent_cfg, 'max_iterations')}"
          f"  num_steps_per_env = {g(agent_cfg, 'num_steps_per_env')}"
          f"  save_interval = {g(agent_cfg, 'save_interval')}")
    print(f"   experiment_name = {g(agent_cfg, 'experiment_name')}")
