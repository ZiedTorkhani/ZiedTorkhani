"""Génère le blogue du site à partir des articles Markdown de `_articles/`.

Utilisation : python build.py

Chaque article est un fichier `_articles/AAAA-MM-JJ-slug.md` qui commence par un
en-tête :

    ---
    titre: Titre de l'article
    description: Une phrase de 150 à 160 caractères pour Google.
    date: 2026-10-29
    ---

Le script produit :
- blogue/<slug>/index.html  (une page par article)
- blogue/index.html         (la liste des articles)
- blogue/flux.xml           (flux RSS)
- sitemap.xml               (régénéré au complet)
- les blocs « derniers articles » de index.html et la section Blogue de llms.txt

Aucune dépendance : Python standard seulement.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent
SITE = "https://ziedtorkhani.github.io"
AUTEUR_ID = f"{SITE}/#person"
PHOTO = f"{SITE}/img/zied-torkhani.jpg"
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
INTERDITS = re.compile(r"[—–]|concrètement", re.IGNORECASE)


@dataclass
class Article:
    slug: str
    titre: str
    description: str
    date: date
    corps_html: str
    minutes: int

    @property
    def url(self) -> str:
        return f"{SITE}/blogue/{self.slug}/"

    @property
    def date_longue(self) -> str:
        return f"{self.date.day} {MOIS[self.date.month - 1]} {self.date.year}"


# ---------------------------------------------------------------- Markdown

def _en_ligne(texte: str) -> str:
    """Convertit la mise en forme en ligne : liens, gras, italique, code."""
    t = html.escape(texte, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    # Apostrophes typographiques dans le texte (pas dans les balises)
    morceaux = re.split(r"(<[^>]+>)", t)
    morceaux = [m if m.startswith("<") else _typo(m) for m in morceaux]
    return "".join(morceaux)


def _typo(t: str) -> str:
    """Apostrophes courbes et espaces insécables du français (« », :, %, ×)."""
    t = re.sub(r"(?<=\w)'(?=\w)", "’", t)
    t = t.replace("« ", "« ").replace(" »", " »")
    return re.sub(r" ([:;%?!])", " \\1", t)


def markdown_vers_html(source: str) -> str:
    """Markdown volontairement réduit : titres ##/###, paragraphes, listes,
    citations, et blocs HTML bruts (une ligne qui commence par « < »)."""
    sortie: list[str] = []
    lignes = source.strip().splitlines()
    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        if not ligne.strip():
            i += 1
            continue
        if ligne.startswith("<"):
            bloc = []
            while i < len(lignes) and lignes[i].strip():
                bloc.append(lignes[i])
                i += 1
            sortie.append("\n".join(bloc))
            continue
        m = re.match(r"(#{2,3}) (.+)", ligne)
        if m:
            niveau = len(m.group(1))
            sortie.append(f"<h{niveau}>{_en_ligne(m.group(2))}</h{niveau}>")
            i += 1
            continue
        if re.match(r"(- |\d+\. )", ligne):
            ordonnee = bool(re.match(r"\d+\. ", ligne))
            balise = "ol" if ordonnee else "ul"
            items = []
            while i < len(lignes) and re.match(r"(- |\d+\. )", lignes[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lignes[i]))
                i += 1
            sortie.append(f"<{balise}>" + "".join(f"<li>{_en_ligne(x)}</li>" for x in items) + f"</{balise}>")
            continue
        if ligne.startswith("> "):
            bloc = []
            while i < len(lignes) and lignes[i].startswith("> "):
                bloc.append(lignes[i][2:])
                i += 1
            sortie.append(f"<blockquote><p>{_en_ligne(' '.join(bloc))}</p></blockquote>")
            continue
        bloc = []
        while i < len(lignes) and lignes[i].strip() and not re.match(r"(#{2,3} |- |\d+\. |> |<)", lignes[i]):
            bloc.append(lignes[i])
            i += 1
        sortie.append(f"<p>{_en_ligne(' '.join(bloc))}</p>")
    return "\n".join(sortie)


def lire_article(chemin: Path) -> Article:
    texte = chemin.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", texte, re.S)
    if not m:
        raise SystemExit(f"{chemin.name} : en-tête --- manquant")
    entete = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    for champ in ("titre", "description", "date"):
        if champ not in entete:
            raise SystemExit(f"{chemin.name} : champ « {champ} » manquant")
    corps = m.group(2)
    if INTERDITS.search(texte):
        raise SystemExit(f"{chemin.name} : tiret long ou mot interdit trouvé : {INTERDITS.search(texte).group()!r}")
    longueur = len(entete["description"])
    if not 120 <= longueur <= 160:
        print(f"  attention : description de {longueur} caractères dans {chemin.name} (viser 150 à 160)")
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", chemin.stem)
    mots = len(re.sub(r"<[^>]+>", " ", corps).split())
    return Article(
        slug=slug,
        titre=entete["titre"],
        description=entete["description"],
        date=date.fromisoformat(entete["date"]),
        corps_html=markdown_vers_html(corps),
        minutes=max(1, round(mots / 220)),
    )


# ---------------------------------------------------------------- Gabarits

def tete(titre: str, description: str, url: str, prefixe: str, type_og: str = "website", extra: str = "") -> str:
    e = lambda s: html.escape(s, quote=True)
    return f"""<!doctype html>
