# How to change this site yourself

## New blog post
1. Copy `blog/2026-09-22-why-this-notebook.html` to `blog/YYYY-MM-DD-slug.html`.
2. Edit the `<title>`, `<h1>`, byline date, and body text.
3. Keep the KaTeX `<head>` block + closing `<script>` if you use math ($..$ inline, $$..$$ display). Delete both if not.
4. Add a `<li>` to `blog/index.html` (top of the list = newest).

## Change the theme
Everything is CSS variables at the top of `style.css` (`:root { ... }`):
```
--bg          background
--ink         main text
--ink-soft    secondary/muted text
--rule        stronger borders/rules
--rule-soft   subtle borders (h2 underline, tables)
--link / --link-visited
--code-bg     code blocks, table headers, callouts
```
Change the hex values, save, refresh. That's the whole theme system. To go back to light mode, swap in light-ish values (light bg, dark ink) — see git history for the original light palette if you want it back exactly.

## Add a short video
```html
<video src="assets/clip.mp4" controls width="100%"></video>
```
Or embed YouTube/Vimeo with their `<iframe>` embed code — drop it straight into a post's `<main>`.

## Add a simulation / interactive widget
Plain HTML/JS, no framework needed:
```html
<canvas id="sim" width="600" height="400" style="border:1px solid var(--rule);"></canvas>
<script>
  const ctx = document.getElementById('sim').getContext('2d');
  // your simulation loop here
</script>
```
For anything more involved (p5.js, Three.js, plotting libraries), load the library from a CDN with a `<script src="...">` tag in the post's `<head>`, same pattern as the KaTeX block.

## General rule
Every page repeats the same `site-header` / `nav` / `site-footer` markup by hand (no templating). Copy an existing page's structure for a new one, and keep the CSS classes (`page`, `entry-list`, `tag-list`, etc.) so it inherits the site's styling automatically.
