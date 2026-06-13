(function () {
  const promoToggle = document.querySelector('[data-testid="promo-toggle"]');
  const promoDrawer = document.querySelector('[data-testid="promo-drawer"]');
  const promoForm = document.querySelector('[data-testid="promo-form"]');
  const promoInput = document.querySelector('[data-testid="promo-input"]');
  const promoMessage = document.querySelector('[data-testid="promo-message"]');

  if (!promoToggle || !promoDrawer || !promoForm || !promoInput || !promoMessage) {
    return;
  }

  function openPromoDrawer() {
    promoDrawer.hidden = false;
    promoDrawer.classList.add('is-open');
    promoToggle.setAttribute('aria-expanded', 'true');

    window.requestAnimationFrame(function () {
      promoInput.focus();
      promoInput.scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  }

  function applyPromoCode() {
    const code = promoInput.value.trim().toUpperCase();

    if (code === 'SAVE10') {
      promoMessage.textContent = 'Promo code applied';
      promoMessage.classList.remove('is-error');
      return;
    }

    promoMessage.textContent = 'Promo code not recognized';
    promoMessage.classList.add('is-error');
  }

  promoToggle.addEventListener('click', openPromoDrawer);

  promoForm.addEventListener('submit', function (event) {
    event.preventDefault();
    applyPromoCode();
  });
}());
