"""Live READ-ONLY data adapter: DexScreener (market) + RugCheck (safety flags).

Field names were checked against real responses captured from a phone browser on
2026-11-19 (one token each). Re-run `python alerts.py --probe` if parsing looks off.
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
    """Fail closed: missing => unsafe defaults.

    Field names verified on 2026-11-19 against one real RugCheck /report response
    (a pump.fun-style Token-2022 token) and one DexScreener response. One sample is
    not a schema: keep an eye on `risk_flags` and re-probe if results look odd.
    """
    rep = rep or {}
    flags = []
    # liquidity-pool token accounts show up as the biggest "holders"; they are not whales
    pool = set()
    for m in rep.get("markets") or []:
        for k in ("pubkey", "liquidityA", "liquidityB"):
            if (m or {}).get(k):
                pool.add(m[k])
    holders = [h for h in (rep.get("topHolders") or [])
               if h.get("address") not in pool and h.get("owner") not in pool]
    top10 = sum(float(h.get("pct", 100)) for h in holders[:10]) if holders else 100.0
    lp = max([float(((m or {}).get("lp") or {}).get("lpLockedPct", 0)) for m in (rep.get("markets") or [])] or [0.0])
    if any(h.get("insider") for h in holders[:10]):
        flags.append("insider wallets in top 10")
    ext = rep.get("token_extensions") or {}
    if ext.get("permanentDelegate"):
        flags.append("permanent delegate")
    if ext.get("transferHook"):
        flags.append("transfer hook")
    if ext.get("nonTransferable"):
        flags.append("non-transferable")
    if float((rep.get("transferFee") or {}).get("pct") or 0) > 5:
        flags.append("transfer fee above 5%")
    if rep.get("rugged"):
        flags.append("RugCheck says rugged")
    for r in rep.get("risks") or []:
        if (r or {}).get("level") == "danger":      # level names assumed: not seen in the sample
            flags.append("RugCheck danger: " + str((r or {}).get("name", "?")))
    return {
        "mint_authority_disabled": "mintAuthority" in rep and rep["mintAuthority"] is None,
        "freeze_authority_disabled": "freezeAuthority" in rep and rep["freezeAuthority"] is None,
        "top10_holders_pct": top10,
        "lp_burned_pct": lp,
        "risk_flags": flags,
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


def fetch_market(mint):
    """DexScreener only (cheap). Returns the parse_market dict or None."""
    m = parse_market(_get(f"{DEX}/tokens/v1/solana/{mint}"), mint)
    return m if m and m["price"] > 0 else None


def fetch_safety(mint):
    """RugCheck report -> safety fields. Any failure => fail-closed defaults."""
    try:
        return parse_safety(_get(f"{RUG}/tokens/{mint}/report"))
    except Exception:
        return parse_safety(None)
