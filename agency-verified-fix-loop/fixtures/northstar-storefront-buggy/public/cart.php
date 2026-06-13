<?php
$items = [
    ['name' => 'Trail Shell Jacket', 'qty' => 1, 'price' => 129.00],
    ['name' => 'Merino Base Layer', 'qty' => 2, 'price' => 42.00],
];

$subtotal = 0;
foreach ($items as $item) {
    $subtotal += $item['qty'] * $item['price'];
}
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northstar Outfitters Cart</title>
  <link rel="stylesheet" href="/assets/css/cart.css">
</head>
<body>
  <main class="cart-shell">
    <p class="eyebrow">Northstar Outfitters</p>
    <h1>Your Cart</h1>
    <p class="lede">Demo storefront fixture for a PHP/JS/CSS agency bug fix.</p>

    <section class="cart-card" aria-labelledby="cart-items-heading">
      <h2 id="cart-items-heading">Items</h2>
      <ul class="cart-items">
        <?php foreach ($items as $item): ?>
          <li>
            <span><?php echo htmlspecialchars($item['name'], ENT_QUOTES, 'UTF-8'); ?></span>
            <strong><?php echo (int) $item['qty']; ?> x $<?php echo number_format($item['price'], 2); ?></strong>
          </li>
        <?php endforeach; ?>
      </ul>
    </section>

    <section class="cart-card promo-card" aria-labelledby="promo-heading">
      <h2 id="promo-heading">Promo code</h2>
      <button
        type="button"
        class="promo-toggle"
        data-testid="promo-toggle"
        aria-expanded="false"
        aria-controls="promo-drawer"
      >
        Have a promo code?
      </button>

      <div id="promo-drawer" class="promo-drawer" data-testid="promo-drawer" hidden>
        <form id="promo-form" data-testid="promo-form" novalidate>
          <label for="promo-code">Promo code</label>
          <div class="promo-row">
            <input
              id="promo-code"
              name="promo_code"
              data-testid="promo-input"
              type="text"
              autocomplete="off"
              placeholder="SAVE10"
            >
            <button type="submit" data-testid="promo-apply">Apply</button>
          </div>
          <p class="promo-message" data-testid="promo-message" role="status" aria-live="polite"></p>
        </form>
      </div>
    </section>
  </main>

  <aside class="checkout-bar" aria-label="Checkout summary">
    <span>Subtotal</span>
    <strong data-testid="cart-subtotal">$<?php echo number_format($subtotal, 2); ?></strong>
    <a class="checkout-button" href="/checkout.php">Checkout</a>
  </aside>

  <script src="/assets/js/cart.js"></script>
</body>
</html>
