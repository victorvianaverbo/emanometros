/**
 * Press Control — recebe os leads do modal do site e grava na planilha.
 *
 * Planilha: "Press Control — Leads do site"
 * https://docs.google.com/spreadsheets/d/1-p6k6LL9grFRyCG8yeY7Qd_U_7M7oh4z7nytTGwpBcc/edit
 *
 * COMO PUBLICAR (o passo 4 é o que costuma ser esquecido):
 *
 *  1. Abra a planilha > menu Extensões > Apps Script.
 *  2. Selecione TUDO que está no editor (Ctrl+A) e apague.
 *  3. Cole este arquivo INTEIRO, do começo ao fim, e salve (Ctrl+S).
 *  4. Implantar > Nova implantação > tipo "App da Web":
 *       Executar como: Eu (vianavictorv@gmail.com)
 *       Quem pode acessar: QUALQUER PESSOA
 *     Atenção: "Qualquer pessoa com uma Conta do Google" NÃO serve — bloqueia
 *     o site com 403. Tem que ser "Qualquer pessoa".
 *  5. Copie a URL que termina em /exec e me mande.
 *
 * Ao ATUALIZAR este código depois: Implantar > Gerenciar implantações >
 * lápis > em "Versão" escolher "Nova versão" > Implantar. Só salvar o código
 * não republica: o Apps Script serve uma versão congelada.
 *
 * Para conferir, abra a URL /exec no navegador: tem que aparecer
 * {"ok":true,...}. Se aparecer "Função de script não encontrada", o passo 4
 * (ou a nova versão) não foi feito.
 */

function doPost(e) {
  try {
    var lead = JSON.parse(e.postData.contents);
    var aba = pegarAba_();

    aba.appendRow([
      formatarData_(lead.enviado_em),
      lead.nome || '',
      lead.telefone || '',
      lead.produto || '',
      lead.specs || '',
      lead.mensagem || '',
      lead.pagina || '',
      lead.referencia || 'acesso direto'
    ]);

    return responder_({ ok: true });
  } catch (erro) {
    return responder_({ ok: false, erro: String(erro) });
  }
}

/* Abrir a URL /exec no navegador cai aqui: serve para conferir se a
   implantação está mesmo servindo esta versão do código. */
function doGet() {
  return responder_({ ok: true, servico: 'leads Press Control' });
}

/* Grava uma linha de mentira, para testar sem depender do site.
   Rode pelo botão "Executar" do editor. */
function testarGravacao() {
  pegarAba_().appendRow([
    formatarData_(null), 'Teste pelo editor', '(31) 90000-0000',
    'Manômetro 63mm', 'Ø63mm · Inox', 'teste', '/', 'teste'
  ]);
}

function pegarAba_() {
  var ID_PLANILHA = '1-p6k6LL9grFRyCG8yeY7Qd_U_7M7oh4z7nytTGwpBcc';
  var COLUNAS = ['Data e hora', 'Nome', 'Telefone', 'Produto',
                 'Especificações', 'Mensagem', 'Página', 'Veio de'];

  /* quando o script é criado a partir da planilha, getActive() já resolve;
     o ID é o caminho de volta se ele virar um projeto solto */
  var planilha = SpreadsheetApp.getActiveSpreadsheet() ||
                 SpreadsheetApp.openById(ID_PLANILHA);
  var aba = planilha.getSheets()[0];

  if (aba.getLastRow() === 0) {
    aba.appendRow(COLUNAS);
    aba.getRange(1, 1, 1, COLUNAS.length).setFontWeight('bold');
    aba.setFrozenRows(1);
  }

  return aba;
}

/* o navegador manda ISO em UTC; a planilha mostra no horário de Brasília */
function formatarData_(iso) {
  var data = iso ? new Date(iso) : new Date();
  return Utilities.formatDate(data, 'America/Sao_Paulo', 'dd/MM/yyyy HH:mm');
}

function responder_(objeto) {
  return ContentService
    .createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
}
