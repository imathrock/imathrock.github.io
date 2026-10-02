# How to change this site yourself

## Daily build-log workflow
```powershell
python tools/buildlog.py new "Short title"   # creates src/entries/<today>.md
# edit the file, then delete the "draft: true" line to publish it
python tools/buildlog.py build               # regenerates log/, the home-page window, pages
git add -A; git commit -m "log: <today>"; git push
```
Preview locally with `python -m http.server 8000` and open http://localhost:8000/.

An entry is short: **Goal / What happened / Evidence / Next**. Evidence is a waveform,
test output, a resource report, a number. Put images in `log/img/` and reference them as
`![alt](img/name.png "caption")` (paths are relative to the generated page).

Entry front matter:
```
---
title: Short descriptive title
date: 2026-10-01
tags: risc-v, verilog
summary: One sentence shown on the log index and the home-page window.
draft: true        <- remove to publish; build skips drafts
---
```
If `summary` is left out, the first paragraph is used. Two entries on one day: `new` makes
`<today>-b.md`. Re-running `build` is always safe; it rebuilds everything from `src/`.

## What you edit vs. what is generated
| Edit these | Generated (don't edit) |
|---|---|
| `src/entries/*.md` | `log/YYYY-MM-DD.html`, `log/index.html` |
| `src/project.md` (goal, milestone checklist, results table) | the block between `LATEST-LOG` markers in `index.html` |
| `src/blog/*.md` (essays that aren't log entries) | `blog/*.html`, `blog/index.html` |

`src/project.md` is the top of the build-log page. Tick milestones with `- [x]`; the
"Milestones: N of M done" line updates itself. Fill in the results table as you measure things.

## Markdown supported
`##`-`######` headers (start at `##`, the title is the h1), paragraphs, `**bold**`, `*italic*`,
`` `code` ``, links, fenced code blocks, bullet and numbered lists, `- [ ]` / `- [x]` checklists,
`| tables |`, `> quotes`, `---` rules, images/video on their own line, and KaTeX math
(`$inline$`, `$$` on its own line for display). KaTeX loads only on pages that contain `$`.

## Change the theme
Everything is CSS variables at the top of `style.css` (`:root { ... }`). Change the hex values,
save, refresh.

## Add a blog post (not a log entry)
Same front matter as an entry, but the file goes in `src/blog/YYYY-MM-DD-slug.md` and `build`
publishes it to `blog/YYYY-MM-DD-slug.html` and lists it on `blog/index.html`.
Images: write paths relative to the generated page, e.g. `../assets/pic.png`.

## Add a hand-written page
Copy an existing top-level page and keep the `site-header` / `nav` / `site-footer` markup.
