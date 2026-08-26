# ============================================================
# er008_audio_validation_gate_05_test.py
# ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05 Part I
# ============================================================
# 実行方法: .venv/Scripts/python.exe er008_audio_validation_gate_05_test.py
from __future__ import annotations

import json
import os
import shutil
import tempfile

import er003_v1_n3_01_assemble as asm

TMP_ROOT = os.path.join(tempfile.gettempdir(), "er008_audio_gate_05_test")


def _fresh_out_dir(name: str) -> str:
    out_dir = os.path.join(TMP_ROOT, name)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    return out_dir


def _write_results(out_dir: str, segments: dict = None, key_phrases: dict = None) -> None:
    data = {"segments": segments or {}, "key_phrases": key_phrases or {}}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_1_standard_asr_pass_allows_assembly():
    out_dir = _fresh_out_dir("test1")
    _write_results(out_dir, segments={"preview": {"status": "OK", "text": "hello"}})
    asm.verify_episode_audio_validation_gate(out_dir, "TEST")  # raises on failure
    print("PASS: test_1_standard_asr_pass_allows_assembly")


def test_2_final_stopped_blocks_even_if_wav_exists():
    out_dir = _fresh_out_dir("test2")
    os.makedirs(f"{out_dir}/narration", exist_ok=True)
    with open(f"{out_dir}/narration/comment_1.wav", "wb") as f:
        f.write(b"RIFF....WAVEfmt ")  # dummy file, presence alone must not matter
    _write_results(out_dir, segments={"comment_1": {"status": "STOPPED", "reason": "6回不合格"}})
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "STOPPEDのままassemblyが通ってはならない"
    except RuntimeError as e:
        assert "EPISODE_BLOCKED_BY_AUDIO_VALIDATION" in str(e)
    print("PASS: test_2_final_stopped_blocks_even_if_wav_exists")


def test_3_missing_status_mid_retry_blocks():
    out_dir = _fresh_out_dir("test3")
    # retry途中で確定statusが無い(空dictのentry)ケース。
    _write_results(out_dir, segments={"point_one": {}})
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "statusが確定していないsegmentでassemblyが通ってはならない"
    except RuntimeError:
        pass
    print("PASS: test_3_missing_status_mid_retry_blocks")


def test_4_stale_prior_run_wav_not_used_when_current_run_failed():
    # ER-008-N7-CONTENT-AUDIO-QA-02で実際に発生したKey Phrase事故の再現:
    # diskに前runの有効そうなWAVが残っていても、今回のrunがSTOPPEDなら
    # assemblyを許可してはならない。
    out_dir = _fresh_out_dir("test4")
    os.makedirs(f"{out_dir}/narration", exist_ok=True)
    with open(f"{out_dir}/narration/kp2_ja_charon.wav", "wb") as f:
        f.write(b"RIFF....WAVEfmt " + b"\x00" * 200)  # 前runの「有効そうな」音声を模擬
    _write_results(out_dir, key_phrases={
        "2": {"english": {"status": "OK", "text": "compare poorly with"},
              "japanese": {"status": "STOPPED", "reason": "placeholder記号混入"}}})
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "現runでSTOPPEDのKey Phraseがstale audioで素通りしてはならない"
    except RuntimeError as e:
        assert "kp2_japanese" in str(e)
    print("PASS: test_4_stale_prior_run_wav_not_used_when_current_run_failed")


def test_5_fallback_primary_pass_secondary_fail_blocks():
    out_dir = _fresh_out_dir("test5")
    # force_secondary=Trueのcascadeで、SecondaryがPrimaryのPASSに同意しない
    # 場合、最終classificationはASR_VALIDATION_UNCERTAIN(verified=False)に
    # なる(er006_secondary_asr_01.py参照)。Human Approval記録が無ければ
    # ブロックされるはず。
    out_dir2 = out_dir
    _write_results(out_dir2, segments={
        "point_one_heading": {"status": "ASR_VALIDATION_UNCERTAIN",
                               "canonical_text": "A desk can feel like a place"}})
    try:
        asm.verify_episode_audio_validation_gate(out_dir2, "TEST")
        assert False, "Secondaryが不一致のfallback音声を承認なしで通してはならない"
    except RuntimeError:
        pass
    print("PASS: test_5_fallback_primary_pass_secondary_fail_blocks")


