<?php

require_once __DIR__ . '/../src/PromoCodeService.php';

function assert_same($expected, $actual, string $message): void
{
    if ($expected !== $actual) {
        fwrite(STDERR, $message . PHP_EOL);
        fwrite(STDERR, 'Expected: ' . var_export($expected, true) . PHP_EOL);
        fwrite(STDERR, 'Actual:   ' . var_export($actual, true) . PHP_EOL);
        exit(1);
    }
}

$service = new PromoCodeService();

$valid = $service->apply(' save10 ', 100.00);
assert_same(true, $valid['ok'], 'SAVE10 should be accepted.');
assert_same('Promo code applied', $valid['message'], 'Success message should match UI expectation.');
assert_same(10.0, $valid['discount'], 'SAVE10 should discount 10 percent.');
assert_same(90.0, $valid['total'], 'Total should reflect discount.');

$invalid = $service->apply('NOPE', 100.00);
assert_same(false, $invalid['ok'], 'Unknown code should be rejected.');
assert_same(0.0, $invalid['discount'], 'Unknown code should not discount.');
assert_same(100.0, $invalid['total'], 'Unknown code should preserve total.');

echo "promo tests passed\n";
