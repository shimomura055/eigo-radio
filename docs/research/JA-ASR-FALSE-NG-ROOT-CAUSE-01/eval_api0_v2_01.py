# Phase 3 API 0 再評価 (v2, 委任_04)。part1=EVAL_01相当(N-1/P-3/P-4) part2=EVAL_02相当(保存済み実転写)。v1の出力との差分表を末尾に出す。API呼出0 (socket guard)、Production file変更0。
# 出力: eval_api0_v2_01.out.json (全結果) + 標準出力サマリ。
import collections, json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import n1_pairs_01 as N1
import er066_ja_asr_orthographic_equivalence_01_cases as c1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as c2

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
E.api0_guard_on()
out = {}

# ---------- N-1 ----------
rows = []
for p in N1.all_pairs():
    b = E.primary_stage(p["canon"], p["asr"], False)
    c = E.primary_stage(p["canon"], p["asr"], True)
    # Secondary側の見立て(ASR転写がAzureから来た場合): 現行受理 / A4(a) / A4(b)
    sb, a4a, a4b, v1s = E.secondary_accept_kind(p["canon"], p["asr"])
    rows.append({**p, "base_pass": b["primary_pass"], "base_label": b["label"], "base_state": b["state"],
                 "cand_pass": c["primary_pass"], "cand_label": c["label"], "cand_state": c["state"],
                 "cand_warnings": c["warnings"], "v1_why": c["v1"].why if c["v1"] else None,
                 "v1_blocked_by": c["v1"].blocked_by if c["v1"] else None,
                 "sec_base": sb, "sec_a4a": a4a, "sec_a4b": a4b})
out["n1"] = rows
inc = [r for r in rows if r["cand_pass"] and not r["base_pass"] and r["kind"] != "structural"]
struct = [r for r in rows if r["kind"] == "structural"]
exist = [r for r in rows if r["base_pass"]]
sec_inc_a = [r for r in rows if r["sec_a4a"] and r["kind"] != "structural"]
sec_inc_b = [r for r in rows if r["sec_a4b"] and r["kind"] != "structural"]
print(f"N-1: {len(rows)} pairs (er066 {sum(1 for r in rows if r['kind']=='er066')} / new {sum(1 for r in rows if r['kind']=='new')})")
print(f"  incremental false PASS (base NG -> v1 PASS): {len(inc)}")
for r in inc: print("   ", r["id"], r["type"], r["canon"], "|", r["asr"], r["cand_label"], r["cand_state"])
print("  structural (same text pair as the P-1 positive; cannot be separated by text; reported separately):", [(r["canon"], r["asr"], r["cand_pass"]) for r in struct])
print(f"  existing false PASS (base already PASS; report only): {len(exist)}")
for r in exist: print("   ", r["id"], r["type"], r["canon"], "|", r["asr"], r["base_label"])
print(f"  Secondary-side: A4(a) value-only accept: {len(sec_inc_a)} / A4(b) pron accept: {len(sec_inc_b)}")
for r in sec_inc_a + sec_inc_b: print("   ", r["id"], r["type"], r["canon"], "|", r["asr"], "a4a" if r["sec_a4a"] else "a4b")
blocked = collections.Counter(r["v1_blocked_by"] for r in rows if r["v1_blocked_by"])
print("  v1 blocked_by counts:", dict(blocked))

# ---------- 正例対照 (期待=救済されうる。informational) ----------
pos = []
for t in [(c, a, k) for c, a, k in c1.POSITIVE] + [(r[0], r[1], r[2]) for r in c2.POSITIVE_02]:
    c, a, k = t
    b = E.primary_stage(c, a, False); n = E.primary_stage(c, a, True)
    pos.append({"canon": c, "asr": a, "type": k, "base_pass": b["primary_pass"], "cand_pass": n["primary_pass"],
                "cand_label": n["label"], "warnings": n["warnings"]})
out["positive_controls"] = pos
print(f"Positive controls (er066 POSITIVE+02): {len(pos)}; base PASS {sum(p['base_pass'] for p in pos)}, v1 PASS {sum(p['cand_pass'] for p in pos)}, "
      f"v1 regressions (base PASS -> v1 NG): {sum(1 for p in pos if p['base_pass'] and not p['cand_pass'])}")

# ---------- 月Std題 attempt別 ----------
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
T = {"attempt1 Primary": "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。",
     "attempt2 Primary": "月の死は八千九百本超。その奥に潜む岩の上着の秘密。",
     "attempt3 Primary": "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"}
