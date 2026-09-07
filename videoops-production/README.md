# VideoOps Production

Initializes a real, arbitrary video-production workspace and emits the exact harness prompt for the `VideoOps Producer`. It does not inject fixture content, call a model provider, or pretend a render occurred. The selected harness performs the production by reading the portable agent and skill contracts and using its own available tools.

```bash
videoops-production/bin/run \
  --workspace /absolute/path/to/new-video-workspace \
  --request /absolute/path/to/MEGA_PROMPT.md \
  --run-id product-release-001
```

Paste the generated `RUN_VIDEOOPS.md` into a file-capable Codex, Claude Code, Hermes, Paperclip, or other compatible agent runtime. The harness must be able to read `kujo-agents/videoops/`, write the target workspace, and access the media tools needed by the request. It may use native subagents or assume the five specialist identities sequentially.

The command refuses broad workspaces, symlinked or oversized requests, and accidental intake replacement. Use `--overwrite` only when intentionally restarting the intake. Paid generation, authenticated capture, publication, and other external effects remain approval-gated.

The generated harness handoff routes authorized audio acquisition through
`videoops-media-generation --media` and the shared kujo-agents/videoops/tools runtime. Planning,
scouting, editing and perceptual critique remain harness-owned. Runtime review
commands bind decisions to candidate SHA-256 and preserve REVIEW_INCOMPLETE for
human/capable review without an empty edit loop. The initializer does not invent
approval or automatically access accounts. See the media-generation README for
its explicit production bridge and fixture separation.
