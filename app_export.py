"""Exporta as figurinhas no formato de assets do app oficial WhatsApp/stickers.

Em vez de depender de um app intermediário (Sticker Maker etc.), você compila
uma vez o app de exemplo oficial do WhatsApp
(https://github.com/WhatsApp/stickers) e este módulo injeta os pacotes gerados
pelo script diretamente na pasta de `assets` do app, além de escrever um
`contents.json` válido. Depois é só compilar/instalar e adicionar ao WhatsApp
com um toque — o app é seu.

Layout gerado dentro de `<assets>`:

    <assets>/
    ├── contents.json          # lista todos os pacotes
    ├── <identifier_1>/
    │   ├── tray.png           # capa 96x96
    │   ├── 01.webp            # figurinhas 512x512, < 100 KB
    │   └── ...
    └── <identifier_2>/ ...
"""

from __future__ import annotations

import json
import os
import shutil

from packer import MAX_PER_PACK, MIN_PER_PACK, _balanced_chunks, _make_tray, _slug

# O WhatsApp exige de 1 a 3 emojis por figurinha. Como não sabemos o conteúdo,
# usamos um emoji neutro por padrão — você pode editar o contents.json depois.
DEFAULT_EMOJIS = ["✨"]


def _pack_entry(identifier: str, name: str, publisher: str,
                sticker_files: list[str]) -> dict:
    """Monta a entrada de um pacote no contents.json (campos exigidos pelo app)."""
    return {
        "identifier": identifier,
        "name": name,
        "publisher": publisher,
        "tray_image_file": "tray.png",
        "image_data_version": "1",
        "avoid_cache": False,
        "publisher_email": "",
        "publisher_website": "",
        "privacy_policy_website": "",
        "license_agreement_website": "",
        "stickers": [
            {"image_file": f, "emojis": list(DEFAULT_EMOJIS)}
            for f in sticker_files
        ],
    }


def export_for_app(sticker_paths: list[str], assets_dir: str,
                   name: str = "Figurinhas",
                   publisher: str = "PinterestSticker") -> list[str]:
    """Escreve os pacotes e o contents.json na pasta de assets do app Android.

    Retorna os identificadores dos pacotes criados. Sobrescreve o contents.json
    existente com os pacotes desta exportação.
    """
    stickers = [p for p in sticker_paths if p.lower().endswith(".webp")]
    if len(stickers) < MIN_PER_PACK:
        print(
            f"Poucas figurinhas para um pacote ({len(stickers)}); "
            f"o WhatsApp exige no mínimo {MIN_PER_PACK}. Nada exportado."
        )
        return []

    os.makedirs(assets_dir, exist_ok=True)
    groups = _balanced_chunks(stickers, MAX_PER_PACK)
    base_slug = _slug(name)

    packs: list[dict] = []
    identifiers: list[str] = []
    for i, group in enumerate(groups, 1):
        identifier = base_slug if len(groups) == 1 else f"{base_slug}_{i}"
        pack_name = name if len(groups) == 1 else f"{name} {i}"
        pack_dir = os.path.join(assets_dir, identifier)
        os.makedirs(pack_dir, exist_ok=True)

        _make_tray(group[0], os.path.join(pack_dir, "tray.png"))

        sticker_files: list[str] = []
        for j, sticker in enumerate(group, 1):
            fname = f"{j:02d}.webp"
            shutil.copyfile(sticker, os.path.join(pack_dir, fname))
            sticker_files.append(fname)

        packs.append(_pack_entry(identifier, pack_name, publisher, sticker_files))
        identifiers.append(identifier)

    contents = {
        "android_play_store_link": "",
        "ios_app_store_link": "",
        "sticker_packs": packs,
    }
    with open(os.path.join(assets_dir, "contents.json"), "w", encoding="utf-8") as f:
        json.dump(contents, f, ensure_ascii=False, indent=2)

    return identifiers
