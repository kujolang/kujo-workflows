#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const [suiteDirArg, ...runDirArgs] = process.argv.slice(2);

if (!suiteDirArg) {
  console.error("usage: generate-suite-review-html.js <suite-dir> [run-dir...]");
  process.exit(2);
}

const suiteDir = path.resolve(suiteDirArg);
let runDirs = runDirArgs.map((dir) => path.resolve(dir));

if (runDirs.length === 0) {
  const listPath = path.join(suiteDir, "run-dirs.txt");
  if (fs.existsSync(listPath)) {
    runDirs = fs.readFileSync(listPath, "utf8").split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((dir) => path.resolve(dir));
  }
}

function readJson(file, fallback = {}) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (_) {
    return fallback;
  }
}

function readText(file, fallback = "") {
  try {
    return fs.readFileSync(file, "utf8");
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

function num(value, digits = 0) {
  const n = Number(value || 0);
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

function money(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return `$${Number(value).toFixed(6)}`;
}

function pct(before, after) {
  if (!Number(before)) return "n/a";
  return `${(((before - after) / before) * 100).toFixed(1)}%`;
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

function ratesForModel(model) {
  const catalogRates = PRICE_CATALOG[String(model || "").trim().toLowerCase()] || null;
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

function modelCost(metrics, rates) {
  if (!rates) return null;
  return (Number(metrics.input_tokens || 0) / 1_000_000 * rates.inputPerMTok) +
    (Number(metrics.output_tokens || 0) / 1_000_000 * rates.outputPerMTok);
}

function contextCost(metrics, rates) {
  if (!rates) return null;
  return Number(metrics.estimated_exposed_local_transcript_tokens || 0) / 1_000_000 * rates.inputPerMTok;
}

function mean(values) {
  const clean = values.filter((value) => Number.isFinite(Number(value))).map(Number);
  if (!clean.length) return 0;
  return clean.reduce((sum, value) => sum + value, 0) / clean.length;
}

function sd(values) {
  const clean = values.filter((value) => Number.isFinite(Number(value))).map(Number);
  if (clean.length < 2) return 0;
  const avg = mean(clean);
  const variance = mean(clean.map((value) => (value - avg) ** 2));
  return Math.sqrt(variance);
}

function min(values) {
  const clean = values.filter((value) => Number.isFinite(Number(value))).map(Number);
  return clean.length ? Math.min(...clean) : 0;
}

function max(values) {
  const clean = values.filter((value) => Number.isFinite(Number(value))).map(Number);
  return clean.length ? Math.max(...clean) : 0;
}

function summarize(values) {
  return {
    mean: mean(values),
    sd: sd(values),
    min: min(values),
    max: max(values)
  };
}

const trials = runDirs.map((runDir, index) => {
  const raw = readJson(path.join(runDir, "raw/metrics.json"));
  const muzzle = readJson(path.join(runDir, "muzzle/metrics.json"));
  const rawAck = readJson(path.join(runDir, "raw/ack.json"));
  const muzzleAck = readJson(path.join(runDir, "muzzle/ack.json"));
  const model = raw.model || muzzle.model || rawAck.model || muzzleAck.model || "unknown";
  const rates = ratesForModel(model);
  return {
    index: index + 1,
    runDir,
    model,
    raw,
    muzzle,
    rawOk: raw.ai_ok === true || raw.ai_ok === "true",
    muzzleOk: muzzle.ai_ok === true || muzzle.ai_ok === "true",
    rawModelApp: raw.app_source === "model",
    muzzleModelApp: muzzle.app_source === "model",
    providerTokenDelta: Number(muzzle.total_tokens || 0) - Number(raw.total_tokens || 0),
    outputTokenDelta: Number(muzzle.output_tokens || 0) - Number(raw.output_tokens || 0),
    localTokenSavings: Number(raw.estimated_exposed_local_transcript_tokens || 0) - Number(muzzle.estimated_exposed_local_transcript_tokens || 0),
    localByteSavings: Number(raw.exposed_local_transcript_bytes || 0) - Number(muzzle.exposed_local_transcript_bytes || 0),
    aiDurationDelta: Number(muzzle.ai_duration_ms || 0) - Number(raw.ai_duration_ms || 0),
    verifyDurationDelta: Number(muzzle.verify_duration_ms || 0) - Number(raw.verify_duration_ms || 0),
    rawModelCost: modelCost(raw, rates),
    muzzleModelCost: modelCost(muzzle, rates),
    rawContextCost: contextCost(raw, rates),
    muzzleContextCost: contextCost(muzzle, rates),
    rates
  };
});

for (const trial of trials) {
  trial.modelCostDelta = trial.rawModelCost === null || trial.muzzleModelCost === null ? null : trial.muzzleModelCost - trial.rawModelCost;
  trial.contextCostSavings = trial.rawContextCost === null || trial.muzzleContextCost === null ? null : trial.rawContextCost - trial.muzzleContextCost;
}

const primaryModel = trials[0]?.model || "unknown";
const primaryRates = trials.find((trial) => trial.rates)?.rates || null;
const successfulPairs = trials.filter((trial) => trial.rawOk && trial.muzzleOk);
const modelAppPairs = trials.filter((trial) => trial.rawModelApp && trial.muzzleModelApp);

const aggregate = {
  trial_count: trials.length,
  successful_pair_count: successfulPairs.length,
  model_app_pair_count: modelAppPairs.length,
  raw_success_rate: trials.length ? trials.filter((trial) => trial.rawOk).length / trials.length : 0,
  muzzle_success_rate: trials.length ? trials.filter((trial) => trial.muzzleOk).length / trials.length : 0,
  provider_token_delta: summarize(trials.map((trial) => trial.providerTokenDelta)),
  output_token_delta: summarize(trials.map((trial) => trial.outputTokenDelta)),
  local_token_savings: summarize(trials.map((trial) => trial.localTokenSavings)),
  local_byte_savings: summarize(trials.map((trial) => trial.localByteSavings)),
  local_savings_percent: summarize(trials.map((trial) => {
    const raw = Number(trial.raw.estimated_exposed_local_transcript_tokens || 0);
    const muzzle = Number(trial.muzzle.estimated_exposed_local_transcript_tokens || 0);
    return raw ? ((raw - muzzle) / raw) * 100 : 0;
  })),
  ai_duration_delta_ms: summarize(trials.map((trial) => trial.aiDurationDelta)),
  verify_duration_delta_ms: summarize(trials.map((trial) => trial.verifyDurationDelta)),
  model_cost_delta: summarize(trials.map((trial) => trial.modelCostDelta).filter((value) => value !== null)),
  context_cost_savings: summarize(trials.map((trial) => trial.contextCostSavings).filter((value) => value !== null))
};

const summaryJson = {
  suite_dir: suiteDir,
  model: primaryModel,
  pricing: primaryRates,
  aggregate,
  trials: trials.map((trial) => ({
    index: trial.index,
    run_dir: trial.runDir,
    raw_ok: trial.rawOk,
    muzzle_ok: trial.muzzleOk,
    raw_app_source: trial.raw.app_source,
    muzzle_app_source: trial.muzzle.app_source,
    provider_token_delta: trial.providerTokenDelta,
    local_token_savings: trial.localTokenSavings,
    ai_duration_delta_ms: trial.aiDurationDelta,
    verify_duration_delta_ms: trial.verifyDurationDelta,
    model_cost_delta: trial.modelCostDelta,
    context_cost_savings: trial.contextCostSavings
  }))
};

function barChart(title, rows, unit = "") {
  const maxValue = Math.max(1, ...rows.map((row) => Math.abs(Number(row.value || 0))));
  const width = 760;
  const rowHeight = 56;
  const height = 62 + rows.length * rowHeight;
  const bars = rows.map((row, index) => {
    const y = 46 + index * rowHeight;
    const barWidth = Math.max(2, Math.round((Math.abs(Number(row.value || 0)) / maxValue) * 440));
    return `
      <text x="0" y="${y + 19}" class="chart-label">${html(row.label)}</text>
      <rect x="190" y="${y}" width="440" height="28" rx="4" class="track"></rect>
      <rect x="190" y="${y}" width="${barWidth}" height="28" rx="4" class="${html(row.className || "bar")}"></rect>
      <text x="646" y="${y + 19}" class="chart-value">${html(num(row.value, row.digits || 0))}${unit ? ` ${html(unit)}` : ""}</text>
    `;
  }).join("");
  return `
    <figure class="chart">
      <figcaption>${html(title)}</figcaption>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${html(title)}">${bars}</svg>
    </figure>
  `;
}

function kpi(label, value, hint) {
  return `<div class="kpi"><span class="label">${html(label)}</span><span class="value">${html(value)}</span><div class="hint">${html(hint)}</div></div>`;
}

const trialRows = trials.map((trial) => `
  <tr>
    <td>${trial.index}</td>
    <td>${trial.rawOk && trial.muzzleOk ? "ok" : "partial"}</td>
    <td>${html(trial.raw.app_source || "-")} / ${html(trial.muzzle.app_source || "-")}</td>
    <td>${num(trial.providerTokenDelta)}</td>
    <td>${num(trial.localTokenSavings)}</td>
    <td>${num(trial.aiDurationDelta)}</td>
    <td>${trial.modelCostDelta === null ? "n/a" : money(trial.modelCostDelta)}</td>
    <td>${trial.contextCostSavings === null ? "n/a" : money(trial.contextCostSavings)}</td>
    <td><a href="${html(path.relative(suiteDir, path.join(trial.runDir, "review.html")))}">review</a></td>
  </tr>
`).join("");

const summaryMd = `# AI SDK + Muzzle Benchmark Suite Summary

- Trials: ${trials.length}
- Model: ${primaryModel}
- Successful paired calls: ${successfulPairs.length}/${trials.length}
- Model-generated app pairs: ${modelAppPairs.length}/${trials.length}

## Averages

| Metric | Mean | Std dev | Min | Max |
|---|---:|---:|---:|---:|
| Provider token delta | ${num(aggregate.provider_token_delta.mean, 1)} | ${num(aggregate.provider_token_delta.sd, 1)} | ${num(aggregate.provider_token_delta.min)} | ${num(aggregate.provider_token_delta.max)} |
| Local transcript tokens saved | ${num(aggregate.local_token_savings.mean, 1)} | ${num(aggregate.local_token_savings.sd, 1)} | ${num(aggregate.local_token_savings.min)} | ${num(aggregate.local_token_savings.max)} |
| Local transcript savings percent | ${num(aggregate.local_savings_percent.mean, 1)}% | ${num(aggregate.local_savings_percent.sd, 1)}% | ${num(aggregate.local_savings_percent.min, 1)}% | ${num(aggregate.local_savings_percent.max, 1)}% |
| AI duration delta ms | ${num(aggregate.ai_duration_delta_ms.mean, 1)} | ${num(aggregate.ai_duration_delta_ms.sd, 1)} | ${num(aggregate.ai_duration_delta_ms.min)} | ${num(aggregate.ai_duration_delta_ms.max)} |
| Verify duration delta ms | ${num(aggregate.verify_duration_delta_ms.mean, 1)} | ${num(aggregate.verify_duration_delta_ms.sd, 1)} | ${num(aggregate.verify_duration_delta_ms.min)} | ${num(aggregate.verify_duration_delta_ms.max)} |
`;

const htmlOut = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI SDK + Muzzle Benchmark Suite</title>
  <style>
    :root {
      --ink: #18212b;
      --muted: #5e6973;
      --paper: #fff;
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
    header { background: var(--paper); border-bottom: 1px solid var(--line); padding: 28px clamp(18px, 4vw, 56px); }
    main { max-width: 1240px; margin: 0 auto; padding: 28px clamp(18px, 4vw, 56px) 64px; }
    h1 { margin: 0 0 10px; font-size: clamp(2rem, 4.6vw, 4.6rem); line-height: 0.98; letter-spacing: 0; }
    h2 { font-size: 1.05rem; margin: 0 0 14px; }
    .sub { color: var(--muted); max-width: 880px; margin: 0; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
    .span-12 { grid-column: span 12; }
    .span-6 { grid-column: span 6; }
    .span-4 { grid-column: span 4; }
    .panel { min-width: 0; background: var(--paper); border: 1px solid var(--line); box-shadow: var(--shadow); padding: 18px; }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .kpi { background: var(--soft); border: 1px solid var(--line); padding: 14px; min-height: 112px; }
    .kpi .label { color: var(--muted); font-size: 0.82rem; font-weight: 760; text-transform: uppercase; }
    .kpi .value { display: block; margin-top: 8px; font-size: clamp(1.45rem, 3vw, 2.35rem); line-height: 1; font-weight: 860; }
    .kpi .hint { color: var(--muted); font-size: 0.86rem; margin-top: 8px; }
    .callout { border-left: 5px solid var(--muzzle); box-shadow: none; }
    .warning { border-left-color: var(--warn); background: #fff7f4; }
    .chart { margin: 0; }
    .chart figcaption { font-weight: 820; margin-bottom: 8px; }
    .chart svg { width: 100%; height: auto; display: block; }
    .track { fill: #edf2f4; }
    .bar { fill: var(--accent); }
    .rawbar { fill: var(--raw); }
    .muzzlebar { fill: var(--muzzle); }
    .chart-label, .chart-value { fill: var(--ink); font-size: 16px; font-weight: 720; }
    .chart-value { fill: var(--muted); }
    table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
    th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 10px 8px; vertical-align: top; }
    th { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; }
    a { color: var(--muzzle); font-weight: 760; }
    pre { white-space: pre-wrap; overflow: auto; max-width: 100%; background: #111820; color: #edf5f6; padding: 16px; }
    @media (max-width: 900px) {
      .span-6, .span-4 { grid-column: span 12; }
      .kpis { grid-template-columns: 1fr; }
      table { display: block; overflow-x: auto; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Benchmark Suite</h1>
    <p class="sub">Repeated paired Raw vs Muzzle trials. Provider tokens are the actual AI SDK usage. Local transcript tokens estimate command output that would otherwise enter the agent context window.</p>
  </header>
  <main class="grid">
    <section class="span-12">
      <div class="kpis">
        ${kpi("Trials", String(trials.length), `${successfulPairs.length}/${trials.length} successful paired AI calls`)}
        ${kpi("Avg Local Context Saved", `${num(aggregate.local_token_savings.mean, 0)} tokens`, `${num(aggregate.local_savings_percent.mean, 1)}% average reduction`)}
        ${kpi("Avg Provider Token Delta", `${num(aggregate.provider_token_delta.mean, 1)}`, "Near zero means Muzzle is not changing the model prompt")}
        ${kpi("Avg AI Time Delta", `${num(aggregate.ai_duration_delta_ms.mean, 0)} ms`, "Muzzle minus raw; negative means Muzzle was faster")}
      </div>
    </section>

    <section class="panel callout span-12">
      <h2>How To Read This</h2>
      <p>Muzzle is a context-window optimization. It should not materially reduce the provider input tokens for the original model request, because the same prompt is sent in both modes. The main signal is local transcript savings: fewer build/test/verify log tokens that an agent has to carry through the conversation.</p>
    </section>

    ${primaryRates ? `<section class="panel span-12"><h2>Pricing Assumptions</h2><p class="sub">${html(primaryModel)}: $${primaryRates.inputPerMTok} / 1M input tokens, $${primaryRates.outputPerMTok} / 1M output tokens. Review context estimates use the input-token rate as a proxy for context-window cost. Source: ${html(primaryRates.source)}.</p></section>` : ""}

    <section class="panel span-6">
      ${barChart("Average Token Counts", [
        { label: "Raw provider tokens", value: mean(trials.map((trial) => trial.raw.total_tokens)), className: "rawbar" },
        { label: "Muzzle provider tokens", value: mean(trials.map((trial) => trial.muzzle.total_tokens)), className: "muzzlebar" },
        { label: "Raw local transcript", value: mean(trials.map((trial) => trial.raw.estimated_exposed_local_transcript_tokens)), className: "rawbar" },
        { label: "Muzzle local transcript", value: mean(trials.map((trial) => trial.muzzle.estimated_exposed_local_transcript_tokens)), className: "muzzlebar" }
      ], "tokens")}
    </section>

    <section class="panel span-6">
      ${barChart("Average Time", [
        { label: "Raw AI request", value: mean(trials.map((trial) => trial.raw.ai_duration_ms)), className: "rawbar" },
        { label: "Muzzle AI request", value: mean(trials.map((trial) => trial.muzzle.ai_duration_ms)), className: "muzzlebar" },
        { label: "Raw verify", value: mean(trials.map((trial) => trial.raw.verify_duration_ms)), className: "rawbar" },
        { label: "Muzzle verify", value: mean(trials.map((trial) => trial.muzzle.verify_duration_ms)), className: "muzzlebar" }
      ], "ms")}
    </section>

    <section class="panel span-6">
      ${barChart("Average Cost Estimates", [
        { label: "Raw model cost", value: mean(trials.map((trial) => trial.rawModelCost || 0)), className: "rawbar", digits: 6 },
        { label: "Muzzle model cost", value: mean(trials.map((trial) => trial.muzzleModelCost || 0)), className: "muzzlebar", digits: 6 },
        { label: "Raw review context", value: mean(trials.map((trial) => trial.rawContextCost || 0)), className: "rawbar", digits: 6 },
        { label: "Muzzle review context", value: mean(trials.map((trial) => trial.muzzleContextCost || 0)), className: "muzzlebar", digits: 6 }
      ], "USD")}
    </section>

    <section class="panel span-6">
      ${barChart("Average Deltas", [
        { label: "Provider token delta", value: aggregate.provider_token_delta.mean, className: "bar", digits: 1 },
        { label: "Output token delta", value: aggregate.output_token_delta.mean, className: "bar", digits: 1 },
        { label: "Local tokens saved", value: aggregate.local_token_savings.mean, className: "muzzlebar", digits: 1 },
        { label: "AI time delta", value: aggregate.ai_duration_delta_ms.mean, className: "bar", digits: 1 }
      ])}
    </section>

    <section class="panel span-12">
      <h2>Aggregate Stats</h2>
      <table>
        <thead><tr><th>Metric</th><th>Mean</th><th>Std dev</th><th>Min</th><th>Max</th></tr></thead>
        <tbody>
          <tr><td>Provider token delta</td><td>${num(aggregate.provider_token_delta.mean, 1)}</td><td>${num(aggregate.provider_token_delta.sd, 1)}</td><td>${num(aggregate.provider_token_delta.min)}</td><td>${num(aggregate.provider_token_delta.max)}</td></tr>
          <tr><td>Local transcript tokens saved</td><td>${num(aggregate.local_token_savings.mean, 1)}</td><td>${num(aggregate.local_token_savings.sd, 1)}</td><td>${num(aggregate.local_token_savings.min)}</td><td>${num(aggregate.local_token_savings.max)}</td></tr>
          <tr><td>Local transcript savings percent</td><td>${num(aggregate.local_savings_percent.mean, 1)}%</td><td>${num(aggregate.local_savings_percent.sd, 1)}%</td><td>${num(aggregate.local_savings_percent.min, 1)}%</td><td>${num(aggregate.local_savings_percent.max, 1)}%</td></tr>
          <tr><td>AI duration delta ms</td><td>${num(aggregate.ai_duration_delta_ms.mean, 1)}</td><td>${num(aggregate.ai_duration_delta_ms.sd, 1)}</td><td>${num(aggregate.ai_duration_delta_ms.min)}</td><td>${num(aggregate.ai_duration_delta_ms.max)}</td></tr>
          <tr><td>Review context cost saved</td><td>${money(aggregate.context_cost_savings.mean)}</td><td>${money(aggregate.context_cost_savings.sd)}</td><td>${money(aggregate.context_cost_savings.min)}</td><td>${money(aggregate.context_cost_savings.max)}</td></tr>
        </tbody>
      </table>
    </section>

    <section class="panel span-12">
      <h2>Trials</h2>
      <table>
        <thead><tr><th>#</th><th>Status</th><th>App source</th><th>Provider token delta</th><th>Local tokens saved</th><th>AI time delta ms</th><th>Model cost delta</th><th>Context cost saved</th><th>Run</th></tr></thead>
        <tbody>${trialRows}</tbody>
      </table>
    </section>

    <section class="panel span-12">
      <h2>Machine Summary</h2>
      <pre>${html(JSON.stringify(summaryJson, null, 2))}</pre>
    </section>
  </main>
</body>
</html>
`;

fs.mkdirSync(suiteDir, { recursive: true });
fs.writeFileSync(path.join(suiteDir, "summary.json"), JSON.stringify(summaryJson, null, 2));
fs.writeFileSync(path.join(suiteDir, "summary.md"), summaryMd);
const outPath = path.join(suiteDir, "review.html");
fs.writeFileSync(outPath, htmlOut);
console.log(outPath);

