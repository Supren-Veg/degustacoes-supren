# Mandato — Hotfix: formulário do degustador não salvava e não dizia por quê

- **Data:** 2026-08-06
- **Projeto:** degustacoes-supren (formulários hospedados no GitHub Pages)
- **Solicitante:** Ygor — **urgência**: "uma das degustadoras está com dificuldade na
  hora de salvar o relatório; quando ela clica em salvar nada acontece"
- **Status:** aprovado (urgência autorizada em sessão)

## Causa

`form3b_degustador.html` (F4, o formulário que o degustador preenche) valida por
JavaScript (`validateForm`) e, ao reprovar, apenas exibia `.error-message` **nos campos**
— sem rolar a tela, sem focar nada e sem qualquer sinal perto do botão "Salvar", que fica
no fim de um formulário longo. Para quem está no fim da página, o clique não produz
nenhuma mudança visível: "nada acontece".

O gatilho mais provável no uso real: a **tabela de porções tinha as 10 células
obrigatórias** (5 produtos × servidas/descartadas). Quem serviu só alguns produtos deixa
células em branco e fica travado sem entender por quê. Consistente com os dados: 6
submissões de F4 em 51 degustações.

## Correção

- Porção em branco = **0** (não obriga mais preencher as 10 células); `required` removido
  das células e valores vazios viram `0` no envio.
- Ao reprovar: aviso em vermelho **ao lado do botão Salvar** + rolagem até o primeiro
  campo pendente (com foco, quando o campo aceita foco — a nota em estrelas vive num
  input escondido, então rola até o grupo).
- Botão mostra "Enviando..." e fica desabilitado durante o envio: em rede fraca (loja),
  o clique também parecia não fazer nada.
- `handleSubmit` deixa de depender de `event.target` (usa o próprio form).

## Fora de escopo

- `form5_relatorio.html` (F6, relatório final): usa validação nativa do navegador, que
  rola e mostra balão sozinha — não tem o bloqueio silencioso. Não foi tocado.
- Regra de negócio dos demais campos obrigatórios: mantida.

## Verificação

Teste funcional com jsdom carregando o HTML real + `form_api.js`, com `fetch` dublado:

1. Caso da degustadora (porções em branco): **envia**, porções vão como 0 — antes travava.
2. Formulário incompleto (sem nota de estrelas): **não envia** e mostra o aviso ao lado do
   botão — antes falhava em silêncio.
3. Preenchimento completo: **envia**.
