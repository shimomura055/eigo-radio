# -*- coding: utf-8 -*-
"""er_hr_listing_policy_01 のtest(純関数。API 0)。実行: .venv\Scripts\python.exe -m pytest er_hr_listing_policy_01_test_01.py -q"""
import er_hr_listing_policy_01 as p


def test_asr_ng_take_not_listed_but_kept_in_internal_record():
    takes = [{"id": "③", "asr_state": "PASS"}, {"id": "④", "asr_state": "PASS_WITH_WARNING"},
             {"id": "⑤", "asr_state": "NG_BOTH"}, {"id": "⑥", "asr_state": "TRUE_CONTENT_MISMATCH"}]
    listed, omitted = p.select_listing_takes(takes)
    assert [t["id"] for t in listed] == ["③", "④"]
    assert [t["id"] for t in omitted] == ["⑤", "⑥"]
    rec = p.omitted_internal_record(omitted)
    assert [r["id"] for r in rec] == ["⑤", "⑥"] and all("内部記録" in r["reason"] for r in rec)
    assert len(takes) == 4        # 入力(試行記録)は不変


def test_ng_but_user_judgment_requested_or_adopted_is_listed():
    takes = [{"id": "a", "asr_state": "NG_BOTH", "user_judgment_requested": True}, {"id": "b", "asr_state": "NG_BOTH", "adopted": True},
             {"id": "c", "asr_state": "NG_BOTH"}]
    listed, omitted = p.select_listing_takes(takes)
    assert [t["id"] for t in listed] == ["a", "b"] and [t["id"] for t in omitted] == ["c"]


def test_asr_ng_bool_overrides_state_and_pass_warning_is_not_ng():
    assert p.is_asr_ng({"asr_ng": True, "asr_state": "PASS"}) is True
    assert p.is_asr_ng({"asr_ng": False, "asr_state": "NG_BOTH"}) is False
    assert p.is_asr_ng({"asr_state": "PASS_WITH_WARNING"}) is False
    assert p.is_asr_ng({}) is False


def test_hr_adoption_section_empty_is_byte_identical_and_lists_final_only():
    assert p.render_hr_adoption_section([]) == ""
    items = p.collect_hr_adoptions({"b1b": {"full_story_part3_c6": {"z_adoption": "human_review_adopted", "local_rewrite_audio_superseded_by_human_approval": True},
                                            "x": {"z_adoption": "adopted"}}})
    assert len(items) == 1 and "Advanced full_story_part3_c6" == items[0]["label"] and "Local Rewrite" in items[0]["note"]
    h = p.render_hr_adoption_section(items)
    assert "<audio" not in h and "full_story_part3_c6" in h


def test_wired_into_hr_page_generators_and_candidate_runner():
    import io
    for f in ("er019_mey_hr_page_02.py", "er019_pp_hr_page_01.py", "er026_family_z_fiction_production_runner_01.py",
              "docs/research/FZ-DIALOGUE-LR-ADOPTION-01/tools/build_hr_page_03.py"):
        assert "er_hr_listing_policy_01" in io.open(f, encoding="utf-8").read(), f


def test_hr_03_page_has_no_ng_take_audio():
    h = open("user_test/family_z_in_a_grove_hr_03/index.html", encoding="utf-8").read()
    assert "c6_try3.mp3" in h and "c6_try4.mp3" in h and "c6_try5" not in h and "c6_try6" not in h
    import os
    assert sorted(os.listdir("user_test/family_z_in_a_grove_hr_03/audio")) == ["c6_try3.mp3", "c6_try4.mp3"]
