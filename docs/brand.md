# Identidade visual — Kodaris Byte

Paleta extraída da logo e da capa da página no LinkedIn (valores aproximados, para refinar com os arquivos originais da marca).

| Token | Hex | Uso |
|---|---|---|
| `--kb-bg` | `#0B0B14` | Fundo principal (quase preto azulado) |
| `--kb-surface` | `#181828` | Superfícies / cards |
| `--kb-surface-2` | `#1C0F24` | Variação arroxeada da superfície |
| `--kb-violet-900` | `#2A1A48` | Sombras roxas profundas |
| `--kb-violet-700` | `#483868` | Roxo médio (aura da logo) |
| `--kb-violet-500` | `#7A5FB0` | Roxo de destaque |
| `--kb-lavender` | `#A898C8` | Cor principal da marca (letreiro "KODARIS BYTE" e "K") |
| `--kb-lavender-light` | `#C8B8E8` | Brilho / realces |

## Logo

- Original de referência: `assets/brand/logo-original-linkedin.png` (membrana com K de fibras).
- Versão animada escolhida pela equipe: **K lavanda dentro de uma esfera de plasma roxa**.
- Versão na capa: "K" geométrico lavanda entre parênteses — `( K )`.
- Tipografia do letreiro: sans-serif geométrica, caixa alta, espaçamento largo.

## Animação (Blender)

`blender/build_logo.py` monta a cena: esfera de plasma surge, filamentos acendem, K aparece com flash e fica pulsando.

### Arquivos gerados (`blender/renders/`)

| Arquivo | Uso |
|---|---|
| `kodaris_logo.mp4` | Intro animada 5 s, 1080×1080, fundo preto — no site usar `mix-blend-mode: screen` |
| `logo.png` / `logo-512.png` | Último frame (logo estática, fundo preto → também com `screen`) |
| `favicon-64.png` | Favicon |

Regerar: `blender -b --factory-startup --python blender/build_logo.py` e depois `blender -b blender/kodaris_logo.blend -a`.
