# Kodaris Byte

> Transformamos ideias em software. Apps, sites e sistemas sob medida para o seu negócio.

Site institucional e portfólio da **Kodaris Byte** (Niterói, RJ).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `site/` | Código do site (portfólio) |
| `blender/` | Arquivos `.blend` da logo animada |
| `blender/renders/` | Renders finais da animação (vídeo/WebM com alpha) usados no site |
| `assets/brand/` | Logo, capa e materiais da marca |
| `docs/` | Documentação: identidade visual, decisões |

## Identidade visual

Veja [`docs/brand.md`](docs/brand.md).

## Como contribuir

Nunca usou Git? Comece pelo [guia de workflow](CONTRIBUTING.md): instalação, dia a dia com branches e Pull Requests, e o que fazer quando algo dá errado.

## Site (Astro + GSAP)

```bash
cd site
npm install
npm run dev      # http://localhost:4321/kodaris-byte/
npm run build    # gera site/dist
```

- Página: `site/src/pages/index.astro` (serviços, projetos e etapas ficam em listas no topo do arquivo — para adicionar um case, acrescente um item em `projetos`).
- Intro animada: `site/src/scripts/intro.ts`. A logo toca grande no centro, encolhe enquanto o site aparece e vai para o canto superior esquerdo. Roda uma vez por sessão e é pulada com "reduzir movimento" ativado no sistema.
- Mídia: `site/public/media/` (gerada a partir de `blender/renders/`).

### Pendências de conteúdo
- E-mail e WhatsApp da empresa na seção Contato (hoje só LinkedIn).
- Mais cases além do ERP UNA.
