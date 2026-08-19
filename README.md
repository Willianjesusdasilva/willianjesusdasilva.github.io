# Presenter de ideias Markdown

O site é apenas um apresentador. Não existe editor e não existe banco ou arquivo JSON central.

## Como adicionar uma ideia

Crie um arquivo `.md` dentro de `ideas/`.

Todo arquivo deve começar com um JSON válido:

```text
{
  "nome": "Bico suplementar para o A3",
  "tags": ["a3", "esp32", "injeção"],
  "status": "pesquisando"
}

# Bico suplementar para o A3

Conteúdo da ideia em Markdown...
```

Campos esperados:

- `nome`: obrigatório, string.
- `tags`: lista de strings.
- `status`: string; se omitido, será `ideia`.

## Descoberta automática

`assets/js/app.js` consulta em tempo de execução:

`GET /repos/Willianjesusdasilva/willianjesusdasilva.github.io/contents/ideas?ref=master`

Como o repositório é público, não é necessário token.

Depois ele baixa cada `.md`, separa o JSON inicial e renderiza o restante usando `marked`. O HTML gerado passa por `DOMPurify` antes de ser exibido.

Portanto, para publicar uma nova ideia basta adicionar o `.md` à pasta `ideas/` e fazer push.

## Estrutura

```text
index.html
ideas/
  exemplo.md
assets/
  css/
    minimal.css
    presenter.css
  js/
    app.js
```

O `minimal.css` mantém o estilo original do site. `presenter.css` contém apenas os complementos necessários para lista, metadados e Markdown.
