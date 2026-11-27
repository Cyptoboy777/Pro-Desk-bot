import json, os, stat, sys
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import update_readme_counts as U


def test_readme_block_tracks_summary_and_keeps_surrounding_text():
    s = json.load(open(os.path.join(ROOT, "docs/api/v1/summary.json")))
    txt = "before\n" + U.START + "\nold\n" + U.END + "\nafter"
    new = U.update(txt, s)
    assert new.startswith("before\n") and new.endswith("\nafter") and f"{s['tokens_recorded']} recorded tokens" in new and "old" not in new
    assert U.update(new, s) == new                      # idempotent


def test_readme_in_repo_matches_summary():
    s = json.load(open(os.path.join(ROOT, "docs/api/v1/summary.json")))
    assert f"{s['tokens_recorded']} recorded tokens, {s['judged_24h']} judged" in open(os.path.join(ROOT, "README.md")).read()


def test_precommit_hook_runs_the_safety_guard_and_is_executable():
    p = os.path.join(ROOT, ".githooks/pre-commit")
    assert "test_safety_policy" in open(p).read() and os.stat(p).st_mode & stat.S_IXUSR
