"""Builds the Leviafan site: the HTML pages from the texts in content/ (Markdown).

    python build.py

Writes index.html, the legal pages (English at the root, every other language in its own folder:
fr/, es/, pt-br/…), app-ads.txt and CNAME. Commit the result: GitHub Pages serves the files as
they are.
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"

# Shown on the published pages only (the texts in content/ keep a placeholder).
POSTAL_ADDRESS = "36 bis Rue Demolombe\n14000 Caen, France"
SIRET = "131 417 099 00010"

DOMAIN = "leviafan.fr"
CONTACT = "studio.leviafan@hotmail.com"
# AdMob account allowed to sell the ads of the studio's apps (its publisher ID).
APP_ADS = "google.com, pub-8320098646485811, DIRECT, f08c47fec0942fa0\n"

# slug: (source name in content/, languages it exists in; None = all of them).
# The legal notice answers a French law: in French, and in English as a courtesy.
PAGES = {
    "privacy-policy": ("privacy_policy", None),
    "terms-of-use": ("terms_of_use", None),
    "delete-your-data": ("data_deletion", None),
    "legal-notice": ("legal_notice", ("en", "fr")),
}

# The game on Google Play; "hl" picks the language of the store page.
STORE_URL = "https://play.google.com/store/apps/details?id=com.leviafan.snake3d&hl={hl}"
# Google's official "Get it on Google Play" badge, in each language (images served by Google).
BADGE_URL = "https://play.google.com/intl/{locale}/badges/static/images/badges/{name}_badge_web_generic.png"

# Key = suffix of the files in content/ (the game's Legal/ names). In the order of the
# language links of the header; each language is named in itself.
LANGUAGES = {
    "en": {
        "folder": "",
        "html_lang": "en",
        "name": "English",
        "tagline": "Independent game studio",
        "game_text": "Grow, jump and survive: a snake game in 3D, with a whole cast of characters "
                     "and levels to unlock.",
        "badge_alt": "Get it on Google Play",
        "badge": "en_us/en",
        "store_hl": "en",
        "contact": "Contact:",
        "titles": ("Privacy policy", "Terms of use", "Delete your data", "Legal notice"),
    },
    "fr": {
        "folder": "fr",
        "html_lang": "fr",
        "name": "Français",
        "tagline": "Studio de jeux vidéo indépendant",
        "game_text": "Grandis, saute et survis : un jeu de serpent en 3D, avec toute une galerie de "
                     "personnages et de niveaux à débloquer.",
        "badge_alt": "Disponible sur Google Play",
        "badge": "fr_fr/fr",
        "store_hl": "fr",
        "contact": "Contact :",
        "titles": ("Politique de confidentialité", "Conditions d'utilisation",
                   "Supprimer vos données", "Mentions légales"),
    },
    "es": {
        "folder": "es",
        "html_lang": "es",
        "name": "Español",
        "tagline": "Estudio de videojuegos independiente",
        "game_text": "Crece, salta y sobrevive: un juego de serpientes en 3D, con todo un elenco de "
                     "personajes y niveles por desbloquear.",
        "badge_alt": "Disponible en Google Play",
        "badge": "es_es/es",
        "store_hl": "es",
        "contact": "Contacto:",
        "titles": ("Política de privacidad", "Condiciones de uso", "Eliminar tus datos",
                   "Aviso legal"),
    },
    "pt_BR": {
        "folder": "pt-br",
        "html_lang": "pt-BR",
        "name": "Português (Brasil)",
        "tagline": "Estúdio independente de jogos",
        "game_text": "Cresça, pule e sobreviva: um jogo de cobrinha em 3D, com uma turma de "
                     "personagens e fases para desbloquear.",
        "badge_alt": "Disponível no Google Play",
        "badge": "pt_br/pt-br",
        "store_hl": "pt-BR",
        "contact": "Contato:",
        "titles": ("Política de Privacidade", "Termos de Uso", "Excluir seus dados",
                   "Aviso legal"),
    },
    "de": {
        "folder": "de",
        "html_lang": "de",
        "name": "Deutsch",
        "tagline": "Unabhängiges Spielestudio",
        "game_text": "Wachse, springe und überlebe: ein Schlangenspiel in 3D, mit vielen "
                     "Charakteren und Levels zum Freischalten.",
        "badge_alt": "Jetzt bei Google Play",
        "badge": "de_de/de",
        "store_hl": "de",
        "contact": "Kontakt:",
        "titles": ("Datenschutzerklärung", "Nutzungsbedingungen", "Deine Daten löschen",
                   "Impressum"),
    },
    "it": {
        "folder": "it",
        "html_lang": "it",
        "name": "Italiano",
        "tagline": "Studio indipendente di videogiochi",
        "game_text": "Cresci, salta e sopravvivi: un gioco del serpente in 3D, con tanti "
                     "personaggi e livelli da sbloccare.",
        "badge_alt": "Disponibile su Google Play",
        "badge": "it_it/it",
        "store_hl": "it",
        "contact": "Contatti:",
        "titles": ("Informativa sulla privacy", "Condizioni d'uso", "Eliminare i tuoi dati",
                   "Note legali"),
    },
    "tr": {
        "folder": "tr",
        "html_lang": "tr",
        "name": "Türkçe",
        "tagline": "Bağımsız oyun stüdyosu",
        "game_text": "Büyü, zıpla ve hayatta kal: açılacak birçok karakter ve bölümle 3D bir "
                     "yılan oyunu.",
        "badge_alt": "Google Play'den alın",
        "badge": "tr_tr/tr",
        "store_hl": "tr",
        "contact": "İletişim:",
        "titles": ("Gizlilik Politikası", "Kullanım Koşulları", "Verilerini sil",
                   "Yasal bildirim"),
    },
    "id": {
        "folder": "id",
        "html_lang": "id",
        "name": "Bahasa Indonesia",
        "tagline": "Studio game independen",
        "game_text": "Tumbuh, lompat, dan bertahan: game ular 3D dengan banyak karakter dan level "
                     "untuk dibuka.",
        "badge_alt": "Temukan di Google Play",
        "badge": "id_id/id",
        "store_hl": "id",
        "contact": "Kontak:",
        "titles": ("Kebijakan Privasi", "Ketentuan Penggunaan", "Hapus data kamu",
                   "Pemberitahuan hukum"),
    },
    "pl": {
        "folder": "pl",
        "html_lang": "pl",
        "name": "Polski",
        "tagline": "Niezależne studio gier",
        "game_text": "Rośnij, skacz i przetrwaj: gra w węża w 3D z całą gromadą postaci "
                     "i poziomów do odblokowania.",
        "badge_alt": "Pobierz z Google Play",
        "badge": "pl_pl/pl",
        "store_hl": "pl",
        "contact": "Kontakt:",
        "titles": ("Polityka prywatności", "Warunki korzystania", "Usuń swoje dane",
                   "Nota prawna"),
    },
    "vi": {
        "folder": "vi",
        "html_lang": "vi",
        "name": "Tiếng Việt",
        "tagline": "Studio game độc lập",
        "game_text": "Lớn lên, nhảy và sống sót: trò chơi rắn 3D với cả dàn nhân vật và màn chơi "
                     "để mở khóa.",
        "badge_alt": "Tải nội dung trên Google Play",
        "badge": "vi_vn/vi",
        "store_hl": "vi",
        "contact": "Liên hệ:",
        "titles": ("Chính sách quyền riêng tư", "Điều khoản sử dụng", "Xóa dữ liệu của bạn",
                   "Thông báo pháp lý"),
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
    """(title, body): headings, paragraphs (lines kept apart), bulleted lists, bold, italics
    (a whole paragraph), links."""
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
        elif len(lines) == 1 and re.fullmatch(r"\*[^*].*[^*]\*", lines[0]):
            blocks.append(f'<p class="note"><em>{_inline(lines[0][1:-1])}</em></p>')
        else:
            blocks.append("<p>" + "<br>".join(_inline(line) for line in lines) + "</p>")
    return title, "\n".join(blocks)


# ==================================================
# PAGES
# ==================================================

def _prefix(lang: str) -> str:
    folder = LANGUAGES[lang]["folder"]
    return f"/{folder}/" if folder else "/"


def _languages_of(slug: str) -> tuple[str, ...]:
    return PAGES[slug][1] or tuple(LANGUAGES)


def _page_url(lang: str, slug: str) -> str:
    """The page in this language, or in English when it only exists in a few."""
    shown = lang if lang in _languages_of(slug) else "en"
    return f"{_prefix(shown)}{slug}/"


# Set in the browser when the visitor picks a language in the menu.
LANGUAGE_CHOSEN_KEY = "leviafan-language-chosen"


def _language_redirect() -> str:
    """Script of the English home page (the address shared on social networks): sends a visitor
    to the home page in their browser's language, if the site has it. Never after a language was
    picked in the menu, and never for a visitor whose first language is English."""
    targets = {LANGUAGES[lang]["html_lang"].split("-")[0].lower(): _prefix(lang)
               for lang in LANGUAGES}
    return f"""
