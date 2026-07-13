"""Monta pacotes .wastickers prontos para importar no WhatsApp.

Um arquivo `.wastickers` é apenas um ZIP (com caminhos "achatados", sem
subpastas) contendo:

- `author.txt`  -> autor do pacote
- `title.txt`   -> título do pacote
- figurinhas    -> WEBP 512x512, fundo transparente, < 100 KB cada
- capa/bandeja  -> PNG 96x96, < 50 KB

Apps como o Sticker Maker leem esse arquivo e importam todas as figurinhas de
uma vez, evitando ter que enviar imagem por imagem.
"""

from __future__ import annotations

import os
import zipfile

from PIL import Image

# O WhatsApp aceita de 3 a 30 figurinhas por pacote.
MIN_PER_PACK = 3
MAX_PER_PACK = 30
TRAY_SIZE = (96, 96)
PACK_DIR = os.path.join("downloads", "packs")


def _balanced_chunks(items: list[str], max_size: int) -> list[list[str]]:
    """Divide a lista em grupos de no máximo `max_size`, o mais equilibrados
    possível — assim evitamos um último pacote com 1 ou 2 figurinhas (inválido).
    """
    n = len(items)
    if n == 0:
        return []
    num = (n + max_size - 1) // max_size
    base, extra = divmod(n, num)
    chunks: list[list[str]] = []
    start = 0
    for i in range(num):
        size = base + (1 if i < extra else 0)
        chunks.append(items[start:start + size])
        start += size
    return chunks


def _make_tray(sticker_path: str, dest: str) -> None:
    """Gera a capa 96x96 PNG do pacote a partir da primeira figurinha."""
    with Image.open(sticker_path) as img:
        img = img.convert("RGBA")
        img.thumbnail(TRAY_SIZE, Image.LANCZOS)
        canvas = Image.new("RGBA", TRAY_SIZE, (0, 0, 0, 0))
        offset = ((TRAY_SIZE[0] - img.width) // 2, (TRAY_SIZE[1] - img.height) // 2)
        canvas.paste(img, offset, img)
    canvas.save(dest, "PNG", optimize=True)


def _write_pack(stickers: list[str], title: str, author: str, out_path: str) -> None:
    """Escreve um único arquivo .wastickers (ZIP achatado)."""
    tray_path = os.path.splitext(out_path)[0] + "_tray.png"
    _make_tray(stickers[0], tray_path)
    try:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("title.txt", title)
            zf.writestr("author.txt", author)
            zf.write(tray_path, arcname="tray.png")
            # Numera as figurinhas para garantir nomes únicos dentro do ZIP.
            for i, sticker in enumerate(stickers):
                zf.write(sticker, arcname=f"{i:02d}.webp")
    finally:
        if os.path.exists(tray_path):
            os.remove(tray_path)


def build_packs(sticker_paths: list[str], title: str = "Figurinhas",
                author: str = "PinterestSticker", dest: str = PACK_DIR) -> list[str]:
    """Monta um ou mais `.wastickers` a partir das figurinhas geradas.

    Retorna os caminhos dos pacotes criados. Se houver menos de 3 figurinhas,
    nenhum pacote é gerado (o WhatsApp exige no mínimo 3).
    """
    stickers = [p for p in sticker_paths if p.lower().endswith(".webp")]
    if len(stickers) < MIN_PER_PACK:
        print(
            f"Poucas figurinhas para um pacote ({len(stickers)}); "
            f"o WhatsApp exige no mínimo {MIN_PER_PACK}. Nenhum pacote gerado."
        )
        return []

    os.makedirs(dest, exist_ok=True)
    groups = _balanced_chunks(stickers, MAX_PER_PACK)

    created: list[str] = []
    for i, group in enumerate(groups, 1):
        pack_title = title if len(groups) == 1 else f"{title} {i}"
        out_path = os.path.join(dest, f"{_slug(title)}_{i}.wastickers")
        _write_pack(group, pack_title, author, out_path)
        created.append(out_path)

    return created


def _slug(text: str) -> str:
    """Nome de arquivo simples e seguro a partir do título."""
    keep = "".join(c if c.isalnum() else "_" for c in text.strip())
    return keep.strip("_").lower() or "figurinhas"
