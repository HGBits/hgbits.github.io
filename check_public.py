#!/usr/bin/env python3
"""Valida que o site publicado não exponha conteúdo adulto fora dos fragmentos sob demanda."""
import html
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "_site"
POSTS = ROOT / "content" / "posts"
FORBIDDEN_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".sh", ".pem", ".key", ".asc", ".gpg"}
FORBIDDEN_DIRS = {"content", "templates", ".github", ".git", "admin", "private"}
TEXT_SUFFIXES = {".html", ".xml", ".js", ".css", ".json", ".txt", ".svg", ""}
MIN_LINE = 20


def parse(text):
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            head, body = parts
            meta = {}
            for line in head.splitlines()[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
            return meta, body.lstrip("-").lstrip("\n")
    return {}, text


def is_adult(meta):
    return meta.get("classification", "").strip().strip("\\'\"").lower() in {"18+", "adult"}


def main():
    if not SITE.is_dir():
        print("ERRO: _site/ não existe. Rode python build.py primeiro.")
        return 1

    errors = []
    files = [path for path in SITE.rglob("*") if path.is_file()]
    bad_dirs = set()
    for path in files:
        rel = path.relative_to(SITE)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"arquivo proibido publicado: {rel}")
        if rel.parts[0] in FORBIDDEN_DIRS:
            bad_dirs.add(rel.parts[0])
    errors.extend(f"diretório proibido publicado: {name}/" for name in sorted(bad_dirs))

    corpus = {}
    for path in files:
        rel = path.relative_to(SITE)
        if rel.parts[0] == "restricted" or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            corpus[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pass

    adult_posts = 0
    for source in sorted(POSTS.glob("*.md")):
        meta, body = parse(source.read_text(encoding="utf-8"))
        if not is_adult(meta):
            continue
        adult_posts += 1
        slug = source.stem
        page = SITE / "posts" / f"{slug}.html"
        fragment = SITE / "restricted" / f"{slug}.html"
        if not page.is_file():
            errors.append(f"página do post adulto ausente: posts/{slug}.html")
        else:
            page_text = page.read_text(encoding="utf-8")
            expected_url = f'data-age-content-url="../restricted/{html.escape(slug, quote=True)}.html"'
            if expected_url not in page_text:
                errors.append(f"URL do fragmento ausente/incorreta em posts/{slug}.html")
        if not fragment.is_file():
            errors.append(f"fragmento do post adulto ausente: restricted/{slug}.html")

        excerpt = meta.get("excerpt", "").strip()
        lines = {line.strip() for line in body.splitlines()
                 if len(line.strip()) >= MIN_LINE and not line.strip().startswith("![")
                 and line.strip() not in excerpt}
        for rel, published_text in corpus.items():
            for line in lines:
                if (line in published_text or html.escape(line, quote=False) in published_text
                        or html.escape(line, quote=True) in published_text):
                    errors.append(f"texto de post 18+ ({source.name}) vazou em {rel}: {line[:50]!r}...")
                    break

    if errors:
        print(f"FALHOU: {len(errors)} problema(s) em _site/")
        for error in errors:
            print("  -", error)
        return 1
    print(f"OK: {len(files)} arquivos em _site/, {adult_posts} posts 18+ verificados; fragmentos separados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