<script>
(function () {{
  var targets = {json.dumps(targets)};
  try {{
    if (localStorage.getItem("{LANGUAGE_CHOSEN_KEY}")) return;
  }} catch (e) {{}}
  var wanted = navigator.languages || [navigator.language || ""];
  for (var i = 0; i < wanted.length; i++) {{
    var target = targets[String(wanted[i]).split("-")[0].toLowerCase()];
    if (target) {{
      if (target !== "/") location.replace(target);
      return;
    }}
  }}
}})();
</script>"""


def _layout(lang: str, title: str, body: str, slug: str = "") -> str:
    t = LANGUAGES[lang]
    langs = _languages_of(slug) if slug else tuple(LANGUAGES)
    language_links = " ".join(
        f'<a href="{_prefix(other)}{slug + "/" if slug else ""}" '
        f'hreflang="{LANGUAGES[other]["html_lang"]}" lang="{LANGUAGES[other]["html_lang"]}">'
        f'{LANGUAGES[other]["name"]}</a>'
        for other in langs if other != lang
    )
    footer_links = " · ".join(
        f'<a href="{_page_url(lang, page_slug)}">{page_title}</a>'
        for page_slug, page_title in zip(PAGES, t["titles"])
    )
    # Every language version of this page, for search engines (English for any other language).
    page_path = slug + "/" if slug else ""
    alternates = "\n".join(
        [f'<link rel="alternate" hreflang="{LANGUAGES[other]["html_lang"]}" '
         f'href="https://{DOMAIN}{_prefix(other)}{page_path}">' for other in langs]
        + [f'<link rel="alternate" hreflang="x-default" href="https://{DOMAIN}/{page_path}">']
    )
    redirect = _language_redirect() if lang == "en" and not slug else ""
    return f"""<!doctype html>
