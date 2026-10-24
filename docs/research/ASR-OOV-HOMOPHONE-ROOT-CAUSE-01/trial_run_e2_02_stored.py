# trial_run_e2_02_stored.py -- 委任_02 §4 保存データ再判定(API 0・読取専用)。OF-OOV-01/02適用後のE2(trial_direct_ledger_phoneme_01 v2)で:
#  (1) 本run Adv part3 8テイク(Primary転写。後半4テイクはAzure転写もある=forced-secondary経路相当)
#  (2) 保存全Primary非PASS行(Ledger読み付きOOVを含むユニークペア110)の受理件数変化(委任_01版=3件との差と落ちた理由)
# 実行: .venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_run_e2_02_stored.py
import copy, glob, json, sys, collections
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1
import er006_preprod_hardening_01_validation as val
import er109_stored_census_01 as C

L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/"
res = json.load(open(base + "audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part3"]
cb, ca = res["canonical_text_before_local_rewrite"], res["text"]
sec_texts = [(a.get("asr_judgement") or {}).get("secondary", {}).get("text") for a in res["attempts_log"]]
out = {"gacha_attempts": [], "stored": {}}
print("== 1. 本run Adv part3 8 attempt (v2: 位置置換・F1残差0・confidence>=medium・3音素以上・role=FULL_STORY)")
for n in range(1, 9):
    j = json.load(open(base + f"narration/attempts/full_story_part3_attempt{n}_englishstyleprefixwidemargin.json", encoding="utf-8"))
    c = cb if n <= 7 else ca
    fz = m1.freeze_candidates(c, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
    r = T.judge_direct(c, j["asr_text"], fz, segment_id="full_story_part3", ledger=L)
    row = {"attempt": n, "base": r["base"], "accepted": r["accepted"], "reason": r["reason"], "primary_asr_has_curly_apostrophe": "’" in j["asr_text"]}
    if n >= 5 and len(sec_texts) >= n - 4 and sec_texts[n - 5]:
        r2 = T.judge_direct(c, j["asr_text"], fz, segment_id="full_story_part3", secondary_asr_text=sec_texts[n - 5], ledger=L)
        row.update(with_secondary_accepted=r2["accepted"], with_secondary_state=r2.get("secondary_state"), with_secondary_reason=r2["reason"])
    print(n, row)
    out["gacha_attempts"].append(row)

print("== 2. 保存全Primary非PASS行(現Ledger全件を『開始前』扱い=最大緩和側)")
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f:
        continue
    rows += C.rows_from_results(f)
seen = set(); cnt = collections.Counter(); acc = []; v1 = []
old = json.load(open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_e2_result_01.json", encoding="utf-8"))["stored"]["accepted"]
for r in rows:
    if not r["asr"] or r["stored_cls"] in C.PASS_LABELS:
        continue
    k = (r["canonical"], r["asr"])
    if k in seen:
        continue
    seen.add(k)
    fz = m1.freeze_candidates(r["canonical"], ledger_snapshot=copy.deepcopy(L), segment_started_at="2099-01-01T00:00:00")
    if not any(c.source.startswith("C2_") for fw in fz.words for c in fw.candidates):
        continue
    x = T.judge_direct(r["canonical"], r["asr"], fz, segment_id=r["seg"], ledger=L)
    cnt[x["reason"].split(":")[0]] += 1
    if x["accepted"]:
        m1r = m1.m1_multi_candidate_judge(r["canonical"], r["asr"], fz)
        acc.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "sub": x["sub"], "stored_cls": r["stored_cls"],
                    "final_status": r["final_status"], "m1_would_accept_already": bool(m1r.accepted)})
print("Ledger読み付きOOVを含む非PASSユニークペア:", sum(cnt.values())); print(dict(cnt))
for a in acc:
    print(" ACCEPT", a["src"].split("/")[-5:-3], a["seg"], a["attempt"], a["sub"]["canonical"], "<-", a["sub"]["asr"], a["sub"]["pron"], a["stored_cls"], a["final_status"], "m1_already=" + str(a["m1_would_accept_already"]))
print("委任_01版(v1)受理 3件:", [(o["sub"]["canonical"], o["sub"]["asr"], o["seg"], o["attempt"]) for o in old])
out["stored"] = {"counts": dict(cnt), "accepted": acc, "v1_accepted_count": len(old)}
json.dump(out, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_e2_02_stored_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
