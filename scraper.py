"""Navegação e extração de URLs de imagens de uma board do Pinterest."""

from __future__ import annotations

import re
import time
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

# Pinterest serve thumbnails em vários tamanhos sob /<size>x/ no caminho da URL.
# Trocamos qualquer tamanho pelo "originals" para obter a maior resolução.
_SIZE_SEGMENT = re.compile(r"/\d+x\d*/")


def _to_high_resolution(url: str) -> str:
    """Reescreve a URL de um thumbnail para a versão em resolução original."""
    return _SIZE_SEGMENT.sub("/originals/", url)


def _is_pin_image(url: str) -> bool:
    """Filtra apenas imagens de pins, ignorando avatares e ícones de UI."""
    if not url:
        return False
    host = urlparse(url).netloc
    if "pinimg.com" not in host:
        return False
    # Avatares (/user/) e assets fixos não interessam.
    return "/avatars/" not in url and "75x75" not in url


class PinterestScraper:
    """Carrega uma board e coleta todas as URLs de imagem em alta resolução."""

    def __init__(self, headless: bool = True, scroll_pause: float = 1.5,
                 max_idle_scrolls: int = 4):
        self.headless = headless
        self.scroll_pause = scroll_pause
        self.max_idle_scrolls = max_idle_scrolls

    def collect_image_urls(self, board_url: str, limit: int = 0) -> list[str]:
        """Retorna as URLs únicas de imagem encontradas na board.

        `limit` 0 significa todas as imagens; qualquer valor maior interrompe
        o scroll assim que a quantidade for atingida.
        """
        found: dict[str, None] = {}  # dict preserva ordem e remove duplicados

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page(viewport={"width": 1280, "height": 1600})
            try:
                page.goto(board_url, wait_until="domcontentloaded", timeout=60000)
                try:
                    page.wait_for_selector("img", timeout=30000)
                except PlaywrightTimeoutError:
                    raise RuntimeError(
                        "Nenhuma imagem encontrada. A board é pública e a URL está correta?"
                    )

                idle = 0
                last_height = 0
                while True:
                    self._harvest(page, found)

                    if limit and len(found) >= limit:
                        break

                    page.mouse.wheel(0, 4000)
                    time.sleep(self.scroll_pause)

                    height = page.evaluate("document.body.scrollHeight")
                    if height == last_height:
                        idle += 1
                        if idle >= self.max_idle_scrolls:
                            break
                    else:
                        idle = 0
                        last_height = height
            finally:
                browser.close()

        urls = list(found.keys())
        return urls[:limit] if limit else urls

    @staticmethod
    def _harvest(page, found: dict[str, None]) -> None:
        """Extrai srcs visíveis no DOM atual e os adiciona ao acumulador."""
        srcs = page.eval_on_selector_all(
            "img",
            "els => els.map(e => e.getAttribute('src') || e.getAttribute('data-src'))",
        )
        for src in srcs:
            if _is_pin_image(src):
                found.setdefault(_to_high_resolution(src), None)
