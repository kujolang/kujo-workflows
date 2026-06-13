#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const [ackPath, outDir, mode] = process.argv.slice(2);

if (!ackPath || !outDir) {
  console.error("usage: render-app-from-ack.js <ack.json> <out-dir> [mode]");
  process.exit(2);
}

function fixtureApp(reason) {
  return {
    source: "fixture",
    reason,
    payload: {
      ack: "kujo-ai-sdk-app-build-v1",
      summary: "Deterministic fallback app used because the model output was not a valid file bundle.",
      files: {
        "public/index.php": `<?php
$errors = [];
$success = false;
$values = [
    'name' => '',
    'email' => '',
    'message' => '',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $values['name'] = trim($_POST['name'] ?? '');
    $values['email'] = trim($_POST['email'] ?? '');
    $values['message'] = trim($_POST['message'] ?? '');

    if ($values['name'] === '') {
        $errors['name'] = 'Name is required.';
    }
    if (!filter_var($values['email'], FILTER_VALIDATE_EMAIL)) {
        $errors['email'] = 'Enter a valid email address.';
    }
    if (strlen($values['message']) < 12) {
        $errors['message'] = 'Message must be at least 12 characters.';
    }

    $success = count($errors) === 0;
}

function e($value) {
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}
?><!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northstar Digital Works</title>
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="#top">Northstar Digital Works</a>
    <nav aria-label="Primary">
      <a href="#services">Services</a>
      <a href="#work">Work</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>

  <main id="top">
    <section class="hero">
      <div>
        <p class="eyebrow">PHP, CSS, and JavaScript studio</p>
        <h1>Fast websites for teams that need useful work shipped.</h1>
        <p>We design, build, and tune compact web experiences for service businesses, product teams, and local organizations.</p>
        <a class="button" href="#contact">Start a project</a>
      </div>
    </section>

    <section id="services" class="band">
      <h2>Services</h2>
      <div class="grid">
        <article><h3>Launch Sites</h3><p>Lean PHP sites with clear messaging, responsive layouts, and tidy handoff notes.</p></article>
        <article><h3>Conversion Fixes</h3><p>Focused improvements for forms, landing pages, speed, and user flows.</p></article>
        <article><h3>Care Plans</h3><p>Small retainers for updates, monitoring, and practical content support.</p></article>
      </div>
    </section>

    <section id="work" class="band work">
      <h2>Recent Work</h2>
      <ul>
        <li><strong>Harbor Clinic:</strong> appointment page redesign with clearer calls to action.</li>
        <li><strong>Trailforge Co:</strong> product microsite with performance-first CSS.</li>
        <li><strong>Civic Pantry:</strong> volunteer intake form and accessible content pass.</li>
      </ul>
    </section>

    <section id="contact" class="band contact">
      <h2>Contact</h2>
      <?php if ($success): ?>
        <div class="notice success" role="status">Thanks, <?= e($values['name']) ?>. We received your message.</div>
      <?php elseif ($_SERVER['REQUEST_METHOD'] === 'POST'): ?>
        <div class="notice error" role="alert">Please fix the highlighted fields.</div>
      <?php endif; ?>
      <form method="post" novalidate data-contact-form>
        <label>Name
          <input name="name" value="<?= e($values['name']) ?>" required>
          <span class="field-error"><?= e($errors['name'] ?? '') ?></span>
        </label>
        <label>Email
          <input name="email" type="email" value="<?= e($values['email']) ?>" required>
          <span class="field-error"><?= e($errors['email'] ?? '') ?></span>
        </label>
        <label>Message
          <textarea name="message" rows="5" required><?= e($values['message']) ?></textarea>
          <span class="field-error"><?= e($errors['message'] ?? '') ?></span>
        </label>
        <button class="button" type="submit">Send message</button>
      </form>
    </section>
  </main>

  <script src="assets/js/app.js"></script>
</body>
</html>
`,
        "public/assets/css/styles.css": `:root {
  color-scheme: light;
  --ink: #17212b;
  --muted: #5e6b76;
  --line: #d9e0e7;
  --paper: #ffffff;
  --soft: #f2f6f8;
  --accent: #0f7c80;
  --accent-dark: #0b575a;
  --alert: #a33d2d;
  --ok: #1d7a47;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background: var(--paper);
  line-height: 1.55;
}
a { color: inherit; }
.site-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  padding: 18px clamp(20px, 5vw, 72px);
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid var(--line);
}
.brand { font-weight: 800; text-decoration: none; }
nav { display: flex; gap: 18px; color: var(--muted); font-size: 0.95rem; }
nav a { text-decoration: none; }
.hero {
  min-height: 72vh;
  display: grid;
  align-items: center;
  padding: clamp(56px, 9vw, 120px) clamp(20px, 5vw, 72px);
  background:
    linear-gradient(120deg, rgba(15, 124, 128, 0.14), rgba(237, 181, 73, 0.16)),
    var(--soft);
}
.hero > div, .band { max-width: 1080px; margin: 0 auto; }
.hero h1 {
  max-width: 820px;
  font-size: clamp(2.5rem, 7vw, 5.6rem);
  line-height: 0.98;
  margin: 0 0 22px;
}
.hero p { max-width: 680px; color: var(--muted); font-size: 1.15rem; }
.eyebrow { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.78rem; font-weight: 800; color: var(--accent-dark); }
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border: 0;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  font-weight: 800;
  cursor: pointer;
}
.button:hover { background: var(--accent-dark); }
.band { padding: clamp(44px, 7vw, 84px) clamp(20px, 5vw, 72px); }
.band h2 { font-size: clamp(1.8rem, 4vw, 3rem); margin: 0 0 24px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
article { border-top: 4px solid var(--accent); padding: 18px; background: var(--soft); }
article h3 { margin-top: 0; }
.work { border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.work ul { display: grid; gap: 12px; padding-left: 20px; color: var(--muted); }
form { display: grid; gap: 16px; max-width: 720px; }
label { display: grid; gap: 6px; font-weight: 700; }
input, textarea {
  width: 100%;
  border: 1px solid var(--line);
  padding: 12px;
  font: inherit;
}
input:focus, textarea:focus { outline: 3px solid rgba(15, 124, 128, 0.22); border-color: var(--accent); }
.field-error { min-height: 1.2em; color: var(--alert); font-size: 0.9rem; }
.notice { padding: 12px 14px; margin-bottom: 16px; border-left: 4px solid; }
.notice.success { border-color: var(--ok); background: #edf8f1; }
.notice.error { border-color: var(--alert); background: #fff0ec; }
@media (max-width: 760px) {
  .site-header { align-items: flex-start; flex-direction: column; }
  nav { flex-wrap: wrap; }
  .grid { grid-template-columns: 1fr; }
}
`,
        "public/assets/js/app.js": `const form = document.querySelector("[data-contact-form]");

if (form) {
  form.addEventListener("submit", (event) => {
    const fields = {
      name: form.elements.name,
      email: form.elements.email,
      message: form.elements.message,
    };
    let valid = true;

    Object.values(fields).forEach((field) => {
      const error = field.parentElement.querySelector(".field-error");
      if (error) error.textContent = "";
      field.removeAttribute("aria-invalid");
    });

    if (!fields.name.value.trim()) {
      setError(fields.name, "Name is required.");
      valid = false;
    }

    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(fields.email.value.trim())) {
      setError(fields.email, "Enter a valid email address.");
      valid = false;
    }

    if (fields.message.value.trim().length < 12) {
      setError(fields.message, "Message must be at least 12 characters.");
      valid = false;
    }

    if (!valid) {
      event.preventDefault();
    }
  });
}

function setError(field, message) {
  field.setAttribute("aria-invalid", "true");
  const error = field.parentElement.querySelector(".field-error");
  if (error) error.textContent = message;
}
`,
        "README.md": `# Northstar Digital Works

Small PHP/CSS/JS benchmark site generated by the Kujo AI SDK + Muzzle workflow.

Run locally:

\`\`\`bash
php -S 127.0.0.1:8120 -t public
\`\`\`
`
      },
      verification: ["php -l public/index.php", "curl local homepage"]
    }
  };
}

