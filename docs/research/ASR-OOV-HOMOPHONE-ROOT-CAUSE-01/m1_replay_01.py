# m1_replay_01.py -- 本runのAdv full_story_part3 の8 attemptのPrimary転写を、Production判定関数(classify_asr_match+M1)へ
# オフラインで再投入し、M1(承認済み・ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01)がなぜ発火しなかったかを層別に特定する。API 0。
import json, sys, copy
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1
import er006_secondary_asr_01 as S
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/"
res = json.load(open(base + "audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part3"]
canon_before = res["canonical_text_before_local_rewrite"]
canon_after = res["text"]
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
rows = []
for n in range(1, 9):
    j = json.load(open(base + f"narration/attempts/full_story_part3_attempt{n}_englishstyleprefixwidemargin.json", encoding="utf-8"))
    rows.append((n, j["asr_text"], j.get("audio_classification")))
for started in ("2026-10-24T18:10:00", "2026-10-24T18:03:00"):
    fz = m1.freeze_candidates(canon_before, ledger_snapshot=copy.deepcopy(L), segment_started_at=started)
    fw = fz.word("gacha")
    print("== segment_started_at", started, "gacha candidates:", [(c.pron, c.source, c.confidence) for c in fw.candidates], "excluded:", fw.excluded[:2], "unconv:", fw.unconvertible)
    for n, asr, stored in rows:
        c = canon_before if n <= 7 else canon_after
        base_cls = val.classify_asr_match(c, asr, segment_id="full_story_part3")
        fzn = fz if n <= 7 else m1.freeze_candidates(c, ledger_snapshot=copy.deepcopy(L), segment_started_at=started)
        r = m1.m1_multi_candidate_judge(c, asr, fzn)
        print(f"attempt{n} stored={stored} now={base_cls.classification} should_pass={base_cls.should_pass} protected_passed={base_cls.protected.passed} | M1 accepted={r.accepted} reason={r.reason} applicable={r.applicable} nm={r.no_match_reason}")
