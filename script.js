/* eManômetros — Script Principal */
const WA_NUMBER = '553195713196';

/* Topbar agora é estática com 4 diferenciais */

/* ── Modal WhatsApp com Captura ── */
(function initWaModal() {
  const modal = document.getElementById('waModal');
  const form = document.getElementById('waForm');
  const nameInput = document.getElementById('waName');
  const phoneInput = document.getElementById('waPhone');
  const productInput = document.getElementById('waProduct');
  const specsInput = document.getElementById('waSpecs');
  const msgInput = document.getElementById('waMsg');
  const subtitle = document.getElementById('waModalSubtitle');
  const backdrop = modal.querySelector('.wa-modal__backdrop');
  const closeBtn = modal.querySelector('.wa-modal__close');

  function openModal(product, specs, msg) {
    productInput.value = product || '';
    specsInput.value = specs || '';
    msgInput.value = msg || '';

    if (product) {
      subtitle.textContent = product;
    } else {
      subtitle.textContent = 'Preencha seus dados para iniciar o atendimento';
    }

    modal.classList.add('wa-modal--open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => nameInput.focus(), 300);
  }

  function closeModal() {
    modal.classList.remove('wa-modal--open');
    document.body.style.overflow = '';
  }

  // Todos os botões .wa-btn abrem o modal
  document.querySelectorAll('.wa-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const product = btn.dataset.product || '';
      const specs = btn.dataset.specs || '';
      const msg = btn.dataset.msg || '';
      openModal(product, specs, msg);
    });
  });

  // Fechar modal
  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Máscara de telefone simples
  phoneInput.addEventListener('input', (e) => {
    let v = e.target.value.replace(/\D/g, '');
    if (v.length > 11) v = v.slice(0, 11);
    if (v.length > 6) {
      v = `(${v.slice(0,2)}) ${v.slice(2,7)}-${v.slice(7)}`;
    } else if (v.length > 2) {
      v = `(${v.slice(0,2)}) ${v.slice(2)}`;
    }
    e.target.value = v;
  });

  // Submit: monta mensagem e abre WhatsApp
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();
    const product = productInput.value;
    const specs = specsInput.value;
    const msg = msgInput.value;

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
    closeModal();
    form.reset();
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
