"""Builds the Leviafan site: the HTML pages from the texts in content/ (Markdown).

    python build.py

Writes index.html, the legal pages (English at the root, French under fr/), app-ads.txt and
CNAME. Commit the result: GitHub Pages serves the files as they are.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"

# Shown on the published pages only (the texts in content/ keep a placeholder).
POSTAL_ADDRESS = "[POSTAL ADDRESS]"
SIRET = "[SIRET]"

DOMAIN = "leviafan.fr"
CONTACT = "studio.leviafan@hotmail.com"
# AdMob account allowed to sell the ads of the studio's apps (its publisher ID).
APP_ADS = "google.com, pub-8320098646485811, DIRECT, f08c47fec0942fa0\n"

PAGES = {
    # slug: (source name, English title, French title)
    "privacy-policy": ("privacy_policy", "Privacy policy", "Politique de confidentialité"),
    "terms-of-use": ("terms_of_use", "Terms of use", "Conditions d'utilisation"),
    "delete-your-data": ("data_deletion", "Delete your data", "Supprimer vos données"),
    "legal-notice": ("legal_notice", "Legal notice", "Mentions légales"),
}

TEXTS = {
    "en": {
        "lang": "en",
        "tagline": "Independent game studio",
        "game": "Snake 3D",
        "game_text": "Grow, jump and survive: a snake game in 3D, with a whole cast of characters "
                     "and levels to unlock.",
        "store": "Coming soon on Google Play",
        "contact": "Contact",
        "other": ("Français", "fr"),
    },
    "fr": {
        "lang": "fr",
        "tagline": "Studio de jeux vidéo indépendant",
        "game": "Snake 3D",
        "game_text": "Grandis, saute et survis : un jeu de serpent en 3D, avec toute une galerie de "
                     "personnages et de niveaux à débloquer.",
        "store": "Bientôt sur Google Play",
        "contact": "Contact",
        "other": ("English", "en"),
    },
}


# ==================================================
# MARKDOWN (the little the legal texts use)
# ==================================================

def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<![\"=>])(https://[^\s<]+)", r'<a href="\1">\1</a>', text)
    return text


def markdown_to_html(source: str) -> tuple[str, str]:
    """(title, body): headings, paragraphs (lines kept apart), bulleted lists, bold, links."""
    title = ""
    blocks = []
    for block in re.split(r"\n\s*\n", source.strip()):
        lines = block.strip().splitlines()
        if lines[0].startswith("# "):
            title = lines[0][2:].strip()
            lines = lines[1:]
            if not lines:
                continue
        if lines[0].startswith("## "):
            blocks.append(f"<h2>{_inline(lines[0][3:].strip())}</h2>")
            lines = lines[1:]
            if not lines:
                continue
        if all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{_inline(line[2:])}</li>" for line in lines)
            blocks.append(f"<ul>{items}</ul>")
        else:
            blocks.append("<p>" + "<br>".join(_inline(line) for line in lines) + "</p>")
    return title, "\n".join(blocks)


# ==================================================
# PAGES
# ==================================================

def _prefix(lang: str) -> str:
    return "/fr/" if lang == "fr" else "/"


def _layout(lang: str, title: str, body: str, other_path: str) -> str:
    t = TEXTS[lang]
    other_name, other_lang = t["other"]
    footer_links = " · ".join(
        f'<a href="{_prefix(lang)}{slug}/">{names[2] if lang == "fr" else names[1]}</a>'
        for slug, names in PAGES.items()
    )
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header>
<a class="brand" href="{_prefix(lang)}"><img src="/assets/logo.png" alt="Leviafan" width="56" height="56"></a>
<a class="lang" href="{other_path}" hreflang="{other_lang}">{other_name}</a>
</header>
<main>
{body}
</main>
<footer>
<p>{footer_links}</p>
<p>{t['contact']} : <a href="mailto:{CONTACT}">{CONTACT}</a></p>
<p>© Leviafan</p>
</footer>
</body>
</html>
"""


def _write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def _fill(text: str) -> str:
    for placeholder in ("[POSTAL ADDRESS]", "[ADRESSE POSTALE]"):
        text = text.replace(placeholder, POSTAL_ADDRESS)
    return text.replace("[SIRET]", SIRET)


def build() -> None:
    for lang in ("en", "fr"):
        t = TEXTS[lang]
        other_lang = t["other"][1]
        home = f"""<section class="hero">
<img src="/assets/logo.png" alt="Leviafan" width="300" height="300">
<p class="tagline">{t['tagline']}</p>
</section>
<section class="game">
<h2>{t['game']}</h2>
<p>{t['game_text']}</p>
<p class="store">{t['store']}</p>
</section>"""
        _write(f"{_prefix(lang)[1:]}index.html",
               _layout(lang, "Leviafan", home, _prefix(other_lang)))
        for slug, (source, _en, _fr) in PAGES.items():
            text = (CONTENT / f"{source}_{lang}.md").read_text(encoding="utf-8")
            title, body = markdown_to_html(_fill(text))
            page = f"<article><h1>{html.escape(title)}</h1>\n{body}</article>"
            _write(f"{_prefix(lang)[1:]}{slug}/index.html",
                   _layout(lang, f"{title} – Leviafan", page,
                           f"{_prefix(other_lang)}{slug}/"))
    _write("app-ads.txt", APP_ADS)
    _write("CNAME", DOMAIN + "\n")


if __name__ == "__main__":
    build()
