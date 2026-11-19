"""Simulated market so the whole desk can be tested offline.

Token kinds:
  good     - random walk with mild upward drift, clean flags
  meh      - random walk, no drift, clean flags
  flagged  - rug-in-waiting with VISIBLE red flags (mint enabled / LP not burned)
  stealth  - rug-in-waiting that LOOKS clean; liquidity collapses at a random tick
Rugs collapse price AND liquidity in one tick, so an exit can only fill after the
damage. That is deliberate: it is what happens on-chain.
"""
import random
from .models import Token


class SimMarket:
    def __init__(self, seed=1, n_tokens=60, steps=120, stealth=0.30, drift=0.004):
        self.rng = random.Random(seed)
        self.drift = drift
        rest = 1.0 - stealth   # good .15 / meh .30 / flagged .25 keep their relative shares
        c_good, c_meh, c_flag = 0.15 / 0.70 * rest, 0.45 / 0.70 * rest, rest   # cumulative cut-offs
        self.steps = steps
        self.t = 0
        self.tokens = {}
        self.kind = {}
        self.rug_at = {}
        for i in range(n_tokens):
            r = self.rng.random()
            kind = "good" if r < c_good else "meh" if r < c_meh else "flagged" if r < c_flag else "stealth"
            mint = f"SIM{i:03d}"
            clean = kind in ("good", "meh", "stealth")
            self.kind[mint] = kind
            if kind in ("flagged", "stealth"):
                self.rug_at[mint] = self.rng.randint(15, steps - 5)
            self.tokens[mint] = Token(
                mint=mint, symbol=f"T{i:03d}",
                price=self.rng.uniform(0.0001, 0.01),
                liquidity_usd=self.rng.uniform(15_000, 150_000),
                volume_24h=self.rng.uniform(10_000, 400_000),
                age_minutes=self.rng.uniform(1, 600),
                top10_holders_pct=self.rng.uniform(15, 35) if clean else self.rng.uniform(30, 70),
                mint_authority_disabled=clean or self.rng.random() < 0.2,
                freeze_authority_disabled=True if clean else self.rng.random() < 0.5,
                lp_burned_pct=self.rng.uniform(92, 100) if clean else self.rng.uniform(0, 80),
            )

    def tick(self):
        """Advance one step; return snapshot of all live tokens."""
        self.t += 1
        out = []
        for mint, tok in self.tokens.items():
            if tok.price <= 0:
                continue
            k = self.kind[mint]
            if mint in self.rug_at and self.t >= self.rug_at[mint]:
                tok.price *= 0.05
                tok.liquidity_usd *= 0.05
                self.rug_at.pop(mint)
                self.kind[mint] = "rugged"
            elif k in ("good", "meh", "flagged", "stealth"):
                drift = self.drift if k == "good" else 0.0
                tok.price *= max(0.5, 1 + drift + self.rng.gauss(0, 0.05))
                tok.volume_24h *= max(0.5, 1 + self.rng.gauss(0, 0.05))
            tok.age_minutes += 1
            out.append(Token(**tok.__dict__))
        return out

    def done(self):
        return self.t >= self.steps
