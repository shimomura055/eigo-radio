# OPEN-517是正案 API 0再評価(事前登録=OPEN517_PREREGISTERED_01.md)。保存済み転写のみ・LLM/ASR/TTS呼出0(socket guard)。Production file無変更。
# 現行(Productionそのまま) vs 是正後(proto_value_gate_fix_01.apply_in_process = F1+F2 を in-process 差替えして judge全経路を実行)。
# 出力: open517_api0_eval_02.out.json / 標準出力。再現: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open517_api0_02.py
import collections, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import n1_pairs_01 as N1
import proto_value_gate_fix_02 as F
import er066_ja_asr_orthographic_equivalence_01_cases as c1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as c2

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
READ = ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
KNOWN_NEG = {"N1-er066a-028", "N1-er066b-020", "N1-er066b-022", "N1-prodbug-006", "N1-prodbug-007", "N1-new-042", "N1-new-044", "N1-new-057", "N3-02"}
E.api0_guard_on()
items = []   # (src, id, canon, asr)
for p in N1.all_pairs():
    items.append(("N1", p["id"], p["canon"], p["asr"]))
seen = set()
for r in json.load(open(D + "attempt_pool_01.json", encoding="utf8")):
    k = (r["canon"], r["primary"])
    if k in seen:
        continue
    seen.add(k)
    items.append(("P4", r["file"] + ":" + str(r["seg"]), r["canon"], r["primary"]))
log = [json.loads(l) for l in open(D + "phase3_run/usage_log.jsonl", encoding="utf8")]
clips = {c["id"]: c for c in json.load(open(D + "n3_clips_01.json", encoding="utf8"))}
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
for r in log:
    if r["stage"] == "N3_asr":
        items.append(("N3", r["item"], clips[r["item"]]["canonical"], r["openai_text"]))
    elif r["stage"] in ("A2_openai_moon_x3", "O1_format_prompt") and r.get("text"):
        items.append(("MOON", r["stage"] + ":" + r["item"], MOON, r["text"]))
for i, (c, a, k) in enumerate(c1.POSITIVE + [(x[0], x[1], x[2]) for x in c2.POSITIVE_02]):
    items.append(("POS", f"pos-{i:03d}", c, a))
pool = json.load(open(D + "ng_pool_cases_01.json", encoding="utf8"))
for j, cse in enumerate(pool):
    if cse.get("canon") and cse.get("primary"):
        items.append(("P3", f"p3-{j:03d}:{cse.get('seg')}", cse["canon"], cse["primary"]))

PASSING = E.uj.PASSING_STATES
rows = []
for src, ident, canon, asr in items:
    b = E.primary_stage(canon, asr, False)
    with F.apply_in_process():
        f = E.primary_stage(canon, asr, False)
    pure = F.reading_match_final_gate(canon, asr).state if b["primary_pass"] and b["label"] in READ else None
    rows.append({"src": src, "id": ident, "canon": canon, "asr": asr,
                 "base_state": b["state"], "base_reason": b["reason"], "base_label": b["label"],
                 "fix_state": f["state"], "fix_reason": f["reason"], "fix_label": f["label"], "pure_verdict": pure,
                 "known_neg": ident in KNOWN_NEG})
E.api0_guard_off()

def passing(s):
    return s in PASSING
base_read_pass = [r for r in rows if passing(r["base_state"]) and r["base_label"] in READ]
def _rs(x):  # PASS時のreason表記差(approved_equivalence/primary_pass)は同一扱い
    return "primary_pass" if str(x).startswith("primary_pass") else x
changed = [r for r in rows if (r["base_state"], _rs(r["base_reason"]), r["base_label"]) != (r["fix_state"], _rs(r["fix_reason"]), r["fix_label"])]
print(f"items: {len(rows)} by src {dict(collections.Counter(r['src'] for r in rows))}")
print(f"base READING_MATCH PASS: {len(base_read_pass)} by src {dict(collections.Counter(r['src'] for r in base_read_pass))}")
print("== 判定が変わった全件(現行 -> 是正後) ==")
for r in changed:
    print(f" {r['src']} {r['id'][-60:]} | {r['canon'][:28]} | {r['asr'][:28]} | {r['base_state']}/{r['base_reason']}/{r['base_label']} -> {r['fix_state']}/{r['fix_reason']} | pure={r['pure_verdict']} | known_neg={r['known_neg']}")
# 基準1: 正常attemptのNG化
normal = [r for r in base_read_pass if r["src"] in ("P4", "POS") ]
ng_normal = [r for r in normal if not passing(r["fix_state"])]
print(f"[K1] 正常attempt(P4+正例対照のREADING_MATCH PASS {len(normal)}件)のNG化/降格: {len(ng_normal)}")
for r in ng_normal: print("   ", r["id"], r["canon"][:30], "|", r["asr"][:30], r["fix_state"], r["fix_reason"])
kn = [r for r in rows if r["known_neg"]]
print("[K2] 既知負例(現行READING_MATCH PASS):")
for r in kn:
    print("   ", r["id"], r["canon"][:20], "|", r["asr"][:20], "base", r["base_state"], "->", r["fix_state"], r["fix_reason"], "pure", r["pure_verdict"])
k2_ok = all(passing(r["base_state"]) and not passing(r["fix_state"]) for r in kn) and len(kn) == 9
print("[K2] 9件全てPASS以外へ:", k2_ok)
ich = [r for r in rows if "いちばん低い" in r["canon"] + r["asr"] or "一番低い" in r["canon"] + r["asr"]]
print("[K1b] いちばん/一番の件:", [(r["id"][-40:], r["base_state"], r["fix_state"]) for r in ich])
# 基準3: 変化の分類
cls = collections.Counter()
other = []
for r in changed:
    if passing(r["base_state"]) and r["base_label"] in READ and not passing(r["fix_state"]):
        cls["F1: READING_MATCH PASS -> not PASS"] += 1
    else:
        cls["other"] += 1; other.append(r)
print("[K3] 変化の分類:", dict(cls))
for r in other: print("   other:", r["src"], r["id"][-50:], r["canon"][:30], "|", r["asr"][:30], r["base_state"], r["base_reason"], "->", r["fix_state"], r["fix_reason"])
nonread_pass_changed = [r for r in rows if passing(r["base_state"]) and r["base_label"] not in READ and (r["base_state"], _rs(r["base_reason"])) != (r["fix_state"], _rs(r["fix_reason"]))]
ng_to_pass = [r for r in rows if (not passing(r["base_state"])) and passing(r["fix_state"])]
print("[K3] 非READING_MATCH PASSの変化:", len(nonread_pass_changed), "/ NG->PASS:", len(ng_to_pass))
# 取りこぼし(是正後もPASSする現行READING_MATCH PASSのうち、既知の誤PASS型)
remain = [r for r in base_read_pass if passing(r["fix_state"])]
print(f"[K6] 是正後もPASSのREADING_MATCH PASS: {len(remain)} (うちN3: {[r['id'] for r in remain if r['src']=='N3']})")
out = {"rows": rows, "changed": changed, "summary": {"items": len(rows), "base_read_pass": len(base_read_pass), "normal_ng": len(ng_normal), "known_neg_ok": k2_ok,
        "changed": len(changed), "other_changed": len(other), "nonread_pass_changed": len(nonread_pass_changed), "ng_to_pass": len(ng_to_pass), "remain_pass": len(remain)}}
json.dump(out, open(D + "open517_api0_eval_02.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
print("out sha256:", hashlib.sha256(open(D + "open517_api0_eval_02.out.json", "rb").read()).hexdigest())
