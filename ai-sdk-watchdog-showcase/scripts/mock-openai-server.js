#!/usr/bin/env node
"use strict";

const http = require("node:http");

const args = process.argv.slice(2);
const portFlagIndex = args.indexOf("--port");
const port = Number.parseInt(portFlagIndex >= 0 ? args[portFlagIndex + 1] : process.env.PORT || "8781", 10);
const listenPort = Number.isFinite(port) && port > 0 ? port : 8781;

function sendJson(res, status, payload) {
	res.writeHead(status, {
		"Content-Type": "application/json",
		"Cache-Control": "no-store"
	});
	res.end(JSON.stringify(payload));
}

function collectBody(req) {
	return new Promise((resolve, reject) => {
		let body = "";
		req.setEncoding("utf8");
		req.on("data", (chunk) => {
			body += chunk;
			if (body.length > 1024 * 1024) {
				reject(new Error("request body too large"));
				req.destroy();
			}
		});
		req.on("end", () => resolve(body));
		req.on("error", reject);
	});
}

function usageFor(promptText, outputText) {
	const inputTokens = Math.max(8, Math.ceil(promptText.length / 4));
	const outputTokens = Math.max(12, Math.ceil(outputText.length / 4));
	return {
		prompt_tokens: inputTokens,
		completion_tokens: outputTokens,
		total_tokens: inputTokens + outputTokens
	};
}

function lastUserMessage(messages) {
	if (!Array.isArray(messages)) {
		return "";
	}
	for (let i = messages.length - 1; i >= 0; i -= 1) {
		const entry = messages[i];
		if (entry && entry.role === "user") {
			return String(entry.content || "");
		}
	}
	return "";
}

function completionText(promptText) {
	if (/latency|slow/i.test(promptText)) {
		return "Watchdog makes latency visible: you can see the model call duration, request status, usage, and proxy lifecycle events without changing the chat app's response contract.";
	}
	return "Watchdog adds an observable control point around the AI SDK call: the chat app keeps its normal OpenAI-compatible flow while Watchdog records requests, usage, cost, errors, and agent-step traces.";
}

const server = http.createServer(async (req, res) => {
	if (req.method === "GET" && req.url === "/healthz") {
		sendJson(res, 200, { ok: true, service: "mock-openai-compatible" });
		return;
	}

	if (req.method !== "POST" || req.url !== "/v1/chat/completions") {
		sendJson(res, 404, { error: { message: "not found", type: "not_found" } });
		return;
	}

	try {
		const raw = await collectBody(req);
		const payload = JSON.parse(raw || "{}");
		const promptText = lastUserMessage(payload.messages);
		const model = String(payload.model || "gpt-4.1-mini");

		if (/force_error|rate limit|429/i.test(promptText)) {
			sendJson(res, 429, {
				error: {
					message: "fixture rate limit: Watchdog should capture this provider failure",
					type: "rate_limit_error",
					code: "fixture_rate_limit"
				}
			});
			return;
		}

		const delayMs = /latency|slow/i.test(promptText) ? 450 : 45;
		const outputText = completionText(promptText);
		setTimeout(() => {
			sendJson(res, 200, {
				id: `chatcmpl_fixture_${Date.now()}`,
				object: "chat.completion",
				created: Math.floor(Date.now() / 1000),
				model,
				choices: [
					{
						index: 0,
						message: {
							role: "assistant",
							content: outputText
						},
						finish_reason: "stop"
					}
				],
				usage: usageFor(promptText, outputText)
			});
		}, delayMs);
	} catch (error) {
		sendJson(res, 400, {
			error: {
				message: error.message || "invalid request",
				type: "invalid_request_error",
				code: "invalid_request"
			}
		});
	}
});

server.listen(listenPort, "127.0.0.1", () => {
	console.log(`mock OpenAI-compatible upstream listening on http://127.0.0.1:${listenPort}`);
});

