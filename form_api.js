// Supren Veg — helper de envio de formulários para a API do gestao-supren

(function () {
  'use strict';

  function getIdFromUrl() {
    return new URLSearchParams(window.location.search).get('id') || null;
  }

  function formDataToObject(formData) {
    const obj = {};
    const keys = new Set(formData.keys());
    for (const key of keys) {
      const values = formData.getAll(key);
      obj[key] = values.length === 1 ? values[0] : values;
    }
    return obj;
  }

  // Sem id não há como a API associar a resposta à degustação, mas o dado do
  // preenchimento não pode ser perdido — guarda sob chave própria.
  function salvarLocal(formNumero, id, data) {
    const chave = id
      ? 'form' + formNumero + '_' + id
      : 'form' + formNumero + '_sem_id_' + Date.now();
    try {
      localStorage.setItem(chave, JSON.stringify(data));
      return true;
    } catch (_) {
      return false;
    }
  }

  function textoDoErro(motivo) {
    if (motivo === 'sem_id') {
      return 'Este formulário foi aberto por um link antigo, sem identificar a degustação. Abra a degustação pelo sistema (Degustações) e clique no formulário por lá.';
    }
    if (motivo === 'sem_config') {
      return 'Este formulário não está configurado para enviar. Avise o responsável pelo sistema.';
    }
    if (motivo === 'rede') {
      return 'Não foi possível enviar: sem conexão. Assim que tiver internet, abra este formulário de novo e envie.';
    }
    return 'O sistema recusou o envio. Tente de novo em alguns minutos; se continuar, avise o responsável.';
  }

  function mostrarErro(resultado) {
    var anterior = document.getElementById('form-api-erro');
    if (anterior) anterior.remove();

    var banner = document.createElement('div');
    banner.id = 'form-api-erro';
    banner.setAttribute('role', 'alert');
    banner.style.cssText = [
      'position:fixed', 'left:0', 'right:0', 'bottom:0', 'z-index:99999',
      'background:#b3261e', 'color:#fff', 'padding:16px 20px',
      'font:500 15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif',
      'box-shadow:0 -2px 12px rgba(0,0,0,.3)',
    ].join(';');

    var titulo = document.createElement('strong');
    titulo.textContent = 'NÃO ENVIADO';
    titulo.style.cssText = 'display:block;font-size:17px;margin-bottom:4px';

    var corpo = document.createElement('span');
    corpo.textContent = textoDoErro(resultado.motivo);

    var guardado = document.createElement('span');
    guardado.style.cssText = 'display:block;margin-top:8px;opacity:.9;font-size:14px';
    guardado.textContent = resultado.salvoLocal
      ? 'Suas respostas estão salvas neste aparelho — não feche o formulário se puder tentar de novo.'
      : 'Atenção: não foi possível nem salvar neste aparelho. Anote as respostas antes de fechar.';

    var fechar = document.createElement('button');
    fechar.type = 'button';
    fechar.textContent = 'Entendi';
    fechar.style.cssText = 'margin-top:12px;background:#fff;color:#b3261e;border:0;border-radius:6px;padding:8px 16px;font-weight:600;cursor:pointer';
    fechar.onclick = function () { banner.remove(); };

    banner.appendChild(titulo);
    banner.appendChild(corpo);
    banner.appendChild(guardado);
    banner.appendChild(fechar);
    document.body.appendChild(banner);
  }

  /**
   * Coleta os dados do formulário, salva sempre no localStorage e tenta enviar
   * para a API do gestao-supren. Em caso de falha, exibe o erro ao usuário.
   *
   * @param {number} formNumero  1=Agendamento 2=Kit 3=Vendedor 4=Degustador 5=Devolução 6=Relatório
   * @param {FormData|Object} entrada  new FormData(formElement), ou um objeto já
   *        montado para formulários que derivam campos (ex.: o relatório e suas porções)
   * @returns {Promise<{ok: boolean, motivo: string|null, salvoLocal: boolean}>}
   *          O chamador deve exibir sucesso apenas se `ok` for true.
   */
  window.submitToApi = async function (formNumero, entrada) {
    const id = getIdFromUrl();
    const data = entrada instanceof FormData
      ? formDataToObject(entrada)
      : Object.assign({}, entrada);
    data.savedAt = new Date().toISOString();

    const salvoLocal = salvarLocal(formNumero, id, data);
    let resultado;

    if (!id) {
      resultado = { ok: false, motivo: 'sem_id', salvoLocal: salvoLocal };
    } else if (!window.FORMS_API_BASE || !window.FORMS_API_KEY) {
      resultado = { ok: false, motivo: 'sem_config', salvoLocal: salvoLocal };
    } else {
      try {
        const resp = await fetch(
          window.FORMS_API_BASE + '/api/forms/' + id + '/' + formNumero,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + window.FORMS_API_KEY,
            },
            body: JSON.stringify(data),
          }
        );
        resultado = resp.ok
          ? { ok: true, motivo: null, salvoLocal: salvoLocal }
          : { ok: false, motivo: 'http_' + resp.status, salvoLocal: salvoLocal };
      } catch (_) {
        resultado = { ok: false, motivo: 'rede', salvoLocal: salvoLocal };
      }
    }

    if (!resultado.ok) mostrarErro(resultado);
    return resultado;
  };
})();
