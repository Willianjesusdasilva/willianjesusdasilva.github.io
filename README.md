# Idea Presenter · PyScript

Apresentador de ideias em Markdown para GitHub Pages.

## O que mudou

- Brython saiu da aplicação.
- A lógica de listagem, busca, leitura do JSON inicial e navegação está em `assets/py/app.py` usando PyScript.
- Foto, nome, bio e empresa continuam vindo automaticamente do perfil público do GitHub.
- Os `.md` são descobertos automaticamente na pasta `ideas/` pela API pública do GitHub.
- Não existe `ideas.json`, backend ou build.
- Markdown é renderizado com `marked.js` e sanitizado com `DOMPurify`.

## Formato de uma ideia

```md
{
  "nome": "Minha ideia",
  "tags": ["python", "automotivo"],
  "status": "ideia"
}

# Minha ideia

Conteúdo aqui.
```

## Aplicar no repositório

Copie o conteúdo do ZIP por cima do repositório. A pasta `ideas/` que você já tem pode permanecer normalmente.

Depois rode:

```powershell
git add .
git commit -m "Migra apresentador de ideias para PyScript"
git push origin master
```

Os arquivos antigos do Brython não são mais referenciados. Se quiser removê-los, execute `cleanup-brython.ps1`.
