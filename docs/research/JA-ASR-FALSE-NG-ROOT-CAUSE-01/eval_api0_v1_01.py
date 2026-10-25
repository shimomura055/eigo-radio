# Phase 3 API 0 評価 (v1)。保存済み転写・合成テキスト対のみ。API呼出0 (socket guard)、Production file変更0。
# 出力: eval_api0_v1_01.out.json (全結果) + 標準出力サマリ。
import collections, json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_01 as E
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

json.dump(out, open(D + "eval_api0_v1_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
E.api0_guard_off()
