# -*- coding: utf-8 -*-
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: Offline再現(API 0・socket guard・Reading Resolver無効・決定的)。
# 目的(TEST_PLAN T-P2/T-P3/T-R1/T-R3/T-R4, Opus R-4/R-5):
#   (1) parity: Production(X scope)の判定が、凍結proto `proto_unified_03.judge(Flags(l1,l2,l3=False,r1=False))` と全行一致するか(2103行)
#   (2) 負例の増分誤PASSを**行の同一性集合**で既知8行(EVAL_UNIFIED_03 §4a: T1 6 + T2 2)と比較(R-5)。回帰(L0 PASS -> NG)も数える
#   (3) 正例(POS)側のPASS系件数、(4) R-4: Secondary側v2の救済行のうち cls_s にE3/E4がある件数
# 使い方: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/tools/offline_recheck_01.py <out.json>
import collections, json, os, socket, sys, tempfile, wave

sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02")
import eval_common_02 as E                  # Reading Resolver無効(LLM 0)・socket guard
import proto_unified_03 as U                # 凍結proto(oracle)
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er109_xz_scope_01 as xz

KNOWN8 = {   # (group, scenario, primary, secondary) = EVAL_UNIFIED_03 §4a の既知8行(T1同音異表記6 + T2 β最悪露出2)
    ("N1_150", "S_canon", "月の詩は8000900本超", "月のしわ、8,900本超"),
    ("R4R3_extra18", "P_only", "月の詩は、8900本超！その奥に潜む「岩の上着」の秘密", None),
    ("R4R3_extra18", "PS_same", "月の詩は、8900本超！その奥に潜む「岩の上着」の秘密", "月の詩は、8900本超！その奥に潜む「岩の上着」の秘密"),
    ("R4R3_extra18", "P_only", "月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密", None),
    ("R4R3_extra18", "PS_same", "月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密", "月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密"),
    ("R4R3_extra18", "S_canon", "月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密", "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"),
    ("UC6_U6_同音異表記便乗", "P_only", "月の死は、8,900本超！その奥に潜む「岩の上着」の秘密", None),
    ("UC6_U6_同音異表記便乗", "PS_same", "月の死は、8,900本超！その奥に潜む「岩の上着」の秘密", "月の死は、8,900本超！その奥に潜む「岩の上着」の秘密"),
}
PASSING = uj.PASSING_STATES


def wav():
    p = os.path.join(tempfile.gettempdir(), "ja_v2beta_recheck_dummy.wav")
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\x00\x00" * 16000 * 3); w.close()
    return p


def prod(canon, prim, sc, w, scope):
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = (lambda p, language="ja-JP", timeout_seconds=90, _s=sc: (_s, None)) if sc is not None else \
        (lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary"))
    try:
        if scope:
            with xz.run_scope(scope):
                r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, w, cascade_enabled=True, attempt_ctx={"max_len": 400})
        else:
            r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, w, cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig
    j = r["asr_judgement"]
    st = j.get("state")
    c = "NG" if st not in PASSING else ("PASS" if st == uj.PASS else ("PASS_W_NEW" if j.get("rescue_basis") else "PASS_W_PROD"))
    return {"cat": c, "state": st, "reason": j.get("reason_code"), "basis": j.get("rescue_basis"), "warnings": list(j.get("warnings") or []),
            "layers": (j.get("ja_v2beta") or {}).get("layers"), "j": j}


