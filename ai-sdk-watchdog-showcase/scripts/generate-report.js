#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const runDir = process.argv[2];
if (!runDir) {
	console.error("usage: generate-report.js <run-dir>");
	process.exit(2);
}

function readJson(file, fallback = null) {
	try {
		return JSON.parse(fs.readFileSync(file, "utf8"));
	} catch {
		return fallback;
	}
}

function listResponses() {
	const dir = path.join(runDir, "ai-chat");
	if (!fs.existsSync(dir)) {
		return [];
	}
	return fs.readdirSync(dir)
		.filter((name) => /^response-\d+\.json$/.test(name))
		.sort()
		.map((name) => {
			const data = readJson(path.join(dir, name), {});
			return { name, data };
		});
}

function dataArray(apiPayload, key) {
	const data = apiPayload && apiPayload.data;
	if (Array.isArray(data)) {
		return data;
	}
	if (data && Array.isArray(data[key])) {
		return data[key];
	}
	if (data && Array.isArray(data.items)) {
		return data.items;
	}
	if (data && Array.isArray(data.rows)) {
		return data.rows;
	}
	return [];
}

function firstString(...values) {
	for (const value of values) {
		if (typeof value === "string" && value.trim()) {
			return value.trim();
		}
	}
	return "";
}

function numberValue(value) {
	const next = Number(value);
	return Number.isFinite(next) ? next : 0;
}

const meta = readJson(path.join(runDir, "run-meta.json"), {});
const stats = readJson(path.join(runDir, "watchdog", "stats.json"), {});
const requestsPayload = readJson(path.join(runDir, "watchdog", "requests.json"), {});
const toolsPayload = readJson(path.join(runDir, "watchdog", "tool-calls.json"), {});
const stepsPayload = readJson(path.join(runDir, "watchdog", "agent-steps.json"), {});
const requests = dataArray(requestsPayload, "requests");
const toolCalls = dataArray(toolsPayload, "tool_calls");
const agentSteps = dataArray(stepsPayload, "agent_steps");
const responses = listResponses();

const successCount = requests.filter((row) => row.status === "success").length;
const errorCount = requests.filter((row) => row.status === "error").length;
const totalTokens = requests.reduce((sum, row) => sum + numberValue(row.total_tokens), 0);
const totalCost = requests.reduce((sum, row) => sum + numberValue(row.cost_usd), 0);
const avgLatency = requests.length
	? Math.round(requests.reduce((sum, row) => sum + numberValue(row.latency_ms), 0) / requests.length)
	: 0;

const lines = [];
lines.push("# AI SDK + Watchdog Showcase Summary");
lines.push("");
lines.push(`Run: \`${path.basename(runDir)}\``);
lines.push("");
lines.push("## Services");
lines.push("");
lines.push(`- Upstream mode: ${meta.upstream_mode || "fixture"}`);
lines.push(`- Watchdog dashboard: ${meta.watchdog_url || ""}`);
lines.push(`- Watchdog proxy: ${meta.watchdog_proxy_url || ""}`);
lines.push(`- Upstream URL: ${meta.upstream_url || ""}`);
lines.push(`- Upstream base URL: ${meta.upstream_base_url || ""}`);
lines.push(`- Model: \`${meta.model || ""}\``);
lines.push(`- AI Chat bridge: \`${meta.ai_chat_bridge || ""}\``);
lines.push(`- AI SDK path: \`${meta.ai_sdk_path || ""}\``);
lines.push("");
lines.push("## AI Chat Bridge Calls");
lines.push("");
lines.push("| Call | Status | Model | Tokens | Notes |");
lines.push("|---|---:|---|---:|---|");
for (const response of responses) {
	const data = response.data || {};
	const ok = data.ok === true ? "ok" : "error";
	const usage = data.usage || {};
	const tokens = numberValue(usage.total_tokens);
	const model = firstString(data.model, data.requested_model, "unknown");
	const note = data.ok
		? firstString(data.output_text, "").slice(0, 110)
		: firstString(data.error && data.error.code, data.error && data.error.message, "non-ok response");
	lines.push(`| \`${response.name}\` | ${ok} | \`${model}\` | ${tokens} | ${note.replace(/\|/g, "\\|")} |`);
}
lines.push("");
lines.push("## Watchdog Evidence");
lines.push("");
lines.push("| Signal | Value |");
lines.push("|---|---:|");
lines.push(`| Requests captured | ${requests.length} |`);
lines.push(`| Successful requests | ${successCount} |`);
lines.push(`| Error requests | ${errorCount} |`);
lines.push(`| Proxy tool-call records | ${toolCalls.length} |`);
lines.push(`| Proxy agent-step records | ${agentSteps.length} |`);
lines.push(`| Total provider tokens | ${totalTokens} |`);
lines.push(`| Estimated cost USD | ${totalCost.toFixed(6)} |`);
lines.push(`| Average latency ms | ${avgLatency} |`);
lines.push("");
lines.push("## Recent Watchdog Requests");
lines.push("");
lines.push("| Status | Model | Latency | Tokens | Error | Prompt Summary |");
lines.push("|---|---|---:|---:|---|---|");
for (const row of requests.slice(0, 8)) {
	const prompt = firstString(row.prompt_summary, "").slice(0, 80).replace(/\|/g, "\\|");
	const error = firstString(row.error_code, row.error_message, "");
	lines.push(`| ${row.status || ""} | \`${row.model || ""}\` | ${numberValue(row.latency_ms)} | ${numberValue(row.total_tokens)} | ${error.replace(/\|/g, "\\|")} | ${prompt} |`);
}
lines.push("");
lines.push("## Artifacts");
lines.push("");
lines.push("- `watchdog/export.json` contains the complete Watchdog export for this demo run.");
lines.push("- `watchdog/requests.json`, `watchdog/tool-calls.json`, and `watchdog/agent-steps.json` are the fastest files to inspect manually.");
lines.push("- `logs/watchdog.log` contains the Watchdog service log.");
if ((meta.upstream_mode || "fixture") === "fixture") {
	lines.push("- `logs/mock-upstream.log` contains the fixture upstream service log.");
}
lines.push("");
lines.push("## Why Watchdog Helped");
lines.push("");
lines.push("The AI Chat bridge only needed the normal AI SDK response contract. Watchdog added an observable proxy layer around the same OpenAI-compatible call, which made success, latency, usage, cost, and provider failure evidence available without changing the example app response shape.");
lines.push("");

fs.writeFileSync(path.join(runDir, "summary.md"), `${lines.join("\n")}\n`);

const compact = {
	run_dir: runDir,
	services: {
		watchdog_url: meta.watchdog_url || "",
		watchdog_proxy_url: meta.watchdog_proxy_url || "",
		upstream_url: meta.upstream_url || "",
		upstream_base_url: meta.upstream_base_url || "",
		upstream_mode: meta.upstream_mode || "fixture",
		model: meta.model || ""
	},
	ai_chat_calls: responses.length,
	watchdog: {
		requests: requests.length,
		successes: successCount,
		errors: errorCount,
		tool_calls: toolCalls.length,
		agent_steps: agentSteps.length,
		total_tokens: totalTokens,
		estimated_cost_usd: Number(totalCost.toFixed(8)),
		average_latency_ms: avgLatency,
		stats: stats && stats.data ? stats.data : stats
	}
};
fs.writeFileSync(path.join(runDir, "summary.json"), `${JSON.stringify(compact, null, 2)}\n`);
