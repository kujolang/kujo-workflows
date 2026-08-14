# The checksum is the editorial boundary

Editorial review is useful only when every participant can identify the same artifact. A local workflow preserves that identity by packaging exact bytes, recording their SHA-256 checksum, and binding the human decision to that checksum.

If any approved byte changes, the package becomes a new version and returns to the necessary review and approval gates. Credentials do not repair that mismatch; only a new decision about the new bytes can authorize publication.

In the fixture proof, PressWire copies the approved package only to a bounded local destination and emits a receipt. The proof makes no network call and does not imply a live publishing adapter exists.
