#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const runDir = process.argv[2];

if (!runDir) {
  console.error("usage: generate-review-html.js <run-dir>");
  process.exit(2);
}

const absRunDir = path.resolve(runDir);

function readText(rel, fallback = "") {
  const file = path.join(absRunDir, rel);
  try {
    return fs.readFileSync(file, "utf8");
  } catch (_) {
    return fallback;
  }
}

function readJson(rel, fallback = {}) {
  const text = readText(rel, "");
  if (!text) return fallback;
  try {
    return JSON.parse(text);
  } catch (_) {
    return fallback;
  }
}

function html(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function pct(before, after) {
  if (!Number(before)) return "n/a";
  return `${(((before - after) / before) * 100).toFixed(1)}%`;
}

function delta(after, before) {
  const d = Number(after || 0) - Number(before || 0);
  return d > 0 ? `+${d}` : String(d);
}

function num(value) {
  return Number(value || 0).toLocaleString();
}

function money(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return `$${Number(value).toFixed(6)}`;
}

const PRICE_CATALOG = {
  "gpt-4.1-mini": {
    inputPerMTok: 0.40,
    outputPerMTok: 1.60,
    cachedInputPerMTok: 0.10,
    source: "OpenAI GPT-4.1 launch pricing"
  }
};

function rateEnv(name) {
  const raw = process.env[name] || "";
  if (!raw.trim()) return null;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : null;
}

function normalizeModelName(value) {
  return String(value || "").trim().toLowerCase();
}

function ratesForModel(model) {
  const catalogRates = PRICE_CATALOG[normalizeModelName(model)] || null;
  const inputOverride = rateEnv("PRICE_INPUT_PER_MTOK");
  const outputOverride = rateEnv("PRICE_OUTPUT_PER_MTOK");
  const rates = {
    inputPerMTok: inputOverride ?? catalogRates?.inputPerMTok ?? null,
    outputPerMTok: outputOverride ?? catalogRates?.outputPerMTok ?? null,
    cachedInputPerMTok: catalogRates?.cachedInputPerMTok ?? null,
    source: catalogRates?.source || "env override"
  };

  if (rates.inputPerMTok === null || rates.outputPerMTok === null) return null;
  if (inputOverride !== null || outputOverride !== null) rates.source = "environment override";
  return rates;
}

function tokenCost(metrics, rates) {
  if (!rates) return null;
  const inRate = rates.inputPerMTok;
  const outRate = rates.outputPerMTok;
  if (inRate === null || outRate === null) return null;
  return ((Number(metrics.input_tokens || 0) / 1_000_000) * inRate) +
    ((Number(metrics.output_tokens || 0) / 1_000_000) * outRate);
}

function barChart(title, rows, unit) {
  const max = Math.max(1, ...rows.map((row) => Number(row.value || 0)));
  const width = 720;
  const rowHeight = 58;
  const height = 62 + rows.length * rowHeight;
  const bars = rows.map((row, index) => {
    const y = 48 + index * rowHeight;
    const barWidth = Math.max(2, Math.round((Number(row.value || 0) / max) * 470));
    return `
      <text x="0" y="${y + 20}" class="chart-label">${html(row.label)}</text>
      <rect x="160" y="${y}" width="470" height="28" rx="4" class="track"></rect>
      <rect x="160" y="${y}" width="${barWidth}" height="28" rx="4" class="${html(row.className || "bar")}"></rect>
      <text x="646" y="${y + 20}" class="chart-value">${html(num(row.value))}${unit ? ` ${html(unit)}` : ""}</text>
    `;
  }).join("");

  return `
    <figure class="chart">
      <figcaption>${html(title)}</figcaption>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${html(title)}">
        ${bars}
      </svg>
    </figure>
  `;
}

function statusPill(label, ok) {
  return `<span class="pill ${ok ? "ok" : "warn"}">${html(label)}</span>`;
}

const prompt = readText("prompt.md", "");
const raw = readJson("raw/metrics.json");
const muzzle = readJson("muzzle/metrics.json");
const rawAck = readJson("raw/ack.json");
const muzzleAck = readJson("muzzle/ack.json");
const rawMeta = readJson("raw/app/generation-meta.json");
const muzzleMeta = readJson("muzzle/app/generation-meta.json");
const compareMd = readText("compare.md", "");
const runledgerReport = readText("runledger-report.md", "");
const summary = readText("summary.md", "");

const modelForRates = raw.model || muzzle.model || rawAck.model || muzzleAck.model || "";
const priceRates = ratesForModel(modelForRates);
const rawCost = tokenCost(raw, priceRates);
const muzzleCost = tokenCost(muzzle, priceRates);
const contextInRate = priceRates?.inputPerMTok ?? null;
const rawContextCost = contextInRate === null ? null : (Number(raw.estimated_exposed_local_transcript_tokens || 0) / 1_000_000) * contextInRate;
const muzzleContextCost = contextInRate === null ? null : (Number(muzzle.estimated_exposed_local_transcript_tokens || 0) / 1_000_000) * contextInRate;

const providerTokenSavings = Number(raw.total_tokens || 0) - Number(muzzle.total_tokens || 0);
const localTokenSavings = Number(raw.estimated_exposed_local_transcript_tokens || 0) - Number(muzzle.estimated_exposed_local_transcript_tokens || 0);
const dataWarnings = [];

if (rawAck.ok === false || muzzleAck.ok === false) {
  dataWarnings.push("At least one AI SDK request failed. Model token usage may be unavailable.");
}
if (raw.app_source === "fixture" || muzzle.app_source === "fixture") {
  dataWarnings.push("At least one app was rendered from the deterministic fixture instead of model output.");
}
if (Number(raw.total_tokens || 0) === 0 && Number(muzzle.total_tokens || 0) === 0) {
  dataWarnings.push("Provider token usage is zero for both runs, so cost and provider-token comparison are not meaningful yet.");
}

const htmlOut = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI SDK + Muzzle Benchmark Review</title>
  <style>
    :root {
      --ink: #18212b;
      --muted: #5e6973;
      --paper: #ffffff;
      --soft: #f4f7f8;
      --line: #d9e2e7;
      --raw: #315f93;
      --muzzle: #0d7b71;
      --accent: #b86b22;
      --ok: #1b7f49;
      --warn: #9d3d2f;
      --shadow: 0 16px 48px rgba(22, 32, 42, 0.11);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--soft);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }
    header {
      background: var(--paper);
      border-bottom: 1px solid var(--line);
      padding: 28px clamp(18px, 4vw, 56px);
    }
    .topline {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      max-width: 1240px;
      margin: 0 auto;
    }
    h1 {
      margin: 0 0 10px;
      font-size: clamp(2rem, 4.6vw, 4.6rem);
      line-height: 0.98;
      letter-spacing: 0;
    }
    .sub { color: var(--muted); max-width: 820px; margin: 0; }
    main { max-width: 1240px; margin: 0 auto; padding: 28px clamp(18px, 4vw, 56px) 64px; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }
    button, .button {
      min-height: 40px;
      border: 1px solid var(--line);
      background: var(--paper);
      color: var(--ink);
      padding: 0 14px;
      font: inherit;
      font-weight: 750;
      cursor: pointer;
      text-decoration: none;
    }
    button:hover, .button:hover { border-color: var(--muzzle); }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
    .panel {
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      padding: 18px;
      min-width: 0;
    }
    .span-12 { grid-column: span 12; }
    .span-8 { grid-column: span 8; }
    .span-6 { grid-column: span 6; }
    .span-4 { grid-column: span 4; }
    h2 { font-size: 1.05rem; margin: 0 0 14px; }
    h3 { margin: 0 0 10px; font-size: 0.98rem; }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .kpi { background: var(--soft); border: 1px solid var(--line); padding: 14px; min-height: 112px; }
    .kpi .label { color: var(--muted); font-size: 0.82rem; font-weight: 760; text-transform: uppercase; }
    .kpi .value { display: block; margin-top: 8px; font-size: clamp(1.5rem, 3vw, 2.4rem); line-height: 1; font-weight: 860; }
    .kpi .hint { color: var(--muted); font-size: 0.86rem; margin-top: 8px; }
    .two-up { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .two-up > *, details { min-width: 0; }
    .run-card.raw { border-top: 5px solid var(--raw); }
    .run-card.muzzle { border-top: 5px solid var(--muzzle); }
    .metric-list { display: grid; gap: 8px; margin-top: 12px; }
    .metric { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }
    .metric span:first-child { color: var(--muted); }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 0 9px;
      font-size: 0.78rem;
      font-weight: 820;
      border: 1px solid;
    }
    .pill.ok { color: var(--ok); background: #edf8f1; border-color: #b7dec6; }
    .pill.warn { color: var(--warn); background: #fff0ec; border-color: #efb9ad; }
    .warning { border-left: 5px solid var(--warn); background: #fff7f4; box-shadow: none; }
    .warning ul { margin: 8px 0 0; padding-left: 20px; }
    .chart { margin: 0; }
    .chart figcaption { font-weight: 820; margin-bottom: 8px; }
    .chart svg { width: 100%; height: auto; display: block; }
    .track { fill: #edf2f4; }
    .bar { fill: var(--accent); }
    .rawbar { fill: var(--raw); }
    .muzzlebar { fill: var(--muzzle); }
    .chart-label, .chart-value { fill: var(--ink); font-size: 16px; font-weight: 720; }
    .chart-value { text-anchor: start; fill: var(--muted); }
    pre {
      white-space: pre-wrap;
      overflow: auto;
      background: #111820;
      color: #edf5f6;
      padding: 16px;
      max-width: 100%;
      min-width: 0;
      max-height: 520px;
      font-size: 0.88rem;
    }
    code {
      display: block;
      max-width: 100%;
      min-width: 0;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    details { border-top: 1px solid var(--line); padding-top: 12px; }
    summary { cursor: pointer; font-weight: 820; }
    dialog {
      width: min(960px, calc(100vw - 28px));
      border: 1px solid var(--line);
      padding: 0;
      box-shadow: var(--shadow);
    }
    dialog::backdrop { background: rgba(16, 24, 32, 0.42); }
    .modal-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      border-bottom: 1px solid var(--line);
      padding: 14px 16px;
    }
    .modal-body { padding: 16px; }
    .muted { color: var(--muted); }
    @media (max-width: 900px) {
      .topline { flex-direction: column; }
      .actions { justify-content: flex-start; }
      .span-8, .span-6, .span-4 { grid-column: span 12; }
      .kpis, .two-up { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="topline">
      <div>
        <h1>AI SDK + Muzzle Benchmark</h1>
        <p class="sub">Side-by-side review of provider tokens, local transcript exposure, elapsed time, verification outcome, prompt, and RunLedger receipts.</p>
      </div>
      <div class="actions">
        <button type="button" onclick="document.querySelector('#promptModal').showModal()">View Prompt</button>
        <a class="button" href="compare.md">Compare MD</a>
        <a class="button" href="runledger-report.md">RunLedger</a>
      </div>
    </div>
  </header>

  <main class="grid">
    ${dataWarnings.length ? `
    <section class="panel warning span-12">
      <h2>Data Quality</h2>
      <ul>${dataWarnings.map((item) => `<li>${html(item)}</li>`).join("")}</ul>
    </section>` : ""}

    <section class="span-12">
      <div class="kpis">
        <div class="kpi">
          <span class="label">Provider Token Delta</span>
          <span class="value">${html(delta(muzzle.total_tokens, raw.total_tokens))}</span>
          <div class="hint">Muzzle should not change provider tokens when the model prompt is the same.</div>
        </div>
        <div class="kpi">
          <span class="label">Local Context Saved</span>
          <span class="value">${html(num(localTokenSavings))}</span>
          <div class="hint">${html(pct(raw.estimated_exposed_local_transcript_tokens, muzzle.estimated_exposed_local_transcript_tokens))} fewer estimated transcript tokens.</div>
        </div>
        <div class="kpi">
          <span class="label">AI Time Delta</span>
          <span class="value">${html(delta(muzzle.ai_duration_ms, raw.ai_duration_ms))} ms</span>
          <div class="hint">Muzzle includes wrapper overhead plus quieter output capture.</div>
        </div>
        <div class="kpi">
          <span class="label">Model Cost Delta</span>
          <span class="value">${rawCost === null || muzzleCost === null ? "n/a" : html(money(muzzleCost - rawCost))}</span>
          <div class="hint">${priceRates ? `${html(modelForRates)} at $${priceRates.inputPerMTok}/$${priceRates.outputPerMTok} per 1M input/output tokens.` : "Set PRICE_INPUT_PER_MTOK and PRICE_OUTPUT_PER_MTOK to estimate costs."}</div>
        </div>
      </div>
    </section>

    ${priceRates ? `
    <section class="panel span-12">
      <h2>Pricing Assumptions</h2>
      <p class="muted">Using <strong>${html(modelForRates)}</strong> rates: $${html(priceRates.inputPerMTok)} / 1M input tokens, $${html(priceRates.outputPerMTok)} / 1M output tokens${priceRates.cachedInputPerMTok !== null ? `, and $${html(priceRates.cachedInputPerMTok)} / 1M cached input tokens` : ""}. Review context cost estimates treat local transcript exposure as hypothetical input tokens at the input-token rate. Source: ${html(priceRates.source)}.</p>
    </section>` : ""}

    <section class="panel span-12">
      <h2>Run Comparison</h2>
      <div class="two-up">
        <article class="panel run-card raw">
          <h3>Raw</h3>
          ${statusPill(rawAck.ok === false ? "AI request failed" : "AI request ok", rawAck.ok !== false)}
          ${statusPill(raw.app_source === "fixture" ? "fixture app" : "model app", raw.app_source !== "fixture")}
          <div class="metric-list">
            <div class="metric"><span>Provider / model</span><strong>${html(raw.provider || rawAck.provider)} / ${html(raw.model || rawAck.model)}</strong></div>
            <div class="metric"><span>Input tokens</span><strong>${html(num(raw.input_tokens))}</strong></div>
            <div class="metric"><span>Output tokens</span><strong>${html(num(raw.output_tokens))}</strong></div>
            <div class="metric"><span>Total tokens</span><strong>${html(num(raw.total_tokens))}</strong></div>
            <div class="metric"><span>AI duration</span><strong>${html(num(raw.ai_duration_ms))} ms</strong></div>
            <div class="metric"><span>Verify duration</span><strong>${html(num(raw.verify_duration_ms))} ms</strong></div>
            <div class="metric"><span>Local transcript estimate</span><strong>${html(num(raw.estimated_exposed_local_transcript_tokens))} tokens</strong></div>
            <div class="metric"><span>Model token cost</span><strong>${rawCost === null ? "n/a" : html(money(rawCost))}</strong></div>
            <div class="metric"><span>Review context cost estimate</span><strong>${rawContextCost === null ? "n/a" : html(money(rawContextCost))}</strong></div>
            <div class="metric"><span>RunLedger ID</span><strong>${html(raw.runledger_id || "not-created")}</strong></div>
          </div>
        </article>
        <article class="panel run-card muzzle">
          <h3>Muzzle</h3>
          ${statusPill(muzzleAck.ok === false ? "AI request failed" : "AI request ok", muzzleAck.ok !== false)}
          ${statusPill(muzzle.app_source === "fixture" ? "fixture app" : "model app", muzzle.app_source !== "fixture")}
          <div class="metric-list">
            <div class="metric"><span>Provider / model</span><strong>${html(muzzle.provider || muzzleAck.provider)} / ${html(muzzle.model || muzzleAck.model)}</strong></div>
            <div class="metric"><span>Input tokens</span><strong>${html(num(muzzle.input_tokens))}</strong></div>
            <div class="metric"><span>Output tokens</span><strong>${html(num(muzzle.output_tokens))}</strong></div>
            <div class="metric"><span>Total tokens</span><strong>${html(num(muzzle.total_tokens))}</strong></div>
            <div class="metric"><span>AI duration</span><strong>${html(num(muzzle.ai_duration_ms))} ms</strong></div>
            <div class="metric"><span>Verify duration</span><strong>${html(num(muzzle.verify_duration_ms))} ms</strong></div>
            <div class="metric"><span>Local transcript estimate</span><strong>${html(num(muzzle.estimated_exposed_local_transcript_tokens))} tokens</strong></div>
            <div class="metric"><span>Model token cost</span><strong>${muzzleCost === null ? "n/a" : html(money(muzzleCost))}</strong></div>
            <div class="metric"><span>Review context cost estimate</span><strong>${muzzleContextCost === null ? "n/a" : html(money(muzzleContextCost))}</strong></div>
            <div class="metric"><span>RunLedger ID</span><strong>${html(muzzle.runledger_id || "not-created")}</strong></div>
          </div>
        </article>
      </div>
    </section>

    <section class="panel span-6">
      ${barChart("Estimated Local Transcript Tokens", [
        { label: "Raw", value: raw.estimated_exposed_local_transcript_tokens, className: "rawbar" },
        { label: "Muzzle", value: muzzle.estimated_exposed_local_transcript_tokens, className: "muzzlebar" }
      ], "tokens")}
    </section>

    <section class="panel span-6">
      ${barChart("AI SDK Provider Tokens", [
        { label: "Raw", value: raw.total_tokens, className: "rawbar" },
        { label: "Muzzle", value: muzzle.total_tokens, className: "muzzlebar" }
      ], "tokens")}
    </section>

    <section class="panel span-6">
      ${barChart("AI Request Time", [
        { label: "Raw", value: raw.ai_duration_ms, className: "rawbar" },
        { label: "Muzzle", value: muzzle.ai_duration_ms, className: "muzzlebar" }
      ], "ms")}
    </section>

    <section class="panel span-6">
      ${barChart("Verification Time", [
        { label: "Raw", value: raw.verify_duration_ms, className: "rawbar" },
        { label: "Muzzle", value: muzzle.verify_duration_ms, className: "muzzlebar" }
      ], "ms")}
    </section>

    <section class="panel span-12">
      <h2>Errors And Raw Ack</h2>
      <div class="two-up">
        <details open>
          <summary>Raw ack</summary>
          <pre><code>${html(JSON.stringify(rawAck, null, 2))}</code></pre>
        </details>
        <details open>
          <summary>Muzzle ack</summary>
          <pre><code>${html(JSON.stringify(muzzleAck, null, 2))}</code></pre>
        </details>
      </div>
    </section>

    <section class="panel span-6">
      <h2>Compare Markdown</h2>
      <pre><code>${html(compareMd)}</code></pre>
    </section>

    <section class="panel span-6">
      <h2>RunLedger Report</h2>
      <pre><code>${html(runledgerReport)}</code></pre>
    </section>

    <section class="panel span-12">
      <h2>Run Summary</h2>
      <pre><code>${html(summary)}</code></pre>
    </section>
  </main>

  <dialog id="promptModal">
    <div class="modal-head">
      <strong>Benchmark Prompt</strong>
      <button type="button" onclick="document.querySelector('#promptModal').close()">Close</button>
    </div>
    <div class="modal-body">
      <pre><code>${html(prompt)}</code></pre>
    </div>
  </dialog>
</body>
</html>
`;

const outPath = path.join(absRunDir, "review.html");
fs.writeFileSync(outPath, htmlOut);
console.log(outPath);
