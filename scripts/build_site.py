"""从名录数据生成 GitHub Pages 静态站点：企业名录 + 产品搜索页（无第三方依赖）。"""
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

CATEGORY_ORDER = [
    "乳品", "饮料", "酒水", "粮油调味", "休闲零食", "生鲜速食",
    "洗护清洁", "纸品卫生", "母婴用品", "美妆个护",
    "家电", "数码产品", "手机应用", "办公用品",
    "服装", "鞋帽箱包", "家居家装", "建材五金",
    "汽车整车", "汽车服务", "能源缴费",
    "酒店住宿", "旅游出行", "餐饮美食", "快递物流",
    "教育培训", "金融理财", "保险服务",
    "医疗健康", "药品保健", "农产品", "宠物用品",
    "通讯服务", "宽带网络", "房产服务", "物业服务",
    "游戏娱乐", "影视视频", "音乐音频", "其他",
]

COMMON_CSS = """
  :root { --fg:#1f2328; --muted:#59636e; --line:#e5e7eb; --bg:#f6f8fa; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
         color:var(--fg); background:#fff; line-height:1.6; }
  header { background:linear-gradient(135deg,#0d3b66,#1a7f37); color:#fff; padding:48px 24px 36px; }
  header .wrap, main, footer { max-width:1080px; margin:0 auto; padding:0 24px; }
  header h1 { margin:0 0 8px; font-size:2rem; }
  header h1 a { color:#fff; text-decoration:none; }
  header p { margin:4px 0; opacity:.92; }
  header a { color:#fff; }
  .en { color:var(--muted); font-weight:400; font-size:.85em; }
  footer { padding:28px 24px 48px; color:var(--muted); font-size:.85rem; max-width:1080px; margin:0 auto; }
  footer a { color:#0a5cb8; }
  .badge { --c:#888; border:1px solid var(--c); color:var(--c); border-radius:12px;
           padding:0 9px; font-size:.78rem; }
"""


def esc(text: str | None) -> str:
    return html.escape(str(text or ""))


def badge(kind: dict, key: str) -> str:
    label = kind[key]
    return f'<span class="badge" style="--c:{label[2]}">{esc(label[0])}</span>'


def company_link(c: dict) -> tuple[str, str, bool]:
    """返回 (href, 提示文字, 是否直达官网)。绝不给死链。"""
    if c.get("link"):
        return c["link"], f'直达 {c["name"]} 招聘页', True
    q = quote(f'{c.get("name_en") or c["name"]} careers 招聘官网')
    return f"https://www.bing.com/search?q={q}", f'搜索 {c["name"]} 招聘信息', False


def is_confirmed(v: dict | None) -> bool:
    """社区确认规则：确认票 > 不确认票，且确认票 >= 3（防 1:0 噪音）。"""
    if not v:
        return False
    return v.get("yes", 0) >= 3 and v.get("yes", 0) > v.get("no", 0)


