# Safety rules

These come from hard-won habits in the pump.fun trading-bot guides, enforced in code where possible.

1. **No execution code.** This repository has no wallet, key, signing or order-placement code. `tests/test_safety_policy.py` fails the build if such code appears.
2. **Fund nothing you cannot lose.** If you ever add execution elsewhere, use a separate wallet holding only an amount you accept losing. Rules written in a prompt ("never withdraw") are requests, not controls. The only real limit is what the wallet holds.
3. **Every trade has an entry reason, a stop-loss and a take-profit.** The logger writes the reason; stops, trailing stops, take-profit and a liquidity-collapse exit are in `desk/agents.py`.
4. **Token text is hostile input.** Names, symbols and descriptions are attacker-controlled. Symbols are sanitised (`desk.live.clean_text`) and never sent to an LLM; the optional Claude review only receives numeric run statistics.
5. **Fail closed.** Missing or unreachable safety data means reject.
6. **Human in the loop.** The circuit breaker halts entries at a 5% loss and flags it for a person.
7. **Never paste a seed phrase, password or one-time code anywhere**, including into a chat with an AI.