def test_6_fallback_primary_and_secondary_pass_allows_assembly():
    out_dir = _fresh_out_dir("test6")
    _write_results(out_dir, segments={"point_one_heading": {"status": "OK", "text": "A desk can feel like a place"}})
    asm.verify_episode_audio_validation_gate(out_dir, "TEST")
    print("PASS: test_6_fallback_primary_and_secondary_pass_allows_assembly")


def test_7_human_review_explicit_approval_allows_assembly():
    out_dir = _fresh_out_dir("test7")
    canonical_text = "A desk can feel like a place"
    _write_results(out_dir, segments={
        "point_one_heading": {"status": "ASR_VALIDATION_UNCERTAIN", "canonical_text": canonical_text}})
    # Human Reviewでユーザー/開発者が実際に聴取しPASSと判断した想定。
    asm.record_human_approval(out_dir, "point_one_heading", canonical_text, approved_by="test")
    asm.verify_episode_audio_validation_gate(out_dir, "TEST")  # raises on failure
    print("PASS: test_7_human_review_explicit_approval_allows_assembly")


def test_7b_human_approval_does_not_carry_over_if_text_changed():
    # canonical_textが変わった後は、古い承認を誤って再利用してはならない。
    out_dir = _fresh_out_dir("test7b")
    asm.record_human_approval(out_dir, "point_one_heading", "A desk can feel like a place", approved_by="test")
    _write_results(out_dir, segments={
        "point_one_heading": {"status": "ASR_VALIDATION_UNCERTAIN", "canonical_text": "A completely different sentence"}})
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "textが変わった後は古いHuman Approval記録を使い回してはならない"
    except RuntimeError:
        pass
    print("PASS: test_7b_human_approval_does_not_carry_over_if_text_changed")


def test_8_one_unvalidated_segment_blocks_whole_episode():
    out_dir = _fresh_out_dir("test8")
    _write_results(out_dir, segments={
        "preview": {"status": "OK"}, "comment_1": {"status": "OK"}, "comment_2": {"status": "OK"},
        "comment_3": {"status": "OK"}, "comment_4": {"status": "STOPPED"},  # 1件だけ失敗
    })
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "1件でも未検証ならepisode全体をブロックしなければならない"
    except RuntimeError as e:
        assert "comment_4" in str(e)
        assert "preview" not in str(e), "正常segmentまでblocked一覧へ含めてはならない"
    print("PASS: test_8_one_unvalidated_segment_blocks_whole_episode")


def test_9_real_no6_failure_pattern_fixture_blocked():
    # 実際にNo.6 Deliveryで発生したfailure(full_story_part1/point_one=
    # STOPPED)のtts_generation_results.jsonをそのままfixtureとして使う。
    real_path = "er006_output/pool_pilot_01/pool_n6_delivery/a2/audit/tts_generation_results.json"
    if not os.path.exists(real_path):
        print("SKIP: test_9_real_no6_failure_pattern_fixture_blocked (fixtureファイルが無い環境)")
        return
    out_dir = _fresh_out_dir("test9")
    shutil.copyfile(real_path, f"{out_dir}/audit/tts_generation_results.json")
    try:
        asm.verify_episode_audio_validation_gate(out_dir, "TEST")
        assert False, "No.6の実際のfailure patternは新仕様でブロックされなければならない"
    except RuntimeError as e:
        msg = str(e)
        assert "full_story_part1" in msg
        assert "point_one=" in msg or "point_one=STOPPED" in msg or "point_one" in msg
    print("PASS: test_9_real_no6_failure_pattern_fixture_blocked")


if __name__ == "__main__":
    test_1_standard_asr_pass_allows_assembly()
    test_2_final_stopped_blocks_even_if_wav_exists()
    test_3_missing_status_mid_retry_blocks()
    test_4_stale_prior_run_wav_not_used_when_current_run_failed()
    test_5_fallback_primary_pass_secondary_fail_blocks()
    test_6_fallback_primary_and_secondary_pass_allows_assembly()
    test_7_human_review_explicit_approval_allows_assembly()
    test_7b_human_approval_does_not_carry_over_if_text_changed()
    test_8_one_unvalidated_segment_blocks_whole_episode()
    test_9_real_no6_failure_pattern_fixture_blocked()
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
    print("ALL TESTS PASSED")
