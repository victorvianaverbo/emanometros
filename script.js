/* Press Control — Script Principal */
const WA_NUMBER = '553195713196';

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
      text = `Olá, sou ${name} (${phone}), tenho interesse no ${product} (${specs}). Qual o prazo e valor?`;
    } else if (msg) {
      text = `Olá, sou ${name} (${phone}), ${msg}`;
    } else {
      text = `Olá, sou ${name} (${phone}), preciso de ajuda`;
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
      .map(([k, label]) => `<div><dt>${label}</dt><dd>${product.specs[k]}</dd></div>`)
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
