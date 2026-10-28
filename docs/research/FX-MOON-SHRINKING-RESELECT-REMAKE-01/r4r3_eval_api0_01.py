# R4/R3是正のAPI 0評価。事前登録=R4R3_PREREGISTERED_01.md。再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/r4r3_eval_api0_01.py
import json, sys, hashlib
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import n1_pairs_01 as N1
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
J = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
EXTRA_NEG = [  # (canon, asr, type)
  (MOON, "月のしわ、8800本超！その奥に潜む「岩の上着」の秘密", "値違い"),
  (MOON, "月のしわ、89000本超！その奥に潜む「岩の上着」の秘密", "桁違い(10倍)"),
  (MOON, "月のしわ、890本超！その奥に潜む「岩の上着」の秘密", "桁違い(1/10)"),
  (MOON, "月のしわ、8900人超！その奥に潜む「岩の上着」の秘密", "単位違い"),
  (MOON, "月の詩は、8900本超！その奥に潜む「岩の上着」の秘密", "しわ→詩は(R1、非受理のまま)"),
  (MOON, "月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密", "しわ→詩は(桁区切り付き)"),
  (MOON, "月のしわ、8900本超！その奥に潜む岩の上着の秘密です", "非数値差併存"),
  (MOON, "月のしわ、8900本超！その奥に潜む「岩の下着」の秘密", "非数値差(上着→下着)"),
  (MOON, "月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密", "値garble"),
  ("売上は1,200円です", "売上は1200ドルです", "単位違い"),
  ("売上は1,200円です", "売上は12000円です", "桁違い"),
  ("売上は1,200円です", "売上は1,300円です", "値違い"),
  ("売上は1,200円です", "売上は1200円ではありません", "否定"),
  ("3,000人が来た", "3000人が来なかった", "否定"),
  ("1,000,000円", "100000円", "桁違い"),
  ("今日は一日中雨", "今日はついたち中雨", "不規則読み"),
  ("二十日に会う", "二十日に会わない", "否定"),
  ("二十日に会う", "20人に会う", "単位違い"),
]
POS = [  # 正例対照(期待=是正後PASS)
  (MOON, "月のしわ、8900本超！その奥に潜む「岩の上着」の秘密", "桁区切り脱落のみ"),
  ("売上は1,200円です", "売上は1200円です", "桁区切り脱落のみ"),
  ("3,000人が来た", "三千人が来た", "漢数字(既存値等価)"),
  ("1,000,000円", "1000000円", "桁区切り脱落のみ"),
]
def corpus():
    c = []
    for p in N1.all_pairs(): c.append(("n1:" + p["kind"], p["canon"], p["asr"], p["type"]))
    for x in EXTRA_NEG: c.append(("extra_neg",) + x)
    for x in POS: c.append(("pos",) + x)
    for r in json.load(open(J + "ng_pool_cases_01.json", encoding="utf-8")):
        if r.get("primary"): c.append(("ng_pool:primary", r["canon"], r["primary"], r.get("seg")))
        if r.get("secondary"): c.append(("ng_pool:secondary", r["canon"], r["secondary"], r.get("seg")))
    for r in json.load(open(J + "unknown_pool_02.json", encoding="utf-8")): c.append(("unknown_pool", r["canon"], r["asr"], r.get("family")))
    for r in json.load(open(J + "attempt_pool_01.json", encoding="utf-8")):
        if r.get("primary"): c.append(("attempt_pool", r["canon"], r["primary"], r.get("seg")))
    c = [t for t in c if isinstance(t[1], str) and isinstance(t[2], str) and t[1].strip() and t[2].strip()]
    seen, out = set(), []
    for t in c:
        k = (t[0].split(":")[0], t[1], t[2])
        if k in seen: continue
        seen.add(k); out.append(t)
    return out
def SECONLY_PRIMARY(canon):
    # Secondary単独の受理面を分離するため、Primaryを必ず非PASSにする(原稿の先頭に定型の言い淀みを付加=内容語差。数値は不変)
    return "えーと、あのー、" + canon
def judge(canon, prim, sec_text, flag):
    sec.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED = flag
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = (lambda p, language="ja-JP", timeout_seconds=90: (sec_text, None)) if sec_text is not None else (lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary"))
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig
    j = r["asr_judgement"]
    return {"sec_called": bool((j.get("secondary") or {}).get("called")), "pass": j.get("state") in uj.PASSING_STATES, "state": j.get("state"), "final": r.get("final_status"),
            "layers": (j.get("adapter") or {}).get("layers")}
def run():
    E.api0_guard_on()
    rows = []
    for src, canon, asr, typ in corpus():
        row = {"src": src, "canon": canon, "asr": asr, "type": typ}
        for mode, pr, st in (("prim_only", asr, None), ("with_sec", asr, asr), ("sec_only", SECONLY_PRIMARY(canon), asr)):
            row[mode + "_off"] = judge(canon, pr, st, False)
            row[mode + "_on"] = judge(canon, pr, st, True)
            row[mode + "_sec_called"] = row[mode + "_on"].get("sec_called")
        rows.append(row)
    sec.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED = True
    E.api0_guard_off()
    return rows
if __name__ == "__main__":
    rows = run()
    s = json.dumps(rows, ensure_ascii=False, sort_keys=True)
    out = {"n": len(rows), "sha256": hashlib.sha256(s.encode()).hexdigest(), "rows": rows}
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/r4r3_eval_api0_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    inc, reg = [], []
    for r in rows:
        for m in ("prim_only", "with_sec", "sec_only"):
            a, b = r[m + "_off"]["pass"], r[m + "_on"]["pass"]
            if b and not a: inc.append((m, r))
            if a and not b: reg.append((m, r))
    print("n=", len(rows), "sha256=", out["sha256"])
    print("incremental PASS:", len(inc), " regression:", len(reg))
    for m, r in inc: print(" INC", m, r["src"], r["type"], "|", r["canon"], "|", r["asr"], r[m + "_on"]["final"], r[m + "_on"]["layers"])
    print("sec_only: primary NG & secondary called (on):", sum(1 for r in rows if r["sec_only_on"]["sec_called"] and not r["sec_only_off"]["pass"] or r["sec_only_on"]["sec_called"]), " / sec_only PASS(on):", sum(r["sec_only_on"]["pass"] for r in rows), " PASS(off):", sum(r["sec_only_off"]["pass"] for r in rows))
    print("negatives(n1/extra_neg) incremental:", sum(1 for m, r in inc if r["src"].startswith(("n1", "extra_neg"))))
    print("pos controls (with_sec on pass):", [(r["type"], r["with_sec_on"]["pass"], r["with_sec_off"]["pass"]) for r in rows if r["src"] == "pos"])
    print("extra_neg any on-pass:", [(r["type"], r["asr"]) for r in rows if r["src"] == "extra_neg" and (r["prim_only_on"]["pass"] or r["with_sec_on"]["pass"])])
