# atharvbhalerao.dev (working title)

A personal site: professional background, projects, and a blog of
autodidactic explorations (physics, embedded systems, machine learning).
Styled after old academic personal pages like
[braeunig.us](http://braeunig.us) &mdash; plain serif text, thin rules,
no chrome.

## Stack

Hand-written HTML, one CSS file, and one small Python script
(`tools/buildlog.py`, no dependencies) that turns markdown build-log
entries into static pages:

```
index.html         Home / about (has an auto-updated "latest build log" window)
experience.html    Professional experience
projects.html      Project write-ups
log/               GENERATED build log (index + one page per entry), log/img/ for images
blog/              GENERATED blog (essays that aren't log entries)
src/               Markdown sources: project.md, entries/, blog/
tools/buildlog.py  python tools/buildlog.py new | build
style.css          The only stylesheet, shared by every page
assets/            Images, resume PDF
```

The generated pages are committed, so the site deploys as plain static
files. Math pages load [KaTeX](https://katex.org/) from a CDN.

## Editing locally

Just open the HTML files in a browser. If you want the same
`/api`-free but proper HTTP behavior a real host would give you (useful
for testing relative links), serve the folder instead of opening files
directly:

```powershell
python -m http.server 8000
```

Then visit http://localhost:8000/.

## Writing a build-log entry

```powershell
python tools/buildlog.py new "Short title"   # then edit src/entries/<today>.md
python tools/buildlog.py build
```

See [HOWTO.md](HOWTO.md) for the entry format and the full workflow.

## Adding a page

Copy an existing top-level page (e.g. `projects.html`), keep the
`site-header`/`site-nav`/`site-footer` blocks as-is so the nav stays
consistent, replace the `<main>` content, and add a link to it in the
`nav.site-nav` block of every page (including itself, marked with
`aria-current="page"`).

## Deploying

Static files only &mdash; push to GitHub Pages (or any static host) and
point it at the repo root. No server process to run or keep alive.
