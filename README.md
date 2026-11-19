<p align="center"><img src="assets/logo-lockup.png" alt="Desk Terminal" width="560"></p>

# Desk Terminal (Pro Desk Bot)

A paper-trading desk of six rule-based agents for new Solana tokens: **Scanner**, **Rug Check**, **Sizer**, **Executor**, **Logger**, **Equity**, with a **Head of Desk** that routes data and flags what needs a human. Every decision is written to a log with a reason.

**[Live dashboard →](https://cyptoboy777.github.io/Pro-Desk-bot/)** (static view of real paper-trading runs from the engine)

> **Paper trading only.** There is no wallet code, no private keys and no order placement. Nothing here is financial advice, and results from the built-in simulator are not evidence of real-market profit.

## What is in the box

| Path | What it does |
|---|---|
| `desk/` | Agents, sizer, protections (cooldown, stoploss guard, edge gate), paper broker, simulator |
| `experiments.py` | Tune on 100 seeds, report on 100 unseen seeds, sensitivity by rug rate and edge |
| `run_desk.py` | One simulated night, or `--seeds N` for a distribution |
| `alerts.py` | Live **read-only** alerts from DexScreener + RugCheck (run `--probe` first, see below) |
| `export_runs.py`, `dashboard_template.html` | Builds the static dashboard from real paper runs |
| `assets/` | Logo, favicon, social preview |

## Quick start

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
python3 run_desk.py --seeds 100
python3 experiments.py
python3 export_runs.py && python3 - <<'PY'
t = open('dashboard_template.html').read().replace('__DATA__', open('dashboard_data.json').read())
open('dashboard.html', 'w').write(t)
PY
```

Live alerts (read-only, optional Telegram via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`):

```bash
python3 alerts.py --probe   # verify the API field names against real responses first
python3 alerts.py --once
```

The live adapter's field names were written from memory of the public APIs and have not been verified against real responses. It fails closed: missing safety data means the token is rejected.

## What the experiments found

On unseen seeds the baseline (fixed ticket, no protections) lost about 3.5% a night. Sizing alone made it worse (-5.3%). Stoploss guard, cooldown and an edge gate that shrinks size while recent closed trades are net negative together cut it to -2.4% with a worst night of -9.3%. None of this makes a no-edge market profitable. Stealth rugs look clean and pass every check, so they are bounded by size and exposure instead of detected. Profit appears only when the market has a strong edge. Details are in the dashboard and `experiments.py`.

## Safety rules the code follows

1. An LLM may comment or veto, and can never override a Rug Check rejection.
2. Missing safety data is treated as unsafe.
3. A circuit breaker halts entries at a 5% loss and flags it for a human.
4. Before any real money: weeks of live read-only alerts, then paper results you checked yourself, then a separate wallet with an amount you can afford to lose.
