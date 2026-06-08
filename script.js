/* Press Control — Script Principal */
const WA_NUMBER = '553197113196';

/* ── Supabase — captura de leads ──
   anon key é pública por design (protegida por RLS: anon só insere, não lê). */
const SUPABASE_URL = 'https://wibecdbznwzerenpnibc.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYmVjZGJ6bnd6ZXJlbnBuaWJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5MjI0MTQsImV4cCI6MjA5NjQ5ODQxNH0.oXWPZg7gYh5Xf7slDasU8Quanh_KNdYBnWpfvpi_RSk';

/* Grava o lead no Supabase. Fire-and-forget com keepalive: não bloqueia
   o redirect pro WhatsApp e sobrevive à navegação da aba. */
function salvarLead(lead) {
  try {
    fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      keepalive: true,
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
      },
      body: JSON.stringify(lead),
    }).catch(() => {});
  } catch (_) { /* nunca quebra o fluxo do usuário */ }
}

const CAT_LABEL = {
  manometros: 'Manômetros',
  manovacuometros: 'Manovacuômetros',
  vacuometros: 'Vacuômetros',
  termometros: 'Termômetros',
};

const SPEC_LABELS = [
  ['material', 'Material'],
  ['sensor', 'Elemento Sensor'],
  ['diametro', 'Diâmetro'],
  ['visor', 'Visor'],
  ['classe', 'Classe de Exatidão'],
  ['conexao', 'Conexão'],
  ['escalas', 'Escalas'],
  ['ponteiro', 'Ponteiro'],
  ['temperatura', 'Temp. Trabalho'],
  ['haste', 'Haste'],
  ['faixa_temperatura', 'Faixa de Temperatura'],
  ['capilar', 'Capilar'],
];

/* Ícones de especificação (vocabulário do Design System Press Control).
   stroke 2px, viewBox 24×24, cor herdada. */
