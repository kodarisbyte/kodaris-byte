# Como trabalhar no projeto (guia para quem nunca usou Git)

Este guia explica, passo a passo, como pegar o projeto, fazer uma mudança e mandar para o time revisar. Não precisa saber nada de Git antes.

## O básico em 1 minuto

- **Git** guarda o histórico de todas as mudanças do projeto. Dá para ver quem mudou o quê e voltar atrás se algo quebrar.
- **GitHub** é o site onde o projeto fica guardado: https://github.com/kodarisbyte/kodaris-byte
- **Repositório (repo)** é a pasta do projeto, com todo o histórico.
- **Commit** é um "salvamento" com uma descrição do que você mudou.
- **Branch** é uma cópia paralela do projeto onde você trabalha sem mexer na versão oficial.
- **`main`** é a branch oficial. Ninguém trabalha direto nela.
- **Pull Request (PR)** é o pedido para juntar a sua branch na `main`. Alguém do time revisa antes.

O fluxo de todo dia é sempre o mesmo:

```
atualizar a main → criar uma branch → mudar arquivos → commit → enviar → abrir PR → revisão → merge
```

---

## Parte 1: preparar o computador (só uma vez)

### 1. Aceite o convite da organização

Você recebeu um convite por e-mail para a organização **kodarisbyte** no GitHub. Aceite por lá ou em https://github.com/kodarisbyte. Sem isso você não consegue enviar mudanças.

### 2. Instale os programas

| Programa | Para quê | Onde baixar |
|---|---|---|
| **GitHub Desktop** | Usar Git com botões, sem terminal | https://desktop.github.com |
| **VS Code** | Editar o código | https://code.visualstudio.com |
| **Node.js (versão LTS)** | Rodar o site no seu computador | https://nodejs.org |

O GitHub Desktop já instala o Git junto.

### 3. Entre na sua conta no GitHub Desktop

Abra o GitHub Desktop, vá em **File → Options → Accounts** e clique em **Sign in** com a sua conta do GitHub.

### 4. Baixe o projeto (clonar)

1. No GitHub Desktop: **File → Clone repository**.
2. Na aba **GitHub.com**, escolha `kodarisbyte/kodaris-byte`.
3. Escolha a pasta onde o projeto vai ficar (por exemplo `Documentos\kodaris-byte`) e clique em **Clone**.

### 5. Rode o site no seu computador

1. No GitHub Desktop: **Repository → Open in Visual Studio Code**.
2. No VS Code, abra o terminal: **Terminal → New Terminal**.
3. Digite, um comando por vez:

```bash
cd site
npm install
npm run dev
```

