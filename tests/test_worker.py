import json, os, shutil, subprocess, pytest
ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_worker_is_read_only_validates_mints_and_matches_python_engine():
    ds = json.load(open(os.path.join(ROOT, "docs/api/v1/dataset.json")))
    mint = next(r["mint"] for r in ds["rows"])
    script = f"""
import {{ handle }} from './worker/risk-check.js';
import {{ createRequire }} from 'node:module';
import fs from 'node:fs';
const assess = createRequire(import.meta.url)('./docs/rubric.js').assess;
const fetchImpl = async u => ({{ ok: true, json: async () => JSON.parse(fs.readFileSync('docs/api/v1/' + u.split('/').pop(), 'utf8')) }});
const call = async (path, method='GET') => {{ const r = await handle(new Request('https://w.test'+path, {{method}}), {{fetchImpl, assess}}); return [r.status, await r.json(), r.headers.get('access-control-allow-origin')]; }};
const out = {{
  ok: await call('/api/v1/actions/risk-check?mint={mint}'), bad: await call('/api/v1/actions/risk-check?mint=nope'),
  missing: await call('/api/v1/actions/risk-check?mint=11111111111111111111111111111111'),
  post: await call('/api/v1/actions/risk-check?mint={mint}', 'POST'), actions: await call('/actions.json'), nf: await call('/swap'),
}};
console.log(JSON.stringify(out));
"""
    r = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["ok"][0] == 200 and o["ok"][2] == "*" and o["bad"][0] == 400 and o["missing"][0] == 404
    assert o["post"][0] == 405 and o["nf"][0] == 404 and o["actions"][1]["rules"][0]["pathPattern"] == "/api/v1/actions/*"
    import sys; sys.path.insert(0, ROOT)
    from desk.risk_engine import assess
    row = next(x for x in ds["rows"] if x["mint"] == mint)
    assert o["ok"][1]["risk_score"] == assess(row)["risk_score"]
