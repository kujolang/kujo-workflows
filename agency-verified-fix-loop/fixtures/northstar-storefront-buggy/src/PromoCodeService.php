<?php

final class PromoCodeService
{
    public function apply(string $code, float $subtotal): array
    {
        $normalized = strtoupper(trim($code));

        if ($normalized !== 'SAVE10') {
            return [
                'ok' => false,
                'message' => 'Promo code not recognized',
                'discount' => 0.0,
                'total' => round($subtotal, 2),
            ];
        }

        $discount = round($subtotal * 0.10, 2);

        return [
            'ok' => true,
            'message' => 'Promo code applied',
            'discount' => $discount,
            'total' => round($subtotal - $discount, 2),
        ];
    }
}
