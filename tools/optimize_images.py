#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 hgbits <https://github.com/HGBits>
"""Gera variantes WebP redimensionadas de assets/ em assets/web/.

Uso (ferramenta de desenvolvimento, NÃO roda no CI e NÃO é dependência do build):

    pip install pillow        # ou: sudo pacman -S python-pillow
    python tools/optimize_images.py

Para cada assets/<nome>.(png|jpg|jpeg) cria assets/web/<nome>-<largura>.webp nas
larguras de WIDTHS (nunca amplia a imagem). O build.py detecta esses arquivos e
passa a emitir <picture> com srcset; os originais continuam sendo o fallback e o
og:image. Sem rodar este script o site continua funcionando igual (só mais pesado).
Arquivos já gerados e mais novos que o original são pulados.
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow não encontrado: pip install pillow (ou pacman -S python-pillow)")

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ASSETS / "web"
WIDTHS = (320, 640, 1200)   # mantenha em sincronia com WEBP_WIDTHS no build.py
QUALITY = 80
EXTS = {".png", ".jpg", ".jpeg"}


def main():
    OUT.mkdir(exist_ok=True)
    seen = {}
    before = after = made = 0
    for src in sorted(p for p in ASSETS.iterdir() if p.is_file() and p.suffix.lower() in EXTS):
        if src.stem in seen:
            sys.exit(f"colisão de nome: {src.name} e {seen[src.stem]} (mesmo nome sem extensão)")
        seen[src.stem] = src.name
        before += src.stat().st_size
        with Image.open(src) as im:
            im.load()
            for width in WIDTHS:
                if width >= im.width:
                    continue
                dst = OUT / f"{src.stem}-{width}.webp"
                if not (dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime):
                    height = round(im.height * width / im.width)
                    frame = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                    frame.resize((width, height), Image.LANCZOS).save(
                        dst, "WEBP", quality=QUALITY, method=6)
                    made += 1
                if width == 1200:
                    after += dst.stat().st_size
    print(f"{made} variantes geradas em assets/web/ "
          f"(originais: {before / 1e6:.1f} MB; variantes de 1200px: {after / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
