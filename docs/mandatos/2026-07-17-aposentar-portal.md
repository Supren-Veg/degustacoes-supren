# Mandato — Aposentar o portal estático de degustações

- **Data:** 2026-07-17
- **Projeto:** degustacoes-supren (`Estrutura de Degustações`)
- **Solicitante:** Ygor
- **Status:** aprovado (direção) — executado nesta worktree, pendente de merge

## Objetivo

Remover o portal estático (`portal.html` e suas dependências), que era uma listagem
paralela e desatualizada das degustações, e fazer o app gestao-supren (`/degustacoes`)
ser a única entrada. O app já lista as 46 degustações e linka estes formulários direto.

## Contexto

O portal publicado estava com os dados congelados em 10/04/2026: 35 das 46 degustações
nunca tiveram card nem link. Foi a causa de 9 de 11 degustações concluídas em 45 dias
não terem recebido formulário. Como o app já acessa os formulários direto
(`degustacoes-view.tsx:15`, `BASE = https://supren-veg.github.io/degustacoes-supren`),
o portal virou duplicata morta e confusa.

## Achado que mudou o conjunto aprovado (importante)

A decisão original listava **apagar `sincronizar_portal.py`**. Isso é INSEGURO:
`sync_app.py` (a sincronização diária Notion→Supabase, gitignored/local) faz
`import sincronizar_portal as s` e usa `fetch_todas_degustacoes`, `parse_degustacao`,
`sync_supabase` e `log`. Apagá-lo derrubaria a lista de degustações do app inteiro.

**Ajuste:** o arquivo permanece como biblioteca; apenas o bloco `if __name__ == "__main__"`
foi neutralizado (deixa de gerar/publicar o portal e sai com aviso+erro). As funções
importadas por `sync_app.py` ficam intactas.

## Escopo

**Removido:**
- `portal.html` — listagem congelada
- `dashboard.html` — segunda tela de estatísticas que lia o `dados.js`
- `dados.js` — dados congelados
- `sincronizar_automatico.bat` — wrapper agendado (caminho quebrado desde a mudança de pasta)

**Alterado:**
- `sincronizar_portal.py` — `__main__` neutralizado; funções de biblioteca preservadas
- `index.html` — passa de redirect para `portal.html` a página de aviso "portal desativado" com link para o app
- `form5_relatorio.html` — removido o link "Voltar ao Portal" do banner de sucesso
- `README.md` — reescrito refletindo a aposentadoria

**Fora (não tocado):**
- `sync_app.py` (não versionado; depende do `sincronizar_portal.py`)
- `form_api.js`, `api_config.js`, os 6 formulários (envio)
- gestao-supren

## Verificação (Art. IV)

- Nenhuma referência de código a `portal.html`/`dashboard.html`/`dados.js`/`.bat` sobrou
  (só prosa histórica no mandato do PR #7).
- `import sincronizar_portal` OK com as 4 funções que o `sync_app.py` usa presentes.
- `pytest tests/` verde (9/9) — a rede do PR #7 não regrediu.
- `index.html` renderizado conferido em navegador headless.

## Riscos

| Risco | Mitigação |
|---|---|
| Quem tem o link antigo salvo cai em página morta | `index.html` vira aviso com link para o app (decisão do Ygor). |
| `sincronizar_portal.py` rodado como script por engano ressuscitaria o portal | `__main__` neutralizado (sai com erro). O `.bat` que o auto-executava foi removido. |
| Perda da geração de `api_config.js` (era `write_api_config_js()` no `main()`) | A função continua definida; `api_config.js` já está commitado e é estável. Editar à mão se a chave mudar. Registrado no README. |
| Tarefa agendada no Windows ainda apontando para o `.bat` removido | Passará a falhar (já falhava pela mudança de pasta). Ygor deve remover a entrada no Agendador se existir. |

## Pendência de processo (não é código)

- Reorientar o time para `/degustacoes` no app (o link antigo agora avisa, mas convém a mensagem direta).
- `api_config.js` expõe `FORMS_API_KEY` em repo público — registrado no README; decisão futura.