moon = {}
for k, t in T.items():
    b = E.primary_stage(MOON, t, False); n = E.primary_stage(MOON, t, True)
    moon[k] = {"base": [b["state"], b["reason"], b["label"]], "v1": [n["state"], n["reason"], n["label"], n["warnings"],
                                                              n["v1"].why if n["v1"] else None]}
sb, a4a, a4b, v1s = E.secondary_accept_kind(MOON, "月の詩は8900本超。その奥に潜む岩の上着の秘密。")
moon["attempt2 Azure(Secondary)"] = {"base_accept": sb, "A4a": a4a, "A4b": a4b, "v1": v1s.why if v1s else None, "cause": v1s.cause if v1s else None}
out["moon"] = moon
print("Moon title:")
for k, v in moon.items(): print("  ", k, v)

# ---------- P-3: NG pool (保存NG転写) ----------
pool = json.load(open(D + "ng_pool_cases_01.json", encoding="utf8"))
flips, tot = [], 0
sec_a = sec_b = 0
sec_rows = []
for cse in pool:
    if not cse["canon"]:
        continue
    for who in ("primary", "secondary"):
        t = cse[who]
        if not t:
            continue
        tot += 1
        if who == "primary":
            b = E.primary_stage(cse["canon"], t, False); n = E.primary_stage(cse["canon"], t, True)
            if n["primary_pass"] and not b["primary_pass"]:
                flips.append({"where": "primary", "file": cse["file"], "seg": cse["seg"], "state": cse["state"], "canon": cse["canon"],
                              "text": t, "label": n["label"], "cause": n["v1"].cause, "kind": n["v1"].kind, "warnings": n["warnings"]})
        else:
            sb, a4a, a4b, v1s = E.secondary_accept_kind(cse["canon"], t)
            sec_rows.append((sb, a4a, a4b))
            if a4a or a4b:
                flips.append({"where": "secondary", "file": cse["file"], "seg": cse["seg"], "state": cse["state"], "canon": cse["canon"],
                              "text": t, "label": v1s.label, "cause": v1s.cause, "kind": v1s.kind, "warnings": list(v1s.warnings)})
out["p3_flips"] = flips
print(f"P-3 NG pool: {tot} texts; flips: {len(flips)} (primary {sum(1 for f in flips if f['where']=='primary')}, secondary {sum(1 for f in flips if f['where']=='secondary')})")
for f in flips: print("  ", f["where"], f["seg"], f["cause"], f["kind"], "|", f["canon"][:30], "|", f["text"][:50])
print("  flip causes:", dict(collections.Counter((f["where"], f["cause"]) for f in flips)))

# ---------- P-4: 全attempt (canonical復元可能) の非回帰 ----------
apool = json.load(open(D + "attempt_pool_01.json", encoding="utf8"))
reg, p4flips, base_pass_n = [], [], 0
seen = set()
for r in apool:
    key = (r["canon"], r["primary"])
    if key in seen:
        continue
    seen.add(key)
    b = E.primary_stage(r["canon"], r["primary"], False); n = E.primary_stage(r["canon"], r["primary"], True)
    if b["primary_pass"]:
        base_pass_n += 1
        if (not n["primary_pass"]) or n["label"] != b["label"] or n["state"] != b["state"]:
            reg.append({"file": r["file"], "canon": r["canon"], "text": r["primary"], "base": [b["state"], b["label"]], "v1": [n["state"], n["label"]]})
    elif n["primary_pass"]:
        p4flips.append({"file": r["file"], "seg": r["seg"], "canon": r["canon"], "text": r["primary"], "label": n["label"],
                        "cause": n["v1"].cause, "kind": n["v1"].kind, "stored_verified": r["verified"], "warnings": n["warnings"]})
out["p4"] = {"unique_pairs": len(seen), "base_pass": base_pass_n, "regressions": reg, "flips": p4flips}
print(f"P-4 attempts: {len(seen)} unique (canon,primary) pairs; base PASS {base_pass_n}; regressions (PASS changed): {len(reg)}; new flips (NG->PASS): {len(p4flips)}")
for f in p4flips: print("  flip", f["seg"], f["cause"], f["kind"], "|", f["canon"][:30], "|", f["text"][:50])

