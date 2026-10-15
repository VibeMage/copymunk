#!/usr/bin/env python3
"""从 PRIVACY.md 生成隐私政策网页 docs/privacy/index.html（https://copymunk.com/privacy/）。

    python3 scripts/make-privacy-page.py          # 重新生成
    python3 scripts/make-privacy-page.py --check  # 只核对网页是否与 PRIVACY.md 一致，不一致时退出码 1

PRIVACY.md 是唯一来源：改隐私政策只改它，再跑本脚本，两者一起提交。网页样式沿用 docs/support/。
只认 PRIVACY.md 用到的那点 Markdown：## / ### 标题、段落、两级「- 」列表、**粗体**、*斜体*、裸网址。
遇到别的写法（链接、代码、表格……）直接报错，免得网页悄悄漏掉或改坏一句话。

中文段落在源文件里是硬换行的：两行相接处两边都是中日韩字符或全角标点时直接拼接，
否则补一个空格，避免浏览器在汉字之间渲染出多余的空格。
"""

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "PRIVACY.md"
OUTPUT = REPO / "docs" / "privacy" / "index.html"

CJK = re.compile(r"[⺀-鿿　-〿＀-￯“”‘’「」『』《》（）]")
UNSUPPORTED = re.compile(r"\]\(|`|^\s*\d+\.\s|^\s*>|\|")


def join(a, b):
    if not a:
        return b
    if CJK.match(a[-1]) and CJK.match(b[0]):
        return a + b
    return a + " " + b


def inline(text):
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", out)
    out = re.sub(r"(https://[^\s<，。）]+)", r'<a href="\1">\1</a>', out)
    return out


def parse_blocks(lines):
    """把一个语言段落的行切成块：('h3', text) / ('p', text) / ('ul', [(text, [subtext…]), …])。"""
    blocks, para, items = [], None, None

    def flush():
        nonlocal para, items
        if para is not None:
            blocks.append(("p", para))
        if items is not None:
            blocks.append(("ul", items))
        para, items = None, None

    for raw in lines:
        if UNSUPPORTED.search(raw):
            raise ValueError(f"PRIVACY.md 里有本脚本不认识的 Markdown：{raw.strip()}")
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("### "):
            flush()
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("- "):
            if para is not None:
                flush()
            if items is None:
                items = []
            items.append([line[2:].strip(), []])
        elif line.startswith("  - "):
            if not items:
                raise ValueError(f"二级列表前面没有一级列表：{line.strip()}")
            items[-1][1].append(line[4:].strip())
        elif items is not None and line.startswith("    ") and items[-1][1]:
            items[-1][1][-1] = join(items[-1][1][-1], line.strip())
        elif items is not None and line.startswith("  "):
            items[-1][0] = join(items[-1][0], line.strip())
        elif line.startswith((" ", "#")):
            raise ValueError(f"无法归类的行：{line}")
        else:
            if items is not None:
                flush()
            para = join(para or "", line.strip())
    flush()
    return blocks


def render_section(lang, blocks):
    """每个 ### 一张卡片；第一个 ### 之前的段落放进一张没有标题的引言卡片。"""
    heads = ["red", "blue", "cream"]
    cards, current = [], None
    for kind, value in blocks:
        if kind == "h3":
            current = {"title": value, "body": []}
            cards.append(current)
            continue
        if current is None:
            current = {"title": None, "body": []}
            cards.append(current)
        if kind == "p":
            current["body"].append(f"        <p>{inline(value)}</p>")
        else:
            lis = []
            for text, subs in value:
                sub = ""
                if subs:
                    sub = "\n          <ul>\n" + "\n".join(
                        f"            <li>{inline(s)}</li>" for s in subs) + "\n          </ul>\n        "
                lis.append(f"          <li>{inline(text)}{sub}</li>")
            current["body"].append("        <ul>\n" + "\n".join(lis) + "\n        </ul>")
    out = [f'  <section data-lang="{lang}">']
    titled = 0
    for card in cards:
        out.append('    <div class="card">')
        if card["title"]:
            color = heads[titled % len(heads)]
            titled += 1
            out.append(f'      <h2 class="card-head {color}"><span class="dot"></span>{inline(card["title"])}</h2>')
        out.append('      <div class="card-body">')
        out.extend(card["body"])
        out.append("      </div>")
        out.append("    </div>")
    out.append("  </section>")
    return "\n".join(out)


