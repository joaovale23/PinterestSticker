"""Conversão de imagens para figurinhas WEBP 512x512 com transparência."""

from __future__ import annotations

import os

from PIL import Image
from tqdm import tqdm

STICKER_SIZE = (512, 512)
STICKER_DIR = os.path.join("downloads", "stickers")

# O WhatsApp rejeita figurinhas estáticas acima de 100 KB. O WEBP lossless
# frequentemente ultrapassa esse limite, então caímos para versões com perda
# de qualidade decrescente até caber.
MAX_STICKER_BYTES = 100 * 1024
_LOSSY_QUALITIES = (90, 80, 70, 60, 50, 40)


def _fit_square(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Redimensiona mantendo proporção e centraliza em uma tela transparente."""
    img = img.convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset, img)
    return canvas


def _save_sticker(canvas: Image.Image, path: str) -> None:
    """Salva como WEBP, garantindo o limite de 100 KB do WhatsApp.

    Tenta lossless primeiro (melhor qualidade); se estourar o limite, reduz a
    qualidade progressivamente até caber.
    """
    canvas.save(path, "WEBP", lossless=True)
    if os.path.getsize(path) <= MAX_STICKER_BYTES:
        return
    for quality in _LOSSY_QUALITIES:
        canvas.save(path, "WEBP", lossless=False, quality=quality, method=6)
        if os.path.getsize(path) <= MAX_STICKER_BYTES:
            return


def convert_to_stickers(paths: list[str], dest: str = STICKER_DIR) -> list[str]:
    """Converte cada imagem para figurinha WEBP. Retorna os caminhos gerados."""
    os.makedirs(dest, exist_ok=True)
    stickers: list[str] = []

    for path in tqdm(paths, desc="Convertendo", unit="img"):
        try:
            with Image.open(path) as img:
                sticker = _fit_square(img, STICKER_SIZE)
            name = os.path.splitext(os.path.basename(path))[0] + ".webp"
            out = os.path.join(dest, name)
            _save_sticker(sticker, out)
            stickers.append(out)
        except (OSError, ValueError):
            continue

    return stickers
