"""Build zh-CN (/), zh-TW (/zh-TW/) and en (/en/) pages from the manual source.

zh-CN body comes from zh-CN.artifact.html; zh-TW is converted from it with OpenCC
(to-tw.mjs + upstream terminology); en body is the hand translation in body-en.html.
"""
import html, pathlib, re, subprocess, sys

SRC = pathlib.Path(__file__).parent
OUT = SRC.parent
TW = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else str(SRC / "to-tw.mjs")

raw = (SRC / "zh-CN.artifact.html").read_text()
css = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
body_zh = raw.split("</style>", 1)[1].replace('<div class="meta">', '<!--LANGSWITCH-->\n    <div class="meta">', 1)
body_en = (SRC / "body-en.html").read_text()


def with_prompts(body, copy, done, failed):
    """Replace <!--PROMPT:key--> with the full prompt from prompts/<key>.txt plus a copy button."""
    def block(m):
        text = html.escape((SRC / "prompts" / f"{m.group(1)}.txt").read_text().rstrip("\n"), quote=False)
        return (f'<div class="prompt"><button type="button" class="copy" data-done="{done}" data-failed="{failed}">{copy}</button>'
                f'<pre>{text}</pre></div>')
    return re.sub(r"<!--PROMPT:([a-z0-9-]+)-->", block, body)


body_zh = with_prompts(body_zh, "复制", "已复制", "请手动选择复制")
body_en = with_prompts(body_en, "Copy", "Copied", "Select to copy")


def with_detailed(body, lang, eyebrow, title, desc, cta):
    """Put a card linking to the detailed lab manual (/lab-manual/) right above the hero's table of contents.
    data-lab-lang presets that page's language: it reads localStorage "itd-lab-language" on the same origin."""
    card = (f'<a class="detailed" href="lab-manual/" data-lab-lang="{lang}">'
            f'<span class="eyebrow">{eyebrow}</span><b>{title}</b><span class="desc">{desc}</span>'
            f'<span class="cta">{cta} →</span></a>\n    ')
    return body.replace('<nav class="toc"', card + '<nav class="toc"', 1)


# zh-TW is converted from body_zh by OpenCC, so its card text is converted too; page() fixes its data-lab-lang and the href depth
body_zh = with_detailed(body_zh, "zh", "详细版 · Lab Manual", "逐步点击的详细版学员手册",
                        "从认识 App 到四个 Lab，每一步都有截图和可复制的提示词；简中 / 繁中 / English 三语。", "打开详细版手册")
body_en = with_detailed(body_en, "en", "Detailed edition · Lab Manual", "The click-by-click learner manual",
                        "From getting to know the App to all four labs, every step with a screenshot and a copyable prompt. Simplified Chinese / Traditional Chinese / English.",
                        "Open the detailed manual")

