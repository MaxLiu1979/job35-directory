"""验证 data/by-industry/*.yaml 中的招聘页链接，剔除死链。

判定规则（保守：宁可保留疑似被墙/反爬的链接，也不错杀）：
- 2xx/3xx、以及 401/403/429/5xx（多半是反爬而非页面不存在）→ 保留
- 404/410、DNS 失败、连接拒绝、超时 → 判定死链并移除
"""
from __future__ import annotations

import concurrent.futures
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "by-industry"
UA = "job35-link-checker/0.1 (+https://github.com/MaxLiu1979/job35-directory)"


def check(url: str, timeout: int = 15) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as exc:
        return exc.code not in (404, 410)
    except Exception:
        return False


def main() -> None:
    entries: list[tuple[Path, int, dict]] = []
    for path in sorted(SRC.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for idx, c in enumerate(data.get("companies", [])):
            if c.get("link"):
                entries.append((path, idx, c))

    print(f"共 {len(entries)} 个链接待验证")
    dead: list[tuple[Path, str, str]] = []

    def worker(item):
        path, idx, c = item
        return path, c, check(c["link"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for path, c, ok in pool.map(worker, entries):
            mark = "OK " if ok else "DEAD"
            print(f"  [{mark}] {c['name']}: {c['link']}")
            if not ok:
                dead.append((path, c["id"], c["name"]))

    # 从源文件中移除死链
    by_path: dict[Path, set[str]] = {}
    for path, cid, _ in dead:
        by_path.setdefault(path, set()).add(cid)
    for path, ids in by_path.items():
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for c in data["companies"]:
            if c["id"] in ids:
                c.pop("link", None)
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    print(f"\n结果：保留 {len(entries) - len(dead)}，移除死链 {len(dead)}")
    for path, _, name in dead:
        print(f"  - {name}（{path.stem}）")


if __name__ == "__main__":
    main()
