#!/usr/bin/env python3
"""
Build-log generator for this site. Plain Python 3, no dependencies.

    python tools/buildlog.py new ["Entry title"]   start today's entry
    python tools/buildlog.py build                 regenerate the whole site's log

Sources (you edit these):
    src/project.md             goal, milestone checklist, results table
    src/entries/YYYY-MM-DD.md  one build-log entry per day
    src/blog/YYYY-MM-DD-slug.md  essays that aren't build-log entries (the Blog section)

Generated (don't edit, rebuilt every run):
    log/index.html             project header + every entry, newest first
    log/YYYY-MM-DD.html        one page per entry
    blog/index.html            blog index
    blog/YYYY-MM-DD-slug.html  one page per blog post
    index.html                 only the block between the LATEST-LOG markers

Entry front matter:

    ---
    title: Short descriptive title
    date: 2026-10-01
    tags: risc-v, verilog
    summary: One sentence for the log index and the home-page window.
    draft: true            <- remove this line to publish
    ---

Markdown supported: ##..###### headers (the title is the page's h1, so start
at ##), paragraphs, **bold**, *italic*, `code`, [links](url), fenced code
blocks, bullet / numbered lists, "- [ ]" / "- [x]" checklists, | tables |,
> blockquotes, --- rules, images on their own line (![alt](img/x.png "caption")),
and KaTeX math ($inline$, $$ on its own line for display).
Image paths are relative to the generated page, so put files in log/img/ and
write ![alt](img/name.png).
"""
import datetime
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
ENTRIES_DIR = SRC / "entries"
BLOG_SRC = SRC / "blog"
BLOG_DIR = ROOT / "blog"
PROJECT_SRC = SRC / "project.md"
LOG_DIR = ROOT / "log"
HOME = ROOT / "index.html"

ENTRY_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}.*\.html$")
HOME_START = "<!-- LATEST-LOG:START"
HOME_END = "<!-- LATEST-LOG:END -->"

ENTRY_TEMPLATE = """---
title: {title}
date: {date}
tags:
summary:
draft: true
---

## Goal
What I was trying to get working today.

## What happened
What I tried, what broke, what fixed it.

## Evidence
A waveform, test output, a resource report, a number. Put images in log/img/ and write ![alt](img/name.png "caption").

## Next
The next thing I'll do.
"""


# ----------------------------- front matter -----------------------------

def parse_front_matter(text, source):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        sys.exit(f"error: {source} must start with a '---' front matter block")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
    return meta, m.group(2)


def is_draft(meta):
    return meta.get("draft", "").lower() in ("true", "yes", "1")


def split_tags(csv):
    return [t.strip() for t in csv.split(",") if t.strip()]


def tag_spans(csv):
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in split_tags(csv))


# --------------------------- markdown -> html ---------------------------

