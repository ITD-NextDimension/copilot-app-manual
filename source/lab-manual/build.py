"""Build lab-manual/index.html (zh-CN / zh-TW / EN in one page) from hand-written sources.

Sources (this folder):
  zh-CN.html   Simplified Chinese body  -> zh-TW is converted from it with ../to-tw.mjs (OpenCC + course terminology)
  en.html      English body (hand translation)
  prompts/     prompts learners paste into the App (Chinese in every edition, exactly as pasted)
Images live in ../../img/lab-manual/<step>-focus.webp and <step>-full.webp.

Markup available in the bodies:
  <shot n="1.7-legal-target">caption</shot>     focus crop, with the full window behind "show full window"
  <prompt k="lab1-brief"></prompt>              prompt block with a copy button
  <cmd>…</cmd>                                  command for both systems
  <cmd><mac>…</mac><win>…</win></cmd>           macOS / Windows variants, switched by the page's OS toggle
  <diagram k="lab1-logic"></diagram>            architecture diagram drawn from DIAGRAMS below

Run:  cd source && npm i --no-save opencc-js@1.0.5 && python3 lab-manual/build.py
"""
import html
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
IMG = ROOT / "img" / "lab-manual"
OUT = ROOT / "lab-manual" / "index.html"

UI = {
    "zh": {"copy": "复制", "done": "已复制", "failed": "请手动选择复制", "full": "查看整个窗口", "missing": "截图待补拍",
           "contents": "目录", "os": "命令", "prompt": "提示词"},
    "en": {"copy": "Copy", "done": "Copied", "failed": "Select to copy", "full": "Show the full window", "missing": "Screenshot to be retaken",
           "contents": "Contents", "os": "Commands", "prompt": "Prompt"},
}

# ---------------------------------------------------------------- diagrams
# Each diagram: columns of nodes left to right; a node is (id, kind, zh title, zh sub, en title, en sub).
# kind: person | app | model | code | data | out. Edges: (from, to, zh label, en label).
D = {}
D["lab1-logic"] = dict(
    cols=[[("you", "person", "学员", "写需求 · 点击验收", "Learner", "writes the brief · clicks to check")],
          [("app", "app", "Copilot App 会话", "Autopilot · GPT-6 Luna", "Copilot App session", "Autopilot · GPT-6 Luna")],
          [("files", "code", "Lab1/Code", "读代码 · 改页面 · 加测试", "Lab1/Code", "reads code · edits page · adds tests"),
           ("pw", "code", "Playwright", "真实点击验证", "Playwright", "real clicks")],
          [("game", "out", "浏览器里的象棋", "127.0.0.1:8011", "Chess in the browser", "127.0.0.1:8011")]],
    edges=[("you", "app", "提示词", "prompt"), ("app", "files", "", ""), ("app", "pw", "", ""),
           ("files", "game", "app.py", "app.py"), ("pw", "game", "", "")])
D["lab1-code"] = dict(
    cols=[[("gen", "code", "generate.py", "让 Luna 生成页面", "generate.py", "asks Luna for the page"),
           ("agent", "code", "tools/agent.py", "受限的 SDK 会话", "tools/agent.py", "locked-down SDK session")],
          [("cli", "model", "Copilot CLI", "stdio · gpt-6-luna", "Copilot CLI", "stdio · gpt-6-luna")],
          [("html", "data", "generated.html", "页面外壳 + app.js", "generated.html", "page shell + app.js"),
           ("app", "code", "app.py", "tools/web.py · /api/*", "app.py", "tools/web.py · /api/*")],
          [("game", "code", "xiangqi.Game", "规则 · 将军 · 悔棋", "xiangqi.Game", "rules · check · undo")]],
    edges=[("gen", "cli", "", ""), ("agent", "cli", "", ""), ("cli", "html", "JSON", "JSON"),
           ("html", "app", "点击", "clicks"), ("app", "game", "合法落点", "legal moves")])
