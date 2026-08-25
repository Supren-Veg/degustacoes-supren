# Listas de produtos dos formulários

Existem **duas** listas de produtos no fluxo de degustação, e elas não são
intercambiáveis. Este arquivo é a referência única — antes de editar qualquer lista
em formulário, confira aqui qual delas é.

## 1. Produtos de venda (estoque)

Usados no **formulário do vendedor** (`form3a_vendedor.html`): verificação de estoque
(antes e depois da degustação, mais a quantidade a repor) e "produtos incluídos no
pedido". O agendamento não anota mais estoque — a verificação passou para o vendedor
em 2026-08-10, que é quem vê o estoque no dia.

| Chave do campo | Produto |
|---|---|
| `empada_palmito_160` | Empada de Palmito 160g |
| `empada_espinafre_160` | Empada de Espinafre 160g |
| `lasanha_berinjela_410` | Lasanha de Berinjela 410g |
| `discos_proteicos_240` | Discos Proteicos 240g |
| `quiche_palmito_130` | Quiche de Palmito 130g |
| `pao_sem_queijo_450` | Pão sem Queijo 450g |
| `empada_maca_120` | Empada de Maçã 120g |
| `estrogonofe_450` | Estrogonofe 450g |
| `empada_palmito_375` | Empada de Palmito 375g |
| `lasanha_abobrinha_410` | Lasanha de Abobrinha 410g |

Sufixos: `_antes`, `_depois` e `_repor` na verificação de estoque. Respostas anteriores
a 2026-08-10 têm `_usado` (e `p1_usado`..`p5_repor`, ainda mais antigas) — o relatório
continua lendo essas chaves, então não reaproveitar nenhuma delas para outro produto.

## 2. Produtos degustados (porções servidas no evento)

Usados no **formulário do degustador** (`form3b_degustador.html`, porções servidas e
descartadas — chaves `p1s`/`p1d`..`p5s`/`p5d`) e em "produto mais comentado pelo
cliente" no formulário do vendedor.

| Posição | Produto |
|---|---|
| 1 | Empada de Maçã PP |
| 2 | Empada de Espinafre PP |
| 3 | Empada de Palmito PP |
| 4 | Discos Proteicos 30g |
| 5 | Estrogonofe de Grão de Bico |

## Por que separadas

São itens de porção (amostra servida no evento) contra itens de venda (o que o cliente
repõe). Misturar as duas atrapalharia tanto a leitura do relatório quanto qualquer
cruzamento futuro entre o que foi degustado e o que foi vendido.

## Cuidado ao renomear chaves

As respostas já enviadas ficam em `form_submissions.dados` (JSON) exatamente com o nome
de campo daquele momento. Chave renomeada **não** migra sozinha: quem lê precisa aceitar
a antiga também. É o que faz `lib/degustacoes-reposicao.ts` no `gestao-supren`, que
mantém as chaves posicionais `p1`..`p5` usadas até 2026-08-06 — e elas nunca podem ser
reaproveitadas por outro produto.
