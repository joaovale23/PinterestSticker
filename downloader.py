"""Download das imagens com deduplicação e barra de progresso."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests
from tqdm import tqdm

# Nem todo pin possui versão /originals/. Em caso de falha, tentamos os maiores
# tamanhos servidos pelo Pinterest, em ordem decrescente.
_FALLBACK_SIZES = ("/736x/", "/564x/", "/474x/")
_ORIGINALS = re.compile(r"/originals/")


def _candidates(url: str) -> list[str]:
    """URL preferida (originals) seguida de fallbacks em tamanhos menores."""
    urls = [url]
    if "/originals/" in url:
        urls += [_ORIGINALS.sub(size, url) for size in _FALLBACK_SIZES]
    return urls

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


@dataclass
class DownloadResult:
    """Acumula estatísticas e os caminhos baixados."""
    found: int = 0
    downloaded: int = 0
    skipped: int = 0
    paths: list[str] = field(default_factory=list)


def _filename_for(url: str) -> str:
    """Nome de arquivo estável derivado da URL (evita colisões e duplicados)."""
    name = os.path.basename(urlparse(url).path)
    ext = os.path.splitext(name)[1] or ".jpg"
    digest = hashlib.sha1(url.encode()).hexdigest()[:16]
    return f"{digest}{ext}"


def _fetch(session: requests.Session, candidates: list[str]) -> bytes | None:
    """Tenta cada candidato em ordem; retorna o conteúdo do primeiro que responder."""
    for candidate in candidates:
        try:
            resp = session.get(candidate, timeout=30)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException:
            continue
    return None


def download_images(urls: list[str], dest: str) -> DownloadResult:
    """Baixa cada URL para `dest`, ignorando arquivos já existentes."""
    os.makedirs(dest, exist_ok=True)
    result = DownloadResult(found=len(urls))
    seen: set[str] = set()

    with requests.Session() as session:
        session.headers.update(_HEADERS)
        for url in tqdm(urls, desc="Baixando", unit="img"):
            filename = _filename_for(url)
            path = os.path.join(dest, filename)

            if filename in seen or os.path.exists(path):
                result.skipped += 1
                continue
            seen.add(filename)

            content = _fetch(session, _candidates(url))
            if content is None:
                result.skipped += 1
                continue
            with open(path, "wb") as f:
                f.write(content)
            result.downloaded += 1
            result.paths.append(path)

    return result
