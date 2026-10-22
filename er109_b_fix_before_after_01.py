# er109_b_fix_before_after_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 C: B不具合3件(B-1複合序数の最終ゲート値DIFF/B-2 1語・短文でratioゲートが同音救済より先行/B-3 `60 %`)の
# 最小修正の前後比較。API 0・ローカル。同一のitem集合を『修正前コード』と『修正後コード』で判定し、PASS->NGが0であること(NG->PASSのみ)を確認する。
# 使い方:
#   修正前: python er109_b_fix_before_after_01.py snapshot --out before.json            (item集合を生成して判定)
#   修正後: python er109_b_fix_before_after_01.py snapshot --items before.json --out after.json   (同じitemを再判定)
#   比較  : python er109_b_fix_before_after_01.py compare before.json after.json --out diff.json
# 判定 = classify_asr_match(+_step_alternate_pass)。非KPは本物のunified judgeと同じ最終ANDゲート(承認済みbasisでない場合、値DIFF/否定差でNG_PROTECTED)も適用。
import argparse
import collections
import glob
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er078_asr_unified_judge_01 as uj
import er109_machine_pairs_eval_01 as mp
import er109_stored_census_01 as census


def judge(c, a, seg, kp):
    cls = val.classify_asr_match(c, a, segment_id=(None if kp else seg))
    alt = None if cls.should_pass else S._step_alternate_pass(cls)
    passed = bool(cls.should_pass or alt)
    label = cls.classification if cls.should_pass else (str(alt) if alt else cls.classification)
    final_ok = passed
    gate = None
    if passed and not kp:
        basis = S._equivalence_basis_of(cls) if cls.should_pass else None
        if basis not in uj.APPROVED_EQUIVALENCE_BASES:
            vgr, neg = uj._protected(c, a, "en")
            if vgr.kind == uj.vg.DIFF or neg:
                final_ok = False
                gate = "value_diff" if vgr.kind == uj.vg.DIFF else "negation_diff"
    return {"label": label, "classify_pass": passed, "final_ok": final_ok, "gate": gate}


def build_items():
    items = []
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    seen = set()
    for f in files:
        for r in census.rows_from_results(f):
            for kind, txt in (("primary", r["asr"]), ("azure", r.get("azure"))):
                if not txt:
                    continue
                k = (r["canonical"], txt, r["seg"], r["kp"])
                if k in seen:
                    continue
                seen.add(k)
                items.append({"set": "stored_" + kind, "c": r["canonical"], "a": txt, "seg": r["seg"], "kp": bool(r["kp"]),
                              "src": r["src"], "attempt": r.get("attempt"), "stored_cls": r.get("stored_cls"), "final_status": r.get("final_status")})
    # 機械生成ペア(正例=発音同一の異表記 / 負例=内容が変わる改変)。seed固定で再現。
    kp = mp.load_kp_phrases()
    body = mp.load_body_sentences(700)
    import pronouncing
    vocab = sorted({w.lower() for p in kp + body for w in __import__("re").findall(r"[A-Za-z]{4,}", p) if pronouncing.phones_for_word(w.lower())})
    for phrases, seg, is_kp, nm in ((kp, "kp1_en", True, "machine_kp"), (body, "full_story_part1", False, "machine_body")):
        for c in phrases:
            for g in mp.POS_GENS:
                r = g(c)
                if r:
                    items.append({"set": nm + "_pos", "c": c, "a": r[0], "seg": seg, "kp": is_kp, "cat": r[1]})
            for g in (mp.neg_number_change, mp.neg_negation_drop, mp.neg_negation_add, mp.neg_content_delete, mp.neg_minimal_pair,
                      lambda t: mp.neg_word_insert(t, vocab), lambda t: mp.neg_word_sub(t, vocab)):
                r = g(c)
                if r:
                    items.append({"set": nm + "_neg", "c": c, "a": r[0], "seg": seg, "kp": is_kp, "cat": r[1]})
    # B不具合の代表fixture(固定)
    fixed = [("the twenty first century", "the 21st century", "full_story_part1", False), ("the sixty eighth day", "the 68th day", "full_story_part1", False),
             ("sixty percent of them", "60 % of them", "full_story_part1", False), ("seize", "sees", "kp3_en", True),
             ("seize", "cease", "kp3_en", True), ("lead", "led", "kp3_en", True), ("desert", "dessert", "kp3_en", True), ("are", "or", "kp3_en", True),
             ("wait", "weight", "kp1_en", True), ("one", "won", "kp1_en", True), ("take part", "take tart", "kp2_en", True)]
    for c, a, seg, kp_ in fixed:
        items.append({"set": "fixture", "c": c, "a": a, "seg": seg, "kp": kp_})
    return items


def snapshot(a):
    if a.items:
        items = json.load(open(a.items, encoding="utf-8"))["items"]
        for it in items:
            it.pop("result", None)
    else:
        items = build_items()
    for it in items:
        it["result"] = judge(it["c"], it["a"], it["seg"], it["kp"])
    json.dump({"generated_by": "er109_b_fix_before_after_01.py", "api_calls": 0, "cost_jpy": 0, "items": items},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = collections.Counter((it["set"], it["result"]["final_ok"]) for it in items)
    print("items", len(items), dict(c))


def compare(a):
    b0 = json.load(open(a.before, encoding="utf-8"))["items"]
    b1 = json.load(open(a.after, encoding="utf-8"))["items"]
    assert len(b0) == len(b1)
    pass_to_ng, ng_to_pass, same = [], [], 0
    by_set = collections.defaultdict(lambda: collections.Counter())
    for x, y in zip(b0, b1):
        assert x["c"] == y["c"] and x["a"] == y["a"]
        ox, oy = x["result"]["final_ok"], y["result"]["final_ok"]
        by_set[x["set"]]["n"] += 1
        if ox and not oy:
            pass_to_ng.append(x | {"after": y["result"]})
            by_set[x["set"]]["PASS_to_NG"] += 1
        elif (not ox) and oy:
            ng_to_pass.append(x | {"after": y["result"]})
            by_set[x["set"]]["NG_to_PASS"] += 1
        else:
            same += 1
        # classify段階の変化も記録
        if x["result"]["classify_pass"] and not y["result"]["classify_pass"]:
            by_set[x["set"]]["classify_PASS_to_NG"] += 1
    out = {"items": len(b0), "unchanged": same, "PASS_to_NG": len(pass_to_ng), "NG_to_PASS": len(ng_to_pass),
           "by_set": {k: dict(v) for k, v in by_set.items()}, "PASS_to_NG_items": pass_to_ng, "NG_to_PASS_items": ng_to_pass}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("items", "unchanged", "PASS_to_NG", "NG_to_PASS", "by_set")}, ensure_ascii=False, indent=1))
    for x in ng_to_pass[:40]:
        print("NG->PASS", x["set"], repr(x["c"][:80]), "|", repr(x["a"][:80]), "|", x["result"]["label"], "->", x["after"]["label"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("snapshot")
    s.add_argument("--out", required=True)
    s.add_argument("--items")
    c = sp.add_parser("compare")
    c.add_argument("before")
    c.add_argument("after")
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    snapshot(a) if a.cmd == "snapshot" else compare(a)