def main(out):
    rows = json.load(open("docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_03.out.json", encoding="utf-8"))["rows"]
    w = wav()
    E.api0_guard_on()
    flags = U.Flags(True, True, False, r1=False)     # Production構成(R-1 OFF, L3なし)
    par_mis, par_n = [], 0
    neg_inc, neg_reg, neg_total = [], [], collections.Counter()
    pos = collections.Counter()
    r4 = []
    by_cat = collections.Counter()
    errors = collections.Counter()
    for i, r in enumerate(rows):
        canon, prim, sc = r["canon"], r["primary"], r["secondary"]
        if not (canon and prim):
            continue
        base = prod(canon, prim, sc, w, None)
        now = prod(canon, prim, sc, w, "X")
        if (now["j"].get("ja_v2beta") or {}).get("error"):
            errors[str((now["j"].get("ja_v2beta") or {}).get("error"))[:120]] += 1
        pr = U.judge(canon, prim, sc, w, flags)
        par_n += 1
        # proto: cat/reason。Productionと完全一致を要求(reason: proto='composite'はProductionの 'ja_beta_composite' へ対応づけ)
        p_cat, p_reason = pr["cat"], pr["reason"]
        n_reason = now["reason"]
        reason_ok = (p_reason == n_reason) or (p_reason == "composite" and n_reason == "ja_beta_composite")
        if now["cat"] != p_cat or not reason_ok:
            par_mis.append({"i": i, "group": r["group"], "scenario": r["scenario"], "canon": canon, "primary": prim, "secondary": sc,
                            "proto": [p_cat, p_reason], "prod": [now["cat"], n_reason], "base": [base["cat"], base["reason"]]})
        by_cat[(r["truth"], now["cat"])] += 1
        if r["truth"] == "NEG":
            neg_total[now["cat"]] += 1
            if base["cat"] == "NG" and now["cat"] != "NG":
                neg_inc.append({"group": r["group"], "scenario": r["scenario"], "primary": prim, "secondary": sc, "canon": canon, "cat": now["cat"], "basis": now["basis"],
                                "reason": n_reason, "key": [r["group"], r["scenario"], prim, sc], "warnings": now["warnings"]})
            if base["cat"] != "NG" and now["cat"] == "NG":
                neg_reg.append({"group": r["group"], "scenario": r["scenario"], "primary": prim, "secondary": sc})
        if r["truth"] == "POS":
            pos[(base["cat"] != "NG", now["cat"] != "NG")] += 1
        # R-4: Secondary側v2の救済行で cls_s にE3/E4があるか
        for L in (now["layers"] or []):
            if L.get("side") == "secondary" and L.get("effective") and sc:
                cs = javal.classify_ja_asr_match(canon, sc, expected_readings=None, allow_reading_resolver=False)
                cs = sec._apply_variant_layer_voicing_upgrade(canon, sc, cs)
                if getattr(cs.protected, "candidate_e_rejections", None) or getattr(cs.protected, "candidate_e_cascade_diffs", None):
                    r4.append({"group": r["group"], "canon": canon, "primary": prim, "secondary": sc})
    E.api0_guard_off()
    inc_keys = {tuple(x["key"]) for x in neg_inc}
    known = set(KNOWN8)
    res = {
        "rows_compared": par_n, "parity_mismatch_count": len(par_mis), "parity_mismatches": par_mis[:40],
        "neg_total_cats": dict(neg_total), "neg_increment_count": len(neg_inc), "neg_increment_rows": neg_inc,
        "neg_increment_identity_vs_known8": {"known8_present": sorted(map(list, known & inc_keys)), "unexpected_new_rows": sorted(map(list, inc_keys - known)),
                                             "missing_known_rows": sorted(map(list, known - inc_keys)), "identical": inc_keys == known},
        "neg_regression_count": len(neg_reg), "neg_regressions": neg_reg[:20],
        "pos_l0_vs_now": {f"L0_pass={a},now_pass={b}": n for (a, b), n in sorted(pos.items())},
        "r4_secondary_v2_rows_with_e3e4_in_cls_s": len(r4), "r4_rows": r4[:20],
        "by_truth_cat": {f"{t}|{c}": n for (t, c), n in sorted(by_cat.items())},
        "new_method_errors": dict(errors),
    }
    s = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=1)
    open(out, "w", encoding="utf-8", newline="\n").write(s)
    print("rows", par_n, "parity_mismatch", len(par_mis), "neg_increment", len(neg_inc), "identical_to_known8", res["neg_increment_identity_vs_known8"]["identical"],
          "neg_regression", len(neg_reg), "r4", len(r4), "errors", dict(errors))


if __name__ == "__main__":
    main(sys.argv[1])
