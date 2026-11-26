"""Ensure the JS SDK validates fixture schemas and uses TTL caching."""
import json
import os
import shutil
import subprocess
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))

@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_client_fixture_and_cache():
    script = r"""
const {TelemetryClient}=require('./sdk/js/pro-desk-telemetry.js');
let calls=0; const c=new TelemetryClient({baseUrl:'https://fixture.invalid',fetchImpl:async()=>({ok:true,json:async()=>{calls++;return {schema:'1.0',features:[]}}})});
Promise.all([c.features(),c.features()]).then(x=>{if(calls!==1||x[0].schema!=='1.0')process.exit(2)});
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
