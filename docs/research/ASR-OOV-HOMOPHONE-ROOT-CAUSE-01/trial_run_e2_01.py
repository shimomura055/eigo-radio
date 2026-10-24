import copy, json, sys, collections, glob
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1
import er109_stored_census_01 as C
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/"
res = json.load(open(base + "audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part3"]
cb, ca = res["canonical_text_before_local_rewrite"], res["text"]
out = {"gacha_attempts": [], "synthetic_negatives": [], "stored": {}}
print("== 1. 本run Adv part3 の8 attempt (Primary転写)")
for n in range(1, 9):
    j = json.load(open(base + f"narration/attempts/full_story_part3_attempt{n}_englishstyleprefixwidemargin.json", encoding="utf-8"))
    c = cb if n <= 7 else ca
    fz = m1.freeze_candidates(c, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
    r = T.judge_direct(c, j["asr_text"], fz, segment_id="full_story_part3")
    print(n, r["base"], "->", r["reason"], r["sub"] and (r["sub"]["canonical"], r["sub"]["asr"], r["sub"]["pron"]))
    out["gacha_attempts"].append({"attempt": n, **r})
print("== 2. 合成負例")
p1 = json.load(open(base + "narration/attempts/full_story_part3_attempt5_englishstyleprefixwidemargin.json", encoding="utf-8"))["asr_text"]
assert "gotcha" in p1 and "’" not in p1
fz = m1.freeze_candidates(cb, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
cases = {
 "gacha->gotcha(単独差=正)": p1,
 "gacha->gutter": p1.replace("gotcha", "gutter"), "gacha->gadget": p1.replace("gotcha", "gadget"), "gacha->gotta": p1.replace("gotcha", "gotta"),
 "gacha->catcher": p1.replace("gotcha", "catcher"), "gacha->gatcha(CMU外)": p1.replace("gotcha", "gatcha"), "gacha->gaycha(CMU外)": p1.replace("gotcha", "gaycha"),
 "gacha脱落": p1.replace("a gotcha at", "a at"), "gacha->got you(2語)": p1.replace("a gotcha at", "a got you at"),
 "gacha->gotcha+内容語差": p1.replace("rare word hunter", "rear word hunter"),
 "gacha->gotcha+数値差": p1.replace("today", "2 today"), "gacha->gotcha+否定": p1.replace("It's unexpected", "It's not unexpected"),
 "gacha->gotcha+語脱落(oh)": p1.replace("Oh, please", "Please"), "gacha->gotcha+you've->you": p1.replace("you've", "you"),
 "gacha->gotcha gotcha(重複)": p1.replace("gotcha", "gotcha gotcha"),
}
for k, t in cases.items():
    r = T.judge_direct(cb, t, fz, segment_id="full_story_part3")
    print(f"{k:34s} base={r['base']:26s} accepted={r['accepted']} {r['reason']}")
    out["synthetic_negatives"].append({"case": k, **r})
print("== 3. 保存済み全Primary非PASS行で再判定(現Ledger全件を『開始前』扱い=最大緩和側)")
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f: continue
    rows += C.rows_from_results(f)
seen = set(); cnt = collections.Counter(); acc = []
for r in rows:
    if not r["asr"] or r["stored_cls"] in C.PASS_LABELS: continue
    k = (r["canonical"], r["asr"])
    if k in seen: continue
    seen.add(k)
    fz = m1.freeze_candidates(r["canonical"], ledger_snapshot=copy.deepcopy(L), segment_started_at="2099-01-01T00:00:00")
    if not any(c.source.startswith("C2_") for fw in fz.words for c in fw.candidates): continue
    x = T.judge_direct(r["canonical"], r["asr"], fz, segment_id=r["seg"])
    cnt[x["reason"].split(":")[0]] += 1
    if x["accepted"]: acc.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "sub": x["sub"], "stored_cls": r["stored_cls"], "final_status": r["final_status"]})
print("Ledger読み付きOOVを含む非PASSユニークペア:", sum(cnt.values())); print(dict(cnt))
for a in acc: print(" ACCEPT", a["src"].split("/")[-5:-3], a["seg"], a["attempt"], a["sub"]["canonical"], "<-", a["sub"]["asr"], a["sub"]["pron"], a["stored_cls"], a["final_status"])
out["stored"] = {"counts": dict(cnt), "accepted": acc}
json.dump(out, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_e2_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
