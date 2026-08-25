# -*- coding: utf-8 -*-
"""Verifica os ajustes pedidos pela operação em 2026-08 nos formulários.

São checagens de conteúdo do HTML, sem navegador: o repositório não tem Node, e
uma verificação que depende de ferramenta não versionada não é reproduzível por
quem clonar (foi exatamente essa a ressalva da revisão técnica).
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Os 10 produtos da operação — item 3 do agendamento e reposição do vendedor.
PRODUTOS = [
    ("empada_palmito_160", "Empada de Palmito 160g"),
    ("empada_espinafre_160", "Empada de Espinafre 160g"),
    ("lasanha_berinjela_410", "Lasanha de Berinjela 410g"),
    ("discos_proteicos_240", "Discos Proteicos 240g"),
    ("quiche_palmito_130", "Quiche de Palmito 130g"),
    ("pao_sem_queijo_450", "Pão sem Queijo 450g"),
    ("empada_maca_120", "Empada de Maçã 120g"),
    ("estrogonofe_450", "Estrogonofe 450g"),
    ("empada_palmito_375", "Empada de Palmito 375g"),
    ("lasanha_abobrinha_410", "Lasanha de Abobrinha 410g"),
]


def ler(nome):
    with open(os.path.join(RAIZ, nome), encoding="utf-8") as f:
        return f.read()


# --- 1.4 Formulários ativos ---------------------------------------------------

def test_restam_apenas_os_quatro_formularios_do_fluxo():
    html = sorted(f for f in os.listdir(RAIZ) if re.match(r"^form\d.*\.html$", f))
    assert html == [
        "form1_agendamento.html",
        "form2_kit_briefing.html",
        "form3a_vendedor.html",
        "form3b_degustador.html",
    ], f"formulários no repositório: {html}"


# --- 1.1 Kit ------------------------------------------------------------------

def test_kit_tem_os_quinze_itens_de_conferencia():
    html = ler("form2_kit_briefing.html")
    itens = re.findall(r'<input type="checkbox" id="kit_item_\d+"', html)
    assert len(itens) == 15, f"{len(itens)} itens no checklist do kit"
    assert "de 15 itens conferidos" in html
    assert "const total = 15;" in html, "o cálculo do progresso ficou com o total antigo"


def test_kit_tem_os_itens_novos_da_operacao():
    html = ler("form2_kit_briefing.html")
    for item in ["Extensão elétrica", "Caixas vazias para amostra", "Álcool", "Perfex"]:
        assert item in html, f"item ausente na conferência: {item}"


def test_kit_nao_tem_mais_briefing_com_a_degustadora():
    html = ler("form2_kit_briefing.html")
    for sobra in ["section-briefing", 'name="brief_items"', "updateBriefingProgress",
                  "briefing_ocorrencia", "briefing_confirmado"]:
        assert sobra not in html, f"sobrou referência ao briefing: {sobra}"


def test_kit_registra_entrega_ao_cliente():
    html = ler("form2_kit_briefing.html")
    assert "entregue ao cliente" in html
    assert "assinada pelo cliente" in html
    assert "entregue ao degustador" not in html
    assert "assinada pelo degustador" not in html


def test_kit_imprime_compacto_em_uma_pagina():
    html = ler("form2_kit_briefing.html")
    print_css = html[html.index("@media print {"):]
    assert "@page" in print_css, "sem controle de página na impressão"
    assert "grid-template-columns: 1fr 1fr" in print_css, "checklist não vai em duas colunas"
    assert ".progress-container" in print_css, "barras de progresso ocupam espaço na impressão"
    # `min-height: 100vh` da tela reserva uma folha inteira antes do conteúdo começar.
    assert "min-height: 0;" in print_css


def test_bloco_de_impressao_vem_depois_das_regras_de_tela():
    """Com a mesma especificidade vence a última declaração: com o `@media print` no
    topo do CSS, metade das regras de impressão era anulada pelas regras de tela
    declaradas depois — e o formulário saía em três páginas mesmo 'compactado'."""
    html = ler("form2_kit_briefing.html")
    assert html.index("@media print {") > html.index(".form-container {"), (
        "o bloco @media print voltou para antes das regras de tela"
    )


def test_kit_nao_esconde_campo_na_impressao():
    """Compactar não pode custar informação: o formulário é preenchido à mão."""
    html = ler("form2_kit_briefing.html")
    print_css = html[html.index("@media print {"):]
    escondidos = re.findall(r"([^{}]+)\{[^{}]*display:\s*none[^{}]*\}", print_css)
    permitidos = {".no-print", ".top-bar", ".progress-container", ".hero-pills",
                  ".section-subtitle", ".conditional-field"}
    for grupo in escondidos:
        for seletor in (s.strip() for s in grupo.split(",")):
            if not seletor or seletor.startswith("/*"):
                continue
            assert seletor in permitidos, f"impressão esconde algo não previsto: {seletor}"


# --- 1.2 Agendamento ----------------------------------------------------------

def test_agendamento_nao_pede_mais_estoque():
    """A verificacao de estoque saiu do agendamento e passou para o formulario do
    vendedor, com estoque antes e depois (decisao do Ygor, 2026-08-10)."""
    html = ler("form1_agendamento.html")
    for sobra in ["stock-input", "stock-grid", "stock-alert", "verificarEstoque",
                  'name="estoque_']:
        assert sobra not in html, f"sobrou estoque no agendamento: {sobra}"


def test_agendamento_avisa_ao_lado_do_botao_quando_falta_campo():
    """A mensagem de erro nasce no campo, lá em cima; quem está no fim da página
    precisa ver algo mudar perto do botão — foi essa a queixa no form da degustadora."""
    html = ler("form1_agendamento.html")
    assert 'id="aviso-obrigatorios"' in html
    assert "aviso.classList.add('show')" in html


def test_agendamento_nao_pede_mais_sim_nao_nem_quantidade_sugerida():
    html = ler("form1_agendamento.html")
    assert 'name="stock-' not in html, "sobrou o sim/não de estoque"
    for antigo in ["Empada de Maçã PP", "Discos Proteicos 30g", "Estrogonofe de Grão de Bico",
                   "25 un.", "50 un."]:
        assert antigo not in html, f"sobrou do formulário antigo: {antigo}"


# --- 1.3 Vendedor -------------------------------------------------------------

def test_vendedor_registra_estoque_antes_depois_e_reposicao():
    """O estoque virou verificacao do vendedor: antes e depois de cada produto, mais
    a quantidade a repor. O 'usado' saiu do formulario — vira antes menos depois."""
    html = ler("form3a_vendedor.html")
    for chave, nome in PRODUTOS:
        for sufixo in ("antes", "depois", "repor"):
            assert f'name="{chave}_{sufixo}"' in html, f"estoque sem {chave}_{sufixo}"
        assert f'id="prod_{chave}"' in html, f"produtos do pedido sem {chave}"
        assert nome in html
        assert f'name="{chave}_usado"' not in html, f"campo usado ficou em {chave}"


def test_vendedor_mantem_a_lista_degustada_no_produto_mais_comentado():
    """Decisão do Ygor: 'mais comentado' são os itens degustados, não os de venda."""
    html = ler("form3a_vendedor.html")
    trecho = html[html.index('id="produto_comentado"'):]
    trecho = trecho[:trecho.index("</select>")]
    assert "Empada de Maçã PP" in trecho
    assert "Empada de Palmito 160g" not in trecho


def test_vendedor_nao_tem_mais_chaves_posicionais_de_reposicao():
    """`p1_usado`..`p5_repor` viraram chaves por produto; o relatório do app lê as duas
    convenções, mas o formulário só grava a nova."""
    html = ler("form3a_vendedor.html")
    assert not re.search(r'name="p[1-5]_(usado|repor)"', html)