D["lab2-logic"] = dict(
    cols=[[("you", "person", "学员", "审方案 · 批准", "Learner", "reviews · approves")],
          [("plan", "app", "Plan 会话", "先出 plan.md", "Plan session", "writes plan.md first"),
           ("auto", "app", "Autopilot", "批准后连续执行", "Autopilot", "runs after approval")],
          [("skills", "model", "HyperFrames Skills", "/hyperframes · -cli · /media-use", "HyperFrames Skills", "/hyperframes · -cli · /media-use"),
           ("tts", "code", "edge-tts", "晓晓普通话女声", "edge-tts", "Xiaoxiao Mandarin voice")],
          [("mp4", "out", "竖屏 MP4", "1080×1920 · 120 s", "Vertical MP4", "1080×1920 · 120 s")]],
    edges=[("you", "plan", "提示词", "prompt"), ("plan", "auto", "批准", "approve"), ("auto", "skills", "", ""),
           ("auto", "tts", "", ""), ("skills", "mp4", "render", "render"), ("tts", "mp4", "", "")])
D["lab2-code"] = dict(
    cols=[[("src", "data", "官网 + 技术规格", "source.json · facts.json", "Product page + specs", "source.json · facts.json")],
          [("story", "data", "分镜与旁白", "story · narration .txt", "Storyboard + script", "story · narration .txt"),
           ("video", "code", "video.py", "prepare · voice · probe", "video.py", "prepare · voice · probe")],
          [("film", "code", "film/", "index.html + 6 个 composition", "film/", "index.html + 6 compositions")],
          [("cli", "code", "HyperFrames CLI", "check · render", "HyperFrames CLI", "check · render"),
           ("probe", "out", "ffprobe 验收", "尺寸 · 帧率 · 音轨", "ffprobe check", "size · fps · audio")]],
    edges=[("src", "story", "", ""), ("src", "video", "", ""), ("story", "film", "", ""), ("video", "film", "素材 · MP3", "assets · MP3"),
           ("film", "cli", "", ""), ("cli", "probe", "MP4", "MP4")])
D["lab3-logic"] = dict(
    cols=[[("ar", "data", "微软 2025 年报", "官网表格", "Microsoft AR 2025", "official tables")],
          [("py", "code", "Python 核对", "营收 · 利润 · 分部之和", "Python reconciles", "revenue · profit · segment sums")],
          [("agent", "app", "一个分析 Agent", "只解释给定数字", "One analysis agent", "explains given numbers only")],
          [("dash", "out", "经营观察室", "127.0.0.1:8013", "Finance observatory", "127.0.0.1:8013")]],
    edges=[("ar", "py", "", ""), ("py", "agent", "数字", "numbers"), ("agent", "dash", "3 条观察", "3 findings"), ("py", "dash", "", "")])
D["lab3-code"] = dict(
    cols=[[("fetch", "code", "tools/fetch_sources.py", "抓表格 · 记 sha256", "tools/fetch_sources.py", "tables · sha256")],
          [("fin", "code", "finance.py", "dataset() · view()", "finance.py", "dataset() · view()")],
          [("an", "code", "analyze.py", "单会话 · 无子 Agent", "analyze.py", "one session · no sub-agents"),
           ("json", "data", "analysis.json", "观察 + 会话记录", "analysis.json", "findings + trace")],
          [("app", "code", "app.py", "/api/data · /api/analysis", "app.py", "/api/data · /api/analysis")]],
    edges=[("fetch", "fin", "tables.json", "tables.json"), ("fin", "an", "", ""), ("an", "json", "", ""),
           ("fin", "app", "", ""), ("json", "app", "", "")])
D["lab4-logic"] = dict(
    cols=[[("mail", "data", "虚构邮件", "3 封 · 固定时钟", "Fictional mail", "3 messages · fixed clock"),
           ("cal", "data", "虚构日历", "3 场会议", "Fictional calendar", "3 meetings")],
          [("triage", "app", "邮件整理员", "独立会话 1", "Mail triage", "session 1"),
           ("reader", "app", "日历观察员", "独立会话 2", "Calendar reader", "session 2")],
          [("planner", "app", "周计划员", "独立会话 3 · 只排序", "Weekly planner", "session 3 · ranks only")],
          [("board", "out", "本周行动清单", "网页 + App Canvas", "Weekly action list", "web page + App Canvas")]],
    edges=[("mail", "triage", "", ""), ("cal", "reader", "", ""), ("triage", "planner", "任务 + 原文", "tasks + quotes"),
           ("reader", "planner", "会议", "meetings"), ("planner", "board", "Python 排程", "Python schedules")])
