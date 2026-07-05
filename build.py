#!/usr/bin/env python3
"""Generate localized static pages + sitemap from template.html and locales.json.

Usage: python3 build.py
Output: index.html (tr, root) + <lang>/index.html per locale + sitemap.xml
"""
import json
import re
import pathlib

ROOT = pathlib.Path(__file__).parent
BASE_URL = "https://berkayaskar06.github.io/foodkin-landing/"

def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


template = (ROOT / "template.html").read_text(encoding="utf-8")
locales = json.loads((ROOT / "locales.json").read_text(encoding="utf-8"))

# hreflang block is identical on every page: one alternate per locale + x-default.
hreflang_lines = []
for code, loc in locales.items():
    hreflang_lines.append(
        f'  <link rel="alternate" hreflang="{code}" href="{BASE_URL}{loc["path"]}" />'
    )
hreflang_lines.append(f'  <link rel="alternate" hreflang="x-default" href="{BASE_URL}" />')
hreflang_block = "\n".join(hreflang_lines)

locale_paths_json = json.dumps({code: loc["path"] for code, loc in locales.items()})

for code, loc in locales.items():
    switcher_lines = []
    for other_code, other in locales.items():
        current = ' aria-current="true"' if other_code == code else ""
        switcher_lines.append(
            f'        <a href="{BASE_URL}{other["path"]}" data-lang="{other_code}"'
            f'{current} hreflang="{other_code}">{other["label"]}</a>'
        )

    page = template
    # Generic: every string key in the locale maps to {{KEY_UPPER}}.
    # Keys landing inside single-quoted JS strings get escaped.
    JS_KEYS = {"msg_bad_email", "msg_ok", "msg_dup", "msg_err", "msg_conn"}
    replacements = {}
    for key, value in loc.items():
        if isinstance(value, str):
            replacements["{{" + key.upper() + "}}"] = (
                js_escape(value) if key in JS_KEYS else value
            )
    replacements.update({
        "{{LANG}}": code,
        "{{CANONICAL}}": BASE_URL + loc["path"],
        "{{HREFLANG_LINKS}}": hreflang_block,
        "{{LANG_SWITCHER}}": "\n".join(switcher_lines),
        "{{BASE_PATH}}": BASE_URL,
        "{{LOCALE_PATHS_JSON}}": locale_paths_json,
        "{{IS_ROOT}}": "yes" if loc["path"] == "" else "no",
    })
    for key, value in replacements.items():
        page = page.replace(key, value)
    leftover = re.findall(r"\{\{[A-Z0-9_]+\}\}", page)
    if leftover:
        raise SystemExit(f"{code}: unreplaced placeholders: {sorted(set(leftover))}")

    out = ROOT / loc["path"] / "index.html" if loc["path"] else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")

# sitemap.xml — every locale URL carries the full alternate set.
xhtml_links = "\n".join(
    f'    <xhtml:link rel="alternate" hreflang="{c}" href="{BASE_URL}{l["path"]}" />'
    for c, l in locales.items()
) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE_URL}" />'

url_entries = "\n".join(
    f"  <url>\n    <loc>{BASE_URL}{loc['path']}</loc>\n{xhtml_links}\n  </url>"
    for loc in locales.values()
)
sitemap = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    f"{url_entries}\n</urlset>\n"
)
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
print("wrote sitemap.xml")
