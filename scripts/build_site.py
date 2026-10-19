"""从名录数据生成 GitHub Pages 静态站点（无第三方依赖）。"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent

STATUS = {
    "pending": ("待核实", "Pending", "#8a8f98"),
    "active": ("招聘活跃", "Active", "#1a7f37"),
    "verified": ("已核实", "Verified", "#0a5cb8"),
    "stale": ("信号过期", "Stale", "#9a6700"),
}
LEVEL = {
    "explicit": ("明确友好", "Explicit", "#1a7f37"),
    "likely": ("大概率友好", "Likely", "#0a5cb8"),
    "unknown": ("暂无信号", "Unknown", "#8a8f98"),
    "risky": ("存在年龄上限", "Risky", "#cf222e"),
}


def esc(text: str | None) -> str:
    return html.escape(str(text or ""))


def company_link(c: dict) -> tuple[str, str, bool]:
    """返回 (href, 提示文字, 是否直达官网)。

    有已验证的招聘页链接则直达；否则退化为搜索引擎查询，绝不给死链。
    """
    if c.get("link"):
        return c["link"], f'直达 {c["name"]} 招聘页', True
    q = quote(f'{c.get("name_en") or c["name"]} careers 招聘官网')
    return f"https://www.bing.com/search?q={q}", f'搜索 {c["name"]} 招聘信息', False


def card_html(c: dict) -> str:
    href, title, direct = company_link(c)
    arrow = '<span class="go">直达招聘页 ↗</span>' if direct else '<span class="go search">搜索招聘页 🔍</span>'
    return f"""
      <a class="card" href="{esc(href)}" target="_blank" rel="noopener" title="{esc(title)}">
        <div class="card-head">
          <strong>{esc(c["name"])}</strong>
          {f'<span class="en">{esc(c["name_en"])}</span>' if c.get("name_en") else ""}
        </div>
        <div class="card-meta">
          <span class="tier">{esc(c["tier"])}</span>
          {f'<span class="country">{esc(c["country"])}</span>' if c.get("country") else ""}
          {badge(STATUS, c["status"])}
          <span class="go-wrap">{arrow}</span>
        </div>
        {f'<div class="note">{esc(c["note"])}</div>' if c.get("note") else ""}
      </a>"""


def badge(kind: str, key: str) -> str:
    label = kind[key]
    return f'<span class="badge" style="--c:{label[2]}">{esc(label[0])}</span>'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    industries = yaml.safe_load(
        (ROOT / "data/industries.yaml").read_text(encoding="utf-8")
    )["industries"]
    companies = yaml.safe_load(
        (ROOT / "data/companies.yaml").read_text(encoding="utf-8")
    )["companies"]

    by_industry: dict[str, list[dict]] = {}
    for c in companies:
        by_industry.setdefault(c["industry"], []).append(c)

    generated = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    sections: list[str] = []
    for ind in industries:
        rows = by_industry.get(ind["code"], [])
        cards = "".join(card_html(c) for c in rows) or '<p class="empty">收录中… / Collecting…</p>'
        sections.append(
            f"""
    <section id="{esc(ind["code"])}">
      <h2>{esc(ind["name_cn"])} <span class="en">{esc(ind["name_en"])}</span>
        <span class="count">{len(rows)}</span></h2>
      <p class="ind-note">{esc(ind.get("note", ""))}</p>
      <div class="grid">{cards}
      </div>
    </section>"""
        )

    nav = "".join(
        f'<a href="#{esc(i["code"])}">{esc(i["name_cn"])}</a>' for i in industries
    )

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>job35-directory · 35+ 友好企业名录</title>
<meta property="og:title" content="job35-directory · 35+ 友好企业名录">
<meta property="og:description" content="收录对 35+ 求职者友好、且近半年招聘仍然活跃的企业。每周自动更新，公开证据可查证。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://maxliu1979.github.io/job35-directory/">
<meta property="og:image" content="https://maxliu1979.github.io/job35-directory/cards/all.png">
<style>
  :root {{ --fg:#1f2328; --muted:#59636e; --line:#e5e7eb; --bg:#f6f8fa; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
         color:var(--fg); background:#fff; line-height:1.6; }}
  header {{ background:linear-gradient(135deg,#0d3b66,#1a7f37); color:#fff; padding:56px 24px 40px; }}
  header .wrap, main, footer {{ max-width:1080px; margin:0 auto; padding:0 24px; }}
  header h1 {{ margin:0 0 8px; font-size:2rem; }}
  header p {{ margin:4px 0; opacity:.92; }}
  nav {{ position:sticky; top:0; background:#fff; border-bottom:1px solid var(--line);
        padding:10px 24px; display:flex; gap:14px; flex-wrap:wrap; z-index:10; }}
  nav a {{ color:var(--muted); text-decoration:none; font-size:.9rem; }}
  nav a:hover {{ color:#0d3b66; }}
  section {{ padding:28px 0; border-bottom:1px solid var(--line); }}
  h2 {{ font-size:1.3rem; margin:0 0 4px; }}
  .en {{ color:var(--muted); font-weight:400; font-size:.85em; }}
  .count {{ background:var(--bg); border-radius:12px; padding:1px 10px; font-size:.8rem;
           color:var(--muted); vertical-align:middle; }}
  .ind-note {{ color:var(--muted); font-size:.88rem; margin:0 0 16px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .card {{ border:1px solid var(--line); border-radius:10px; padding:14px 16px; background:#fff; }}
  .card-head strong {{ font-size:1.02rem; }}
  .card-head .en {{ margin-left:6px; }}
  .card-meta {{ display:flex; gap:8px; align-items:center; margin-top:8px; flex-wrap:wrap; }}
  .tier, .country {{ background:var(--bg); border-radius:6px; padding:1px 8px; font-size:.78rem;
                     color:var(--muted); }}
  .badge {{ --c:#888; border:1px solid var(--c); color:var(--c); border-radius:12px;
            padding:0 9px; font-size:.78rem; }}
  .card {{ display:block; text-decoration:none; color:inherit; border:1px solid var(--line);
          border-radius:10px; padding:14px 16px; background:#fff; transition:border-color .15s, box-shadow .15s; }}
  .card:hover {{ border-color:#0d3b66; box-shadow:0 2px 10px rgba(13,59,102,.12); }}
  .go-wrap {{ margin-left:auto; }}
  .go {{ color:#1a7f37; font-size:.8rem; white-space:nowrap; }}
  .go.search {{ color:var(--muted); }}
  .card:hover .go {{ text-decoration:underline; }}
  .note {{ color:var(--muted); font-size:.82rem; margin-top:8px; }}
  .empty {{ color:var(--muted); }}
  footer {{ padding:28px 24px 48px; color:var(--muted); font-size:.85rem; }}
  footer a {{ color:#0a5cb8; }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>job35-directory</h1>
  <p>收录对 35+ 求职者友好、且近半年招聘仍然活跃的企业 · Companies friendly to 35+ job seekers, actively hiring in the last 6 months</p>
  <p>数据与证据见 <a href="https://github.com/MaxLiu1979/job35-directory" style="color:#fff">GitHub 仓库</a> · 判定方法见 methodology</p>
</div></header>
<nav>{nav}</nav>
<main>{"".join(sections)}
<section id="share">
  <h2>分享本项目 <span class="en">Share</span></h2>
  <p>把这张卡片或本页链接，转发给正在找工作的 35+ 朋友。每个行业都有对应卡片：
     把网址后面加上 <code>cards/行业code.png</code> 即可（如 <code>.../cards/energy.png</code>）。</p>
  <img src="cards/all.png" alt="job35-directory 分享卡片" style="max-width:480px;width:100%;border-radius:10px;border:1px solid var(--line)">
  <p><button onclick="navigator.clipboard.writeText(location.href).then(()=>this.textContent='已复制链接 ✓')"
       style="padding:8px 18px;border-radius:8px;border:1px solid var(--line);background:var(--bg);cursor:pointer;font-size:.95rem">复制本页链接</button></p>
</section>
</main>
<footer>
  <p>本名录只做公开信息的聚合与标注，不构成求职建议。数据：CC0-1.0 · 最后生成：{generated}</p>
  <p>收录 ≠ 背书。发现错误请 <a href="https://github.com/MaxLiu1979/job35-directory/issues">提交 issue</a> 并附公开证据。</p>
</footer>
<script type="application/json" id="raw-data">{json.dumps(companies, ensure_ascii=False)}</script>
</body>
</html>
"""
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"已生成 {out / 'index.html'}（{len(companies)} 家企业 / {len(industries)} 个行业）")


if __name__ == "__main__":
    main()
