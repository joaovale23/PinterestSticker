"""Aplicação de terminal para baixar imagens de uma board do Pinterest."""

from __future__ import annotations

import argparse
import sys
import time

from converter import convert_to_stickers
from downloader import download_images
from scraper import PinterestScraper


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa todas as imagens de uma board do Pinterest."
    )
    parser.add_argument("--url", help="URL da board do Pinterest")
    parser.add_argument("--dest", help="Pasta de destino dos downloads")
    parser.add_argument(
        "--webp", action="store_true",
        help="Converter imagens para figurinhas WEBP 512x512",
    )
    parser.add_argument(
        "--limit", type=int,
        help="Limite de imagens (0 = todas)",
    )
    return parser.parse_args()


def _prompt(label: str, default: str = "") -> str:
    # Sem terminal interativo (ex.: argumentos ou entrada redirecionada),
    # usa o valor padrão em vez de bloquear em input().
    if not sys.stdin.isatty():
        return default
    value = input(label).strip()
    return value or default


def _resolve_options(args: argparse.Namespace) -> dict:
    """Combina argumentos de linha de comando com perguntas interativas."""
    url = args.url or _prompt("URL da board do Pinterest: ")
    if not url:
        print("Erro: URL da board é obrigatória.")
        sys.exit(1)

    dest = args.dest or _prompt("Pasta de destino: ", "downloads")

    if args.webp:
        webp = True
    else:
        webp = _prompt("Converter para WEBP? (s/n): ", "n").lower().startswith("s")

    if args.limit is not None:
        limit = args.limit
    else:
        raw = _prompt("Limite de imagens (0 = todas): ", "0")
        try:
            limit = int(raw)
        except ValueError:
            limit = 0

    return {"url": url, "dest": dest, "webp": webp, "limit": max(limit, 0)}


def main() -> None:
    opts = _resolve_options(_parse_args())
    start = time.time()

    print("\nCarregando a board (isso pode levar alguns minutos)...")
    try:
        urls = PinterestScraper().collect_image_urls(opts["url"], opts["limit"])
    except Exception as exc:  # noqa: BLE001 - feedback amigável no terminal
        print(f"Falha ao carregar a board: {exc}")
        sys.exit(1)

    if not urls:
        print("Nenhuma imagem encontrada.")
        sys.exit(0)

    result = download_images(urls, opts["dest"])

    stickers = 0
    if opts["webp"] and result.paths:
        stickers = convert_to_stickers(result.paths)

    elapsed = time.time() - start
    print("\n=== Estatísticas ===")
    print(f"Imagens encontradas: {result.found}")
    print(f"Imagens baixadas:    {result.downloaded}")
    print(f"Imagens ignoradas:   {result.skipped}")
    if opts["webp"]:
        print(f"Figurinhas geradas:  {stickers}")
    print(f"Tempo total:         {elapsed:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        sys.exit(130)
