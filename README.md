# Pinterest Board Downloader

Aplicação de terminal em Python para baixar todas as imagens de uma board
pública do Pinterest, em alta resolução, com opção de convertê-las em
figurinhas WEBP 512x512.

## Requisitos

- Python 3.12+

## Instalação

```bash
# (opcional) ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# dependências
pip install -r requirements.txt

# navegador usado pelo Playwright
playwright install chromium
```

## Uso

Modo interativo:

```bash
python main.py
```

O programa solicitará:

```
URL da board do Pinterest:
Pasta de destino:
Converter para WEBP? (s/n):
Limite de imagens (0 = todas):
```

Modo com argumentos:

```bash
python main.py --url "URL_DA_BOARD"
python main.py --url "URL_DA_BOARD" --webp
python main.py --url "URL_DA_BOARD" --limit 100
```

Argumentos disponíveis:

| Argumento  | Descrição                                      |
|------------|------------------------------------------------|
| `--url`    | URL da board do Pinterest                      |
| `--dest`   | Pasta de destino (padrão: `downloads`)         |
| `--webp`   | Converte as imagens em figurinhas WEBP         |
| `--limit`  | Máximo de imagens a baixar (`0` = todas)       |

## Funcionamento

1. O **scraper** (`scraper.py`) abre a board com o Playwright, faz scroll
   automático até carregar todas as imagens e extrai as URLs em resolução
   original (`/originals/`), evitando avatares e ícones.
2. O **downloader** (`downloader.py`) baixa cada imagem, ignora duplicados e
   exibe uma barra de progresso (`tqdm`).
3. O **converter** (`converter.py`), quando `--webp` está ativo, redimensiona
   cada imagem para 512x512 mantendo a transparência e salva em
   `downloads/stickers/`.

Ao final são exibidas as estatísticas: imagens encontradas, baixadas,
ignoradas e o tempo total.

## Estrutura

```
PinterestDownloader/
├── main.py          # interface de terminal e orquestração
├── scraper.py       # navegação e extração de URLs (Playwright)
├── downloader.py    # download e deduplicação (Requests + tqdm)
├── converter.py     # conversão para figurinha WEBP (Pillow)
├── requirements.txt
└── README.md
```

## Observações

- Funciona apenas com boards **públicas**.
- O Pinterest pode alterar seu layout; caso nenhuma imagem seja encontrada,
  verifique se a URL está correta e se a board é pública.
- Respeite os Termos de Uso do Pinterest e os direitos autorais das imagens.
