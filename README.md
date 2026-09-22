# atharvbhalerao.dev (working title)

A personal site: professional background, projects, and a blog of
autodidactic explorations (physics, embedded systems, machine learning).
Styled after old academic personal pages like
[braeunig.us](http://braeunig.us) &mdash; plain serif text, thin rules,
no chrome.

## Stack

There isn't one. This is hand-written HTML and a single CSS file:

```
index.html         Home / about
experience.html    Professional experience
projects.html      Project write-ups
blog/
  index.html        Post index (edit this to list a new post)
  YYYY-MM-DD-*.html One file per post
style.css           The only stylesheet, shared by every page
assets/             Images, résumé PDF
```

No framework, no build step, no backend, no npm/pip install. A browser
can open `index.html` directly and the whole site works.

Math is the one modern concession: pages that need equations load
[KaTeX](https://katex.org/) from a CDN and auto-render `$...$` (inline)
and `$$...$$` (display) delimiters client-side. See the `<head>` and the
closing `<script>` block in
`blog/2026-09-22-why-this-notebook.html` for the exact snippet to copy.

## Editing locally

Just open the HTML files in a browser. If you want the same
`/api`-free but proper HTTP behavior a real host would give you (useful
for testing relative links), serve the folder instead of opening files
directly:

```powershell
python -m http.server 8000
```

Then visit http://localhost:8000/.

## Adding a blog post

1. Copy `blog/2026-09-22-why-this-notebook.html` to
   `blog/YYYY-MM-DD-slug.html`.
2. Replace the title, byline, and body. Keep the KaTeX `<head>` block
   if the post has math; delete it if not.
3. Add a matching `<li>` entry to `blog/index.html`, above the previous
   newest post.

That's the entire publishing workflow.

## Adding a page

Copy an existing top-level page (e.g. `projects.html`), keep the
`site-header`/`site-nav`/`site-footer` blocks as-is so the nav stays
consistent, replace the `<main>` content, and add a link to it in the
`nav.site-nav` block of every page (including itself, marked with
`aria-current="page"`).

## Deploying

Static files only &mdash; push to GitHub Pages (or any static host) and
point it at the repo root. No server process to run or keep alive.
