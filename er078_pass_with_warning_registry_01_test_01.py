# AUW 委任_02b: PASS_WITH_WARNING registry(試聴リスト導出・HTML・途中STOP)のUnit test。API 0。
import json
import os

import er078_pass_with_warning_registry_01 as reg


def _j(state="PASS_WITH_WARNING", warnings=("SECONDARY_CONFIRMED",), ptxt="p text", stxt="s text"):
    return {"state": state, "warnings": list(warnings), "reason_code": "secondary_confirmed", "slot": 2, "script_version": "v0",
            "lang": "en", "primary": {"text": ptxt}, "secondary": {"text": stxt}}


def _results():
    return {
        "segments": {
            "topic_intro": {"status": "OK", "text": "Hello", "path": "a/topic.wav", "sha256": "s1", "language": "en", "asr_judgement": _j("PASS", ())},
            "full_story_part1": {"status": "OK", "text": "Story one", "path": "a/fs1.wav", "sha256": "s2", "language": "en",
                                 "asr_judgement": _j(), "original_wav": "a/fs1_raw.wav"},
            "point_one": {"status": "STOPPED", "reason": "x", "asr_judgement": _j()},   # STOPPED=採用音声なし
            "preview": {"status": "OK", "text": "予告", "path": "a/pv.wav", "sha256": "s3", "language": "ja",
                        "asr_judgement": _j(warnings=("NUMERIC_AMBIGUOUS_SURFACE",))},
        },
        "key_phrases": {"1": {"english": {"status": "OK", "text": "mirror image", "path": "a/kp1.wav", "sha256": "s4",
                                          "asr_judgement": _j(warnings=("LR_REWRITTEN",))}}},
    }


def test_derive_only_pass_with_warning_adopted_audio():
    es = reg.derive_listening_list(_results())
    ids = [e["segment_id"] for e in es]
    assert sorted(ids) == sorted(["full_story_part1", "preview", "key_phrases/1/english"])
    fs = [e for e in es if e["segment_id"] == "full_story_part1"][0]
    assert fs["warning_labels"] == ["SECONDARY_CONFIRMED"] and fs["original_wav"] == "a/fs1_raw.wav"
    assert fs["primary_text"] == "p text" and fs["secondary_text"] == "s text" and fs["audio_path"] == "a/fs1.wav" and fs["adopted_sha256"] == "s2"


def test_dedupe_by_sha256_and_labels():
    r = _results()
    r["key_phrases"]["2"] = {"english": dict(r["key_phrases"]["1"]["english"])}  # 複製行(KP phrase_repeat等)
    es = reg.derive_listening_list(r)
    assert len([e for e in es if e["adopted_sha256"] == "s4"]) == 1


def test_inherited_warning_is_kept_and_marked():
    r = {"segments": {"c1": {"status": "OK", "text": "t", "path": "p.wav", "sha256": "s9", "asr_judgement_inherited": _j()}}}
    es = reg.derive_listening_list(r)
    assert len(es) == 1 and es[0]["inherited"] is True
    assert "(引継ぎ)" in reg.render_html_section(es)


def test_derive_is_pure_idempotent_and_does_not_mutate():
    r = _results()
    snap = json.dumps(r, sort_keys=True)
    a, b = reg.derive_listening_list(r), reg.derive_listening_list(r)
    assert a == b and json.dumps(r, sort_keys=True) == snap


def test_mid_run_stop_partial_results_still_listed():
    r = {"segments": {"a": {"status": "OK", "text": "t", "path": "a.wav", "sha256": "x", "asr_judgement": _j()},
                      "b": {"status": "STOPPED"}, "c": {}}}
    assert [e["segment_id"] for e in reg.derive_listening_list(r)] == ["a"]
    assert reg.derive_listening_list({}) == [] and reg.derive_listening_list(None) == []


def test_write_listening_list(tmp_path):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    (run / "audit" / "tts_generation_results.json").write_text(json.dumps(_results(), ensure_ascii=False), encoding="utf-8")
    p = reg.write_listening_list(str(run))
    assert p.endswith(os.path.join("audit", "pass_with_warning_listening_list.json"))
    d1 = open(p, encoding="utf-8").read()
    data = json.loads(d1)
    assert data["count"] == 3
    reg.write_listening_list(str(run))  # 冪等
    assert open(p, encoding="utf-8").read() == d1


def test_write_listening_list_without_results_is_empty_not_error(tmp_path):
    p = reg.write_listening_list(str(tmp_path / "norun"))
    assert json.load(open(p, encoding="utf-8"))["count"] == 0


def test_html_section_and_standalone_escape_and_content():
    es = reg.derive_listening_list(_results())
    es[0]["canonical_text"] = "<script>alert(1)</script>"
    sec = reg.render_html_section(es)
    assert "<script>" not in sec and "&lt;script&gt;" in sec
    assert "WARNING音声 試聴リスト" in sec and "<audio" in sec
    full = reg.render_standalone_html(es)
    assert full.startswith("<!DOCTYPE html>") and sec in full
    assert "該当なし" in reg.render_html_section([])


def test_registry_does_not_touch_non_blocking_artifacts(tmp_path):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    (run / "audit" / "tts_generation_results.json").write_text(json.dumps(_results()), encoding="utf-8")
    before = set(os.listdir(run / "audit"))
    reg.write_listening_list(str(run))
    assert set(os.listdir(run / "audit")) - before == {"pass_with_warning_listening_list.json"}
