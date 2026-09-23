#!/usr/bin/env python3
"""
Convert a Markdown post (with front matter) into a blog HTML page that
matches this site's hand-written template, and add it to blog/index.html.

Usage:
    python3 tools/build_post.py posts/why-this-notebook.md

Markdown source format (posts/*.md):

    ---
    title: Why this notebook
    date: 2026-09-22
    tags: meta, physics
    excerpt: One or two sentences shown on the blog index.
    ---

    Body in Markdown. Supports: # and ## and ### headers (mapped to
    h1/h2/h3, though the post title itself becomes the page's h1 so
    start the body at ##), paragraphs, **bold**, *italic*, `inline code`,
    [links](url), fenced code blocks (```lang ... ```), images on their
    own line (![alt](src) or ![alt](src "caption")), rendered as a
    <figure> with optional <figcaption>, and LaTeX math left untouched
    for KaTeX: $inline$ and $$display$$.

Re-running on the same .md file overwrites the generated .html and
updates (rather than duplicates) its entry in blog/index.html.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"
INDEX_PATH = BLOG_DIR / "index.html"


def parse_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        sys.exit("error: markdown file must start with a '---' front matter block")
    raw, body = m.group(1), m.group(2)
    meta = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip()
    for required in ("title", "date"):
        if required not in meta:
            sys.exit(f"error: front matter missing required field '{required}'")
    meta.setdefault("tags", "")
    meta.setdefault("excerpt", "")
    return meta, body


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug


# --- inline markdown -> html (applied to text outside code/math spans) ---

def render_inline(text):
    # protect inline math $...$ and inline code `...` from further escaping/markup
    placeholders = []

    def stash(s):
        placeholders.append(s)
        return f"\x00{len(placeholders) - 1}\x00"

    # stash inline code first, then inline math
    text = re.sub(r"`([^`]+)`", lambda m: stash(
        "<code>" + html.escape(m.group(1)) + "</code>"), text)
    text = re.sub(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)",
                   lambda m: stash("$" + m.group(1) + "$"), text)

    text = html.escape(text, quote=False)

    # inline images ![alt](src) (block-level standalone images are handled
    # separately in render_body before this function ever sees the line)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
                   lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    # links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                   lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    # bold then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    def unstash(m):
        return placeholders[int(m.group(1))]

    text = re.sub(r"\x00(\d+)\x00", unstash, text)
    return text


def render_body(body):
    lines = body.splitlines()
    out = []
    i = 0
    para_buf = []

    def flush_para():
        if para_buf:
            joined = " ".join(l.strip() for l in para_buf).strip()
            if joined:
                out.append(f"  <p>\n    {render_inline(joined)}\n  </p>\n")
            para_buf.clear()

    while i < len(lines):
        line = lines[i]

        # fenced code block
        fence = re.match(r"^```(\w*)\s*$", line)
        if fence:
            flush_para()
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code = html.escape("\n".join(code_lines))
            out.append(f"  <pre><code>{code}</code></pre>\n")
            continue

        # display math $$ ... $$ (own block, left untouched for KaTeX)
        if line.strip() == "$$":
            flush_para()
            math_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                math_lines.append(lines[i])
                i += 1
            i += 1
            out.append("  <p>\n    $$\n" + "\n".join(math_lines) + "\n    $$\n  </p>\n")
            continue

        # standalone image on its own line -> <figure> with optional caption
        img = re.match(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$', line)
        if img:
            flush_para()
            alt, src, caption = img.group(1), img.group(2), img.group(3)
            out.append(f'  <figure>\n    <img src="{src}" alt="{html.escape(alt, quote=False)}">\n')
            if caption:
                out.append(f'    <figcaption>{render_inline(caption)}</figcaption>\n')
            out.append("  </figure>\n")
            i += 1
            continue

        # headers
        h = re.match(r"^(#{2,3})\s+(.*)$", line)
        if h:
            flush_para()
            level = len(h.group(1))
            out.append(f"  <h{level}>{render_inline(h.group(2).strip())}</h{level}>\n")
            i += 1
            continue

        if line.strip() == "":
            flush_para()
            i += 1
            continue

        para_buf.append(line)
        i += 1

    flush_para()
    return "\n".join(out)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &mdash; Atharv Bhalerao</title>
<link rel="stylesheet" href="../style.css">

<!-- KaTeX: renders $...$ and $$...$$ in the page body. Loaded from a
     CDN, no build step. Delete this block on pages that have no math. -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
</head>
<body>

<header class="site-header">
  <p class="site-title"><a href="../index.html">Atharv Bhalerao</a></p>
  <p class="site-tagline">physics &middot; embedded systems &middot; machine learning</p>
  <nav class="site-nav">
    <a href="../index.html">Home</a><span class="sep">|</span><a href="../experience.html">Experience</a><span class="sep">|</span><a href="../projects.html">Projects</a><span class="sep">|</span><a href="index.html" aria-current="page">Blog</a>
  </nav>
</header>

<main class="page">

  <p><a href="index.html">&larr; back to blog</a></p>

  <h1>{title}</h1>
  <p class="byline">{date} &middot; <span class="tag-list">{tag_spans}</span></p>

{body}
</main>

<footer class="site-footer">
  <p>&copy; {year} Atharv Bhalerao.</p>
</footer>

<script>
  window.addEventListener("DOMContentLoaded", function () {{
    if (window.renderMathInElement) {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{ left: "$$", right: "$$", display: true }},
          {{ left: "$", right: "$", display: false }}
        ]
      }});
    }}
  }});
</script>

</body>
</html>
"""