4. Abra no navegador o endereço que aparecer (normalmente http://localhost:4321/kodaris-byte/).

O `npm install` só precisa ser feito na primeira vez (ou quando alguém adicionar uma biblioteca nova). Para parar o site, clique no terminal e aperte `Ctrl + C`.

---

## Parte 2: o dia a dia

### Passo 1: atualize a `main` antes de começar

Sempre comece com a versão mais recente do projeto.

1. No topo do GitHub Desktop, em **Current branch**, escolha `main`.
2. Clique em **Fetch origin** e depois em **Pull origin** (se aparecer).

### Passo 2: crie uma branch para a sua tarefa

1. Clique em **Current branch → New branch**.
2. Dê um nome curto que diga o que você vai fazer, em minúsculas e com hífen:
   - `secao-equipe`
   - `corrige-menu-celular`
   - `case-loja-x`
3. Confirme que ela parte da `main` e clique em **Create branch**.

Uma branch = uma tarefa. Terminou a tarefa, abre o PR. Tarefa nova, branch nova.

### Passo 3: faça as mudanças

Edite os arquivos no VS Code normalmente e salve (`Ctrl + S`). Com `npm run dev` rodando, o site no navegador atualiza sozinho.

O GitHub Desktop mostra na lateral esquerda todos os arquivos que você mudou, com as linhas removidas em vermelho e as adicionadas em verde. Confira se só estão ali as mudanças que você quis fazer.

### Passo 4: faça um commit

1. No canto inferior esquerdo do GitHub Desktop, escreva um **resumo** do que você fez.
2. Clique em **Commit to nome-da-sua-branch**.

Como escrever um bom resumo:

| Bom | Ruim |
|---|---|
| `Adiciona seção de equipe com fotos` | `mudanças` |
| `Corrige menu cortado no celular` | `fix` |
| `Atualiza texto do case ERP UNA` | `asdf` |

Faça commits pequenos e frequentes, um para cada parte que fizer sentido sozinha. Fica mais fácil de revisar e de desfazer.

### Passo 5: envie para o GitHub

Clique em **Publish branch** (na primeira vez) ou **Push origin** (nas próximas). Até aqui, tudo estava só no seu computador.

### Passo 6: abra um Pull Request

1. Depois do push, o GitHub Desktop mostra o botão **Create Pull Request**. Clique nele e o navegador abre.
2. Preencha o título e a descrição (o modelo já vem pronto: o que mudou, como testar e um print se mexeu no visual).
3. Clique em **Create pull request**.
4. Avise o time no grupo que tem um PR esperando revisão.

### Passo 7: revisão e merge

- Alguém do time lê o PR, testa e aprova, ou comenta pedindo ajustes.
- Para ajustar: continue na mesma branch, faça novos commits e dê **Push origin**. O PR atualiza sozinho. Depois de um ajuste, a aprovação anterior cai e alguém precisa aprovar de novo.
- Cada comentário da revisão precisa ser marcado como **Resolve conversation** antes do merge.
- Depois de aprovado, clique em **Merge pull request** no GitHub. Pronto, a mudança está na `main`.
- Volte ao **Passo 1** para a próxima tarefa.

---

## Regras do time

1. **Nunca trabalhe direto na `main`.** Sempre crie uma branch. O GitHub bloqueia push direto na `main`: se aparecer um erro de *protected branch*, é isso.
2. **Todo PR precisa da aprovação de outra pessoa** antes do merge. O botão de merge só libera depois disso.
3. **Teste antes de abrir o PR**: rode `npm run dev` e confira no navegador, também com a janela estreita (celular).
4. **Não suba senhas, chaves ou arquivos pessoais.** Na dúvida, pergunte antes.
5. **Atualize a `main` todo dia** antes de começar (Passo 1).

---

## Quando algo dá errado

### "Minha branch ficou desatualizada" ou o PR diz *This branch is out-of-date*

No GitHub Desktop, com a sua branch aberta: **Branch → Update from main**. Depois dê **Push origin**.

### Conflito (*conflict*)

Acontece quando você e outra pessoa mudaram a mesma linha do mesmo arquivo. Não é grave.

1. O GitHub Desktop mostra os arquivos em conflito. Clique em **Open in Visual Studio Code**.
2. O VS Code marca os dois lados da mudança. Escolha **Accept Current Change** (a sua), **Accept Incoming Change** (a da outra pessoa) ou **Accept Both Changes**. Se precisar, edite à mão até ficar certo.
3. Salve o arquivo, volte ao GitHub Desktop, faça o commit e dê **Push origin**.

Se ficar na dúvida, peça ajuda no grupo antes de escolher. Ninguém perde trabalho num conflito.

### "Fiz commit na `main` sem querer"

Não dê push. Peça ajuda no grupo que alguém resolve com você em 2 minutos.

### "Quero desfazer o que mudei num arquivo"

No GitHub Desktop, clique com o botão direito no arquivo → **Discard changes**. Atenção: isso apaga as mudanças não commitadas daquele arquivo.

### "Quero desfazer o último commit (ainda não dei push)"

**History** (aba lateral) → botão direito no commit → **Undo commit**. As mudanças voltam para você editar.

---

## Para quem prefere o terminal

Os mesmos passos, em comandos:

```bash
# Passo 1: atualizar a main
git switch main
git pull

# Passo 2: criar uma branch
git switch -c secao-equipe

# Passo 4: ver o que mudou e fazer o commit
git status
git add .
git commit -m "Adiciona seção de equipe com fotos"

# Passo 5: enviar
git push -u origin secao-equipe      # na primeira vez
git push                             # nas próximas

# Passo 6: abrir o PR (com o GitHub CLI instalado)
gh pr create --fill

# Branch desatualizada
git switch main && git pull
git switch secao-equipe && git merge main
```

---

## Onde fica cada coisa

| Pasta | O que tem |
|---|---|
| `site/src/pages/index.astro` | O conteúdo e o visual da página. Serviços, projetos e etapas ficam em listas no topo do arquivo. |
| `site/src/scripts/intro.ts` | A animação de abertura da logo |
| `site/src/styles/global.css` | Cores, fontes e estilos gerais |
| `site/public/media/` | Imagens e vídeos usados no site |
| `blender/` | Arquivos da logo animada no Blender |
| `docs/brand.md` | Cores e regras da identidade visual |
