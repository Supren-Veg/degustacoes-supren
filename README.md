# Formulários de Degustação — Supren Veg

Formulários estáticos hospedados no GitHub Pages, usados no fluxo de degustações da Supren Veg.

URL pública: `https://supren-veg.github.io/degustacoes-supren`

> **Portal aposentado (jul/2026).** A listagem de degustações deixou de viver aqui.
> A entrada agora é o app **gestao-supren** (`/degustacoes`), que lista as degustações
> e abre estes formulários já preenchidos com os dados de cada evento. O antigo
> `portal.html` (e o `dashboard.html`/`dados.js` que ele usava) foi removido; o
> `index.html` agora só avisa que o portal saiu e aponta para o app.

## Estrutura

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Aviso de portal desativado, com link para o app |
| `form1_agendamento.html` | Formulário de agendamento (vendedor) |
| `form2_kit_briefing.html` | Montagem do kit (assina quem separou) |
| `form3a_vendedor.html` | Avaliação pós-evento (vendedor) |
| `form3b_degustador.html` | Avaliação pós-evento (degustador) |
| `form_api.js` | Envia os dados do formulário para a API do gestao-supren |
| `api_config.js` | Endereço e chave da API (ver observação abaixo) |
| `sincronizar_portal.py` | **Biblioteca** de sincronização Notion→Supabase (ver abaixo) |

## Como os formulários são abertos

Pelo app gestao-supren: **Degustações** → escolher a degustação → botão do formulário.
O app monta a URL do formulário aqui no Pages já com `?id=` e os campos do evento.
Abrir um formulário sem `?id=` faz o envio falhar de propósito (não há como associá-lo
a uma degustação) — o formulário avisa e orienta a abrir pelo app.

## Sincronização Notion → Supabase

A sincronização diária roda pelo `sync_app.py` (fora deste repositório, gitignored),
que **importa** `sincronizar_portal.py` como biblioteca (`fetch_todas_degustacoes`,
`parse_degustacao`, `sync_supabase`). Por isso `sincronizar_portal.py` continua aqui.

`sincronizar_portal.py` **não deve mais ser executado como script** — ele gerava o
portal estático, que não existe mais. Rodá-lo diretamente sai com aviso e erro.

## Observação de segurança

`api_config.js` contém a `FORMS_API_KEY` e está versionado neste repositório **público**.
Qualquer visitante consegue ler a chave e postar submissões na API. É inerente a um site
estático que chama uma API autenticada (o segredo precisa estar no cliente), mas fica
registrado — se as submissões passarem a alimentar indicadores, considerar mover o
recebimento para trás de uma verificação mais forte.

## Deploy

Push na branch `main` publica automaticamente no GitHub Pages.
