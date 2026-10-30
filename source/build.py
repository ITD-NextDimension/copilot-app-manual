"""Build zh-CN (/), zh-TW (/zh-TW/) and en (/en/) pages from the manual source.

zh-CN body comes from zh-CN.artifact.html; zh-TW is converted from it with OpenCC
(to-tw.mjs + upstream terminology); en body is the hand translation in body-en.html.
"""
import pathlib, re, subprocess, sys

SRC = pathlib.Path(__file__).parent
OUT = SRC.parent
TW = sys.argv[1] if len(sys.argv) > 1 else str(SRC / "to-tw.mjs")

raw = (SRC / "zh-CN.artifact.html").read_text()
css = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
body_zh = raw.split("</style>", 1)[1].replace('<div class="meta">', '<!--LANGSWITCH-->\n    <div class="meta">', 1)
body_en = (SRC / "body-en.html").read_text()

css += """
.lang { display: flex; gap: 4px; background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 3px; }
.lang a { font: 500 12.5px var(--font-cn); color: var(--text-2); text-decoration: none; padding: 5px 12px; border-radius: 999px; }
.lang a:hover { color: var(--text); }
.lang a[aria-current="page"] { background: var(--orchid); color: #fff; }
"""
FONTS = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Sans:wght@400;700&family=IBM+Plex+Mono:wght@400;500;600&family=Geist:wght@500;600&family=Instrument+Serif:ital@0;1&display=swap"
PAGES = {  # lang: (dir, title, description)
    "zh-CN": ("", "Copilot App 实跑手册", "用 GitHub Copilot App（GPT-6 Luna）实跑 hol_ghc_app 四个 Lab 的操作手册。"),
    "zh-TW": ("zh-TW/", "Copilot App 實跑手冊", "用 GitHub Copilot App（GPT-6 Luna）實跑 hol_ghc_app 四個 Lab 的操作手冊。"),
    "en": ("en/", "Copilot App Field Manual", "A real run of the four hol_ghc_app labs with GitHub Copilot App (GPT-6 Luna)."),
}
LABELS = [("zh-CN", "简体中文"), ("zh-TW", "繁體中文"), ("en", "English")]


def switcher(cur):
    up = "../" if PAGES[cur][0] else ""
    links = "".join(
        f'<a href="{up}{PAGES[l][0] or "./"}" hreflang="{l}" lang="{l}"' + (' aria-current="page"' if l == cur else "") + f">{name}</a>"
        for l, name in LABELS)
    return f'<nav class="lang" aria-label="Language">{links}</nav>'


def page(lang, body):
    d, title, desc = PAGES[lang]
    up = "../" if d else ""
    page_css = css.replace('url("img/', f'url("{up}img/')
    fonts = FONTS
    if lang == "zh-TW":
        fonts = FONTS.replace("family=Noto+Sans+SC", "family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Sans+SC")
        page_css = page_css.replace('--font-cn: "Noto Sans SC", "PingFang SC"', '--font-cn: "Noto Sans TC", "PingFang TC", "Noto Sans SC", "PingFang SC"')
    body = body.replace("<!--LANGSWITCH-->", switcher(lang))
    body = body.replace('src="img/', f'src="{up}img/').replace('data-full="img/', f'data-full="{up}img/')
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="https://itd-nextdimension.github.io/copilot-app-manual/{PAGES[l][0]}">' for l in PAGES)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{alts}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{fonts}">
<style>{page_css}</style>
</head>
<body>{body}</body>
</html>
"""


zh = page("zh-CN", body_zh)
tw = subprocess.run(["node", TW], input=body_zh, capture_output=True, text=True, check=True).stdout
# OpenCC 的台湾词汇把「通过」一律转成「透過」；本手册里多数是「验收通过」，只有两处是「经由」
tw = tw.replace("透過", "通過").replace("能通過 Playwright", "能透過 Playwright").replace("並通過 CLI", "並透過 CLI")
for lang, html in (("zh-CN", zh), ("zh-TW", page("zh-TW", tw)), ("en", page("en", body_en))):
    target = OUT / PAGES[lang][0] / "index.html"
    target.parent.mkdir(exist_ok=True)
    target.write_text(html)
    print(lang, target.relative_to(OUT), len(html))