css += """
.lang { display: flex; gap: 4px; background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 3px; }
.lang a { font: 500 12.5px var(--font-cn); color: var(--text-2); text-decoration: none; padding: 5px 12px; border-radius: 999px; }
.lang a:hover { color: var(--text); }
.lang a[aria-current="page"] { background: var(--orchid); color: #fff; }
.lang.float { position: fixed; z-index: 20; top: max(12px, env(safe-area-inset-top, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); box-shadow: 0 6px 20px rgba(20, 12, 28, .45); }
.lang[hidden] { display: none; }
.prompt { position: relative; max-width: 52em; margin: 8px 0 14px; }
.prompt pre { margin: 0; padding-top: 44px; max-width: none; overflow-wrap: anywhere; }
.copy { position: absolute; top: 8px; right: 8px; font: 600 12.5px var(--font-cn); color: var(--text); background: var(--orchid-chip); border: 1px solid var(--border); border-radius: 999px; padding: 6px 14px; cursor: pointer; }
.copy:hover { background: #6A4A7E; }
.copy.done { background: var(--orchid); border-color: transparent; color: #fff; }
.detailed { display: grid; gap: 6px; max-width: 40em; margin: 24px 0 4px; padding: 18px 20px; text-decoration: none; color: var(--text); background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--orchid); border-radius: 12px; transition: border-color .15s, transform .15s; }
.detailed:hover { border-color: var(--orchid-soft); transform: translateY(-1px); }
.detailed b { font-size: 17px; }
.detailed .desc { color: var(--text-2); font-size: 14px; }
.detailed .cta { color: var(--orchid-soft); font-weight: 600; font-size: 14px; }
"""
FONTS = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Sans:wght@400;700&family=IBM+Plex+Mono:wght@400;500;600&family=Geist:wght@500;600&family=Instrument+Serif:ital@0;1&display=swap"
PAGES = {  # lang: (dir, title, description)
    "zh-CN": ("", "Copilot App 实跑手册", "用 GitHub Copilot App（GPT-6 Luna）实跑 hol_ghc_app 四个 Lab 的操作手册。"),
    "zh-TW": ("zh-TW/", "Copilot App 實跑手冊", "用 GitHub Copilot App（GPT-6 Luna）實跑 hol_ghc_app 四個 Lab 的操作手冊。"),
    "en": ("en/", "Copilot App Field Manual", "A real run of the four hol_ghc_app labs with GitHub Copilot App (GPT-6 Luna)."),
}
COPY_JS = """<script>
(() => {
  // 每条提示词的复制按钮：优先用剪贴板 API，被拒时选中全文让读者手动复制
  for (const btn of document.querySelectorAll(".prompt .copy")) {
    const label = btn.textContent, pre = btn.nextElementSibling;
    const flash = (text, ok) => { btn.textContent = text; btn.classList.toggle("done", ok); setTimeout(() => { btn.textContent = label; btn.classList.remove("done"); }, 1600); };
    const select = () => { const r = document.createRange(); r.selectNodeContents(pre); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); };
    btn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(pre.textContent); flash(btn.dataset.done, true); }
      catch { select(); let ok = false; try { ok = document.execCommand("copy"); } catch {} flash(ok ? btn.dataset.done : btn.dataset.failed, ok); }
    });
  }
})();
</script>"""
SWITCH_JS = """<script>
(() => {
  // 切换语言时带上当前章节；在切换器上选过的语言记在本机，下次从根地址进入时自动跳转
  const KEY = "manual-lang";
  const store = { get() { try { return localStorage.getItem(KEY); } catch { return null; } },
                  set(v) { try { localStorage.setItem(KEY, v); } catch {} } };
  const here = document.documentElement.lang;
  const nav = document.querySelector(".lang");
  // 页首的切换器滚出视口后，右上角浮出同一组链接，读到哪里都能直接切换
  const float = nav.cloneNode(true);
  float.classList.add("float"); float.hidden = true; float.setAttribute("aria-label", nav.getAttribute("aria-label") + " (floating)");
  document.body.append(float);
  new IntersectionObserver(([e]) => { float.hidden = e.isIntersecting; }).observe(nav);
  const links = [...document.querySelectorAll(".lang a[hreflang]")];
  const pref = store.get();
  if (here === "zh-CN" && pref && pref !== here) {
    const target = links.find(a => a.hreflang === pref);
    if (target) { location.replace(target.href + location.hash); return; }
  }
  const currentSection = () => {
    const sections = [...document.querySelectorAll("section[id]")];
    const atBottom = innerHeight + scrollY >= document.documentElement.scrollHeight - 4;
    if (atBottom && sections.length) return sections.at(-1).id;
    let id = "";
    for (const s of sections) if (s.getBoundingClientRect().top <= 140) id = s.id;
    return id || location.hash.slice(1);
  };
  for (const a of links) a.addEventListener("click", e => {
    store.set(a.hreflang);
    const id = currentSection();
    if (id) { e.preventDefault(); location.href = a.href.split("#")[0] + "#" + id; }
  });
  // 详细版手册按 localStorage 的 itd-lab-language 选语言（同源），点入口时带上当前页面的语言
  for (const a of document.querySelectorAll("a[data-lab-lang]"))
    a.addEventListener("click", () => { try { localStorage.setItem("itd-lab-language", a.dataset.labLang); } catch {} });
})();
</script>"""
LABELS = [("zh-CN", "简体中文"), ("zh-TW", "繁體中文"), ("en", "English")]