D["lab4-code"] = dict(
    cols=[[("demo", "code", "collect_demo.py", "Playwright 读训练页", "collect_demo.py", "Playwright reads the page")],
          [("plan", "code", "plan.py", "三个会话 · 校验证据", "plan.py", "three sessions · checks evidence"),
           ("sched", "code", "schedule.py", "本周 · 时区 · 撞会", "schedule.py", "week · time zone · clashes")],
          [("json", "data", "output/plan.json", "store.py 持久化", "output/plan.json", "persisted by store.py")],
          [("app", "code", "app.py :8014", "网页", "app.py :8014", "web page"),
           ("ext", "code", "extension.mjs", "bridge.py · install_canvas.py", "extension.mjs", "bridge.py · install_canvas.py")]],
    edges=[("demo", "plan", "collected-demo.json", "collected-demo.json"), ("plan", "sched", "", ""), ("plan", "json", "", ""),
           ("sched", "json", "", ""), ("json", "app", "", ""), ("json", "ext", "complete", "complete")])

STYLE = {  # fill, stroke, text, dash
    "person": ("#FFFFFF", "#2A1E4A", "#2A1E4A", "4 3"),
    "app": ("#2A1E4A", "#2A1E4A", "#FFFFFF", ""),
    "model": ("#ECE8F2", "#4A3D6E", "#2A1E4A", ""),
    "code": ("#FFFFFF", "#C5BCD0", "#2A1E4A", ""),
    "data": ("#F9F8F4", "#C5BCD0", "#2A1E4A", "2 3"),
    "out": ("#F4F2EC", "#2A1E4A", "#2A1E4A", ""),
}


