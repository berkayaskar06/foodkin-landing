#!/usr/bin/env python3
"""Generate localized static pages + sitemap from template.html and locales.json.

Usage: python3 build.py
Output: index.html (tr, root) + <lang>/index.html per locale + sitemap.xml
"""
import json
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
    replacements = {
        "{{LANG}}": code,
        "{{DIR}}": loc["dir"],
        "{{TITLE}}": loc["title"],
        "{{META_DESC}}": loc["meta_desc"],
        "{{OG_TITLE}}": loc["og_title"],
        "{{OG_DESC}}": loc["og_desc"],
        "{{OG_LOCALE}}": loc["og_locale"],
        "{{CANONICAL}}": BASE_URL + loc["path"],
        "{{HREFLANG_LINKS}}": hreflang_block,
        "{{LANG_NAV_LABEL}}": loc["lang_nav_label"],
        "{{LANG_SWITCHER}}": "\n".join(switcher_lines),
        "{{HERO_H1}}": loc["hero_h1"],
        "{{LEAD}}": loc["lead"],
        "{{SOON}}": loc["soon"],
        "{{EMAIL_PLACEHOLDER}}": loc["email_placeholder"],
        "{{EMAIL_ARIA}}": loc["email_aria"],
        "{{SUBMIT}}": loc["submit"],
        "{{NOTE}}": loc["note"],
        "{{FEATURES_H2}}": loc["features_h2"],
        "{{F1_H}}": loc["f1_h"], "{{F1_P}}": loc["f1_p"],
        "{{F2_H}}": loc["f2_h"], "{{F2_P}}": loc["f2_p"],
        "{{F3_H}}": loc["f3_h"], "{{F3_P}}": loc["f3_p"],
        "{{F4_H}}": loc["f4_h"], "{{F4_P}}": loc["f4_p"],
        "{{FOOTER_SOON}}": loc["footer_soon"],
        # These land inside single-quoted JS strings — escape backslashes and quotes.
        "{{MSG_BAD_EMAIL}}": js_escape(loc["msg_bad_email"]),
        "{{MSG_OK}}": js_escape(loc["msg_ok"]),
        "{{MSG_DUP}}": js_escape(loc["msg_dup"]),
        "{{MSG_ERR}}": js_escape(loc["msg_err"]),
        "{{MSG_CONN}}": js_escape(loc["msg_conn"]),
        "{{BASE_PATH}}": BASE_URL,
        "{{LOCALE_PATHS_JSON}}": locale_paths_json,
        "{{IS_ROOT}}": "yes" if loc["path"] == "" else "no",
    }
    for key, value in replacements.items():
        page = page.replace(key, value)

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
