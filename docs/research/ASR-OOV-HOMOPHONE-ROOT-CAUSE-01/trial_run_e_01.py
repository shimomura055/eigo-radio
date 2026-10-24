# trial_run_e_01.py -- 候補E(Ledger読み付きOOVのM1入口緩和)のオフライン検証。API 0。
import copy, json, sys, collections, re
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
import trial_oov_ledger_m1_01 as T
import er006_m1_multi_candidate_01 as m1
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/"
res = json.load(open(base + "audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part3"]
cb, ca = res["canonical_text_before_local_rewrite"], res["text"]
out = {"gacha_attempts": [], "synthetic_negatives": [], "stored_rows": {}}
print("== 1. 本run Adv part3 の8 attempt(Primary転写)")
for n in range(1, 9):
    j = json.load(open(base + f"narration/attempts/full_story_part3_attempt{n}_englishstyleprefixwidemargin.json", encoding="utf-8"))
    c = cb if n <= 7 else ca
    fz = m1.freeze_candidates(c, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
    r = T.judge_relaxed(c, j["asr_text"], fz, segment_id="full_story_part3")
    print(n, r["base"], "->", r["outcome"], r["subs"]); out["gacha_attempts"].append({"attempt": n, **{k: v for k, v in r.items()}})
print("== 2. 合成負例(誤PASS検査): 実際の誤発音/別語/内容差が混じる転写が受理されないこと")
p1 = json.load(open(base + "narration/attempts/full_story_part3_attempt1_englishstyleprefixwidemargin.json", encoding="utf-8"))["asr_text"]
fz = m1.freeze_candidates(cb, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
cases = {
  "gacha->gotcha(正)": p1,
  "gacha->gutter(別語)": p1.replace("gotcha", "gutter"),
  "gacha->gadget(別語)": p1.replace("gotcha", "gadget"),
  "gacha->gotta(別語)": p1.replace("gotcha", "gotta"),
  "gacha->gatcha(CMU未収録の綴り)": p1.replace("gotcha", "gatcha"),
  "gacha->gaycha(誤発音様・CMU未収録)": p1.replace("gotcha", "gaycha"),
  "gacha脱落": p1.replace("a gotcha at", "a at"),
  "gacha->gotcha + 別の内容語差(rare->rear)": p1.replace("gotcha", "gotcha").replace("rare word hunter", "rear word hunter"),
  "gacha->gotcha + 数値差": p1.replace("gotcha", "gotcha") .replace("today", "2 today"),
  "gacha->gotcha + 否定追加": p1.replace("gotcha", "gotcha").replace("It's unexpected", "It's not unexpected"),
  "gacha->got you": p1.replace("a gotcha at", "a got you at"),
  "gacha->gotcha gotcha(重複)": p1.replace("gotcha", "gotcha gotcha"),
}
for k, t in cases.items():
    r = T.judge_relaxed(cb, t, fz, segment_id="full_story_part3")
    print(f"{k:40s} base={r['base']:28s} outcome={r['outcome']}")
    out["synthetic_negatives"].append({"case": k, **r})
print("== 3. 保存済み全Primary NG行(Ledgerに読みがあるOOV語がdiffに関与する行)での再判定")
import glob, os, er109_stored_census_01 as C
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f: continue
    rows += C.rows_from_results(f)
cnt = collections.Counter(); ex = []
seen = set()
for r in rows:
    if r["stored_cls"] in C.PASS_LABELS or not r["asr"]: continue
    key = (r["canonical"], r["asr"])
    if key in seen: continue
    seen.add(key)
    fz = m1.freeze_candidates(r["canonical"], ledger_snapshot=copy.deepcopy(L), segment_started_at="2099-01-01T00:00:00")
    if not T._backed_words(fz): continue
    x = T.judge_relaxed(r["canonical"], r["asr"], fz, segment_id=r["seg"])
    cnt[x["outcome"].split(":")[0] if x["outcome"].startswith(("UNCHANGED", "PROMOTED")) else x["outcome"]] += 1
    if x["accepted"] or x["promoted"]:
        ex.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "outcome": x["outcome"], "subs": x["subs"], "stored_cls": r["stored_cls"], "final_status": r["final_status"]})
print("Ledger読み付きOOV語を含む『Primary非PASS』ユニーク(canonical,asr)ペア:", sum(cnt.values())); print(dict(cnt))
for e in ex: print(" ", e)
out["stored_rows"] = {"counts": dict(cnt), "accepted_or_promoted": ex}
json.dump(out, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_e_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
