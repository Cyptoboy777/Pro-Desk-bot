"""Live READ-ONLY data adapter: DexScreener (market) + RugCheck (safety flags).

NOTE: response field names below come from memory of the public APIs and were NOT
verified from the build environment (network was blocked). Run `python alerts.py --probe`
on your machine first and compare the raw JSON with the parsing here.
Design rule: FAIL CLOSED. Any missing safety field is treated as unsafe.
"""
import json
import time
import urllib.request

from .models import Token

DEX = "https://api.dexscreener.com"
RUG = "https://api.rugcheck.xyz/v1"


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={"accept": "application/json", "user-agent": "desk-app/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def latest_solana_mints(limit=20):
    prof = _get(f"{DEX}/token-profiles/latest/v1")
    return [p["tokenAddress"] for p in prof if p.get("chainId") == "solana"][:limit]


def parse_market(pairs, mint):
    """Pick the deepest-liquidity pair for this mint. Returns dict or None."""
    best = None
    for p in pairs or []:
        if (p.get("baseToken") or {}).get("address") != mint:
            continue
        liq = float((p.get("liquidity") or {}).get("usd") or 0)
        if best is None or liq > best["liquidity_usd"]:
            created = p.get("pairCreatedAt")
            best = {
                "symbol": (p.get("baseToken") or {}).get("symbol", "?"),
                "price": float(p.get("priceUsd") or 0),
                "liquidity_usd": liq,
                "volume_24h": float((p.get("volume") or {}).get("h24") or 0),
                "age_minutes": (time.time() * 1000 - created) / 60000 if created else 0.0,
            }
    return best


def parse_safety(rep):
    """Fail closed: missing => unsafe defaults."""
    rep = rep or {}
    holders = rep.get("topHolders") or []
    top10 = sum(float(h.get("pct", 100)) for h in holders[:10]) if holders else 100.0
    lp = max([float(((m or {}).get("lp") or {}).get("lpLockedPct", 0)) for m in (rep.get("markets") or [])] or [0.0])
    return {
        "mint_authority_disabled": "mintAuthority" in rep and rep["mintAuthority"] is None,
        "freeze_authority_disabled": "freezeAuthority" in rep and rep["freezeAuthority"] is None,
        "top10_holders_pct": top10,
        "lp_burned_pct": lp,
    }


def fetch_token(mint):
    pairs = _get(f"{DEX}/tokens/v1/solana/{mint}")
    m = parse_market(pairs, mint)
    if not m or m["price"] <= 0:
        return None
    try:
        s = parse_safety(_get(f"{RUG}/tokens/{mint}/report"))
    except Exception:
        s = parse_safety(None)  # unreachable safety data => unsafe
    return Token(mint=mint, **m, **s)