const SPEC_ICONS = {
  material: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><line x1="4" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="20" y2="12"/>',
  sensor: '<path d="M4 18 C 4 10 10 4 14 4 C 18 4 20 6 20 9 C 20 12 17 14 14 12"/><circle cx="4" cy="18" r="1.5" fill="currentColor"/>',
  diametro: '<circle cx="12" cy="12" r="8"/><line x1="4" y1="12" x2="20" y2="12"/><polyline points="6 10 4 12 6 14"/><polyline points="18 10 20 12 18 14"/>',
  visor: '<rect x="4" y="6" width="16" height="12" rx="2"/><line x1="4" y1="10" x2="20" y2="10"/>',
  classe: '<path d="M12 3 L20 6 V12 C20 17 16 20 12 21 C8 20 4 17 4 12 V6 Z"/><path d="M9 12 L11 14 L15 10"/>',
  conexao: '<rect x="3" y="10" width="6" height="4"/><rect x="13" y="9" width="3" height="6"/><line x1="9" y1="12" x2="13" y2="12"/><line x1="16" y1="12" x2="21" y2="12"/>',
  escalas: '<path d="M4 16 A 8 8 0 0 1 20 16"/><line x1="12" y1="16" x2="16" y2="10"/><circle cx="12" cy="16" r="1.5" fill="currentColor"/>',
  ponteiro: '<circle cx="12" cy="12" r="8"/><line x1="12" y1="12" x2="16" y2="8"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/>',
  temperatura: '<path d="M10 4a2 2 0 0 1 4 0v10.5a4 4 0 1 1-4 0z"/><line x1="12" y1="8" x2="12" y2="14"/>',
  haste: '<line x1="12" y1="3" x2="12" y2="16"/><rect x="9" y="16" width="6" height="5"/>',
  faixa_temperatura: '<path d="M4 16 A 8 8 0 0 1 20 16"/><line x1="12" y1="16" x2="16" y2="10"/><circle cx="12" cy="16" r="1.5" fill="currentColor"/>',
  capilar: '<path d="M3 12 C 6 8 6 16 9 12 S 12 8 15 12 18 16 21 12"/>',
};
const SPEC_ICON_FALLBACK = '<circle cx="12" cy="12" r="8"/><path d="M9 12 h6 M12 9 v6"/>';
function specIcon(key) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${SPEC_ICONS[key] || SPEC_ICON_FALLBACK}</svg>`;
}

/* Bloco de specs do card — linhas mono (padrão técnico extraído do IndusGauge) */
const MAT_LABEL = {
  'aco-carbono': 'Aço Carbono',
  'inox-latao': 'Inox + Latão',
  'total-inox': 'Total Inox',
};
function specRowsHTML(p) {
  const s = p.specs || {};
  const rows = [];
  const dia = s.diametro || (p.diametro_mm ? `${p.diametro_mm}mm` : '');
  if (dia) rows.push(['Ø', dia]);
  const mat = MAT_LABEL[p.material_class]
    || (s.material ? s.material.replace(/^Caixa\s*/i, '').split(/\s+e\s+os?\s+/i)[0].trim() : '');
  if (mat) rows.push(['Mat', mat]);
  if (s.conexao) rows.push(['Con', s.conexao]);
  else if (s.escalas) rows.push(['Esc', s.escalas]);
  else if (s.faixa_temperatura) rows.push(['Faixa', s.faixa_temperatura]);
  return `<ul class="product-card__specs">${rows.map(([k, v]) =>
    `<li><span class="product-card__spec-key">${k}</span><span class="product-card__spec-val">${v}</span></li>`).join('')}</ul>`;
}

// Produtos carregados via fetch (catalogo.html); index.html não precisa do array completo
let productMap = {};

/* ── Modal WhatsApp ── */
const waState = {
  open: (opts = {}) => {
    const modal = document.getElementById('waModal');
    if (!modal) return;
    document.getElementById('waProduct').value = opts.product || '';
    document.getElementById('waSpecs').value = opts.specs || '';
    document.getElementById('waMsg').value = opts.msg || '';
    const subtitle = document.getElementById('waModalSubtitle');
    if (subtitle) {
      subtitle.textContent = opts.product || 'Preencha seus dados para iniciar o atendimento';
    }
    modal.classList.add('wa-modal--open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => document.getElementById('waName').focus(), 300);
  },
  close: () => {
    const modal = document.getElementById('waModal');
    if (!modal) return;
    modal.classList.remove('wa-modal--open');
    document.body.style.overflow = '';
  },
};

(function initWaModal() {
  const modal = document.getElementById('waModal');
  if (!modal) return;
  const form = document.getElementById('waForm');
  const phoneInput = document.getElementById('waPhone');
  const backdrop = modal.querySelector('.wa-modal__backdrop');
  const closeBtn = modal.querySelector('.wa-modal__close');

  closeBtn.addEventListener('click', waState.close);
  backdrop.addEventListener('click', waState.close);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      waState.close();
      dsState.close();
    }
  });

  // Máscara telefone
  phoneInput.addEventListener('input', (e) => {
    let v = e.target.value.replace(/\D/g, '');
    if (v.length > 11) v = v.slice(0, 11);
    if (v.length > 6) v = `(${v.slice(0,2)}) ${v.slice(2,7)}-${v.slice(7)}`;
    else if (v.length > 2) v = `(${v.slice(0,2)}) ${v.slice(2)}`;
    e.target.value = v;
  });

  // Submit
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('waName').value.trim();
    const phone = document.getElementById('waPhone').value.trim();
    const product = document.getElementById('waProduct').value;
    const specs = document.getElementById('waSpecs').value;
    const msg = document.getElementById('waMsg').value;
    if (!name || !phone) return;

    let text;
    if (product) {
      text = `Olá, sou ${name}, tenho interesse no ${product} (${specs}). Qual o prazo e valor?`;
    } else if (msg) {
      text = `Olá, sou ${name}, ${msg}`;
    } else {
      text = `Olá, sou ${name}, preciso de ajuda`;
    }

    // Supabase — grava o lead antes de redirecionar (não perde se não enviar no WhatsApp)
    salvarLead({
      nome: name,
      telefone: phone,
      produto: product || null,
      specs: specs || null,
      mensagem: msg || null,
      pagina: location.pathname + location.search,
    });

    // Google Ads — conversão de lead (envio do formulário)
    if (typeof gtag === 'function') {
      gtag('event', 'conversion', {
        'send_to': 'AW-18211286792/9hsSCOvQzLgcEIje6OtD',
        'value': 1.0,
        'currency': 'BRL'
      });
    }

    const url = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');

    waState.close();
    form.reset();
  });
})();

/* ── Click handler global para .wa-btn ── */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.wa-btn');
  if (!btn) return;
  e.preventDefault();
  waState.open({
    product: btn.dataset.product || '',
    specs: btn.dataset.specs || '',
    msg: btn.dataset.msg || '',
  });
});

/* ── Modal Data Sheet ── */
const dsState = {
  open: (product) => {
    const modal = document.getElementById('dsModal');
    if (!modal || !product) return;
    document.getElementById('dsCategory').textContent = CAT_LABEL[product.categoria] || product.categoria;
    modal.querySelector('.ds-modal__content').setAttribute('data-cat', product.categoria || '');
    document.getElementById('dsTitle').textContent = product.nome;
    const gallery = document.getElementById('dsGallery');
    if (gallery) {
      const imgs = [];
      if (product.imagem) imgs.push({ src: product.imagem, label: 'Frente' });
      if (product.imagem_verso) imgs.push({ src: product.imagem_verso, label: 'Verso' });
      gallery.innerHTML = imgs.map(({ src, label }) => `
        <figure class="ds-modal__photo">
          <img src="${src}" alt="${product.nome} (${label})">
          <figcaption>${label}</figcaption>
        </figure>`).join('') || '<p style="color:#94A3B8;font-size:.85rem">Sem imagem disponível</p>';
    }
    const specsEl = document.getElementById('dsSpecs');
    specsEl.innerHTML = SPEC_LABELS
      .filter(([k]) => product.specs && product.specs[k])
      .map(([k, label]) => `<div>${specIcon(k)}<dt>${label}</dt><dd>${product.specs[k]}</dd></div>`)
      .join('');
    document.getElementById('dsApplication').textContent = product.aplicacao || 'Consulte nossos especialistas para detalhes da aplicação.';

    const cta = document.getElementById('dsCta');
    cta.dataset.product = product.nome;
    cta.dataset.specs = [product.specs.diametro, product.specs.material, product.specs.conexao].filter(Boolean).join(' · ');

    modal.classList.add('ds-modal--open');
    document.body.style.overflow = 'hidden';
  },
  close: () => {
    const modal = document.getElementById('dsModal');
    if (!modal) return;
    modal.classList.remove('ds-modal--open');
    document.body.style.overflow = '';
  },
};

(function initDsModal() {
  const modal = document.getElementById('dsModal');
  if (!modal) return;
  modal.querySelector('.ds-modal__backdrop').addEventListener('click', dsState.close);
  modal.querySelector('.ds-modal__close').addEventListener('click', dsState.close);
})();

/* ── API pública ── */
window.eMan = {
  openWa: waState.open,
  specRows: specRowsHTML,
  openDatasheet: (id) => {
    const p = productMap[id];
    if (!p) return;
    dsState.open(p);
  },
  setProducts: (list) => {
    productMap = {};
    list.forEach(p => { productMap[p.id] = p; });
  },
};

/* ── Mobile Menu Drawer ── */
(function initMobileMenu() {
  const menu = document.getElementById('mobileMenu');
  if (!menu) return;
  const toggle = document.querySelector('.navbar__toggle');
  const closeBtn = menu.querySelector('.mobile-menu__close');
  const backdrop = menu.querySelector('.mobile-menu__backdrop');
  const navLinks = menu.querySelectorAll('.mobile-menu__nav a');

  const open = () => {
    menu.classList.add('mobile-menu--open');
    menu.setAttribute('aria-hidden', 'false');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  };
  const close = () => {
    menu.classList.remove('mobile-menu--open');
    menu.setAttribute('aria-hidden', 'true');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  if (toggle) toggle.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (backdrop) backdrop.addEventListener('click', close);
  navLinks.forEach(a => a.addEventListener('click', close));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && menu.classList.contains('mobile-menu--open')) close();
  });
})();

/* ── Scroll Animations ── */
(function initScrollAnimations() {
  const elements = document.querySelectorAll('.categories, .products, .why, .cta-b2b, .testimonials, .blog');
  if (!elements.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('section--visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  elements.forEach(el => observer.observe(el));
})();
