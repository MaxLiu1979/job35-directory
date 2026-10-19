"""生成行业分享卡片 PNG（1200x630，用于微信/即刻/小红书传播）。

依赖 Pillow：pip install pillow
中文字体：Windows 用微软雅黑，Linux CI 装 fonts-noto-cjk 后用 Noto。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
TOP, BOTTOM = (13, 59, 102), (26, 127, 55)  # 深蓝 -> 绿，与站点头部一致

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",   # 微软雅黑 Bold
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise SystemExit("找不到中文字体：Windows 需 msyh.ttc，Linux 需 fonts-noto-cjk")


def gradient() -> Image.Image:
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        base.putpixel(
            (0, y),
            tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)),
        )
    return base.resize((W, H))


def draw_card(title_cn: str, title_en: str, count: int, out: Path) -> None:
    img = gradient()
    d = ImageDraw.Draw(img)
    f_kicker = font(34)
    f_title = font(96)
    f_en = font(40)
    f_count = font(52)
    f_foot = font(30)

    d.text((80, 90), "job35-directory · 35+ 友好企业名录", font=f_kicker, fill=(255, 255, 255, 200))
    d.text((80, 190), title_cn, font=f_title, fill="#ffffff")
    d.text((80, 320), title_en, font=f_en, fill=(255, 255, 255, 190))

    badge = f"{count} 家企业在收录 / tracked"
    bbox = d.textbbox((0, 0), badge, font=f_count)
    pad = 28
    d.rounded_rectangle(
        (80, 430, 80 + (bbox[2] - bbox[0]) + pad * 2, 430 + 90),
        radius=45,
        fill=(255, 255, 255),
        outline="#ffffff",
        width=2,
    )
    d.text((80 + pad, 442), badge, font=f_count, fill=TOP)

    d.text((80, 560), "每周自动更新 · 公开证据可查证 · maxliu1979.github.io/job35-directory",
           font=f_foot, fill=(255, 255, 255, 190))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print(f"  {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site/cards")
    args = parser.parse_args()
    out_dir = Path(args.out)

    industries = yaml.safe_load(
        (ROOT / "data/industries.yaml").read_text(encoding="utf-8")
    )["industries"]
    companies = yaml.safe_load(
        (ROOT / "data/companies.yaml").read_text(encoding="utf-8")
    )["companies"]

    by_industry: dict[str, int] = {}
    for c in companies:
        by_industry[c["industry"]] = by_industry.get(c["industry"], 0) + 1

    print("生成分享卡片：")
    total = 0
    for ind in industries:
        n = by_industry.get(ind["code"], 0)
        total += n
        draw_card(ind["name_cn"], ind["name_en"], n, out_dir / f"{ind['code']}.png")
    draw_card("全部行业", "All Industries", total, out_dir / "all.png")


if __name__ == "__main__":
    main()
