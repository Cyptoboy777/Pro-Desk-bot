"""The JS and Python SDKs must import cleanly, cache by TTL, reject bad shapes and accept every published fixture."""
import glob
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
API = os.path.join(ROOT, "docs/api/v1")
NODE = pytest.mark.skipif(not shutil.which("node"), reason="node not installed")


def run_node(script):
    r = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout.strip()


def test_every_expected_fixture_is_published():
    names = {os.path.basename(f)[:-5] for f in glob.glob(API + "/*.json")}
    assert {"summary", "features", "recent_scans", "rubric", "dataset", "actions"} <= names


@NODE
def test_js_sdk_is_valid_javascript_not_python_docstring():
    src = open(os.path.join(ROOT, "sdk/js/pro-desk-telemetry.js")).read()
    assert not src.lstrip().startswith('"""')
    run_node("const m=require('./sdk/js/pro-desk-telemetry.js');if(typeof m.TelemetryClient!=='function')process.exit(3)")
    subprocess.run(["node", "--check", "sdk/js/pro-desk-telemetry.js"], cwd=ROOT, check=True)


@NODE
def test_js_sdk_validates_every_published_fixture_with_all_convenience_methods():
    out = run_node(r"""
const fs=require('fs'),path=require('path');
const {TelemetryClient}=require('./sdk/js/pro-desk-telemetry.js');
const dir='docs/api/v1', calls=[];
const fetchImpl=async url=>{calls.push(url);const f=path.join(dir,path.basename(url));
  return fs.existsSync(f)?{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(f,'utf8'))}:{ok:false,status:404,json:async()=>({})};};
(async()=>{
  const c=new TelemetryClient({baseUrl:'https://fixture.invalid/api/v1',fetchImpl});
  const res=await Promise.all([c.getSummary(),c.getFeatures(),c.getRecentScans(),c.getRubric(),c.getDataset(),c.getActions()]);
  if(calls.length!==6)throw new Error('expected 6 fetches, got '+calls.length);
  await c.getSummary(); await c.getFeatures();
  if(calls.length!==6)throw new Error('TTL cache not used');
  if(!['INSUFFICIENT_DATA','NO_EDGE','STATISTICAL_EDGE_DETECTED'].includes(res[0].edge_status))throw new Error('bad edge status');
  if(!res[5].rules.length)throw new Error('actions rules empty');
  const c2=new TelemetryClient({baseUrl:'https://x/',ttlMs:0,fetchImpl});
  await c2.getSummary(); await c2.getSummary();
  if(calls.length!==8)throw new Error('ttl 0 must refetch');
  console.log('ok');
})().catch(e=>{console.error(e);process.exit(1)});
""")
    assert out == "ok"


@NODE
def test_js_sdk_rejects_bad_shapes_http_errors_and_unknown_resources():
    out = run_node(r"""
const {TelemetryClient}=require('./sdk/js/pro-desk-telemetry.js');
const mk=(body,ok=true)=>new TelemetryClient({fetchImpl:async()=>({ok,status:ok?200:500,json:async()=>body})});
const expectFail=async(p)=>{try{await p;}catch(e){return true;}return false;};
(async()=>{
  const r=[await expectFail(mk({features:[]}).getFeatures()),          // no schema
           await expectFail(mk({schema:'1.0',features:'x'}).getFeatures()),
           await expectFail(mk({schema:'1.0'}).getSummary()),
           await expectFail(mk({}, false).getSummary()),
           await expectFail(mk({schema:'1.0'}).get('wallet')),
           await expectFail(mk({rules:'no'}).getActions())];
  const c=mk({schema:'1.0',features:'x'}); await expectFail(c.getFeatures());
  if(c.cache.size!==0)throw new Error('failed result was cached');
  console.log(r.every(Boolean)?'ok':'bad '+r);
})();
""")
    assert out == "ok"


def test_python_sdk_validates_every_published_fixture_and_caches():
    from sdk.python.pro_desk_telemetry import TelemetryClient, validate
    calls = []

    def fetch(url):
        calls.append(url)
        return json.load(open(os.path.join(API, os.path.basename(url))))
    c = TelemetryClient("https://fixture.invalid/api/v1", fetcher=fetch)
    got = [c.get_summary(), c.get_features(), c.get_recent_scans(), c.get_rubric(), c.get_dataset(), c.get_actions()]
    assert len(calls) == 6 and c.get_summary() is got[0] and len(calls) == 6
    assert got[5]["rules"]
    with pytest.raises(ValueError):
        validate("features", {"schema": "1.0", "features": "x"})
    with pytest.raises(ValueError):
        validate("summary", {"schema": "1.0"})
    with pytest.raises(ValueError):
        c.get("wallet")
