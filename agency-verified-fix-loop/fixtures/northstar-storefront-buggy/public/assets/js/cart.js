(function () {
  const promoToggle = document.querySelector('[data-testid="promo-toggle"]');
  const promoDrawer = document.querySelector('[data-testid="promo-drawer"]');
  const promoInput = document.querySelector('[data-testid="promo-input"]');
  const promoApply = document.querySelector('[data-testid="promo-apply"]');
  const promoMessage = document.querySelector('[data-testid="promo-message"]');

  if (!promoToggle || !promoDrawer || !promoInput || !promoApply || !promoMessage) {
    return;
  }

  let applyHandlerArmed = false;

  function openPromoDrawer() {
    promoDrawer.hidden = false;
    promoDrawer.classList.add('is-open');
    promoToggle.setAttribute('aria-expanded', 'true');
    promoInput.focus();
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

  promoApply.addEventListener('click', function (event) {
    event.preventDefault();

    if (!applyHandlerArmed) {
      applyHandlerArmed = true;
      return;
    }

    applyPromoCode();
  });
}());
