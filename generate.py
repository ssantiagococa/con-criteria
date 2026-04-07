#!/usr/bin/env python3
"""
Con CriterIA — Newsletter generator

Usage:
    python generate.py              # Generate current week's edition
    python generate.py --week 14    # Generate specific week
    python generate.py --no-archive # Don't archive bookmarks after generating
    python generate.py --dry-run    # Generate HTML without calling Claude API (uses placeholders)
"""
import argparse
import json
import os
import sys
from datetime import date

import config
from src.instapaper import InstapaperClient
from src.extractor import extract_og_image, extract_source_domain
from src.translator import generate_translation
from src.renderer import render_newsletter, render_index, infer_content_type

PLACEHOLDER_TRANSLATION = "[traducción a humano — ejecuta sin --dry-run para generarla con IA]"

def _dry_run_articles(folder, count):
    """Return placeholder articles for dry-run mode."""
    return [
        {
            "title": f"[DRY-RUN] Artículo de ejemplo #{i+1} ({folder})",
            "url": "https://example.com",
            "source": "Fuente de ejemplo",
            "excerpt": "Este es un resumen de ejemplo para ver el diseño.",
            "image_url": f"https://picsum.photos/seed/{folder}{i}/400/300",
            "translation": PLACEHOLDER_TRANSLATION,
            "content_type": "📄 Artículo",
            "bookmark_id": 0,
        }
        for i in range(count)
    ]


MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def fetch_articles(client, folder_name, limit, dry_run):
    """Fetch bookmarks from a folder and enrich with image + translation."""
    folder_id = client.get_folder_id(folder_name)
    bookmarks = client.get_bookmarks(folder_id=folder_id, limit=limit)
    articles = []
    for bm in bookmarks:
        url = bm["url"]
        title = bm["title"]
        excerpt = bm.get("description", "")
        source = extract_source_domain(url)
        print(f"  → {title[:60]}...")
        image_url = extract_og_image(url)
        if dry_run:
            translation = PLACEHOLDER_TRANSLATION
        else:
            translation = generate_translation(
                api_key=config.CLAUDE_API_KEY,
                title=title,
                source=source,
                excerpt=excerpt,
            )
        articles.append({
            "title": title,
            "url": url,
            "source": source,
            "excerpt": excerpt,
            "image_url": image_url,
            "translation": translation,
            "content_type": infer_content_type(url),
            "bookmark_id": bm["bookmark_id"],
        })
    return articles, folder_id


def load_edition_index(index_path):
    """Load existing edition list from a JSON sidecar file."""
    if os.path.exists(index_path):
        with open(index_path) as f:
            return json.load(f)
    return []


def save_edition_index(editions, index_path):
    with open(index_path, "w") as f:
        json.dump(editions, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate Con CriterIA newsletter")
    parser.add_argument("--week", type=int, default=None,
                        help="ISO week number (default: current week)")
    parser.add_argument("--year", type=int, default=None,
                        help="Year (default: current year)")
    parser.add_argument("--no-archive", action="store_true",
                        help="Don't archive bookmarks after generating")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip Claude API calls (use placeholders)")
    parser.add_argument("--no-translate", action="store_true",
                        help="Fetch real Instapaper articles but skip Claude API calls")
    args = parser.parse_args()

    today = date.today()
    year = args.year or today.isocalendar()[0]
    week = args.week or today.isocalendar()[1]
    edition_filename = f"{year}-W{week:02d}.html"
    output_path = os.path.join("editions", edition_filename)

    print(f"\n🌶️  Generando Con CriterIA · Semana {week}, {year}...\n")

    if args.dry_run:
        print("⚡ Modo dry-run: usando datos de ejemplo, sin conectar a Instapaper ni Claude.\n")
        pepper = _dry_run_articles("hot-topic", 3)
        needy = _dry_run_articles("aprende", 2)
        deepy_list = _dry_run_articles("profundidad", 1)
        goofy_list = _dry_run_articles("funny", 1)
    else:
        if args.no_translate:
            print("⚡ Modo --no-translate: leyendo Instapaper real, sin llamar a Claude.\n")
        client = InstapaperClient(
            consumer_key=config.INSTAPAPER_CONSUMER_KEY,
            consumer_secret=config.INSTAPAPER_CONSUMER_SECRET,
            username=config.INSTAPAPER_USERNAME,
            password=config.INSTAPAPER_PASSWORD,
        )

        skip_translate = args.no_translate

        print("📰 lo pepper (hot-topic):")
        pepper, _ = fetch_articles(client, "hot-topic", 3, dry_run=skip_translate)

        print("\n✦  lo needy (aprende):")
        needy, _ = fetch_articles(client, "aprende", 2, dry_run=skip_translate)

        print("\n◎  lo deepy (profundidad):")
        deepy_list, _ = fetch_articles(client, "profundidad", 1, dry_run=skip_translate)

        print("\n😄 lo goofy (funny):")
        goofy_list, _ = fetch_articles(client, "funny", 1, dry_run=skip_translate)

    if not pepper:
        print("\n⚠️  Aviso: no hay artículos en 'hot-topic'. La sección lo pepper aparecerá vacía.")

    index_path = os.path.join("editions", ".index.json")
    editions = load_edition_index(index_path)
    edition_num = len(editions) + 1

    date_str = f"{today.day} de {MONTHS_ES[today.month - 1]} de {today.year}"

    data = {
        "edition_num": edition_num,
        "week": week,
        "year": year,
        "date": date_str,
        "intro": (
            f"Semana {week} lista. Aquí tienes lo más relevante del mundo de la IA "
            f"— curado con criterio."
        ),
        "pepper": pepper,
        "needy": needy,
        "deepy": deepy_list[0] if deepy_list else {},
        "goofy": goofy_list[0] if goofy_list else {},
    }

    render_newsletter(data, output_path=output_path)
    print(f"\n✓ Newsletter generada: {output_path}")

    editions.append({
        "num": edition_num,
        "week": week,
        "year": year,
        "date": date_str,
        "filename": edition_filename,
    })
    save_edition_index(editions, index_path)
    render_index(editions, output_path="index.html")
    print("✓ index.html actualizado")

    should_archive = not args.no_archive and getattr(config, "ARCHIVE_AFTER_GENERATE", True)
    if should_archive and not args.dry_run:
        all_bookmark_ids = (
            [a["bookmark_id"] for a in pepper] +
            [a["bookmark_id"] for a in needy] +
            [a["bookmark_id"] for a in deepy_list] +
            [a["bookmark_id"] for a in goofy_list]
        )
        for bid in all_bookmark_ids:
            client.archive_bookmark(bid)
        print(f"✓ {len(all_bookmark_ids)} bookmarks archivados en Instapaper")

    print(f"\nListo ✓")
    print(f"Abre {output_path} en tu navegador para revisarlo.")
    print(f"Cuando estés conforme:")
    print(f"  git add editions/ index.html && git commit -m 'newsletter: semana {week}' && git push")


if __name__ == "__main__":
    main()