function extractJsonObject(text) {
  const trimmed = String(text || "").trim();
  const fenced = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  const candidate = fenced ? fenced[1].trim() : trimmed;
  try {
    return JSON.parse(candidate);
  } catch (_) {
    const start = candidate.indexOf("{");
    const end = candidate.lastIndexOf("}");
    if (start !== -1 && end > start) {
      return JSON.parse(candidate.slice(start, end + 1));
    }
    throw _;
  }
}

function safeWriteFile(base, rel, content) {
  if (rel.startsWith("/") || rel.includes("..") || rel.includes("\0")) {
    throw new Error(`unsafe output path: ${rel}`);
  }
  const dest = path.join(base, rel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, String(content));
}

let ack;
let app;

try {
  ack = JSON.parse(fs.readFileSync(ackPath, "utf8"));
  const parsed = extractJsonObject(ack.output_text || "");
  if (!parsed || typeof parsed !== "object" || !parsed.files || typeof parsed.files !== "object") {
    throw new Error("model JSON did not include a files object");
  }
  app = { source: "model", reason: "", payload: parsed };
} catch (error) {
  app = fixtureApp(error.message);
}

fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

for (const [rel, content] of Object.entries(app.payload.files)) {
  safeWriteFile(outDir, rel, content);
}

const meta = {
  mode: mode || "",
  source: app.source,
  reason: app.reason,
  ack_path: ackPath,
  summary: app.payload.summary || "",
  file_count: Object.keys(app.payload.files).length,
  files: Object.keys(app.payload.files).sort(),
  verification: app.payload.verification || []
};

fs.writeFileSync(path.join(outDir, "generation-meta.json"), JSON.stringify(meta, null, 2));
console.log(JSON.stringify(meta, null, 2));

