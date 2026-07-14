# Relay lifecycle handoff

This workflow exercises Relay's durable pause/resume path, exports the
verified run, and maps its identifiers into the versioned Relay message and
delivery receipt contracts. It records local persistence and operator-resume
semantics; it does not claim remote exactly-once delivery.

Run: `KUJO_BIN=/path/to/kujo relay-lifecycle-handoff/scripts/run.sh`
