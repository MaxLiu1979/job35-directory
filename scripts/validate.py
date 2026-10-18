"""名录数据格式校验（无第三方依赖，GitHub Actions 直接运行）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("需要 pyyaml：pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
VALID_TIERS = {"top10", "top50", "top100", "candidate"}
VALID_STATUS = {"pending", "active", "verified", "stale"}
VALID_SOURCE_TYPES = {"greenhouse", "lever", "careers_page", "rss"}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    industries = yaml.safe_load(
        (ROOT / "data/industries.yaml").read_text(encoding="utf-8")
    )
    codes = {i["code"] for i in industries["industries"]}
    print(f"行业目录：{len(codes)} 个行业")

    companies = yaml.safe_load(
        (ROOT / "data/companies.yaml").read_text(encoding="utf-8")
    )["companies"]

    seen: set[str] = set()
    errors: list[str] = []
    for c in companies:
        cid = c.get("id", "?")
        if cid in seen:
            errors.append(f"重复 id: {cid}")
        seen.add(cid)
        for field in ("name", "industry", "tier", "status"):
            if field not in c:
                errors.append(f"{cid}: 缺少字段 {field}")
        if c.get("industry") not in codes:
            errors.append(f"{cid}: 未知行业 '{c.get('industry')}'")
        if c.get("tier") not in VALID_TIERS:
            errors.append(f"{cid}: 非法 tier '{c.get('tier')}'")
        if c.get("status") not in VALID_STATUS:
            errors.append(f"{cid}: 非法 status '{c.get('status')}'")
        for s in c.get("sources", []):
            if s.get("type") not in VALID_SOURCE_TYPES:
                errors.append(f"{cid}: 非法 source.type '{s.get('type')}'")
            if s["type"] in ("careers_page", "rss") and not s.get("url"):
                errors.append(f"{cid}: {s['type']} 缺少 url")
            if s["type"] in ("greenhouse", "lever") and not s.get("slug"):
                errors.append(f"{cid}: {s['type']} 缺少 slug")
        for e in c.get("evidence", []):
            for field in ("url", "quote", "checked_at"):
                if field not in e:
                    errors.append(f"{cid}: evidence 缺少 {field}")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        sys.exit(1)
    print(f"[OK] {len(companies)} 家企业条目校验通过")


if __name__ == "__main__":
    main()