SITE = "https://itd-nextdimension.github.io/copilot-app-manual/"


def switcher(cur, absolute=False):
    up = "../" if PAGES[cur][0] else ""
    href = lambda l: SITE + PAGES[l][0] if absolute else up + (PAGES[l][0] or "./")
    extra = ' target="_blank" rel="noopener"' if absolute else ""
    links = "".join(
        f'<a href="{href(l)}" hreflang="{l}" lang="{l}"' + (' aria-current="page"' if l == cur else extra) + f">{name}</a>"
        for l, name in LABELS)
    return f'<nav class="lang" aria-label="Language">{links}</nav>'


def sized(body):
    """Give every <img> its real width/height so lazy images reserve space and #anchors land correctly."""
    from PIL import Image
    def add(m):
        w, h = Image.open(OUT / m.group(1)).size
        return f'<img src="{m.group(1)}" width="{w}" height="{h}"'
    return re.sub(r'<img src="(img/[^"]+)"', add, body)


def page(lang, body):
    d, title, desc = PAGES[lang]
    up = "../" if d else ""
    page_css = css.replace('url("img/', f'url("{up}img/')
    fonts = FONTS
    if lang == "zh-TW":
        fonts = FONTS.replace("family=Noto+Sans+SC", "family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Sans+SC")
        page_css = page_css.replace('--font-cn: "Noto Sans SC", "PingFang SC"', '--font-cn: "Noto Sans TC", "PingFang TC", "Noto Sans SC", "PingFang SC"')
    body = sized(body).replace("<!--LANGSWITCH-->", switcher(lang))
    body = body.replace('src="img/', f'src="{up}img/').replace('data-full="img/', f'data-full="{up}img/')
    body = body.replace('href="lab-manual/"', f'href="{up}lab-manual/"')
    if lang == "zh-TW":
        body = body.replace('data-lab-lang="zh"', 'data-lab-lang="tw"')
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
<body>{body}
{COPY_JS}
{SWITCH_JS}
</body>
</html>
"""


zh = page("zh-CN", body_zh)
tw = subprocess.run(["node", TW], input=body_zh, capture_output=True, text=True, check=True).stdout
# OpenCC 的台湾词汇把「通过」一律转成「透過」；本手册里多数是「验收通过」，只有两处是「经由」
tw = tw.replace("透過", "通過").replace("能通過 Playwright", "能透過 Playwright").replace("並通過 CLI", "並透過 CLI")
for lang, doc in (("zh-CN", zh), ("zh-TW", page("zh-TW", tw)), ("en", page("en", body_en))):
    target = OUT / PAGES[lang][0] / "index.html"
    target.parent.mkdir(exist_ok=True)
    target.write_text(doc)
    print(lang, target.relative_to(OUT), len(doc))

# --artifact PATH: the Simplified page in claude.ai Artifact format (no document skeleton,
# language links point to the Pages site, copy script only)
if "--artifact" in sys.argv:
    target = pathlib.Path(sys.argv[sys.argv.index("--artifact") + 1])
    body = sized(body_zh).replace("<!--LANGSWITCH-->", switcher("zh-CN", absolute=True))
    doc = f"""<title>{PAGES["zh-CN"][1]}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{FONTS}">
<style>{css}</style>
{body}
{COPY_JS}
"""
    target.write_text(doc)
    print("artifact", target, len(doc))