<html lang="fr-CA">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titre)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="author" content="Zied Torkhani">
  <link rel="canonical" href="{url}">
  <link rel="alternate" type="application/rss+xml" title="Blogue de Zied Torkhani" href="{SITE}/blogue/flux.xml">
  <meta name="theme-color" content="#f2f3f1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121722" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="{type_og}">
  <meta property="og:locale" content="fr_CA">
  <meta property="og:site_name" content="Zied Torkhani">
  <meta property="og:title" content="{e(titre)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{PHOTO}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{e(titre)}">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="{PHOTO}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&display=swap">
  <link rel="stylesheet" href="{prefixe}css/site.css">
{extra}</head>
<body>
  <a class="skip" href="#contenu">Aller au contenu</a>

  <header class="wrap top">
    <a class="monogram" href="{prefixe}" aria-label="Zied Torkhani, accueil">ZT</a>
    <nav aria-label="Navigation principale">
      <ul>
        <li><a href="{prefixe}#parcours">Parcours</a></li>
        <li><a href="{prefixe}#publications">Publications</a></li>
        <li><a href="{prefixe}blogue/">Blogue</a></li>
        <li><a href="{prefixe}#contact">Contact</a></li>
      </ul>
    </nav>
  </header>
"""


def pied(prefixe: str) -> str:
    return f"""
  <footer>
    <div class="wrap">
      <span>© {date.today().year} Zied Torkhani</span>
      <a href="{prefixe}blogue/flux.xml">Flux RSS</a>
    </div>
  </footer>
</body>
</html>
"""


def page_article(a: Article) -> str:
    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": a.titre,
        "description": a.description,
        "datePublished": a.date.isoformat(),
        "dateModified": a.date.isoformat(),
        "inLanguage": "fr-CA",
        "url": a.url,
        "mainEntityOfPage": a.url,
        "image": PHOTO,
        "author": {"@type": "Person", "@id": AUTEUR_ID, "name": "Zied Torkhani", "url": f"{SITE}/"},
        "publisher": {"@type": "Person", "@id": AUTEUR_ID, "name": "Zied Torkhani"},
    }
    extra = ('  <script type="application/ld+json">\n'
             + json.dumps(jsonld, ensure_ascii=False, indent=2)
             + "\n  </script>\n")
    return (tete(f"{a.titre} | Zied Torkhani", a.description, a.url, "../../", "article", extra)
            + f"""
  <main id="contenu" class="wrap">
    <article class="post">
      <header class="post-head">
        <p class="post-meta"><a href="../">Blogue</a>, <time datetime="{a.date.isoformat()}">{a.date_longue}</time>, {a.minutes} min de lecture</p>
        <h1>{_en_ligne(a.titre)}</h1>
        <p class="post-lede">{_en_ligne(a.description)}</p>
      </header>
      <div class="prose">
{a.corps_html}
      </div>
      <footer class="post-foot">
        <p>Zied Torkhani est gestionnaire de l’excellence organisationnelle chez Soleno. Il écrit sur la planification industrielle et l’aide à la décision. <a href="../../">En savoir plus</a> ou <a href="https://www.linkedin.com/in/zied-torkhani/">le suivre sur LinkedIn</a>.</p>
      </footer>
    </article>
  </main>
