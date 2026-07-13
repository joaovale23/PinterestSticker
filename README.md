# Pinterest Board Downloader

Aplicação de terminal em Python para baixar todas as imagens de uma board
pública do Pinterest, em alta resolução, com opção de convertê-las em
figurinhas WEBP 512x512 e montá-las em pacotes `.wastickers` prontos para
importar no WhatsApp de uma vez só.

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
python main.py --url "URL_DA_BOARD" --pack
python main.py --url "URL_DA_BOARD" --pack --pack-title "Meu Pack" --pack-author "João"
python main.py --url "URL_DA_BOARD" --app-export "C:\stickers\Android\app\src\main\assets"
python main.py --url "URL_DA_BOARD" --limit 100
```

Argumentos disponíveis:

| Argumento       | Descrição                                                |
|-----------------|----------------------------------------------------------|
| `--url`         | URL da board do Pinterest                                |
| `--dest`        | Pasta de destino (padrão: `downloads`)                   |
| `--webp`        | Converte as imagens em figurinhas WEBP                   |
| `--pack`        | Monta pacote(s) `.wastickers` p/ o WhatsApp (ativa `--webp`) |
| `--pack-title`  | Título do pacote (padrão: `Figurinhas`)                  |
| `--pack-author` | Autor/publisher do pacote (padrão: `PinterestSticker`)   |
| `--app-export`  | Exporta os pacotes para a pasta `assets` do app oficial (ativa `--webp`) |
| `--limit`       | Máximo de imagens a baixar (`0` = todas)                 |

## Funcionamento

1. O **scraper** (`scraper.py`) abre a board com o Playwright, faz scroll
   automático até carregar todas as imagens e extrai as URLs em resolução
   original (`/originals/`), evitando avatares e ícones.
2. O **downloader** (`downloader.py`) baixa cada imagem, ignora duplicados e
   exibe uma barra de progresso (`tqdm`).
3. O **converter** (`converter.py`), quando `--webp` está ativo, redimensiona
   cada imagem para 512x512 mantendo a transparência e salva em
   `downloads/stickers/`. As figurinhas são limitadas a 100 KB (exigência do
   WhatsApp), reduzindo a qualidade automaticamente quando necessário.
4. O **packer** (`packer.py`), quando `--pack` está ativo, agrupa as
   figurinhas em arquivos `.wastickers` (ZIP com `title.txt`, `author.txt`,
   capa `tray.png` 96x96 e as figurinhas), em `downloads/packs/`. Cada pacote
   tem no máximo 30 figurinhas; quando há mais, são divididos em pacotes
   equilibrados.
5. O **app_export** (`app_export.py`), quando `--app-export` está ativo, escreve
   os pacotes e um `contents.json` válido direto na pasta `assets` do app oficial
   do WhatsApp (veja a seção abaixo), para você compilar o **seu próprio** app.

Ao final são exibidas as estatísticas: imagens encontradas, baixadas,
ignoradas, figurinhas geradas, pacotes montados e o tempo total.

## Importando no WhatsApp

Há duas formas de levar os pacotes para o WhatsApp — nenhuma exige enviar
imagem por imagem.

### A) App intermediário (mais rápido de começar)

O arquivo `.wastickers` (gerado por `--pack`) é lido por apps como
**Sticker Maker** (Android/iOS). Transfira o `.wastickers` para o celular,
abra-o com o app de figurinhas e escolha "Adicionar ao WhatsApp" — o pacote
inteiro entra de uma vez.

### B) Seu próprio app Android (sem app de terceiros)

O WhatsApp nunca lê um arquivo/pasta diretamente: ele só aceita pacotes vindos
de um app instalado, via um `ContentProvider`. Para não depender de apps de
terceiros, você compila **o seu próprio** app a partir do exemplo oficial do
WhatsApp e este projeto injeta os pacotes nele.

Requisitos: [Android Studio](https://developer.android.com/studio) (traz o JDK e
o Android SDK) e o celular Android com "Depuração USB" ligada.

Passos:

```bash
# 1. Clone o app de exemplo oficial do WhatsApp
git clone https://github.com/WhatsApp/stickers.git

# 2. Gere e injete os pacotes na pasta 'assets' do app
python main.py --url "URL_DA_BOARD" --app-export "stickers/Android/app/src/main/assets"
```

3. Abra a pasta `stickers/Android` no Android Studio, conecte o celular e clique
   em **Run** (instala o app no aparelho).
4. Abra o app instalado, escolha o pacote e toque em **"Adicionar ao WhatsApp"**.

Para adicionar pacotes novos depois, basta repetir os passos 2 e 3 (recompilar).
Cada figurinha recebe um emoji padrão (`✨`) no `contents.json`; você pode editar
esse arquivo para personalizar os emojis de cada figurinha.

> Observação: para uso pessoal não é preciso publicar na Play Store — instalar
> direto pelo Android Studio (sideload) já funciona. No iOS o caminho é bem mais
> restrito (exige distribuição pela App Store), por isso não é coberto aqui.

## Estrutura

```
PinterestDownloader/
├── main.py          # interface de terminal e orquestração
├── scraper.py       # navegação e extração de URLs (Playwright)
├── downloader.py    # download e deduplicação (Requests + tqdm)
├── converter.py     # conversão para figurinha WEBP (Pillow)
├── packer.py        # montagem dos pacotes .wastickers (zipfile)
├── app_export.py    # exporta para o app oficial WhatsApp/stickers (contents.json)
├── requirements.txt
└── README.md
```

## Observações

- Funciona apenas com boards **públicas**.
- O Pinterest pode alterar seu layout; caso nenhuma imagem seja encontrada,
  verifique se a URL está correta e se a board é pública.
- Respeite os Termos de Uso do Pinterest e os direitos autorais das imagens.