def card_html(c: dict, votes: dict) -> str:
    href, title, direct = company_link(c)
    v = votes.get(c["id"]) or {}
    yes, no = v.get("yes", 0), v.get("no", 0)
    arrow = '<span class="go">直达招聘页 ↗</span>' if direct else '<span class="go search">搜索招聘页 🔍</span>'
    confirmed = '<span class="badge" style="--c:#1a7f37">✓ 社区已确认</span>' if is_confirmed(v) else ""
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
          {confirmed}
          <span class="go-wrap">{arrow}</span>
        </div>
        {f'<div class="note">{esc(c["note"])}</div>' if c.get("note") else ""}
        <div class="vote-row" title="看过这家招聘页或面试过？无记名投一票，票数每周一更新">
          <span class="vote-btn yes" data-vote="yes" data-id="{esc(c['id'])}" onclick="vote(event,this)">✓ 我确认招35+ <b>{yes}</b></span>
          <span class="vote-btn no" data-vote="no" data-id="{esc(c['id'])}" onclick="vote(event,this)">✗ 不确认 <b>{no}</b></span>
        </div>
      </a>"""


VOTE_JS = """
function vote(ev, el){
  ev.preventDefault(); ev.stopPropagation();
  const id = el.dataset.id, kind = el.dataset.vote;
  if (localStorage.getItem('job35-vote-' + id)) { el.classList.add('voted'); return; }
  fetch('https://abacus.jasoncameron.dev/hit/job35-v1/' + encodeURIComponent(id) + '-' + kind, {mode:'no-cors'})
    .catch(()=>{});
  localStorage.setItem('job35-vote-' + id, kind);
  const b = el.querySelector('b'); b.textContent = (parseInt(b.textContent)||0) + 1;
  el.classList.add('voted');
  el.title = '已记录，票数每周一更新';
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.vote-btn').forEach(el => {
    if (localStorage.getItem('job35-vote-' + el.dataset.id)) el.classList.add('voted');
  });
});
"""


def build_index(out: Path, industries: list, companies: list, votes: dict, generated: str) -> None:
    by_industry: dict[str, list[dict]] = {}
    for c in companies:
        by_industry.setdefault(c["industry"], []).append(c)

    sections: list[str] = []
    for ind in industries:
        rows = by_industry.get(ind["code"], [])
        cards = "".join(card_html(c, votes) for c in rows) or '<p class="empty">收录中… / Collecting…</p>'
        sections.append(
            f"""
    <section id="{esc(ind['code'])}">
      <h2>{esc(ind['name_cn'])} <span class="en">{esc(ind['name_en'])}</span>
        <span class="count">{len(rows)}</span></h2>
      <p class="ind-note">{esc(ind.get('note', ''))}</p>
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
<style>{COMMON_CSS}
  nav {{ position:sticky; top:0; background:#fff; border-bottom:1px solid var(--line);
        padding:10px 24px; display:flex; gap:14px; flex-wrap:wrap; z-index:10; }}
  nav a {{ color:var(--muted); text-decoration:none; font-size:.9rem; }}
  nav a:hover {{ color:#0d3b66; }}
  nav a.nav-products {{ margin-left:auto; color:#1a7f37; font-weight:600; }}
  section {{ padding:28px 0; border-bottom:1px solid var(--line); }}
  h2 {{ font-size:1.3rem; margin:0 0 4px; }}
  .count {{ background:var(--bg); border-radius:12px; padding:1px 10px; font-size:.8rem;
           color:var(--muted); vertical-align:middle; }}
  .ind-note {{ color:var(--muted); font-size:.88rem; margin:0 0 16px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .card {{ display:block; text-decoration:none; color:inherit; border:1px solid var(--line);
          border-radius:10px; padding:14px 16px; background:#fff;
          transition:border-color .15s, box-shadow .15s; }}
  .card:hover {{ border-color:#0d3b66; box-shadow:0 2px 10px rgba(13,59,102,.12); }}
  .card-head strong {{ font-size:1.02rem; }}
  .card-head .en {{ margin-left:6px; }}
  .card-meta {{ display:flex; gap:8px; align-items:center; margin-top:8px; flex-wrap:wrap; }}
  .tier, .country {{ background:var(--bg); border-radius:6px; padding:1px 8px; font-size:.78rem;
                     color:var(--muted); }}
  .go-wrap {{ margin-left:auto; }}
  .go {{ color:#1a7f37; font-size:.8rem; white-space:nowrap; }}
  .go.search {{ color:var(--muted); }}
  .card:hover .go {{ text-decoration:underline; }}
  .note {{ color:var(--muted); font-size:.82rem; margin-top:8px; }}
  .empty {{ color:var(--muted); }}
  .vote-row {{ display:flex; gap:10px; margin-top:10px; padding-top:8px;
               border-top:1px dashed var(--line); }}
  .vote-btn {{ font-size:.8rem; color:var(--muted); cursor:pointer; user-select:none;
               padding:1px 8px; border-radius:10px; border:1px solid var(--line); }}
  .vote-btn.yes:hover {{ color:#1a7f37; border-color:#1a7f37; }}
  .vote-btn.no:hover {{ color:#cf222e; border-color:#cf222e; }}
  .vote-btn.voted {{ opacity:.55; cursor:default; }}
  .vote-btn b {{ margin-left:2px; }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>job35-directory</h1>
  <p>收录对 35+ 求职者友好、且近半年招聘仍然活跃的企业 · Companies friendly to 35+ job seekers, actively hiring in the last 6 months</p>
  <p>数据与证据见 <a href="https://github.com/MaxLiu1979/job35-directory">GitHub 仓库</a> · 判定方法见 methodology · 点卡片可直达企业招聘页</p>
</div></header>
<nav>{nav}<a class="nav-products" href="products.html">🛒 35+ 友好产品搜索 →</a></nav>
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
<script>{VOTE_JS}</script>
</body>
</html>
"""
    (out / "index.html").write_text(page, encoding="utf-8")


def build_products(out: Path, companies: list, generated: str) -> None:
    company_by_id = {c["id"]: c for c in companies}
    flat: list[dict] = []
    for path in sorted((ROOT / "data" / "products").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for p in data.get("products", []):
            c = company_by_id.get(p["company_id"])
            if not c:
                continue
            href, _, _ = company_link(c)
            for it in p.get("items", []):
                flat.append({
                    "n": it["name"],
                    "c": p.get("company_name") or c["name"],
                    "cat": it["category"],
                    "k": it.get("keywords", []),
                    "href": href,
                })

    cats = [c for c in CATEGORY_ORDER if any(f["cat"] == c for f in flat)]
    cats += sorted({f["cat"] for f in flat} - set(cats))

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>35+ 友好产品搜索 · job35-directory</title>
<meta property="og:title" content="35+ 友好产品搜索 · job35-directory">
<meta property="og:description" content="按日常需求搜索招 35+ 员工的企业产品：说“牛奶”，出来的都是善待资深员工的公司。">
<meta property="og:image" content="https://maxliu1979.github.io/job35-directory/cards/all.png">
<style>{COMMON_CSS}
  .search-bar {{ display:flex; gap:10px; margin:24px auto; max-width:720px; padding:0 24px; }}
  #q {{ flex:1; padding:12px 16px; font-size:1.05rem; border:1.5px solid var(--line);
        border-radius:10px; outline:none; }}
  #q:focus {{ border-color:#0d3b66; }}
  .mic {{ padding:0 18px; font-size:1.3rem; border:1.5px solid var(--line); border-radius:10px;
          background:#fff; cursor:pointer; }}
  .mic.on {{ border-color:#cf222e; color:#cf222e; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:8px; max-width:1080px; margin:0 auto 20px; padding:0 24px; }}
  .chip {{ padding:3px 12px; border-radius:14px; border:1px solid var(--line); font-size:.85rem;
           color:var(--muted); cursor:pointer; user-select:none; }}
  .chip.on {{ background:#0d3b66; color:#fff; border-color:#0d3b66; }}
  #hint {{ text-align:center; color:var(--muted); font-size:.9rem; margin-bottom:16px; }}
  .p-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px;
             max-width:1080px; margin:0 auto; padding:0 24px 40px; }}
  .p-card {{ border:1px solid var(--line); border-radius:10px; padding:12px 14px; display:block;
             text-decoration:none; color:inherit; }}
  .p-card:hover {{ border-color:#1a7f37; }}
  .p-card .p-name {{ font-weight:600; }}
  .p-card .p-co {{ color:var(--muted); font-size:.85rem; margin-top:4px; }}
  .p-card .p-cat {{ display:inline-block; margin-top:6px; background:var(--bg); border-radius:6px;
                   padding:1px 8px; font-size:.75rem; color:var(--muted); }}
  #count {{ text-align:center; color:var(--muted); font-size:.85rem; margin-bottom:10px; }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1><a href="index.html">← job35-directory</a></h1>
  <p>35+ 友好产品搜索 · 每个产品背后，都是一家招 35+ 员工的企业</p>
  <p>点任意产品 → 直达该企业招聘页 · 数据每周更新 · 点击麦克风说出你想买的东西（如"牛奶"）</p>
</div></header>
<div class="search-bar">
  <input id="q" type="search" placeholder="输入或语音说出你想买的东西，如：牛奶、洗衣液、加油……" autofocus>
  <button id="mic" class="mic" title="语音输入（浏览器需支持语音识别，推荐 Chrome/Edge）">🎤</button>
</div>
<div class="chips" id="chips"></div>
<p id="hint"></p>
<p id="count"></p>
<div class="p-grid" id="results"></div>
<footer>
  <p>本页列出的是名录企业在售的代表性产品，用于支持"雇佣友好"的消费选择，不构成对产品质量的评价。数据：CC0-1.0 · 最后生成：{generated}</p>
  <p>产品信息有误？<a href="https://github.com/MaxLiu1979/job35-directory/issues">提交 issue</a>。</p>
</footer>
<script id="product-data" type="application/json">{json.dumps(flat, ensure_ascii=False)}</script>
<script>
const DATA = JSON.parse(document.getElementById('product-data').textContent);
const q = document.getElementById('q');
const results = document.getElementById('results');
const chipsEl = document.getElementById('chips');
const hint = document.getElementById('hint');
const countEl = document.getElementById('count');
const CATS = {json.dumps(cats, ensure_ascii=False)};
let activeCat = null;

function match(item, query) {{
  if (!query) return true;
  const hay = (item.n + item.c + item.cat + item.k.join(' ')).toLowerCase();
  return query.toLowerCase().split(/\\s+/).every(w => hay.includes(w));
}}

function render() {{
  const query = q.value.trim();
  const list = DATA.filter(f => (!activeCat || f.cat === activeCat) && match(f, query));
  countEl.textContent = list.length ? `共 ${{list.length}} 个产品 / ${{new Set(list.map(f => f.c)).size}} 家企业` : '';
  hint.textContent = list.length ? '' : (query || activeCat ? '没有匹配的产品，换个词试试（数据持续收录中）' : '');
  results.innerHTML = list.map(f => `
    <a class="p-card" href="${{f.href}}" target="_blank" rel="noopener" title="直达 ${{f.c}} 招聘页">
      <div class="p-name">${{f.n}}</div>
      <div class="p-co">${{f.c}}</div>
      <span class="p-cat">${{f.cat}}</span>
    </a>`).join('');
}}

chipsEl.innerHTML = CATS.map(c =>
  `<span class="chip" data-cat="${{c}}">${{c}}</span>`).join('');
chipsEl.addEventListener('click', e => {{
  const chip = e.target.closest('.chip');
  if (!chip) return;
  activeCat = (activeCat === chip.dataset.cat) ? null : chip.dataset.cat;
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('on', x.dataset.cat === activeCat));
  render();
}});
q.addEventListener('input', render);

const mic = document.getElementById('mic');
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SR) {{
  mic.style.display = 'none';
  hint.textContent = '当前浏览器不支持语音输入，请直接用文字搜索（推荐 Chrome/Edge）';
}} else {{
  let rec = null;
  mic.addEventListener('click', () => {{
    if (rec) {{ rec.stop(); return; }}
    rec = new SR();
    rec.lang = 'zh-CN'; rec.interimResults = false;
    mic.classList.add('on');
    rec.onresult = e => {{
      q.value = e.results[0][0].transcript;
      render();
    }};
    rec.onend = () => {{ rec = null; mic.classList.remove('on'); }};
    rec.onerror = () => {{ rec = null; mic.classList.remove('on'); }};
    rec.start();
  }});
}}
render();
</script>
</body>
</html>
"""
    (out / "products.html").write_text(page, encoding="utf-8")
    print(f"已生成 {out / 'products.html'}（{len(flat)} 个产品 / {len(cats)} 个分类）")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    industries = yaml.safe_load(
        (ROOT / "data" / "industries.yaml").read_text(encoding="utf-8")
    )["industries"]
    companies = yaml.safe_load(
        (ROOT / "data" / "companies.yaml").read_text(encoding="utf-8")
    )["companies"]
    votes_path = ROOT / "data" / "votes.json"
    votes = {}
    if votes_path.exists():
        votes = json.loads(votes_path.read_text(encoding="utf-8"))

    generated = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    build_index(out, industries, companies, votes, generated)
    build_products(out, companies, generated)
    print(f"已生成 {out / 'index.html'}（{len(companies)} 家企业 / {len(industries)} 个行业）")


if __name__ == "__main__":
    main()