<html lang="{t['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
{alternates}{redirect}
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header>
<a class="brand" href="{_prefix(lang)}"><img src="/assets/logo.png" alt="Leviafan" width="112" height="112"><span class="tagline">{t['tagline']}</span></a>
<details class="langs">
<summary><span>{t['name']}</span></summary>
<nav>{language_links}</nav>
</details>
</header>
<main>
{body}
</main>
<footer>
<p>{footer_links}</p>
<p>{t['contact']} <a href="mailto:{CONTACT}">{CONTACT}</a></p>
<p>© Leviafan</p>
</footer>
<script>
// A language picked in the menu is remembered: the home page never redirects again.
document.querySelectorAll(".langs a").forEach(function (link) {{
  link.addEventListener("click", function () {{
    try {{ localStorage.setItem("{LANGUAGE_CHOSEN_KEY}", "1"); }} catch (e) {{}}
  }});
}});
</script>
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


def _home(lang: str, t: dict) -> str:
    """The game (the page is the download link of the social networks)."""
    store = html.escape(STORE_URL.format(hl=t["store_hl"]))
    locale, name = t["badge"].split("/")
    badge = BADGE_URL.format(locale=locale, name=name)
    return f"""<section class="app">
<a class="app-banner" href="{store}"><img src="/assets/snake3d/feature.webp" alt="" width="1024" height="500"></a>
<div class="app-card">
<a class="app-head" href="{store}">
<img class="app-icon" src="/assets/snake3d/icon.png" alt="" width="128" height="128">
<span><span class="app-name">Snake 3D</span><span class="app-dev">Leviafan</span></span>
</a>
<p>{t['game_text']}</p>
<a class="badge" href="{store}"><img src="{badge}" alt="{html.escape(t['badge_alt'])}" width="250" height="97"></a>
</div>
</section>"""


def build() -> None:
    for lang, t in LANGUAGES.items():
        home = _home(lang, t)
        _write(f"{_prefix(lang)[1:]}index.html", _layout(lang, "Leviafan", home))
        for slug, (source, _langs) in PAGES.items():
            if lang not in _languages_of(slug):
                continue
            text = (CONTENT / f"{source}_{lang}.md").read_text(encoding="utf-8")
            title, body = markdown_to_html(_fill(text))
            page = f"<article><h1>{html.escape(title)}</h1>\n{body}</article>"
            _write(f"{_prefix(lang)[1:]}{slug}/index.html",
                   _layout(lang, f"{title} – Leviafan", page, slug))
    _write("app-ads.txt", APP_ADS)
    _write("CNAME", DOMAIN + "\n")


if __name__ == "__main__":
    build()
