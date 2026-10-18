"""把 data/by-industry/*.yaml 合并为 data/companies.yaml。

- 同名（中文名或英文名）企业在多个行业文件中重复时，保留首次出现的一条
- 保证 id 全局唯一
- 修正 YAML 1.1 把 country: NO（挪威）解析成 False 的问题
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "by-industry"
DST = ROOT / "data" / "companies.yaml"


def norm_country(value):
    if value is False:  # YAML 1.1: 未加引号的 NO 被解析为布尔值
        return "NO"
    return value


def main() -> None:
    merged: list[dict] = []
    seen_names: set[str] = set()
    seen_ids: set[str] = set()
    dropped: list[str] = []

    for path in sorted(SRC.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for c in data.get("companies", []):
            names = {str(c.get("name", "")).strip().lower()}
            if c.get("name_en"):
                names.add(str(c["name_en"]).strip().lower())
            if names & seen_names:
                dropped.append(f"{c.get('name')}（{path.stem}）")
                continue
            seen_names |= names
            cid = c["id"]
            if cid in seen_ids:
                cid = f"{cid}-{len(seen_ids)}"
            c["id"] = cid
            seen_ids.add(cid)
            c["country"] = norm_country(c.get("country"))
            merged.append(c)

    header = (
        "# 企业名录（由 scripts/merge_industries.py 从 data/by-industry/*.yaml 合并生成，"
        "请编辑 by-industry 下的分行业文件后重新运行合并）\n"
        "#\n"
        "# status 生命周期：pending 待核实 | active 近180天有信号 | verified 已人工核实 | stale 信号过期\n"
    )
    body = yaml.safe_dump(
        {"version": 1, "companies": merged},
        allow_unicode=True,
        sort_keys=False,
    )
    DST.write_text(header + body, encoding="utf-8")
    print(f"合并完成：{len(merged)} 家企业（去重移除 {len(dropped)} 条）")
    for d in dropped:
        print(f"  - 重复移除: {d}")


if __name__ == "__main__":
    main()
