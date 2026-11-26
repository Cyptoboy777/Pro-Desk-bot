"""The browser rubric (docs/rubric.js) must give the same answers as desk/risk_engine.py."""
import sys, os, json, random, shutil, subprocess, pytest
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
from desk.risk_engine import assess, DEFAULT


def cases(n=300):
    rnd, out = random.Random(7), []
    for _ in range(n):
        r = {"liq": rnd.choice([500, 9_000, 12_000, 40_000, 300_000]), "vol24": rnd.choice([0, 5_000, 90_000, 9_000_000]),
             "age_min": rnd.choice([None, 5, 31, 59, 100, 239, 500, 3000]), "top10": rnd.choice([None, 3, 15, 24.9, 30, 41]),
             "lp": rnd.choice([None, 50, 100]), "flags": rnd.choice([[], [], ["RugCheck danger: X"]]),
             "auth_ok": rnd.choice([None, True, True, False]), "reasons": rnd.choice([[], ["mint authority enabled"]]),
             "mcap": rnd.choice([None, 100_000, 2_000_000, 50_000_000]), "top1": rnd.choice([None, 2, 10, 33.3]),
             "insiders": rnd.choice([None, 0, 4]), "buy_ratio_h1": rnd.choice([None, 0.1, 0.4, 0.7]),
             "total_holders": None, "creator_pct": None, "chg_h1": None}
        out.append(r)
    return out


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_matches_python():
    cs = cases()
    js = ("const R=require('./docs/rubric.js');const c=JSON.parse(require('fs').readFileSync(0,'utf8'));"
          "console.log(JSON.stringify(c.map(r=>{const a=R.assess(r);return {risk_score:a.risk_score,passed:a.passed,components:a.components,failed_reasons:a.failed_reasons,unknown:a.feature_vector.unknown}})))")
    got = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(cs), capture_output=True, text=True, cwd=ROOT, check=True).stdout)
    for r, g in zip(cs, got):
        p = assess(r)
        assert (g["risk_score"], g["passed"], g["components"]) == (p["risk_score"], p["passed"], p["components"]), r
        assert g["unknown"] == p["feature_vector"]["unknown"], r
        assert g["failed_reasons"] == p["failed_reasons"], (r, g["failed_reasons"], p["failed_reasons"])


def test_default_config_in_js_matches_python():
    if not shutil.which("node"):
        pytest.skip("node")
    out = subprocess.run(["node", "-e", "console.log(JSON.stringify(require('./docs/rubric.js').DEFAULT))"], capture_output=True, text=True, cwd=ROOT, check=True).stdout
    assert json.loads(out) == DEFAULT.to_dict()
