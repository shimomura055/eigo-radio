# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A: オフライン監査(API 0円、既存記録のみ)。
目的: 現行『KPにスロット語が無いのにglossに「～」が残ればFAIL』(OF-230)の誤NG候補と、
canonicalization伸長による意味欠落候補の規模を、既存記録(census/A'再判定/replay)から推定する。
生成物のコード/Prompt/Gateは一切変更しない(import して読むだけ)。
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_gloss_alignment_correction_01_offline_audit.py --census ... --aprime ... --replay ... --out ...
"""
import argparse
import difflib
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_gloss_alignment as ga
import er003_key_words_canonicalization as kc

PREP_TAILS = {"to", "on", "of", "for", "in", "at", "with", "from", "by", "into", "onto", "about", "over", "up",
              "out", "off", "down", "as", "against", "toward", "towards", "through", "past", "around", "after"}

# 人手確認ラベル(Sonnet目視、ユーザー未確認)。census 29件(tilde_gloss_without_kp_slot_items)を読んで付与。
# key=(kp, gloss) -> (label, 理由)。LEGIT_DICTIONARY_TILDE=承認済み規則上は辞書的に自然 / STALE_OMISSION=KP伸長に対しglossが欠落
MANUAL_LABELS = {
    ("urge to watch", "～したい衝動"): ("STALE_OMISSION", "KPはurge to watch。watchに当たる語がglossに無い(『～したい』のスロットのまま)"),
    ("moderate-to-vigorous activity", "中～高強度の運動"): ("LEGIT_DICTIONARY_TILDE", "範囲表記の『中～高』。スロットではなく範囲(別問題: TTSは『なになに』に変換する既存仕様)"),
    ("put solo travel at", "ソロ旅行を～％とする"): ("LEGIT_DICTIONARY_TILDE", "数値スロット。KP末尾atが取る補語を～で表す辞書表記"),
    ("turn out not to be", "結局〜ではないと分かる"): ("LEGIT_DICTIONARY_TILDE", "KP末尾beが取る補語を〜で表す辞書表記"),
    ("turn out", "結局～だと分かる"): ("LEGIT_DICTIONARY_TILDE", "turn outが取る補語を～で表す辞書表記"),
    ("not fully match", "～と完全には一致しない"): ("LEGIT_DICTIONARY_TILDE", "matchの目的語を～で表す辞書表記"),
    ("put good odds on", "～の可能性が高いと見る"): ("LEGIT_DICTIONARY_TILDE", "onの目的語を～で表す辞書表記"),
}

# 委任_01 VALIDATION_01 3節の目視ラベル(Sonnet、ユーザー未確認)
BEFORE = {
    ("locked into a narrow view", "狭い見方に閉じ込められる"): "CONSISTENT",
    ("based on interviews", "～をもとにした"): "INCONSISTENT_OMISSION",
    ("based on interviews", "〜をもとにして"): "INCONSISTENT_OMISSION",
    ("based on interviews", "インタビューをもとにした"): "CONSISTENT",
    ("raw-bean prices", "焙煎前のコーヒー豆"): "INCONSISTENT_OMISSION",
    ("bring in a human helper", "人を呼んで加える"): "INCONSISTENT_AMBIGUOUS",
    ("close around me", "周りから迫ってくる"): "INCONSISTENT_WEAK_OMISSION",
    ("urge to watch", "～したい衝動"): "INCONSISTENT_OMISSION",
}


def added_content_words(display, kp):
    """kp_adds_words_beyond_displayと同じ判定で、追加語そのものを返す(参考。本番関数は変更しない)。"""
    d = kc._normalize_for_match(display or "").replace("’", "'")
    k = kc._normalize_for_match(kp or "").replace("’", "'")
    if not k or d == k:
        return []
    arts = {"a", "an", "the"}
    dset = {ga._stem(t) for t in ga._TOKEN_RE.findall(d)}
    ks = [t for t in ga._TOKEN_RE.findall(k) if t not in arts]

    def near(t):
        return any(difflib.SequenceMatcher(None, ga._stem(t), x).ratio() >= 0.7 for x in dset)

    return [t for t in ks if t not in ga._GENERIC_TOKENS and ga._stem(t) not in dset and not near(t)]


def classify_tilde(kp, gloss):
    lab = MANUAL_LABELS.get((kp, gloss))
    toks = ga._TOKEN_RE.findall(kc._normalize_for_match(kp or ""))
    heur = "LEGIT_DICTIONARY_TILDE" if (toks and toks[-1] in PREP_TAILS) else "UNDETERMINED"
    return {"heuristic": heur, "manual": lab[0] if lab else None, "manual_reason": lab[1] if lab else None}


def main():
    ap = argparse.ArgumentParser()
    for a in ("census", "aprime", "replay", "out"):
        ap.add_argument("--" + a, required=True)
    a = ap.parse_args()
    census = json.load(open(a.census, encoding="utf-8"))
    aprime = json.load(open(a.aprime, encoding="utf-8"))
    replay = json.load(open(a.replay, encoding="utf-8"))
    out = {"inputs": {"census": a.census, "aprime": a.aprime, "replay": a.replay}, "api_calls": 0, "cost_jpy": 0}

    # (a1) replay結果へ現行ルール適用。分母=27 row(実対象16 + 対照10 + スロット罠1)
    rows = replay["rows"]
    a1 = {"denominator_rows": len(rows), "by_tag": {}, "current_rule_fail_rows": []}
    for r in rows:
        a1["by_tag"][r["tag"]] = a1["by_tag"].get(r["tag"], 0) + 1
        if ga.gloss_has_unjustified_slot(r["kp"], r["gloss_after"]):
            a1["current_rule_fail_rows"].append({"kp": r["kp"], "gloss_after": r["gloss_after"]})
    a1["current_rule_fail_count"] = len(a1["current_rule_fail_rows"])
    out["a1_replay_current_rule"] = a1

    # (a2) census: KPにスロット語が無いのにglossに『～』がある item(全er*_output、分母1,129)
    allc = census["all_er_output"]
    tl = allc["tilde_gloss_without_kp_slot_items"]
    a2 = {"denominator_items": allc["items"], "tilde_without_slot_items": len(tl), "rows": []}
    ch, cm = {}, {}
    for x in tl:
        c = classify_tilde(x["kp"], x["gloss"])
        is_target = x["display"] != x["kp"]
        a2["rows"].append({"kp": x["kp"], "display": x["display"], "gloss": x["gloss"], "kp_differs_from_display": is_target, **c})
        ch[c["heuristic"]] = ch.get(c["heuristic"], 0) + 1
        if c["manual"]:
            k = c["manual"] + "(manual)"
        elif (not is_target) and c["heuristic"] == "LEGIT_DICTIONARY_TILDE":
            k = "LEGIT_DICTIONARY_TILDE(inferred: KP==displayで前置詞/不変化詞終わり)"
        else:
            k = "UNLABELED"
        cm[k] = cm.get(k, 0) + 1
    a2["counts_heuristic"] = ch
    a2["counts_manual_or_inferred"] = cm
    a2["note"] = ("29件の大半はKP==display(=再整合の対象外)。現行『～』機械FAILは対象item(KPが伸びたもの)のLLM出力にのみ適用されるため、"
                  "ここは『もし対象に入ったら機械的にFAILになるが承認済み規則上は正当』な規模の目安(誤NG候補の母集団)であり、実測誤NGではない。")
    out["a2_census_tilde_items"] = a2

    # (a3) 誤NG候補母集団
    legit = sum(1 for r in a2["rows"] if r["manual"] == "LEGIT_DICTIONARY_TILDE"
                or (r["manual"] is None and r["heuristic"] == "LEGIT_DICTIONARY_TILDE" and not r["kp_differs_from_display"]))
    stale = sum(1 for r in a2["rows"] if r["manual"] == "STALE_OMISSION")
    out["a3_false_ng_candidate_population"] = {
        "tilde_without_slot_items": len(tl), "legit_under_approved_rule_estimated": legit, "stale_omission": stale,
        "other_unlabeled": len(tl) - legit - stale,
        "basis": "手動ラベル7件(Sonnet目視)+KP==displayで前置詞/不変化詞終わりの機械推定。ユーザー未確認。"}

    # (b) 意味欠落候補
    b = {"denominator": {"aprime_replayed_attempts": aprime["valid_replayed_attempts"], "aprime_items": aprime["items_total"],
                         "aprime_target_rows": aprime["target_rows"], "aprime_unique_targets": len(aprime["unique_targets"]),
                         "census_items": allc["items"], "census_target_items": allc["targets"],
                         "census_unique_target_triples": len(allc["unique_target_triples"])}, "rows": []}
    seen = set()
    cands = list(aprime["unique_targets"]) + [{"display": t["display"], "kp": t["kp"], "gloss": t["gloss"]}
                                              for t in allc["unique_target_triples"]]
    for u in cands:
        key = (u.get("display"), u.get("kp"), u.get("gloss"))
        if key in seen or not key[2]:
            continue
        seen.add(key)
        disp, kp, gl = key
        add = added_content_words(disp, kp)
        b["rows"].append({"display": disp, "kp": kp, "gloss": gl, "added_content_words": add,
                          "before_label_manual": BEFORE.get((kp, gl), "UNLABELED"),
                          "gloss_has_tilde": bool(ga._TILDE_RE.search(gl)),
                          "current_rule_would_fail_this_old_gloss": ga.gloss_has_unjustified_slot(kp, gl)})
    lc = {}
    for r in b["rows"]:
        lc[r["before_label_manual"]] = lc.get(r["before_label_manual"], 0) + 1
    b["unique_targets_listed"] = len(b["rows"])
    b["before_label_counts"] = lc
    b["omission_candidates_by_added_words"] = sum(1 for r in b["rows"] if r["added_content_words"])
    inc = [r for r in b["rows"] if r["before_label_manual"].startswith("INCONSISTENT")]
    b["inconsistent_total_manual"] = len(inc)
    b["inconsistent_caught_by_current_tilde_rule"] = sum(1 for r in inc if r["current_rule_would_fail_this_old_gloss"])
    b["inconsistent_missed_by_current_tilde_rule"] = len(inc) - b["inconsistent_caught_by_current_tilde_rule"]
    out["b_meaning_omission_candidates"] = b

    out["c_limits"] = [
        "census: 全er*_output keywords_canonicalized.json 226 record/1,129 item(再集計せずcensus_01.jsonを入力)。",
        "A'窓再判定: 153 attempt/765 item、対象11 row/ユニーク6。replay: 実対象8ユニークx2 rep=16 eval+対照10+スロット罠1。",
        "ユニーク対象が少ない(6〜8)。比率は参考値。ゼロ件は『発生しなかった』であって『起きない』の証明ではない(rule of three)。",
        "Beforeラベル・tildeラベルはSonnet目視(ユーザー未確認)。機械判定(heuristic)とは件数を分けて記載。",
        "現行ルールの誤NG(承認規則上正当な『～』を持つ出力のFAIL)は、再整合の実出力では0/16。母集団推定(a3)は『対象に入ったら』の仮想値。",
    ]
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("a1:", a1["denominator_rows"], a1["by_tag"], "current_rule_fail_count", a1["current_rule_fail_count"])
    print("a2 heuristic:", ch, "| manual/inferred:", cm)
    print("a3:", out["a3_false_ng_candidate_population"])
    print("b:", {k: v for k, v in b.items() if k != "rows"})
    for r in b["rows"]:
        print(r["kp"], "|", r["gloss"], "|", r["added_content_words"], "|", r["before_label_manual"], "|", r["current_rule_would_fail_this_old_gloss"])


if __name__ == "__main__":
    main()