def build():
    text = SOURCE.read_text(encoding="utf-8")
    m = re.search(r"\*\*Effective date / 生效日期: (\d{4}-\d{2}-\d{2})\*\*", text)
    if not m:
        raise ValueError("PRIVACY.md 里找不到「**Effective date / 生效日期: YYYY-MM-DD**」")
    date = m.group(1)
    parts = re.split(r"^## (English|中文)\s*$", text, flags=re.M)
    if len(parts) != 5 or parts[1] != "English" or parts[3] != "中文":
        raise ValueError("PRIVACY.md 应当先是「## English」、再是「## 中文」两段")
    en = render_section("en", parse_blocks(parts[2].splitlines()))
    zh = render_section("zh", parse_blocks(parts[4].splitlines()))
    return TEMPLATE.replace("{{DATE}}", date).replace("{{EN}}", en).replace("{{ZH}}", zh)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- 由 scripts/make-privacy-page.py 从 PRIVACY.md 生成，不要手改；改 PRIVACY.md 后重跑脚本。 -->
<title>Copymunk Privacy Policy · 隐私政策</title>
<meta name="description" content="Privacy policy for Copymunk, the open-source clipboard manager for Mac, iPhone and iPad. Copymunk collects no data.">
<meta name="theme-color" content="#F4F2ED">
<meta property="og:title" content="Copymunk Privacy Policy">
<meta property="og:description" content="Copymunk does not collect, transmit, or sell any data.">
<meta property="og:image" content="../support/icon.png">
<link rel="icon" href="../support/icon.png" type="image/png">
<link rel="canonical" href="https://copymunk.com/privacy/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: light;
    --bg: #F4F2ED;
    --panel: #EFECE5;
    --card: #FCFBF8;
    --card-hover: #EBE8E1;
    --line: rgba(22, 22, 26, 0.12);
    --fg: #16161A;
    --muted: #6E6E76;
    --dim: #63636B;
    --ink: #16161A;
    --cream: #F4F2ED;
    --link: #0068D6;
    --link-hover: #005ABD;
    --radius: 12px;
    --shadow: 0 8px 28px rgba(52, 49, 61, 0.08);
    --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Hiragino Sans GB", "Helvetica Neue", Helvetica, Arial, sans-serif;
    --display: "Space Grotesk", var(--sans);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font: 16px/1.65 var(--sans);
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }
  a { color: var(--link); text-underline-offset: 0.18em; overflow-wrap: anywhere; }
  a:hover { color: var(--link-hover); }
  a:focus-visible, button:focus-visible { outline: 2px solid var(--link); outline-offset: 3px; }
  [hidden] { display: none !important; }

  .hero {
    position: relative;
    isolation: isolate;
    padding: 56px 20px 8px;
    text-align: center;
    overflow: hidden;
  }
  .hero::before {
    content: "";
    position: absolute;
    inset: -20% -10%;
    z-index: -1;
    pointer-events: none;
    background:
      radial-gradient(42% 55% at 16% 22%, rgba(255, 45, 85, 0.10), transparent 70%),
      radial-gradient(40% 55% at 86% 34%, rgba(10, 132, 255, 0.09), transparent 70%);
    filter: blur(24px);
  }
  .icon {
    width: 88px; height: 88px;
    display: block; margin: 0 auto 18px;
    border-radius: 20px;
    filter: drop-shadow(-4px -3px 18px rgba(255, 45, 85, 0.14)) drop-shadow(4px 3px 18px rgba(10, 132, 255, 0.14));
  }
  .wordmark {
    font: 700 clamp(40px, 7vw, 60px)/1 var(--display);
    letter-spacing: -0.045em;
    color: var(--ink);
    margin: 0;
    text-shadow: -0.018em -0.014em 0 rgba(255, 45, 85, 0.65), 0.018em 0.014em 0 rgba(10, 132, 255, 0.65);
  }
  .wordmark a { color: inherit; text-decoration: none; }
  .wordmark small {
    display: block;
    margin-top: 12px;
    font: 600 clamp(20px, 3vw, 26px)/1.2 var(--sans);
    letter-spacing: 0;
    text-shadow: none;
    color: var(--fg);
  }
  .tagline { margin: 12px auto 0; max-width: 560px; color: var(--dim); font-size: 15px; }
  .lang {
    display: inline-flex;
    gap: 4px;
    margin-top: 22px;
    padding: 4px;
    border-radius: 999px;
    background: var(--bg);
    border: 1px solid var(--line);
  }
  .lang button {
    appearance: none;
    border: 0;
    background: transparent;
    color: var(--muted);
    font: 600 13px/1 var(--sans);
    padding: 8px 14px;
    border-radius: 999px;
    cursor: pointer;
    transition: background .15s, color .15s;
  }
  .lang button:hover { background: var(--card-hover); color: var(--fg); }
  .lang button[aria-pressed="true"] { background: var(--card); color: var(--ink); box-shadow: 0 1px 4px rgba(52, 49, 61, 0.10); }

  main { max-width: 760px; margin: 0 auto; padding: 32px 20px 64px; }
  .card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin: 0 0 22px;
    overflow: hidden;
  }
  .card-head {
    display: flex; align-items: center; gap: 10px;
    margin: 0;
    padding: 12px 18px;
    font-weight: 700; font-size: 15px; line-height: 1.4;
    color: var(--ink);
    border-bottom: 1px solid var(--line);
  }
  .card-head .dot {
    width: 18px; height: 18px; border-radius: 6px; flex: none;
    background: var(--card);
    display: grid; place-items: center;
  }
  .card-head .dot::before {
    content: ""; width: 9px; height: 2px; border-radius: 1px;
    background: var(--ink);
    box-shadow: 0 -3px 0 var(--ink), 0 3px 0 var(--ink);
  }
  .card-head.red { background: linear-gradient(180deg, #FBE7E9, #F9DEE3); }
  .card-head.blue { background: linear-gradient(180deg, #EAF2FA, #DFEAF5); }
  .card-head.cream { background: linear-gradient(180deg, var(--cream), var(--panel)); }
  .card-body { padding: 18px 20px 20px; }
  .card-body p { margin: 0 0 12px; }
  .card-body ul { padding-left: 22px; margin: 0 0 12px; }
  .card-body ul ul { margin: 6px 0 0; }
  .card-body li { margin: 8px 0; }
  .card-body > :last-child { margin-bottom: 0; }

  footer {
    max-width: 760px; margin: 0 auto; padding: 0 20px 48px;
    color: var(--dim); font-size: 13px;
    display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center;
  }

  @media (max-width: 640px) {
    .card-body { padding: 16px; }
  }
</style>
</head>
<body>

<header class="hero">
  <a href="../support/"><img class="icon" src="../support/icon.png" width="88" height="88" alt="Copymunk app icon"></a>
  <h1 class="wordmark"><a href="../support/">Copymunk</a>
    <small data-lang="en">Privacy Policy</small>
    <small data-lang="zh">隐私政策</small>
  </h1>
  <p class="tagline" data-lang="en">Effective date: {{DATE}}</p>
  <p class="tagline" data-lang="zh">生效日期：{{DATE}}</p>
  <div class="lang" role="group" aria-label="Language / 语言">
    <button type="button" data-set-lang="en" aria-pressed="true">English</button>
    <button type="button" data-set-lang="zh" aria-pressed="false">中文</button>
  </div>
</header>

<main>
{{EN}}
{{ZH}}
</main>

<footer>
  <span>© 2026 Copymunk Contributors · GNU GPLv3</span>
  <a href="../support/" data-lang="en">Support</a>
  <a href="../support/" data-lang="zh">支持与帮助</a>
  <a href="https://github.com/VibeMage/copymunk/blob/main/PRIVACY.md" data-lang="en">Source of this policy</a>
  <a href="https://github.com/VibeMage/copymunk/blob/main/PRIVACY.md" data-lang="zh">本政策原文</a>
</footer>

<script>
(function () {
  var buttons = document.querySelectorAll('[data-set-lang]');
  function apply(lang) {
    document.documentElement.lang = lang === 'zh' ? 'zh-Hans' : 'en';
    document.querySelectorAll('[data-lang]').forEach(function (el) {
      el.hidden = el.getAttribute('data-lang') !== lang;
    });
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-set-lang') === lang ? 'true' : 'false');
    });
    try { localStorage.setItem('copyo-lang', lang); } catch (e) {}
  }
  var initial = 'en';
  var hash = location.hash.replace('#', '');
  if (hash === 'zh' || hash === 'en') {
    initial = hash;
  } else {
    var saved = null;
    try { saved = localStorage.getItem('copyo-lang'); } catch (e) {}
    if (saved === 'zh' || saved === 'en') initial = saved;
    else if ((navigator.language || '').toLowerCase().indexOf('zh') === 0) initial = 'zh';
  }
  apply(initial);
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      apply(b.getAttribute('data-set-lang'));
      history.replaceState(null, '', '#' + b.getAttribute('data-set-lang'));
    });
  });
})();
</script>
</body>
</html>
"""


def main():
    page = build()
    if "--check" in sys.argv[1:]:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != page:
            print(f"{OUTPUT.relative_to(REPO)} 与 PRIVACY.md 不一致，请运行 python3 scripts/make-privacy-page.py", file=sys.stderr)
            sys.exit(1)
        print("隐私政策网页与 PRIVACY.md 一致")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"已生成 {OUTPUT.relative_to(REPO)}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        sys.exit(str(error))
