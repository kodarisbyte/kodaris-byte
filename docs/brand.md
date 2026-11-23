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

- Símbolo: membrana gelatinosa lavanda com um **K** formado por feixes de fibras trançadas, fios soltos enrolando por dentro (original: `assets/brand/logo-original-linkedin.png`).
- Versão na capa: "K" geométrico lavanda entre parênteses — `( K )`.
- Tipografia do letreiro: sans-serif geométrica, caixa alta, espaçamento largo.

## Animação (Blender)

Objetivo: versão animada da logo (esfera de plasma pulsando com o K surgindo), renderizada com fundo transparente para uso no hero do site.

### Arquivos gerados (`blender/renders/`)

| Arquivo | Uso |
|---|---|
| `logo-intro.webm` | Intro animada 4 s, VP9 **com transparência** (Chrome, Edge, Firefox) |
| `logo-intro.mp4` | Mesma intro sobre `#0B0B14` (fallback para Safari) |
| `logo.png` / `logo-512.png` | Logo estática transparente (header, redes) |
| `favicon-64.png` | Favicon |

Regerar: `blender -b --factory-startup --python blender/build_logo.py` e depois `blender -b blender/kodaris_logo.blend -a`.
