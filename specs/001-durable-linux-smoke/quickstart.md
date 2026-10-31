# Feature 001 validation guide

Status: command details arrive with each implementation packet. This guide defines the tests you will run before approving the next packet.

## P2 review

From Windows PowerShell in the repository root, run `python -m pytest -q`. Verify the Linux lifecycle accepts the canonical normal sequence, rejects an out-of-order Linux test, rejects a product mismatch, rejects insufficient memory and missing thermal control, validates the default retry schedule, rejects policies beyond five retries or ten-minute limits, rejects a stale fencing token, and accepts only the reviewed Linux smoke workflow sequence.

## P3 review

Start local PostgreSQL with Docker Desktop. Run migrations against an empty database. Verify duplicate caller/key submission returns one run; a changed payload with the same key conflicts; concurrent platform ownership produces one lease; and stale fencing cannot accept a result.

## P4 review

Set the ignored development-token configuration, start API/Orchestrator/Worker, submit a Linux workflow, poll the run, inspect events and evidence, and cancel an eligible run. Verify a missing or invalid token cannot mutate a run.

## P5 review

Use deterministic simulator fixtures to cause three retryable Linux-readiness failures, a lost acknowledgement, and a Worker stop during work. Confirm the delays, attempts, evidence, and terminal state match the contract and that no stale Worker result is accepted.
