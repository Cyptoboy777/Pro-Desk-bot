# Risk-check edge worker (read-only)

`risk-check.js` serves `/actions.json` and `GET /api/v1/actions/risk-check?mint=…`. It reads the public telemetry JSON, runs the open rubric and returns an informational report. No POST, no transaction, no wallet, no signing; the zero-execution CI guard scans this folder.

Deploy (not done yet: needs your own Cloudflare account): `npm create cloudflare` or `wrangler deploy`, bundling `docs/rubric.js` with the worker. Until then the same logic runs locally with `python sdk/action_server.py`.