def render_inline(text):
    stash_list = []

    def stash(s):
        stash_list.append(s)
        return f"\x00{len(stash_list) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: stash("<code>" + html.escape(m.group(1)) + "</code>"), text)
    text = re.sub(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)", lambda m: stash("$" + m.group(1) + "$"), text)
    text = html.escape(text, quote=False)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
                  lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash_list[int(m.group(1))], text)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render_table(rows):
    header, body = rows[0], rows[2:]
    out = ["  <table>\n    <thead><tr>"]
    out += [f"<th>{render_inline(c)}</th>" for c in header]
    out.append("</tr></thead>\n    <tbody>\n")
    for r in body:
        out.append("      <tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in r) + "</tr>\n")
    out.append("    </tbody>\n  </table>\n")
    return "".join(out)


def render_body(body):
    lines = body.splitlines()
    out, para = [], []
    i = 0

    def flush():
        if para:
            joined = " ".join(l.strip() for l in para).strip()
            if joined:
                out.append(f"  <p>\n    {render_inline(joined)}\n  </p>\n")
            para.clear()

    while i < len(lines):
        line = lines[i]

        if re.match(r"^```(\w*)\s*$", line):
            flush()
            code = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(f"  <pre><code>{html.escape(chr(10).join(code))}</code></pre>\n")
            continue

        if line.strip() == "$$":
            flush()
            math = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                math.append(lines[i])
                i += 1
            i += 1
            out.append("  <p>\n    $$\n" + "\n".join(math) + "\n    $$\n  </p>\n")
            continue

        img = re.match(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$', line)
        if img:
            flush()
            alt, src, caption = img.groups()
            if src.lower().endswith((".mp4", ".webm", ".mov")):
                out.append(f'  <figure>\n    <video src="{src}" controls width="100%"></video>\n')
            else:
                out.append(f'  <figure>\n    <img src="{src}" alt="{html.escape(alt, quote=False)}">\n')
            if caption:
                out.append(f"    <figcaption>{render_inline(caption)}</figcaption>\n")
            out.append("  </figure>\n")
            i += 1
            continue

        # table: header row, |---| separator row, then body rows
        if (line.lstrip().startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", lines[i + 1])):
            flush()
            rows = [split_row(line), split_row(lines[i + 1])]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            out.append(render_table(rows))
            continue

        if re.match(r"^[-*]\s+", line):
            flush()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(re.match(r"^[-*]\s+(.*)$", lines[i]).group(1).strip())
                i += 1
            checks = [re.match(r"^\[([ xX])\]\s+(.*)$", it) for it in items]
            if all(checks):
                out.append('  <ul class="checklist">\n')
                for c in checks:
                    cls = ' class="done"' if c.group(1) in "xX" else ""
                    out.append(f"    <li{cls}>{render_inline(c.group(2))}</li>\n")
            else:
                out.append("  <ul>\n")
                for it in items:
                    out.append(f"    <li>{render_inline(it)}</li>\n")
            out.append("  </ul>\n")
            continue

        if re.match(r"^\d+\.\s+", line):
            flush()
            out.append("  <ol>\n")
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                out.append(f"    <li>{render_inline(re.match(r'^\d+\.\s+(.*)$', lines[i]).group(1).strip())}</li>\n")
                i += 1
            out.append("  </ol>\n")
            continue

        if re.match(r"^>\s?", line):
            flush()
            quote = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                quote.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(f"  <blockquote>\n    <p>{render_inline(' '.join(quote).strip())}</p>\n  </blockquote>\n")
            continue

        h = re.match(r"^(#{2,6})\s+(.*)$", line)
        if h:
            flush()
            n = len(h.group(1))
            out.append(f"  <h{n}>{render_inline(h.group(2).strip())}</h{n}>\n")
            i += 1
            continue

        if re.match(r"^(---+|\*\*\*+)\s*$", line):
            flush()
            out.append("  <hr>\n")
            i += 1
            continue

        if line.strip() == "":
            flush()
        else:
            para.append(line)
        i += 1

    flush()
    return "\n".join(out)


def plain_text(md):
    """Strip markdown/math to plain text for previews."""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[`*$]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def first_paragraph(body):
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if b and not re.match(r"^(#|```|\||!\[|[-*]\s|\d+\.\s|>|\$\$)", b):
            return plain_text(b)
    return ""


def truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "…"


# ------------------------------ page shell ------------------------------

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@title@@ &mdash; Atharv Bhalerao</title>
<link rel="stylesheet" href="@@root@@style.css">
@@katex@@</head>
<body>

<header class="site-header">
  <p class="site-title"><a href="@@root@@index.html">Atharv Bhalerao</a></p>
  <p class="site-tagline">physics &middot; embedded systems &middot; machine learning</p>
  <nav class="site-nav">
    <a href="@@root@@index.html">Home</a><span class="sep">|</span><a href="@@root@@experience.html">Experience</a><span class="sep">|</span><a href="@@root@@projects.html">Projects</a><span class="sep">|</span><a href="@@root@@log/index.html"@@current_log@@>Build Log</a><span class="sep">|</span><a href="@@root@@blog/index.html"@@current_blog@@>Blog</a>
  </nav>
</header>

<main class="page">
@@main@@
</main>

<footer class="site-footer">
  <p>&copy; @@year@@ Atharv Bhalerao.</p>
</footer>
@@script@@
</body>
</html>
"""

KATEX_HEAD = """
<!-- KaTeX: renders $...$ and $$...$$ in the page body (loaded only when the page has math). -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
"""

KATEX_SCRIPT = """
<script>
  window.addEventListener("DOMContentLoaded", function () {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ]
      });
    }
  });
