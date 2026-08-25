"""
tests/test_form_api.py — Rede anti-regressão do feedback de envio dos formulários.
Execução: pytest tests/

Estes são testes ESTÁTICOS: leem o texto dos arquivos e travam os invariantes que
a correção da falha silenciosa estabeleceu. Não substituem o teste manual com stub
local (não há infra de teste JS neste repo, e npm está vedado por decisão do projeto);
servem para impedir que o padrão antigo — mostrar sucesso sem confirmar o envio —
volte despercebido num PR futuro.
"""
import os
import re

RAIZ = os.path.join(os.path.dirname(__file__), "..")

# form_numero canônico: 1=Agendamento 2=Kit 3=Vendedor 4=Degustador
# (5=Devolução e 6=Relatório final foram aposentados em 2026-08-06)
FORMS = {
    "form1_agendamento.html": 1,
    "form2_kit_briefing.html": 2,
    "form3a_vendedor.html": 3,
    "form3b_degustador.html": 4,
}


def ler(nome):
    with open(os.path.join(RAIZ, nome), encoding="utf-8") as f:
        return f.read()


# ── form_api.js ───────────────────────────────────────────────────────────────

def test_helper_nao_engole_erro_silenciosamente():
    """`catch (_) {}` de corpo vazio foi o defeito original: engolia rede/4xx/5xx."""
    js = ler("form_api.js")
    assert not re.search(r"catch\s*\(\s*_\s*\)\s*\{\s*\}", js), (
        "catch com corpo vazio de volta no form_api.js — o envio voltaria a falhar em silêncio"
    )


def test_helper_checa_resp_ok():
    """Sem checar resp.ok, 4xx/5xx passam como sucesso: fetch não lança nesses casos."""
    js = ler("form_api.js")
    assert "resp.ok" in js, "form_api.js precisa checar resp.ok — 4xx/5xx não lançam exception"


def test_helper_retorna_resultado():
    js = ler("form_api.js")
    assert "ok: true" in js and "ok: false" in js, (
        "submitToApi precisa devolver {ok, motivo, salvoLocal} para o form decidir o que exibir"
    )


def test_helper_salva_local_mesmo_sem_id():
    """Sem id o dado não pode ser enviado, mas o preenchimento não pode ser perdido."""
    js = ler("form_api.js")
    assert "_sem_id_" in js, "form_api.js precisa salvar no localStorage mesmo sem ?id="
    assert "sem_id" in js, "form_api.js precisa reportar o motivo sem_id"


def test_helper_sem_cabecalho_falso():
    """O arquivo é fonte à mão; o .py só gera api_config.js e faz git add deste."""
    js = ler("form_api.js")
    assert "NÃO EDITE MANUALMENTE" not in js, (
        "cabeçalho falso de volta: mente para o próximo dev sobre o arquivo que ele precisa editar"
    )


# ── Os 6 formulários ──────────────────────────────────────────────────────────

def test_todos_os_forms_usam_o_helper():
    for nome, numero in FORMS.items():
        html = ler(nome)
        assert "form_api.js" in html, f"{nome} não carrega o form_api.js"
        assert f"submitToApi({numero}," in html, (
            f"{nome} deveria enviar como form_numero {numero}"
        )


def test_nenhum_form_ignora_o_resultado_do_envio():
    """`await submitToApi(...)` sem capturar o retorno = sucesso incondicional de volta."""
    for nome in FORMS:
        html = ler(nome)
        assert not re.search(r"(?<!=\s)await submitToApi\(", html), (
            f"{nome} chama submitToApi sem usar o retorno — exibiria sucesso sem envio confirmado"
        )
        # Aceita `if (!r.ok)` e `if (!r || !r.ok)` — o segundo também cobre o caso de
        # o helper não devolver nada. O que importa é a UI de sucesso ficar guardada.
        assert re.search(r"if \(!r(?:\s*\|\|\s*!r)?\.ok\) return;", html), (
            f"{nome} não guarda a UI de sucesso pelo resultado do envio"
        )


def test_cache_busting_no_helper():
    """Pages publica direto da main; sem ?v= o usuário fica com o script que mente."""
    for nome in FORMS:
        html = ler(nome)
        assert "form_api.js?v=" in html, (
            f"{nome} carrega o form_api.js sem cache-busting — a correção não chegaria a quem já abriu"
        )
