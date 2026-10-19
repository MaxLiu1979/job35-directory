"""修复产品数据：重映射被去重企业的 id、修复乱码条目。"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products"


# 乱码条目的人工修复（原文编码损坏，按品牌事实重写）
FIXES = {
    ("agriculture-cofco-cn", "中茶"): {
        "name": "中茶茶叶",
        "category": "休闲零食",
        "keywords": ["中茶", "茶叶", "红茶", "绿茶"],
    },
    ("agriculture-beidahuang-cn", "大米"): {
        "name": "北大荒大米",
        "category": "粮油调味",
        "keywords": ["北大荒", "大米", "东北大米"],
    },
    ("healthcare-otsuka-jp", "宝矿力"): {
        "name": "宝矿力水特",
        "category": "饮料",
        "keywords": ["宝矿力", "宝矿力水特", "电解质水"],
    },
    ("healthcare-otsuka-jp", "奥乐蜜"): {
        "name": "奥乐蜜C维生素饮料",
        "category": "饮料",
        "keywords": ["奥乐蜜C", "维生素饮料", "营养碳酸"],
    },
}


def main() -> None:
    companies = yaml.safe_load(
        (ROOT / "data/companies.yaml").read_text(encoding="utf-8")
    )["companies"]
    ids = {c["id"] for c in companies}
    name_to_id = {c["name"]: c["id"] for c in companies}
    suffix_to_id = {}
    for c in companies:
        parts = c["id"].split("-", 1)
        if len(parts) == 2:
            suffix_to_id.setdefault(parts[1], c["id"])

    remapped, dropped, fixed = 0, 0, 0
    for path in sorted(PRODUCTS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out = []
        for p in data.get("products", []):
            cid = p["company_id"]
            if cid not in ids:
                suffix = cid.split("-", 1)[-1] if "-" in cid else cid
                new_id = suffix_to_id.get(suffix) or name_to_id.get(p.get("company_name"))
                if new_id:
                    p["company_id"] = new_id
                    remapped += 1
                else:
                    print(f"DROP（找不到企业）: {cid} {p.get('company_name')}")
                    dropped += 1
                    continue
            for it in p.get("items", []):
                key = (p["company_id"], it.get("name") or "")
                for (fix_cid, kw), fix in FIXES.items():
                    if p["company_id"] == fix_cid and kw in str(it.get("name", "")):
                        it.update(fix)
                        fixed += 1
            out.append(p)
        path.write_text(
            yaml.safe_dump({"products": out}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    print(f"重映射 {remapped} 条企业 id，修复 {fixed} 条乱码，移除 {dropped} 条孤儿数据")


if __name__ == "__main__":
    main()