json.dump(out, open(D + "eval_api0_v2_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)


# ===== part 2: Phase 3 保存転写(月題・Melos・N-3) =====
# Phase 3 有料結果の評価 (委任_03)。phase3_run/usage_log.jsonl の実転写を、v1(凍結)と現行に通す。API 0(socket guard)。
# 出力: eval_api0_v2_01_phase3.out.json / 標準出力。判定にLLMは使わない。
log = [json.loads(l) for l in open(D + "phase3_run/usage_log.jsonl", encoding="utf8")]
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
out = {}

def judge(canon, ptext, stext):
    """Primary転写(必須) + Secondary転写(任意)の最終判定。base=現行 / v1=Primary差替+A4(a) / v1b=A4(b)も含む(新仕様候補)。"""
    b = E.primary_stage(canon, ptext, False) if ptext else {"primary_pass": False, "label": None, "state": None, "warnings": []}
    c = E.primary_stage(canon, ptext, True) if ptext else b
    sb = a4a = a4b = False; v1s = None
    if stext:
        sb, a4a, a4b, v1s = E.secondary_accept_kind(canon, stext)
    base_pass = bool(b["primary_pass"] or sb)
    v1_pass = bool(c["primary_pass"] or sb or a4a)
    v1b_pass = bool(v1_pass or a4b)
    return {"base_pass": base_pass, "v1_pass": v1_pass, "v1_incl_a4b_pass": v1b_pass,
            "primary_base": [b["primary_pass"], b["label"], b["state"]], "primary_v1": [c["primary_pass"], c["label"], c["state"], c["warnings"]],
            "sec": {"base": sb, "a4a": a4a, "a4b": a4b}, "v1why": c["v1"].why if c.get("v1") else None, "v1cause": c["v1"].cause if c.get("v1") else None}

# ---- A1/A2/A3/O1 (月題・Melos) ----
moon = []
for r in log:
    if r["stage"] in ("A1_azure_moon", "A3_azure_flip", "A2_openai_moon_x3", "O1_format_prompt"):
        item = r["item"]
        if r["stage"] == "A3_azure_flip" and item.startswith("preview"):
            continue
        a = r["stage"]
        if a in ("A1_azure_moon", "A3_azure_flip"):
            j = judge(MOON, None, r["text"])
        else:
            j = judge(MOON, r["text"], None)
        moon.append({"stage": a, "item": item, "text": r["text"], **j})
out["moon"] = moon
print("== moon ==")
for m in moon:
    print(m["stage"], m["item"][:40], "|", m["text"][:30], "| base", m["base_pass"], "v1", m["v1_pass"], "v1+a4b", m["v1_incl_a4b_pass"], m["primary_v1"][1])
# A3 Melos preview: Azure転写
mel = [r for r in log if r["stage"] == "A3_azure_flip" and r["item"].startswith("preview")]
p4 = json.load(open(D + "eval_api0_v2_01.out.json", encoding="utf8"))["p4"]["flips"]
for r in mel:
    cand = [f for f in p4 if "preview_attempt2" in f["file"]]
    if cand:
        canon = cand[0]["canon"]
        j = judge(canon, cand[0]["text"], r["text"])
        out["melos_preview"] = {"canon": canon, "primary_text": cand[0]["text"], "azure_text": r["text"], **j}
        print("== melos preview ==", canon[:40], "| P:", cand[0]["text"][:40], "| A:", r["text"][:60]); print(j)

# ---- N-3 ----
clips = json.load(open(D + "n3_clips_01.json", encoding="utf8"))
asr = {r["item"]: r for r in log if r["stage"] == "N3_asr"}
rows = []
for c in clips:
    r = asr.get(c["id"])
    if not r:
        continue
    j = judge(c["canonical"], r["openai_text"], r["azure_text"])
    rows.append({"id": c["id"], "type": c["type"], "canon": c["canonical"], "tts_input": c["tts_input"], "openai": r["openai_text"], "azure": r["azure_text"], **j})
out["n3"] = rows
print("== N-3 ==", len(rows), "clips")
for r in rows:
    print(r["id"], r["type"][:18], "|", r["canon"], "|", r["openai"], "|", r["azure"], "| base", r["base_pass"], "v1", r["v1_pass"], "v1+a4b", r["v1_incl_a4b_pass"])
inc = [r for r in rows if r["v1_pass"] and not r["base_pass"]]
inc_b = [r for r in rows if r["v1_incl_a4b_pass"] and not r["base_pass"]]
exist = [r for r in rows if r["base_pass"]]
print("N-3 incremental false PASS (v1; includes A4a):", [r["id"] for r in inc])
print("N-3 incremental incl A4(b) (new-spec candidate):", [r["id"] for r in inc_b])
print("N-3 existing false PASS (report only):", [(r["id"], r["type"][:14]) for r in exist])
json.dump(out, open(D + "eval_api0_v2_01_phase3.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)

# ===== part 3: v1 -> v2 差分表 =====
v1a = json.load(open(D + "eval_api0_v1_01.out.json", encoding="utf8"))
v2a = json.load(open(D + "eval_api0_v2_01.out.json", encoding="utf8"))
v1p = json.load(open(D + "eval_phase3_02.out.json", encoding="utf8"))
v2p = json.load(open(D + "eval_api0_v2_01_phase3.out.json", encoding="utf8"))
diff = {"n1": [], "p3": None, "p4": None, "n3": [], "moon": [], "melos": None}
for a, b in zip(v1a["n1"], v2a["n1"]):
    if (a["cand_pass"], a["sec_a4a"], a["sec_a4b"], a["cand_label"]) != (b["cand_pass"], b["sec_a4a"], b["sec_a4b"], b["cand_label"]):
        diff["n1"].append({"id": a["id"], "canon": a["canon"], "asr": a["asr"], "v1": [a["cand_pass"], a["sec_a4a"], a["sec_a4b"]], "v2": [b["cand_pass"], b["sec_a4a"], b["sec_a4b"]]})
f1 = {(f["where"], f["seg"], f["text"]) for f in v1a["p3_flips"]}; f2 = {(f["where"], f["seg"], f["text"]) for f in v2a["p3_flips"]}
diff["p3"] = {"v1": len(f1), "v2": len(f2), "lost": sorted(f1 - f2), "gained": sorted(f2 - f1)}
g1 = {(f["file"], f["text"]) for f in v1a["p4"]["flips"]}; g2 = {(f["file"], f["text"]) for f in v2a["p4"]["flips"]}
diff["p4"] = {"unique_pairs": v2a["p4"]["unique_pairs"], "base_pass": v2a["p4"]["base_pass"], "v1_regressions": len(v1a["p4"]["regressions"]),
              "v2_regressions": len(v2a["p4"]["regressions"]), "flips_v1": len(g1), "flips_v2": len(g2), "lost": sorted(g1 - g2), "gained": sorted(g2 - g1)}
for a, b in zip(v1p["n3"], v2p["n3"]):
    if (a["v1_pass"], a["v1_incl_a4b_pass"], a["primary_v1"][:3]) != (b["v1_pass"], b["v1_incl_a4b_pass"], b["primary_v1"][:3]):
        diff["n3"].append({"id": a["id"], "canon": a["canon"], "openai": a["openai"], "azure": a["azure"], "base": a["base_pass"], "v1": a["v1_pass"], "v2": b["v1_pass"]})
for a, b in zip(v1p["moon"], v2p["moon"]):
    if (a["v1_pass"], a["v1_incl_a4b_pass"], a["primary_v1"][:3]) != (b["v1_pass"], b["v1_incl_a4b_pass"], b["primary_v1"][:3]):
        diff["moon"].append({"stage": a["stage"], "item": a["item"], "text": a["text"], "v1": a["v1_pass"], "v2": b["v1_pass"]})
m1, m2 = v1p.get("melos_preview"), v2p.get("melos_preview")
diff["melos"] = {"v1": m1 and [m1["v1_pass"], m1["primary_v1"], m1["sec"]], "v2": m2 and [m2["v1_pass"], m2["primary_v1"], m2["sec"]]}
inc_v2 = [r["id"] for r in v2p["n3"] if r["v1_pass"] and not r["base_pass"]]
inc_v2b = [r["id"] for r in v2p["n3"] if r["v1_incl_a4b_pass"] and not r["base_pass"]]
n1_inc_v2 = [r["id"] for r in v2a["n1"] if r["kind"] != "structural" and (not r["base_pass"]) and (r["cand_pass"] or r["sec_a4a"] or r["sec_a4b"])]
n1_inc_v1 = [r["id"] for r in v1a["n1"] if r["kind"] != "structural" and (not r["base_pass"]) and (r["cand_pass"] or r["sec_a4a"] or r["sec_a4b"])]
n1_a4a_v1 = [r["id"] for r in v1a["n1"] if r["kind"] != "structural" and r["sec_a4a"]]
n1_a4a_v2 = [r["id"] for r in v2a["n1"] if r["kind"] != "structural" and r["sec_a4a"]]
diff["summary"] = {"n1_incremental_false_pass_incl_a4_v1": n1_inc_v1, "n1_incremental_false_pass_incl_a4_v2": n1_inc_v2, "n1_secondary_a4a_accepts_v1(already Primary base PASS)": n1_a4a_v1, "n1_secondary_a4a_accepts_v2": n1_a4a_v2, "n3_incremental_false_pass_incl_a4a_v2": inc_v2,
                   "n3_incremental_incl_a4b_v2": inc_v2b, "n3_existing_false_pass": len([r for r in v2p["n3"] if r["base_pass"]])}
print("== v1 -> v2 diff =="); print(json.dumps(diff, ensure_ascii=False, indent=1, default=str))
json.dump(diff, open(D + "eval_api0_v2_01_diff.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
E.api0_guard_off()
