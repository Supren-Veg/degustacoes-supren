# Mandato — Corrigir a falha silenciosa de envio dos formulários

- **Data:** 2026-07-17
- **Projeto:** degustacoes-supren (`Estrutura de Degustações`)
- **Solicitante:** Ygor
- **Status:** rascunho

## Objetivo

Fazer os 6 formulários dizerem a verdade sobre o envio: quando o POST não chega à API, o usuário **vê** que não chegou e sabe o que fazer. Nenhum "Enviado!" sem envio confirmado.

## Contexto

Em 45 dias: 13 degustações, 11 concluídas, **9 sem nenhum formulário**. A causa da ausência de dado foi o portal congelado em 10/04 (`sincronizar_automatico.bat:7` aponta para caminho inexistente) — 35 das 46 degustações nunca tiveram card nem link, então não havia formulário a preencher. O Ygor vai reorientar o time para o app (`/degustacoes`), que funciona e linka **estes mesmos** formulários.

Ou seja: **a partir de agora o time vai preencher de verdade.** É isso que torna a falha silenciosa prioridade 1 — sem corrigi-la, é impossível distinguir "não preencheram" de "preencheram e o dado evaporou", e o futuro painel de KPI (mandato suspenso) leria envio falho como baixo desempenho de pessoas reais. Corrigir o feedback **antes** do volume chegar é o que impede um KPI que acusa gente inocente.

**Defeitos confirmados (não re-verificar):**
- `form_api.js:41` — POST **e** localStorage condicionados a `?id=`. Sem id: no-op absoluto e silencioso.
- `form_api.js:54` — `catch (_) {}` engole rede/4xx/5xx; nunca checa `resp.ok`, então 4xx/5xx passam como sucesso **sem exception**.
- `form_api.js:2` — cabeçalho "Gerado automaticamente por sincronizar_portal.py — NÃO EDITE MANUALMENTE" é **falso**: o `.py` só gera `api_config.js` (`write_api_config_js()`, :255) e apenas faz `git add` do form_api.js (:352). É fonte à mão (ddd255e). O cabeçalho mente para o próximo dev/agente exatamente sobre o arquivo que precisa ser editado → remover.
- `form5_relatorio.html:1304-1320` — **não usa** o form_api.js; tem fetch inline próprio com `catch (_) {}` (:1317) e banner de sucesso incondicional (:1324). Segundo caminho de envio, mesmo defeito, e é o Relatório final (form_numero **6**) — o mais importante para o KPI.
- Sucesso incondicional após o `await` nos 6: form1:855-857, form2:827-828, form3a:760-761, form3b:825-826, form4:826-827, form5:1322-1324.
- Mapeamento: `1=Agendamento 2=Kit 3=Vendedor 4=Degustador 5=Devolução 6=Relatório` (o **arquivo** `form5_relatorio.html` grava como **6** — nome de arquivo ≠ form_numero).

**API confirmada sadia** em produção (read-only: Bearer→200, sem Bearer→401, preflight do github.io→204 com CORS correto). Não há bug de servidor — nada a mexer no gestao-supren.

**Dois achados desta análise que mudam o desenho:**
1. `form5_relatorio.html:1297-1301` **já salva no localStorage sem id**, com chave de fallback `relatorio_sem_id_<cliente>_<data>` — comportamento melhor que o do helper (que no-opa sem id). Esse comportamento vira o padrão do helper (D2), não se perde na migração.
2. As UIs de sucesso **divergem**: form1/2/3a/4 mutam o texto do botão (`'Enviado!'`), form3b/form5 exibem um `successBanner`. Isso decide a questão da centralização (D1).

## Escopo

**Dentro:**
- `form_api.js` — retorno de resultado, checagem de `resp.ok`, localStorage sempre, banner de erro genérico, remoção do cabeçalho falso.
- Os 6 HTMLs — guardar o bloco de sucesso pelo resultado; migrar o form5 para o helper.
- `tests/test_form_api.py` — rede anti-regressão em pytest (padrão de `tests/test_sincronizar.py`).

**Fora (não tocar):**
- `sincronizar_automatico.bat` / portal congelado / `sincronizar_portal.py` — o portal está sendo abandonado em favor do app; consertar o sync é outra decisão do Ygor.
- `api_config.js` — este **é** gerado de verdade pelo `.py`; o cabeçalho dele é verdadeiro.
- `gestao-supren` (API sadia), validação de payload no servidor.
- Fila de sincronização, service worker, retry automático, indicador de "pendente para reenvio". **YAGNI** — o objetivo é feedback verdadeiro, não robustez.
- npm, bundler, dependência, framework. São páginas estáticas e continuam assim.

## Decisões de arquitetura

### D1 — Centralizar o feedback no `form_api.js`? → **Sim, o resultado e o erro. Não o sucesso.**

