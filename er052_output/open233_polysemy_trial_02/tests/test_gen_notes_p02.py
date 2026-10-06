# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "er052_output" / "open233_polysemy_trial_02" / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT))
import gen_notes_p02 as G
import check_notes_only_diff_p02 as C

RL = ROOT / "er019_output/meta/run_03/research_ledger"


def load():
    return (json.loads((RL / "fact_ledger_draft.json").read_text(encoding="utf-8")),
            json.loads((RL / "fact_ledger_verification.json").read_text(encoding="utf-8")))


def test_validate():
    assert G.validate_note(G.PREFIX + "原語'x'=y。z ではない。") is None
    assert G.validate_note("注意: x") == "bad_prefix"
    assert G.validate_note(G.PREFIX + "あ\nい") == "newline"
    assert G.validate_note(G.PREFIX + "あ" * 80).startswith("too_long")
    assert G.validate_note(G.PREFIX + "あ" * (80 - len(G.PREFIX))) is None


def test_postprocess_one_per_fact():
    n = G.PREFIX + "ok"
    acc, rej = G.postprocess([{"fact_id": "A", "note": n}, {"fact_id": "A", "note": n},
                              {"fact_id": "Z", "note": n}, {"fact_id": "B", "note": "bad"}], {"A", "B"})
    assert list(acc) == ["A"] and len(rej) == 3


def test_concat_only_notes_changes():
    d, _ = load()
    fid = d["facts"][0]["fact_id"]
    nb = G.concat_notes(d, {fid: G.PREFIX + "t"})
    for f0, f1 in zip(d["facts"], nb["facts"]):
        a, b = dict(f0), dict(f1)
        na, nn = a.pop("notes_for_writer"), b.pop("notes_for_writer")
        assert a == b
        if f0["fact_id"] == fid:
            assert nn == ((na + " / " if na else "") + G.PREFIX + "t")
        else:
            assert na == nn


def test_control_matches_original_meta():
    d, v = load()
    txt, _ = G.rebuild_ledger_text(d, v)
    assert txt == (RL / "verified_fact_ledger.txt").read_text(encoding="utf-8")
    other = (ROOT / "er019_output/meta/run_03/ledger/verified_fact_ledger.txt").read_text(encoding="utf-8")
    assert G.sha256(txt) == G.sha256(other)


def test_prompt_contains_rules_verbatim():
    d, v = load()
    p = G.build_prompt(d, v)
    assert G.RULES in p and "source_url" in p


def _write_pair(tmp_path, mutate_claim=False):
    d, v = load()
    c, _ = G.rebuild_ledger_text(d, v)
    nbd = G.concat_notes(d, {d["facts"][0]["fact_id"]: G.PREFIX + "ダミー"})
    if mutate_claim:
        nbd["facts"][1]["claim"] = nbd["facts"][1]["claim"] + "X"
    n, _ = G.rebuild_ledger_text(nbd, v)
    (tmp_path / "c.txt").write_text(c, encoding="utf-8")
    (tmp_path / "n.txt").write_text(n, encoding="utf-8")
    return tmp_path / "c.txt", tmp_path / "n.txt"


def test_check_pass_and_fail(tmp_path):
    c, n = _write_pair(tmp_path)
    r = C.check(c, n)
    assert r["result"] == "PASS" and r["added_count"] == 1, r
    c2, n2 = _write_pair(tmp_path, mutate_claim=True)
    assert C.check(c2, n2)["result"] == "FAIL"


def test_check_fail_on_modified_existing_notes(tmp_path):
    d, v = load()
    c, _ = G.rebuild_ledger_text(d, v)
    d2 = json.loads(json.dumps(d))
    f = next(f for f in d2["facts"] if f.get("notes_for_writer"))
    f["notes_for_writer"] = "改変" + f["notes_for_writer"]
    n, _ = G.rebuild_ledger_text(d2, v)
    (tmp_path / "c.txt").write_text(c, encoding="utf-8")
    (tmp_path / "n.txt").write_text(n, encoding="utf-8")
    assert C.check(tmp_path / "c.txt", tmp_path / "n.txt")["result"] == "FAIL"


def _txt_with_and_without_notes():
    return ("[VERIFIED] A-1: 主張1\n  scope: s\n  notes_for_writer: 既存\n\n"
            "[VERIFIED] A-2: 主張2\n  scope: s2\n\n"
            "[AMBIGUOUS - 断定禁止、曖昧さを保持すること] A-3: 主張3\n  ambiguity_note: x\n")


def test_append_to_txt_pass_and_fail(tmp_path):
    t = _txt_with_and_without_notes()
    n1, n2 = G.PREFIX + "ダミー1", G.PREFIX + "ダミー2"
    nb, done = G.append_notes_to_txt(t, {"A-1": n1, "A-2": n2})
    assert done == ["A-1", "A-2"]
    assert "  notes_for_writer: 既存 / " + n1 in nb
    assert "  scope: s2\n  notes_for_writer: " + n2 + "\n\n" in nb
    (tmp_path / "c.txt").write_text(t, encoding="utf-8")
    (tmp_path / "n.txt").write_text(nb, encoding="utf-8")
    r = C.check(tmp_path / "c.txt", tmp_path / "n.txt")
    assert r["result"] == "PASS" and r["added_count"] == 2, r
    (tmp_path / "bad.txt").write_text(nb.replace("主張3", "主張3改"), encoding="utf-8")
    assert C.check(tmp_path / "c.txt", tmp_path / "bad.txt")["result"] == "FAIL"
    (tmp_path / "bad2.txt").write_text(nb.replace("既存 / ", "改変 / "), encoding="utf-8")
    assert C.check(tmp_path / "c.txt", tmp_path / "bad2.txt")["result"] == "FAIL"


def test_append_no_change_when_no_notes():
    t = _txt_with_and_without_notes()
    nb, done = G.append_notes_to_txt(t, {})
    assert nb == t and done == []


def test_append_crlf_preserved(tmp_path):
    t = _txt_with_and_without_notes().replace("\n", "\r\n")
    n1 = G.PREFIX + "ダミー1"
    nb, _ = G.append_notes_to_txt(t, {"A-1": n1, "A-2": n1})
    assert "既存 / " + n1 + "\r\n" in nb
    assert "  scope: s2\r\n  notes_for_writer: " + n1 + "\r\n" in nb
    (tmp_path / "c.txt").write_bytes(t.encode("utf-8"))
    (tmp_path / "n.txt").write_bytes(nb.encode("utf-8"))
    assert C.check(tmp_path / "c.txt", tmp_path / "n.txt")["result"] == "PASS"


def test_trim_notes_cap_and_severity_order():
    n = G.PREFIX + "ok"
    raw = [{"fact_id": f, "note": n, "severity": sv} for f, sv in (("A", 1), ("B", 3), ("C", 2), ("D", 3), ("E", 2))]
    acc = {r["fact_id"]: n for r in raw}
    kept, trimmed = G.trim_notes(raw, acc, ["A", "B", "C", "D", "E"], 3)
    assert set(kept) == {"B", "D", "C"}
    assert [t["fact_id"] for t in trimmed] == ["E", "A"]
    k2, t2 = G.trim_notes(raw, {"A": n}, ["A"], 3)
    assert k2 == {"A": n} and t2 == []


def test_schema_has_reverse_reading_severity():
    it = G.NOTES_SCHEMA["schema"]["properties"]["notes"]["items"]
    assert "reverse_reading" in it["required"] and "severity" in it["required"]
