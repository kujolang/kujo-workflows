# Northstar Storefront Fixture

Northstar Storefront is the deterministic PHP, JavaScript, and CSS fixture used by the Agency Verified Fix Loop. It begins with a browser-visible mobile promo-code bug so the workflow can prove failure, apply a bounded fix, and record post-fix evidence.

## Install

The fixture has no third-party application dependencies. It requires PHP and Node.js on the local host.

## Usage

From the fixture root:

```bash
make test
make lint
make serve
```

Open `http://127.0.0.1:8099/cart.php` after starting the server.

## Release Boundary

This is a fictional, private demo fixture. Version and changelog metadata exist so release-readiness tools can evaluate the fixture honestly; the fixture is not published as a package or production storefront.