| Opção | Trade-off |
|---|---|
| A) Helper renderiza tudo (sucesso + erro) | Elimina a repetição, mas o helper teria de conhecer o DOM de cada form (botão `'Enviado!'` vs. `successBanner`) ou substituir 6 UIs de sucesso que já existem e funcionam. Troca duplicação por acoplamento pior. Rejeitada. |
| B) Helper só retorna status; cada form renderiza sucesso **e** erro | Desacoplado, mas duplica a mensagem de erro (e a orientação de recuperação) 6×. É a mesma falha de DRY que gerou dois caminhos de envio divergentes. Rejeitada. |
| **C) Híbrido — recomendada** | Helper decide `{ok, motivo}` **e** renderiza o erro (banner genérico que ele mesmo cria, sem markup por form). Cada form mantém sua UI de sucesso, agora guardada por `if (r.ok)`. |

**Justificativa:** os 6 forms serão tocados de qualquer jeito — só o form sabe suprimir a própria UI de sucesso. Dado isso, o que sobra para centralizar é o que é **idêntico** nos 6: a lógica "chegou ou não" e a mensagem de falha. O helper já é o ponto comum de 5 deles; o form5 entra (E4).

### D2 — `id` ausente → salvar local **sempre** e mostrar erro (nunca no-op)

`submitToApi` passa a: (1) salvar no localStorage **sempre**, inclusive sem id, sob `form<n>_sem_id_<timestamp>` — generalização do que o form5 já faz; (2) retornar falha com `motivo`. Motivos: `sem_id`, `sem_config`, `rede`, `http_<status>`. Preserva o fallback (degustador em campo, celular, rede ruim) sem mentir que enviou.

### D3 — Cache-busting no `<script src>`

O GitHub Pages publica direto da `main` e o navegador pode servir `form_api.js` antigo — o usuário continuaria vendo a versão que mente. Como os 6 HTMLs já serão editados, incluir `form_api.js?v=2` no `src`. Custo zero, sem infra.

### D4 — Mensagem do erro

Precisa dizer as três coisas, sem jargão: **não foi enviado**, **está salvo neste aparelho**, **o que fazer** (reenviar com internet, pelo link do app). No caso `sem_id`, a orientação certa é "abra o formulário pelo link do app (`/degustacoes`)" — o erro vira onboarding para o fluxo novo.

## Micro-etapas (Art. II.5 / Art. IV)

| # | Entrega | Evidência de verificação |
|---|---|---|
| 1 | `form_api.js`: remover cabeçalho falso (:2); `submitToApi` retorna `{ok, motivo, salvoLocal}`; checar `resp.ok`; localStorage sempre (D2); `sem_config` deixa de ser skip mudo. **Sem UI ainda.** | Servir local + stub; no console, o objeto retornado nos 4 cenários (200 / 500 / offline / sem `?id=`). Os 5 forms seguem funcionando como antes (sem regressão). |
| 2 | Banner de erro genérico dentro do `form_api.js` (o helper cria o elemento; zero markup por form), exibido quando `!ok`, com a mensagem de D4. | Stub 500 → banner aparece. Offline (DevTools) → banner aparece. |
| 3 | Guardar o sucesso dos 5 forms com `if (r.ok)`: form1:855-857, form2:827-828, form3a:760-761, form3b:825-826, form4:826-827. Mudança mecânica idêntica + `?v=2` (D3). | Por form: stub 200 → sucesso normal; stub 500 → **não** diz 'Enviado!' e mostra erro; localStorage tem o dado nos dois casos. |
| 4 | `form5_relatorio.html`: trocar o fetch inline (1304-1320) por `submitToApi(6, ...)`, incluir `<script src="form_api.js?v=2">`, guardar o `successBanner` (:1322-1324) por `if (r.ok)`. Mata o segundo caminho de envio. | Idem E3 + confirmar no Network que a URL termina em `/6` (não `/5`). |
| 5 | `tests/test_form_api.py` (pytest, padrão de `tests/test_sincronizar.py`) travando os invariantes: nenhum `catch (_) {}` mudo; `resp.ok` checado; nenhum `submitToApi(` sem uso do retorno; nenhum `'Enviado!'`/banner fora de guarda; form5 sem fetch inline. | `pytest tests/` verde. |

**Verificação sem POST em produção** (Art. IV, e a restrição é dura): servir o repo com `python -m http.server` e, no console do DevTools, `window.FORMS_API_BASE = 'http://localhost:8787'` **antes** de submeter — aponta para um stub local descartável que responde 200/500 sob demanda. Não edita `api_config.js` (evita risco de commitar config de teste) e não toca a produção. Falha de rede: DevTools → Offline. **Nunca** exercitar cenário de falha contra a API real.

## Autonomia concedida

**Pode decidir sozinho:** forma do objeto de retorno, nomes dos motivos, markup/estilo do banner (seguindo `supren-governanca/BRANDING.md`), redação final da mensagem (respeitando D4), casos do teste estático.

**Exige aprovação do Ygor:**
- Qualquer coisa além do feedback (fila, retry, service worker) — é o limite explícito do MVP.
- Mexer no `sincronizar_portal.py`, no `.bat` ou em `api_config.js`.
- Alterar o gestao-supren.
- Adicionar dependência/npm/bundler.

