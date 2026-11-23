import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import notify


def write(p, evs):
    open(p, "w").write("\n".join(json.dumps(e) for e in evs) + "\n")


EV = [{"kind": "ENTER", "sym": "AAA", "size_pct": 2.5, "reason": "vol 3x", "ts": "t1"},
      {"kind": "FILTERED", "sym": "BBB", "reason": "x", "ts": "t2"},
      {"kind": "EXIT", "sym": "AAA", "pnl": -5.3, "reason": "stop-loss", "ts": "t3"}]


def test_first_run_skips_history_then_sends_only_new(tmp_path):
    e, m, sent = str(tmp_path / "e.jsonl"), str(tmp_path / "n.txt"), []
    snd = lambda tok, chat, text: sent.append(text)
    write(e, EV)
    assert notify.run(e, m, "T", "C", snd) == 0 and open(m).read() == "3"        # history skipped
    write(e, EV + [{"kind": "HALT", "sym": "-", "reason": "loss limit", "ts": "t4"}])
    assert notify.run(e, m, "T", "C", snd) == 1
    assert "HALT" in sent[0] and "Paper trading only" in sent[0]
    assert notify.run(e, m, "T", "C", snd) == 0                                    # nothing twice


def test_only_decisions_are_sent_and_formatting(tmp_path):
    e, m, sent = str(tmp_path / "e.jsonl"), str(tmp_path / "n.txt"), []
    open(m, "w").write("0")
    write(e, EV)
    assert notify.run(e, m, "T", "C", lambda a, b, t: sent.append(t)) == 2        # FILTERED not pushed
    assert "BUY (paper) AAA" in sent[0] and "-5.30 USD" in sent[0]


def test_without_secrets_nothing_is_sent_but_marker_advances(tmp_path):
    e, m = str(tmp_path / "e.jsonl"), str(tmp_path / "n.txt")
    open(m, "w").write("0")
    write(e, EV)
    def boom(*a): raise AssertionError("must not send")
    assert notify.run(e, m, None, None, boom) == 0 and open(m).read() == "3"
