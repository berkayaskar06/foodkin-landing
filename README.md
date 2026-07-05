# FoodKin Landing

Pre-launch waitlist page for FoodKin — the kitchen assistant that knows what's in your home.

- Static site served via GitHub Pages; pages are generated, not hand-edited
- 6 locales: `tr` (root, x-default) + `en/ es/ zh/ ar/ pt/` — Arabic is RTL
- Browser-language auto-redirect on the root page; explicit switcher choice wins
- SEO: per-page canonical + hreflang alternates, localized title/meta, MobileApplication JSON-LD, `sitemap.xml`, `robots.txt`
- Waitlist signups go to Supabase (`waitlist_signups`, insert-only anon policy)
- Channel attribution via `?utm_source=` (used in TikTok/Instagram bio links)

## Editing content

Never edit `index.html` or `<lang>/index.html` directly — they are build output.

1. Edit copy in `locales.json` (all languages) and/or markup in `template.html`
2. Run `python3 build.py`
3. Commit everything and push

Live: https://berkayaskar06.github.io/foodkin-landing/