""" + pied("../../"))


def liste_html(articles: list[Article], prefixe: str) -> str:
    items = []
    for a in articles:
        items.append(
            f'<li><time datetime="{a.date.isoformat()}">{a.date_longue}</time>'
            f'<h3><a href="{prefixe}blogue/{a.slug}/">{_en_ligne(a.titre)}</a></h3>'
            f"<p>{_en_ligne(a.description)}</p></li>"
        )
    return '<ul class="posts">' + "".join(items) + "</ul>"


def page_index(articles: list[Article]) -> str:
    desc = "Le blogue de Zied Torkhani : planification industrielle, physique des opérations et aide à la décision, expliquées simplement pour les manufacturiers."
    return (tete("Blogue | Zied Torkhani", desc, f"{SITE}/blogue/", "../")
            + f"""
  <main id="contenu" class="wrap">
    <header class="post-head">
      <h1>Blogue</h1>
      <p class="post-lede">La planification industrielle et l’aide à la décision, expliquées simplement.</p>
    </header>
    {liste_html(articles, "../")}
  </main>
""" + pied("../"))


def flux_rss(articles: list[Article]) -> str:
    e = html.escape
    items = "".join(
        f"""
    <item>
      <title>{e(a.titre)}</title>
      <link>{a.url}</link>
      <guid>{a.url}</guid>
      <pubDate>{format_datetime(datetime(a.date.year, a.date.month, a.date.day, 8, tzinfo=timezone.utc))}</pubDate>
      <description>{e(a.description)}</description>
    </item>""" for a in articles)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Blogue de Zied Torkhani</title>
    <link>{SITE}/blogue/</link>
    <description>Planification industrielle et aide à la décision, expliquées simplement.</description>
    <language>fr-CA</language>{items}
  </channel>
</rss>
"""


def sitemap(articles: list[Article]) -> str:
    aujourdhui = date.today().isoformat()
    alt = (f'\n    <xhtml:link rel="alternate" hreflang="fr-CA" href="{SITE}/"/>'
           f'\n    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/"/>')
    urls = [f"  <url>\n    <loc>{SITE}/</loc>\n    <lastmod>{aujourdhui}</lastmod>{alt}\n  </url>",
            f"  <url>\n    <loc>{SITE}/en/</loc>\n    <lastmod>{aujourdhui}</lastmod>{alt}\n  </url>",
            f"  <url>\n    <loc>{SITE}/blogue/</loc>\n    <lastmod>{aujourdhui}</lastmod>\n  </url>"]
    urls += [f"  <url>\n    <loc>{a.url}</loc>\n    <lastmod>{a.date.isoformat()}</lastmod>\n  </url>" for a in articles]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def remplacer_bloc(chemin: Path, debut: str, fin: str, contenu: str) -> None:
    texte = chemin.read_text(encoding="utf-8")
    motif = re.compile(re.escape(debut) + r".*?" + re.escape(fin), re.S)
    if not motif.search(texte):
        raise SystemExit(f"{chemin.name} : marqueurs {debut} introuvables")
    texte = motif.sub(lambda _: f"{debut}\n{contenu}\n{fin}", texte)
    chemin.write_text(texte, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- Programme

def main() -> None:
    articles = sorted((lire_article(p) for p in (RACINE / "_articles").glob("*.md")),
                      key=lambda a: a.date, reverse=True)
    blogue = RACINE / "blogue"
    blogue.mkdir(exist_ok=True)
    for a in articles:
        dossier = blogue / a.slug
        dossier.mkdir(exist_ok=True)
        (dossier / "index.html").write_text(page_article(a), encoding="utf-8", newline="\n")
        print(f"  article : blogue/{a.slug}/")
    (blogue / "index.html").write_text(page_index(articles), encoding="utf-8", newline="\n")
    (blogue / "flux.xml").write_text(flux_rss(articles), encoding="utf-8", newline="\n")
    (RACINE / "sitemap.xml").write_text(sitemap(articles), encoding="utf-8", newline="\n")

    remplacer_bloc(RACINE / "index.html", "<!-- BLOGUE:debut -->", "<!-- BLOGUE:fin -->",
                   "          " + liste_html(articles[:3], ""))
    lignes = "\n".join(f"- [{a.titre}]({a.url}) : {a.description} ({a.date.isoformat()})" for a in articles)
    remplacer_bloc(RACINE / "llms.txt", "<!-- BLOGUE:debut -->", "<!-- BLOGUE:fin -->", lignes)
    print(f"{len(articles)} article(s) généré(s). Sitemap, flux RSS et accueil à jour.")


if __name__ == "__main__":
    main()
