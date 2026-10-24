# trial_run_e2_02_whisper.py -- trial02の23 clipをローカルfaster-whisper small(無料・API 0)で転写し、独立エンジンの聞こえ方を記録する。
# 目的: (1) 負例(lyft/loft, kewl/coal)でPrimaryの誤りかどうかの切り分け (2) 『E2 + ローカルWhisper非矛盾』変種の効果(救済率・誤受理)を無料で評価。
import json, sys, copy, datetime
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
import er008_disfluency_qa_18 as dq
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1
import trial_direct_ledger_phoneme_01 as T
OUT = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/trial02"
r = json.load(open(OUT + "/trial02_result.json", encoding="utf-8"))
ledger = json.load(open(OUT + "/ledger_trial.json", encoding="utf-8"))
SEG = "full_story_part1"
rows = []
for c in r["clips"]:
    words = dq.transcribe_verbatim(f"{OUT}/clips/{c['id']}.wav", language="en", model_size="small")
    wt = " ".join(w["text"].strip() for w in words).strip()
    fz = m1.freeze_candidates(c["canonical"], ledger_snapshot=copy.deepcopy(ledger), segment_started_at="2099-01-01T00:00:00")
    # 変種 E2W: Primary転写でE2受理 かつ ローカルWhisper転写も (should_pass | 同じE2で受理) かつ矛盾(protected fail/TRUE_CONTENT_MISMATCH で E2不受理)でない
    e2 = T.judge_direct(c["canonical"], c["primary_asr"], fz, segment_id=SEG, secondary_asr_text=wt, ledger=ledger) if c.get("primary_asr") else None
    base_w = val.classify_asr_match(c["canonical"], wt, segment_id=SEG)
    row = {"id": c["id"], "kind": c["kind"], "spoken": c["spoken"], "primary": c.get("primary_asr"), "whisper": wt, "whisper_base": base_w.classification,
           "outcome_primary_only": c.get("outcome"), "e2w_accepted": bool(e2 and e2["accepted"]), "e2w_secondary_state": e2 and e2.get("secondary_state"),
           "e2w_reason": e2 and e2["reason"]}
    rows.append(row)
    print(row["id"], "| P:", row["primary"], "| W:", wt, "|", row["outcome_primary_only"], "| E2+W:", row["e2w_accepted"], row["e2w_secondary_state"], flush=True)
json.dump(rows, open(OUT + "/trial02_whisper_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
