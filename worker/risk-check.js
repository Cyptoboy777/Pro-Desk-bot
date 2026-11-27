/**
 * Read-only risk-check edge worker (Cloudflare Workers / any fetch-style runtime).
 *   GET /actions.json                         -> Solana Actions routing file
 *   GET /api/v1/actions/risk-check?mint=<m>   -> informational risk report for a RECORDED mint
 * It reads the published static JSON, runs the open rubric, and returns JSON. There is no POST route, no transaction
 * building, no wallet, no signing: any non-GET request is rejected with 405.
 */
import { createRequire } from 'node:module';
const BASE = 'https://cyptoboy777.github.io/Pro-Desk-bot/';
const MINT = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
const CORS = {
  'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, Content-Encoding, Accept-Encoding',
  'Content-Type': 'application/json; charset=utf-8',
};
const ACTIONS = { rules: [{ pathPattern: '/api/v1/actions/*', apiPath: '/api/v1/actions/*' }] };
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: CORS });

export async function handle(request, { fetchImpl = fetch, base = BASE, assess } = {}) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (request.method !== 'GET') return json({ error: 'method_not_allowed', message: 'read-only: GET only' }, 405);
  const url = new URL(request.url);
  if (url.pathname === '/actions.json') return json(ACTIONS);
  if (url.pathname !== '/api/v1/actions/risk-check') return json({ error: 'not_found' }, 404);
  const mint = url.searchParams.get('mint') || '';
  if (!MINT.test(mint)) return json({ error: 'invalid_mint', message: 'Provide a base58 token mint address (case-sensitive).' }, 400);
  let rows, summary;
  try {
    [rows, summary] = await Promise.all(['api/v1/dataset.json', 'api/v1/summary.json'].map(async p => {
      const r = await fetchImpl(base + p); if (!r.ok) throw new Error(p); return r.json();
    }));
  } catch (e) { return json({ error: 'data_unavailable', message: 'Published telemetry data is not available.' }, 502); }
  const row = (rows.rows || []).find(r => r.mint === mint);
  if (!row) return json({ error: 'not_found', mint, message: 'Mint is not in the recorded dataset; no live claim is made.' }, 404);
  const v = assess(row);
  return json({
    schema: '1.0', mint, risk_score: v.risk_score, passed_rubric: v.passed, failed_reasons: v.failed_reasons,
    components: v.components, bad_24h: row.bad_24h, historical_survival_benchmark: summary.pass_vs_reject_24h,
    benchmark_status: summary.edge_status,
    disclaimer: 'Empirical, sample-limited informational data only; not a safety guarantee or trading recommendation.',
  });
}

// Runtime entry. `assess` comes from the shared rubric (bundle docs/rubric.js alongside this file when deploying).
const require_ = createRequire(import.meta.url);
let rubric = null;
try { rubric = require_('../docs/rubric.js'); } catch (e) { /* bundled deployments inject it via handle(..., {assess}) */ }
export default { fetch: (request) => handle(request, { assess: rubric && rubric.assess }) };