def diagram(key, lang):
    spec = D[key]
    w, h, gx, gy, pad = 178, 62, 64, 26, 18
    rows = max(len(c) for c in spec["cols"])
    height = pad * 2 + rows * h + (rows - 1) * gy + 18
    width = pad * 2 + len(spec["cols"]) * w + (len(spec["cols"]) - 1) * gx
    pos = {}
    for ci, col in enumerate(spec["cols"]):
        total = len(col) * h + (len(col) - 1) * gy
        top = (height - total) / 2
        for ri, node in enumerate(col):
            pos[node[0]] = (pad + ci * (w + gx), top + ri * (h + gy), node)
    parts = [f'<svg class="dg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(key)}" xmlns="http://www.w3.org/2000/svg">',
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0 0L10 5L0 10z" fill="#4A3D6E"/></marker></defs>']
    for a, b, zl, el in spec["edges"]:
        ax, ay, _ = pos[a]
        bx, by, _ = pos[b]
        label = zl if lang == "zh" else el
        if ax == bx:  # same column: vertical
            x1, y1, x2, y2 = ax + w / 2, ay + h, bx + w / 2, by
        else:
            x1, y1, x2, y2 = ax + w, ay + h / 2, bx, by + h / 2
        parts.append(f'<path d="M{x1:.0f} {y1:.0f} C{(x1 + x2) / 2:.0f} {y1:.0f} {(x1 + x2) / 2:.0f} {y2:.0f} {x2 - 2:.0f} {y2:.0f}" '
                     f'fill="none" stroke="#8B82A0" stroke-width="1.4" marker-end="url(#ah)"/>')
        if label:
            parts.append(f'<text x="{(x1 + x2) / 2:.0f}" y="{(y1 + y2) / 2 - 6:.0f}" class="el">{html.escape(label)}</text>')
    for nid, (x, y, node) in pos.items():
        _, kind, zt, zs, et, es = node
        title, sub = (zt, zs) if lang == "zh" else (et, es)
        fill, stroke, text, dash = STYLE[kind]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{d}/>')
        parts.append(f'<text x="{x + w / 2:.0f}" y="{y + 26:.0f}" class="nt" fill="{text}">{html.escape(title)}</text>')
        parts.append(f'<text x="{x + w / 2:.0f}" y="{y + 45:.0f}" class="ns" fill="{text}">{html.escape(sub)}</text>')
    parts.append("</svg>")
    return f'<figure class="diagram"><div class="dg-scroll">{"".join(parts)}</div></figure>'


# ---------------------------------------------------------------- body transforms
def esc(s):
    return html.escape(s.strip("\n"), quote=False)


def render(body, lang):
    ui = UI["en" if lang == "en" else "zh"]
    dl = "en" if lang == "en" else "zh"

    def shot(m):
        n, cap = m.group(1), m.group(2).strip()
        focus, full = IMG / f"{n}-focus.webp", IMG / f"{n}-full.webp"
        main = focus if focus.exists() else full if full.exists() else None
        cap_html = f"<figcaption>{cap}</figcaption>" if cap else ""
        if main is None:
            return f'<figure class="shot missing"><div class="ph">{ui["missing"]} · {html.escape(n)}</div>{cap_html}</figure>'
        img = f'<img src="../img/lab-manual/{main.name}" alt="{html.escape(re.sub("<[^>]+>", "", cap) or n)}" loading="lazy">'
        more = ""
        if main == focus and full.exists():
            more = (f'<details class="full"><summary>{ui["full"]}</summary>'
                    f'<img src="../img/lab-manual/{full.name}" alt="" loading="lazy"></details>')
        return f'<figure class="shot">{img}{cap_html}{more}</figure>'

    def prompt(m):
        text = esc((HERE / "prompts" / f"{m.group(1)}.txt").read_text(encoding="utf-8"))
        return (f'<div class="code prompt"><div class="head"><span>{ui["prompt"]}</span>'
                f'<button type="button" class="copy" data-done="{ui["done"]}" data-failed="{ui["failed"]}">{ui["copy"]}</button></div>'
                f'<pre>{text}</pre></div>')

    def cmd(m):
        inner = m.group(1)
        mac = re.search(r"<mac>(.*?)</mac>", inner, re.S)
        win = re.search(r"<win>(.*?)</win>", inner, re.S)
        blocks = ([("mac", "macOS", mac.group(1)), ("win", "Windows PowerShell", win.group(1))]
                  if mac and win else [("both", "macOS · Windows", inner)])
        out = []
        for cls, label, text in blocks:
            out.append(f'<div class="code cmd os-{cls}"><div class="head"><span>{label}</span>'
                       f'<button type="button" class="copy" data-done="{ui["done"]}" data-failed="{ui["failed"]}">{ui["copy"]}</button></div>'
                       f'<pre>{esc(text)}</pre></div>')
        return "".join(out)

    body = re.sub(r'<shot n="([^"]+)">(.*?)</shot>', shot, body, flags=re.S)
    body = re.sub(r'<prompt k="([^"]+)"></prompt>', prompt, body)
    body = re.sub(r"<cmd>(.*?)</cmd>", cmd, body, flags=re.S)
    body = re.sub(r'<diagram k="([^"]+)"></diagram>', lambda m: diagram(m.group(1), dl), body)
    return body


def toc(body):
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
        level, hid, text = m.groups()
        text = re.sub(r"<[^>]+>", "", text).strip()
        items.append(f'<li class="l{level}"><a href="#{hid}">{text}</a></li>')
    return "<ol>" + "".join(items) + "</ol>"


def to_tw(text):
    return subprocess.run(["node", str(HERE.parent / "to-tw.mjs")], input=text, capture_output=True,
                          text=True, check=True, cwd=HERE.parent).stdout


def main():
    zh_src = (HERE / "zh-CN.html").read_text(encoding="utf-8")
    en_src = (HERE / "en.html").read_text(encoding="utf-8")
    zh = render(zh_src, "zh")
    tw = to_tw(zh)
    en = render(en_src, "en")
    # ids must be unique on the page: prefix each edition
    editions = []
    for code, body, label in (("zh", zh, "简"), ("tw", tw, "繁"), ("en", en, "EN")):
        body = re.sub(r'id="([^"]+)"', lambda m: f'id="{code}-{m.group(1)}"', body)
        body = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{code}-{m.group(1)}"', body)
        editions.append((code, body))
    template = (HERE / "template.html").read_text(encoding="utf-8")
    sections, tocs = [], []
    for code, body in editions:
        sections.append(f'<article class="edition" data-lang="{code}" lang="{ {"zh": "zh-Hans", "tw": "zh-Hant", "en": "en"}[code] }" hidden>{body}</article>')
        tocs.append(f'<nav class="toc" data-lang="{code}" hidden>{toc(body)}</nav>')
    page = template.replace("<!--EDITIONS-->", "\n".join(sections)).replace("<!--TOCS-->", "\n".join(tocs))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
