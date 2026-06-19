"""Conversão de imagens para figurinhas WEBP 512x512 com transparência."""

from __future__ import annotations

import os

from PIL import Image
from tqdm import tqdm

STICKER_SIZE = (512, 512)
STICKER_DIR = os.path.join("downloads", "stickers")


def _fit_square(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Redimensiona mantendo proporção e centraliza em uma tela transparente."""
    img = img.convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset, img)
    return canvas


def convert_to_stickers(paths: list[str], dest: str = STICKER_DIR) -> int:
    """Converte cada imagem para figurinha WEBP. Retorna a quantidade gerada."""
    os.makedirs(dest, exist_ok=True)
    count = 0

    for path in tqdm(paths, desc="Convertendo", unit="img"):
        try:
            with Image.open(path) as img:
                sticker = _fit_square(img, STICKER_SIZE)
            name = os.path.splitext(os.path.basename(path))[0] + ".webp"
            sticker.save(os.path.join(dest, name), "WEBP", lossless=True)
            count += 1
        except (OSError, ValueError):
            continue

    return count
