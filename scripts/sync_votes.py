"""把 Abacus 匿名投票计数同步回 data/votes.json（供站点展示）。

Abacus 免费计数 API：https://abacus.jasoncameron.dev
- 投票：GET /hit/job35-v1/{company_id}-yes | -no（浏览器端 no-cors 提交，无记名）
- 读数：GET /get/job35-v1/{company_id}-yes | -no

规则：确认票 > 不确认票 且确认票 >= 3 → 企业在页面上标记"社区已确认"。
拉取失败时保留旧值，绝不丢票。
"""
from __future__ import annotations

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "votes.json"


def get_count(key: str, retries: int = 3) -> int | None:
    url = f"https://abacus.jasoncameron.dev/get/job35-v1/{key}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "job35-votesync/0.1 (github.com/MaxLiu1979/job35-directory)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return int(json.loads(resp.read()).get("value", 0))
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def main() -> None:
    companies = yaml.safe_load(
        (ROOT / "data" / "companies.yaml").read_text(encoding="utf-8")
    )["companies"]
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    keys = {c["id"]: ("yes", "no") for c in companies}

    def fetch(item):
        cid, _ = item
        yes = get_count(f"{cid}-yes")
        time.sleep(0.05)  # 尊重限流（30次/10秒）
        no = get_count(f"{cid}-no")
        return cid, yes, no

    votes: dict[str, dict] = {}
    failed = 0
    with ThreadPoolExecutor(max_workers=2) as pool:
        for cid, yes, no in pool.map(fetch, keys.items()):
            prev = old.get(cid, {})
            votes[cid] = {
                "yes": yes if yes is not None else prev.get("yes", 0),
                "no": no if no is not None else prev.get("no", 0),
            }
            if yes is None or no is None:
                failed += 1

    OUT.write_text(json.dumps(votes, ensure_ascii=False, indent=1), encoding="utf-8")
    confirmed = sum(
        1 for v in votes.values() if v["yes"] >= 3 and v["yes"] > v["no"]
    )
    print(f"同步完成：{len(votes)} 家企业，社区已确认 {confirmed} 家，拉取失败保留旧值 {failed} 家")


if __name__ == "__main__":
    main()
