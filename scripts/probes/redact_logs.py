"""脱敏证据日志：公开仓库不携带本机用户名。按守则：落盘执行 + assert 替换发生。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = [ROOT / "logs" / "baseline_w1.log", ROOT / "logs" / "smoke_w1_evidence.log"]
BAD = "C:\\Users\\c1349\\"
GOOD = "C:\\Users\\<user>\\"

for path in TARGETS:
    text = path.read_text(encoding="utf-8", errors="replace")
    count = text.count(BAD)
    assert count >= 1, f"{path.name} 未找到待替换模式（可能已脱敏）"
    path.write_text(text.replace(BAD, GOOD), encoding="utf-8")
    # 重新读盘验证（不信任写入口的自己说成功）
    after = path.read_text(encoding="utf-8")
    assert BAD not in after and GOOD in after, f"{path.name} 脱敏后校验失败"
    print(f"{path.name}: 已替换 {count} 处，落盘校验通过")