## Riscos e rollback

**Rollback: baixo — revertível pelo git.** Só arquivos estáticos atrás de PR. Se algo quebrar em produção, `git revert` + push na `main` republica em minutos. Nenhum dado é destruído: o localStorage só passa a ser escrito **mais** vezes que hoje.

| Id | Risco | Mitigação |
|---|---|---|
| R1 | **Sem staging:** Pages publica direto da `main` no merge; bug vai a todos de imediato | Verificação manual dos 5 cenários por form **antes** do PR (E1-E4) + rede estática (E5). Revert é rápido. |
| R2 | Cache: usuário continua com o `form_api.js` velho, que mente | D3 (`?v=2`). Sem isso, a correção não chega a quem já abriu o form. |
| R3 | Form5 muda a chave do localStorage (`relatorio_<id>` → `form6_<id>`); relatórios salvos localmente sob a chave antiga ficam órfãos | Aceito: o dado continua no localStorage do aparelho, recuperável à mão se preciso. **Não** construir migração (YAGNI). Provável impacto ~zero: com o portal congelado, quase não houve preenchimento. |
| R4 | **Fadiga de alarme:** rede ruim em campo → erro recorrente → o time ignora ou abandona o preenchimento | Mensagem de D4: "salvo neste aparelho, **não** enviado" + o que fazer. O erro precisa parecer acionável, não um pop-up de sistema. Se virar queixa recorrente, aí sim discutir fila — não antes. |
| R5 | `id` ausente vira erro visível em uso legítimo — o form1 tem caminho de PDF/impressão (`salvarEGerar`), que pode ser aberto sem `?id=` de propósito | Aceito e correto: sem id o dado **realmente** não é enviado; hoje isso é mudo. A mensagem `sem_id` orienta a abrir pelo app. Se o Ygor confirmar que existe fluxo legítimo sem id, reavaliar só o tom da mensagem — não o fato de avisar. |
| R6 | Falso senso de conclusão: o feedback conserta o **futuro**; os 9 eventos sem formulário continuam sem dado | Fora de escopo aqui. O painel de KPI (mandato suspenso) só ganha base depois que o volume novo entrar. |
| R7 | Uma tela de erro que não aparece (bug no próprio banner) reproduz o problema original em outra camada | E2 é verificada isoladamente, antes de qualquer form depender dela. |

**Observação de segurança (fora de escopo, reportar ao Ygor):** `api_config.js` traz `FORMS_API_KEY` em repo público publicado no github.io — a chave é lida por qualquer visitante. É inerente a site estático que chama API autenticada (o segredo tem de estar no cliente), então provavelmente é aceito por desenho; registrado aqui porque não deve seguir implícito.

## Execução (fluxo git — Art. I)

Repo diferente do gestao-supren; a pasta principal está na `main`. Trabalho em worktree própria:

```
git worktree add C:\c\tmp\degustacoes-feedback-envio-wt -b fix/feedback-envio-formularios origin/main
```

Dentro da worktree: `docs/mandatos/` **não existe neste repo** — criar a pasta e salvar como `docs/mandatos/2026-07-17-falha-silenciosa-envio.md`. Commits atômicos por micro-etapa, push, PR com `/cto-review`. Conferir `git branch --show-current` antes de cada `add/commit/push`. Após o merge (que publica no Pages):

```
git worktree remove C:\c\tmp\degustacoes-feedback-envio-wt
```

## Critérios de conclusão

- [ ] Nenhum dos 6 formulários exibe sucesso sem `resp.ok` confirmado (form1:855-857, form2:827-828, form3a:760-761, form3b:825-826, form4:826-827, form5:1322-1324).
- [ ] Falha de rede, 4xx e 5xx produzem erro **visível** — verificado por form com stub local (200/500/offline).
- [ ] `?id=` ausente → erro visível com orientação, **não** no-op silencioso.
- [ ] localStorage preservado e gravado **sempre**, inclusive sem id e em qualquer falha.
- [ ] `form5_relatorio.html` usa o `form_api.js`; não resta fetch inline; envia como form_numero **6**.
- [ ] Cabeçalho falso removido do `form_api.js`; o de `api_config.js` intacto.
- [ ] `?v=2` nos `<script src>` dos 6 forms.
- [ ] `pytest tests/` verde, incluindo `tests/test_form_api.py`.
- [ ] Nenhuma dependência/npm/bundler; nenhuma fila/retry/service worker; nada alterado no gestao-supren nem no `.py`/`.bat`.
- [ ] Nenhum POST de teste contra produção durante todo o trabalho.
- [ ] Mandato salvo em `docs/mandatos/2026-07-17-falha-silenciosa-envio.md` (pasta criada).
- [ ] PR aberto com `/cto-review` executado.

## Aprovação

- Aprovado por: [pendente] em [AAAA-MM-DD]