def tag_list(tags_csv):
    tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags), tags


def build_page(meta, body_html):
    tag_spans, _ = tag_list(meta["tags"])
    year = meta["date"].split("-")[0]
    return PAGE_TEMPLATE.format(
        title=html.escape(meta["title"], quote=False),
        date=meta["date"],
        tag_spans=tag_spans,
        body=body_html,
        year=year,
    )


ENTRY_TEMPLATE = """    <li>
      <span class="entry-date">{date}</span>
      &mdash;
      <span class="entry-title"><a href="{filename}">{title}</a></span>
      <p class="entry-excerpt">
        {excerpt}
      </p>
      <p class="tag-list">{tag_spans}</p>
    </li>"""


def update_index(meta, filename):
    index_html = INDEX_PATH.read_text(encoding="utf-8")
    tag_spans, _ = tag_list(meta["tags"])
    entry = ENTRY_TEMPLATE.format(
        date=meta["date"],
        filename=filename,
        title=html.escape(meta["title"], quote=False),
        excerpt=html.escape(meta["excerpt"], quote=False),
        tag_spans=tag_spans,
    )

    # remove any existing entry pointing at this filename (re-run = update)
    entry_re = re.compile(
        r'[ \t]*<li>\s*<span class="entry-date">.*?</li>\n?',
        re.S,
    )
    existing_entries = []
    for m in entry_re.finditer(index_html):
        if f'href="{filename}"' not in m.group(0):
            existing_entries.append(m.group(0).rstrip("\n"))

    all_entries = existing_entries + [entry]

    def entry_date(e):
        dm = re.search(r'entry-date">([\d-]+)<', e)
        return dm.group(1) if dm else ""

    all_entries.sort(key=entry_date, reverse=True)

    new_list_inner = "\n".join(all_entries)
    new_ul = f'<ul class="entry-list">\n{new_list_inner}\n  </ul>'

    index_html = re.sub(
        r'<ul class="entry-list">.*?</ul>', new_ul, index_html, flags=re.S
    )
    INDEX_PATH.write_text(index_html, encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_post.py posts/<name>.md")
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        sys.exit(f"error: {md_path} not found")

    text = md_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)

    filename = f"{meta['date']}-{slugify(meta['title'])}.html"
    body_html = render_body(body)
    page = build_page(meta, body_html)

    BLOG_DIR.mkdir(exist_ok=True)
    (BLOG_DIR / filename).write_text(page, encoding="utf-8")
    update_index(meta, filename)

    print(f"wrote blog/{filename}")
    print(f"updated blog/index.html")


if __name__ == "__main__":
    main()
