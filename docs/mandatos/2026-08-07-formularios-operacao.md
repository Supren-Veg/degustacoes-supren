# Mandato — Ajustes dos formulários pedidos pela operação

- **Data:** 2026-08-07
- **Projeto:** degustacoes-supren (formulários) + gestao-supren (app)
- **Solicitante:** Ygor — "todas essas alterações devem ser feitas o quanto antes, pois
  o módulo já está sendo usado e é extremamente necessário para a nossa operação"
- **Status:** aprovado (pedido em sessão, com duas decisões confirmadas por pergunta)

## Escopo

**1.1 Kit/Briefing (`form2_kit_briefing.html`)**
- Conferência do kit ganha extensão elétrica, caixas vazias para amostra, álcool e
  perfex (11 → 15 itens).
- Sai a seção de briefing com a degustadora (HTML, JS e validação).
- Entrega passa a ser ao **cliente**, não ao degustador.
- Impressão cabe em uma folha: `@page` A4 8 mm, 10 pt, checklist em duas colunas,
  progresso e barra superior ocultos.

**1.2 Agendamento (`form1_agendamento.html`), item 3**
- Os 10 produtos reais da operação (ver `docs/PRODUTOS.md`), cada um com campo para
  anotar o estoque existente. Sai o sim/não com quantidade sugerida.
- O alerta de "não agendar" passa a disparar quando algum produto é anotado como zerado.

**1.3 Vendedor (`form3a_vendedor.html`)**
- Reposição de estoque e "produtos incluídos no pedido" com os mesmos 10 produtos.
- **"Produto mais comentado" fica como está** — decisão do Ygor: são os itens
  degustados, não os de venda.

**1.4 Formulários aposentados**
- `form5_relatorio.html` (Relatório Final) e `form4_devolucao.html` (Devolução, fora do
  app desde julho). **Decisão do Ygor:** ficam quatro — agendamento, kit, vendedor e
  degustadora.
- No `gestao-supren`, o botão do Relatório Final sai do fluxo (PR #65), senão vira 404.

## Fora de escopo

- `form3b_degustador.html` (degustadora) — intocado nesta tarefa.
- Renumerar `form_numero` dos formulários que ficam: mudaria o dono das respostas já
  gravadas em `form_submissions`.
- Tornar os campos de estoque obrigatórios: hoje são opcionais. Obrigar dez números no
  agendamento adicionaria a mesma fricção que travou o formulário da degustadora nesta
  semana. **Aberto para o Ygor decidir.**

## Achado crítico da revisão (corrigido antes do merge)

Renomear os campos de reposição (`p1_usado` → `empada_palmito_160_usado`) apagaria a
seção "Reposição de estoque" do relatório do `gestao-supren` — sem erro e com o dado
presente no banco. Corrigido no PR #66: `lib/degustacoes-reposicao.ts` lê as chaves
novas **e** as antigas, com teste fixando que `p1`..`p5` nunca sejam reaproveitadas.

## Verificação

- `pytest`: 19 testes nos formulários (`test_form_api.py` + `test_formularios_operacao.py`,
  este último criado aqui para versionar a verificação — antes ela dependia de um script
  jsdom fora do repositório, irreproduzível por quem clonasse).
- `gestao-supren`: 249/249, `tsc` e `eslint` limpos.
- Ordem de deploy: PR #66 e #65 (app) **antes** da publicação do Pages.