</script>
"""


def fill(template, **kw):
    for k, v in kw.items():
        template = template.replace(f"@@{k}@@", v)
    return template


def page(root, title, main, year, current="", math=False):
    """current is "log" or "blog": which nav link gets aria-current."""
    mark = ' aria-current="page"'
    return fill(PAGE, root=root, title=html.escape(title, quote=False), main=main, year=str(year),
                current_log=mark if current == "log" else "", current_blog=mark if current == "blog" else "",
                katex=KATEX_HEAD if math else "", script=KATEX_SCRIPT if math else "")


# ------------------------------- loading --------------------------------

def load_entries():
    entries, drafts = [], []
    for path in sorted(ENTRIES_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path.name)
        stem = path.stem
        date = meta.get("date") or stem[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            sys.exit(f"error: {path.name} needs a date like 2026-10-01 (front matter or filename)")
        summary = meta.get("summary") or truncate(first_paragraph(body), 220)
        entry = {
            "stem": stem, "date": date, "meta": meta, "body": body, "summary": summary,
            "title": meta.get("title") or f"Log {date}", "tags": meta.get("tags", ""),
        }
        (drafts if is_draft(meta) else entries).append(entry)
    entries.sort(key=lambda e: (e["date"], e["stem"]))
    for n, e in enumerate(entries, 1):
        e["n"] = n
    return entries, drafts


# ----------------------------- page builders ----------------------------

def entry_page(e, prev, nxt):
    body_html = render_body(e["body"])
    tags = tag_spans(e["tags"])
    byline = f'{e["date"]} &middot; Log #{e["n"]}'
    if tags:
        byline += f' &middot; <span class="tag-list">{tags}</span>'
    byline += (f' &middot; <img class="view-badge" '
               f'src="https://visitor-badge.laobi.icu/badge?page_id=imathrock.log.{e["stem"]}" alt="view count">')
    nav = []
    if prev:
        nav.append(f'<a href="{prev["stem"]}.html">&larr; Log #{prev["n"]}: {html.escape(prev["title"], quote=False)}</a>')
    if nxt:
        nav.append(f'<a href="{nxt["stem"]}.html">Log #{nxt["n"]}: {html.escape(nxt["title"], quote=False)} &rarr;</a>')
    sep = ' <span class="sep">|</span> '
    pager = f'  <p class="pager">{sep.join(nav)}</p>\n' if nav else ""
    main = (f'  <p><a href="index.html">&larr; back to build log</a></p>\n\n'
            f'  <h1>{html.escape(e["title"], quote=False)}</h1>\n'
            f'  <p class="byline">{byline}</p>\n\n{body_html}\n{pager}')
    return page("../", e["title"], main, e["date"][:4], current="log", math="$" in e["body"])


def project_block():
    if not PROJECT_SRC.exists():
        return "", "Build Log", ""
    meta, body = parse_front_matter(PROJECT_SRC.read_text(encoding="utf-8"), PROJECT_SRC.name)
    done = len(re.findall(r"^[-*]\s+\[[xX]\]", body, re.M))
    total = done + len(re.findall(r"^[-*]\s+\[ \]", body, re.M))
    progress = f'  <p class="progress">Milestones: {done} of {total} done</p>\n\n' if total else ""
    return progress + render_body(body), meta.get("title", "Build Log"), meta.get("summary", "")


def index_page(entries):
    project_html, project_title, summary = project_block()
    items = []
    for e in reversed(entries):
        tags = tag_spans(e["tags"])
        items.append(
            f'    <li>\n'
            f'      <span class="entry-date">{e["date"]}</span>\n'
            f'      &mdash;\n'
            f'      <span class="entry-title"><a href="{e["stem"]}.html">{html.escape(e["title"], quote=False)}</a></span>'
            f' <span class="entry-num">Log #{e["n"]}</span>\n'
            + (f'      <p class="entry-excerpt">{html.escape(e["summary"], quote=False)}</p>\n' if e["summary"] else "")
            + (f'      <p class="tag-list">{tags}</p>\n' if tags else "")
            + "    </li>")
    listing = "\n".join(items) if items else "    <li>No entries yet.</li>"
    intro = f"  <p>{html.escape(summary, quote=False)}</p>\n" if summary else ""
    main = (f'  <h1>{html.escape(project_title, quote=False)}</h1>\n{intro}\n{project_html}\n'
            f'  <h2>Entries</h2>\n'
            f'  <p>Newest first. One short entry per working session: goal, what happened, evidence, next.</p>\n\n'
            f'  <ul class="entry-list">\n{listing}\n  </ul>')
    year = entries[-1]["date"][:4] if entries else str(datetime.date.today().year)
    return page("../", "Build Log", main, year, current="log")


def home_window(entries):
    if not entries:
        return f"{HOME_START} -- generated by tools/buildlog.py; do not edit by hand -->\n{HOME_END}"
    e = entries[-1]
    preview = html.escape(truncate(e["summary"], 300), quote=False)
    return (
        f"{HOME_START} -- generated by tools/buildlog.py; do not edit by hand -->\n"
        f'  <div class="log-window">\n'
        f'    <div class="log-window-bar"><span>latest.log</span><span>{e["date"]} &middot; Log #{e["n"]}</span></div>\n'
        f'    <div class="log-window-body">\n'
        f'      <p class="log-window-title"><a href="log/{e["stem"]}.html">{html.escape(e["title"], quote=False)}</a></p>\n'
        f'      <p>{preview}</p>\n'
        f'      <p class="log-window-links"><a href="log/{e["stem"]}.html">Read the entry &rarr;</a> <span class="sep">|</span> <a href="log/index.html">All entries</a></p>\n'
        f'    </div>\n'
        f'  </div>\n'
        f"  {HOME_END}")


def update_home(entries):
    text = HOME.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(HOME_START) + r".*?" + re.escape(HOME_END), re.S)
    if not pattern.search(text):
        sys.exit(f"error: index.html is missing the {HOME_START} ... {HOME_END} markers")
    HOME.write_text(pattern.sub(lambda m: home_window(entries), text, count=1), encoding="utf-8")


def build_blog():
    posts = []
    for path in sorted(BLOG_SRC.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path.name)
        if is_draft(meta):
            continue
        for required in ("title", "date"):
            if required not in meta:
                sys.exit(f"error: {path.name} front matter missing '{required}'")
        posts.append({"stem": path.stem, "meta": meta, "body": body, "title": meta["title"], "date": meta["date"],
                      "tags": meta.get("tags", ""),
                      "summary": meta.get("summary") or meta.get("excerpt") or truncate(first_paragraph(body), 220)})
    posts.sort(key=lambda p: (p["date"], p["stem"]), reverse=True)

    BLOG_DIR.mkdir(exist_ok=True)
    wanted = {f"{p['stem']}.html" for p in posts} | {"index.html"}
    for old in BLOG_DIR.glob("*.html"):
        if old.name not in wanted:
            old.unlink()

    items = []
    for p in posts:
        tags = tag_spans(p["tags"])
        byline = p["date"]
        if tags:
            byline += f' &middot; <span class="tag-list">{tags}</span>'
        byline += (f' &middot; <img class="view-badge" '
                   f'src="https://visitor-badge.laobi.icu/badge?page_id=imathrock.blog.{p["stem"]}" alt="view count">')
        main = (f'  <p><a href="index.html">&larr; back to blog</a></p>\n\n'
                f'  <h1>{html.escape(p["title"], quote=False)}</h1>\n'
                f'  <p class="byline">{byline}</p>\n\n{render_body(p["body"])}')
        (BLOG_DIR / f"{p['stem']}.html").write_text(
            page("../", p["title"], main, p["date"][:4], current="blog", math="$" in p["body"]), encoding="utf-8")
        items.append(
            f'    <li>\n'
            f'      <span class="entry-date">{p["date"]}</span>\n'
            f'      &mdash;\n'
            f'      <span class="entry-title"><a href="{p["stem"]}.html">{html.escape(p["title"], quote=False)}</a></span>\n'
            + (f'      <p class="entry-excerpt">{html.escape(p["summary"], quote=False)}</p>\n' if p["summary"] else "")
            + (f'      <p class="tag-list">{tags}</p>\n' if tags else "")
            + "    </li>")
    listing = "\n".join(items) if items else "    <li>No posts yet.</li>"
    main = ('  <h1>Blog</h1>\n'
            '  <p>Essays and write-ups that are not part of the day-to-day <a href="../log/index.html">build log</a>.</p>\n\n'
            f'  <ul class="entry-list">\n{listing}\n  </ul>')
    year = posts[0]["date"][:4] if posts else str(datetime.date.today().year)
    (BLOG_DIR / "index.html").write_text(page("../", "Blog", main, year, current="blog"), encoding="utf-8")
    return len(posts)


# -------------------------------- commands -------------------------------

def cmd_build():
    entries, drafts = load_entries()
    LOG_DIR.mkdir(exist_ok=True)

    wanted = {f"{e['stem']}.html" for e in entries}
    for old in LOG_DIR.glob("*.html"):
        if ENTRY_NAME_RE.match(old.name) and old.name not in wanted:
            old.unlink()  # entry was deleted or turned back into a draft

    for i, e in enumerate(entries):
        prev = entries[i - 1] if i > 0 else None
        nxt = entries[i + 1] if i + 1 < len(entries) else None
        (LOG_DIR / f"{e['stem']}.html").write_text(entry_page(e, prev, nxt), encoding="utf-8")
    (LOG_DIR / "index.html").write_text(index_page(entries), encoding="utf-8")
    update_home(entries)
    posts = build_blog()

    print(f"built {len(entries)} entries, log/index.html, home-page window, {posts} blog post(s)")
    if entries:
        print(f"latest: {entries[-1]['date']}  {entries[-1]['title']}")
    for d in drafts:
        print(f"skipped draft: src/entries/{d['stem']}.md (remove 'draft: true' to publish)")


def cmd_new(title):
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = ENTRIES_DIR / f"{today}.md"
    suffix = ord("b")
    while path.exists():
        if suffix > ord("z"):
            sys.exit("error: too many entries for one day")
        path = ENTRIES_DIR / f"{today}-{chr(suffix)}.md"
        suffix += 1
    path.write_text(ENTRY_TEMPLATE.format(title=title, date=today), encoding="utf-8")
    print(f"created {path.relative_to(ROOT)}")
    print("edit it, delete the 'draft: true' line, then run: python tools/buildlog.py build")


def main():
    args = sys.argv[1:]
    if args and args[0] == "build" and len(args) == 1:
        cmd_build()
    elif args and args[0] == "new":
        cmd_new(" ".join(args[1:]).strip())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
