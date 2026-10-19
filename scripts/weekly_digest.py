"""从采集结果生成每周更新帖文案（复制到 V2EX/即刻/小红书发布）。

用法：python scripts/weekly_digest.py [data/signals/results.json]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/signals/results.json")
if not path.exists():
    sys.exit(f"找不到 {path}：请先合并每周爬取 PR 再运行")

results = json.loads(path.read_text(encoding="utf-8"))

levels = Counter(r["age_level"] for r in results)
active = Counter(r["activity"]["active"] for r in results)
explicit = [r for r in results if r["age_level"] == "explicit"]

print(f"""【job35 名录本周更新】

📊 当前数据：{len(results)} 家企业
· 近半年招聘活跃：{active.get(True, 0)} 家
· 明确欢迎 35+：{levels.get('explicit', 0)} 家
· 大概率友好：{levels.get('likely', 0)} 家
""")

if explicit:
    names = "、".join(r["name"] for r in explicit[:10])
    print(f"✅ 本周明确友好名单（前 10）：{names}")

print("""
🔗 在线名录：https://maxliu1979.github.io/job35-directory/
🛠 开源框架：https://github.com/MaxLiu1979/job35-crawler

知道对 35+ 友好的公司？来补充 → https://github.com/MaxLiu1979/job35-directory/issues""")
