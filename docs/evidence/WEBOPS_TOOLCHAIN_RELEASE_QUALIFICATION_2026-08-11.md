# WebOps toolchain first-release qualification

Date: 2026-08-11. Status: PASS for SiteProbe, SearchBridge, and ContentGraph
`0.1.0` within their documented local/optional-provider contracts.

## Baseline and dogfood

The immutable campaign baseline is
`docs/evidence/siteprobe-live-final-2026-08-11`: 60 pages, 1,177 links, zero
redirects, and zero findings. A fresh bounded live SiteProbe crawl of
`https://agents.kujolang.ai/` reproduced all four counts and its baseline
comparison contained zero changes. ContentGraph rebuilt the same 60 nodes,
1,558 edges, eight clusters, zero orphans, 742 link opportunities, and one
overlap candidate; comparison to
`docs/evidence/contentgraph-local-final-2026-08-11` contained zero changes.

SearchBridge dogfood ran `doctor` and `capabilities` without credentials, then
normalized a deterministic offline PageSpeed fixture scoped to the public
origin. PageSpeed's unauthenticated capability was available; analytics,
backlink, CrUX, submission, keyword, search-performance, and URL-inspection
capabilities degraded independently because credentials were unavailable.
No live provider data or submission was attempted.

## Qualification surface

Deterministic tests cover URL/path/config fuzzing, redirects, robots/canonical
conflicts, duplicate content, malformed HTML/JSON/JSON-LD, cyclic links,
timeouts, bounded retries, 429/5xx responses, capability partial failure,
cache invalidation, offline behavior, deterministic reruns, and explicit
page/node/row/byte/token budgets. Read-only source/fixture hashes are checked,
SiteProbe fixture servers admit GET only, and ContentGraph has no network
surface. SearchBridge `submit` requires `--capability index.submission --act
--yes` plus provider credentials for live execution.

Development-host scale receipts: SiteProbe crawled 1,000 pages in 2.992 seconds
and wrote 1,554,928 bytes; SearchBridge normalized 100 deterministic fixture
runs in 13.876 seconds and wrote 76,200 bytes; ContentGraph built 1,000 nodes
in 0.984 seconds and wrote 1,087,979 bytes. These are regression baselines, not
portable performance guarantees.

## Current primary guidance

- Google Search Central crawling/indexing overview, robots handling,
  canonicalization, and structured-data guidance, retrieved 2026-08-11:
  `https://developers.google.com/search/docs/crawling-indexing`,
  `https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec`,
  `https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls`,
  `https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data`.
- IndexNow submission and ownership protocol, retrieved 2026-08-11:
  `https://www.indexnow.org/documentation`. A 200/202 receipt means received or
  accepted, not indexed.
- Bing Webmaster API and authenticated SubmitUrl guidance, retrieved
  2026-08-11: `https://learn.microsoft.com/en-us/bingwebmaster/` and
  `https://learn.microsoft.com/en-us/bingwebmaster/oauth2`.
- Schema.org documentation, retrieved 2026-08-11:
  `https://schema.org/docs/documents.html`.

Google/Bing/Search Console analytics, index coverage, rankings, traffic,
citations, field CWV, and provider quotas are NOT AVAILABLE — DATA ACCESS
REQUIRED. No outcome claim is made from technical qualification alone.

The Kujo Workflows repository's portable tests plus Tribunal and Relay gates
passed. Its host-dependent Workcell gate could not connect to
`unix:///var/run/docker.sock` because Docker/Colima was not running; the local
`.runs/workcell-execution-gate/run-result.json` preserves the blocker receipt.
This does not invalidate the three independently passing tool release gates,
but it blocks a new Kujo Workflows release tag in this session.
