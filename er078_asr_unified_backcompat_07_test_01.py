# -*- coding: utf-8 -*-
"""AUW 委任_07: 後方互換test(DESIGN_02_ADDENDUM_01 §2 L99 / OF-AUW-13)。API 0・通信なし。
(1) 新キー(asr_judgement / asr_judgement_inherited / asr_judgement_pre_slowdown / technical_stop_status / 試聴リストJSON)を
    持たない**旧出力**(main時点の実ファイル er003_output/n3_01/*/audit/tts_generation_results.json)を、既存の下流reader
    (HR Lock build_attempts_detail / 試聴リスト・ページ節 / Assemble Gate / Master Store / 集計script / J11 reader)が従来どおり読める。
(2) 新キーあり(AUW後の実evidence)でも、旧reader(旧キーのみを見るreader)の出力が「新キーを除いた場合」と一致する(= 新キーはadditive)。
本番stateへは書かない(Master Storeはtmp_pathへ向ける)。"""
from __future__ import annotations

import glob
import json
import os
import shutil

import pytest

import er003_v1_n3_01_assemble as asm
import er006_master_audio_store_01 as ms
import er011_human_review_lock_01 as lock
import er019_family_x_validation_inheritance_01 as vi
import er078_auw_aggregate_06d as agg
import er078_pass_with_warning_registry_01 as reg

NEW_KEYS = ("asr_judgement", "asr_judgement_inherited", "asr_judgement_pre_slowdown", "technical_stop_status")
OLD_FILES = sorted(glob.glob("er003_output/n3_01/*/a2/audit/tts_generation_results.json")
                   + glob.glob("er003_output/n3_01/*/b1b/audit/tts_generation_results.json"))[:8]
EV = "er058_output/unified_all_roles_production_wiring_01"
NEW_FILES = [p for p in (f"{EV}/evidence_06e/dlg_cap2/run/a2/audit/tts_generation_results.json",
                         f"{EV}/evidence_06d/xkp/x_out/a2/audit/tts_generation_results.json",
                         f"{EV}/evidence_06b/zep/run/a2/audit/tts_generation_results.json",
                         f"{EV}/evidence_06b/xrun/x_out/b1b/audit/tts_generation_results.json") if os.path.exists(p)]


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _strip(node):
    """新キーを再帰的に除いた深いコピー(= AUW前の形)。"""
    if isinstance(node, dict):
        return {k: _strip(v) for k, v in node.items() if k not in NEW_KEYS}
    if isinstance(node, list):
        return [_strip(v) for v in node]
    return node


def _has_new_key(node):
    if isinstance(node, dict):
        return any(k in NEW_KEYS for k in node) or any(_has_new_key(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_new_key(v) for v in node)
    return False


def _entries(doc):
    for k, e in (doc.get("segments") or {}).items():
        if isinstance(e, dict):
            yield k, e
    for rank, kp in (doc.get("key_phrases") or {}).items():
        for sub, e in (kp or {}).items():
            if isinstance(e, dict):
                yield f"kp{rank}_{sub}", e


def test_fixture_sets_are_what_they_claim():
    assert len(OLD_FILES) >= 4
    for p in OLD_FILES:
        assert not _has_new_key(_load(p)), p          # 旧出力は新キーを持たない(実ファイル)
    assert len(NEW_FILES) >= 3
    assert any(_has_new_key(_load(p)) for p in NEW_FILES)   # 新出力には新キーがある


# ---------------------------------------------------------------- 試聴リスト・ページ節
@pytest.mark.parametrize("p", OLD_FILES)
def test_listening_list_reads_old_output_as_zero_items(p, tmp_path):
    doc = _load(p)
    assert reg.derive_listening_list(doc) == []
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    shutil.copyfile(p, run / "audit" / "tts_generation_results.json")
    assert reg.load_listening_list(str(run)) == []                      # 「導出失敗」ではなく「0件」
    rep = reg.write_listening_list_safe(str(run), standalone_html=True)
    assert rep["error"] is None and rep["count"] == 0
    html = reg.render_html_section([])
    assert isinstance(html, str) and html


@pytest.mark.parametrize("p", NEW_FILES)
def test_listening_list_new_keys_do_not_change_old_fields(p):
    doc = _load(p)
    lst = reg.derive_listening_list(doc)
    assert isinstance(lst, list)
    assert reg.derive_listening_list(_strip(doc)) == []                 # 新キーを除けば旧と同じ「0件」(新キーだけがリストを生む)
    reg.render_html_section(lst)


# ---------------------------------------------------------------- HR Lock build_attempts_detail
@pytest.mark.parametrize("p", OLD_FILES)
def test_build_attempts_detail_reads_old_output(p):
    for name, e in _entries(_load(p)):
        d = lock.build_attempts_detail(e)
        assert isinstance(d, list)
        for row in d:
            assert row["asr_judgement"] is None                         # 旧attemptは新キーなし -> None(KeyErrorにならない)
            for k in ("route", "attempt", "status", "primary_asr_text", "audio_classification", "verified",
                      "style_prefix", "instruction_label", "cascade_steps"):
                assert k in row


@pytest.mark.parametrize("p", NEW_FILES)
def test_build_attempts_detail_new_keys_are_additive(p):
    for name, e in _entries(_load(p)):
        new = lock.build_attempts_detail(e)
        old = lock.build_attempts_detail(_strip(e))
        assert len(new) == len(old)
        for a, b in zip(new, old):
            assert b["asr_judgement"] is None
            assert {k: v for k, v in a.items() if k != "asr_judgement"} == {k: v for k, v in b.items() if k != "asr_judgement"}


# ---------------------------------------------------------------- Assemble Gate(tts_generation_results の下流reader)
def _gate_outcome(doc, tmp_path, level):
    out = tmp_path / "ep"
    if out.exists():
        shutil.rmtree(out)
    (out / "audit").mkdir(parents=True)
    (out / "narration").mkdir()
    with open(out / "audit" / "tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
    try:
        asm.verify_episode_audio_validation_gate(str(out), level)
        return ("ok", None)
    except BaseException as exc:  # noqa: BLE001  種別とメッセージで比較(新キーの有無で変わってはならない)
        return (type(exc).__name__, str(exc))


@pytest.mark.parametrize("p", OLD_FILES)
def test_assemble_gate_reads_old_output_without_structural_errors(p, tmp_path):
    level = "A2" if "/a2/" in p.replace("\\", "/") else "B1"
    kind, _ = _gate_outcome(_load(p), tmp_path, level)
    assert kind not in ("KeyError", "TypeError", "AttributeError", "JSONDecodeError")


@pytest.mark.parametrize("p", NEW_FILES)
def test_assemble_gate_outcome_unchanged_by_new_keys(p, tmp_path):
    level = "A2" if "/a2/" in p.replace("\\", "/") else "B1"
    doc = _load(p)
    assert _gate_outcome(doc, tmp_path, level) == _gate_outcome(_strip(doc), tmp_path, level)


# ---------------------------------------------------------------- 集計script(06d)・J11 reader
@pytest.mark.parametrize("p", OLD_FILES[:3] + NEW_FILES)
def test_aggregate_walk_reads_both(p):
    doc = _load(p)
    assert [k for k, _ in agg.walk(doc)] == [k for k, _ in agg.walk(_strip(doc))]
    for k, e in agg.walk(_strip(doc)):
        assert e.get("asr_judgement") is None      # 06d main()は `if aj:` で旧entryを自然に除外する


@pytest.mark.parametrize("p", OLD_FILES[:3])
def test_j11_reader_old_entry_returns_none(p):
    for _, e in _entries(_load(p)):
        assert vi._j11_adopted_judgement(e) == (None, None)


# ---------------------------------------------------------------- Master Store(旧manifest/新manifest)
def _point_store(monkeypatch, tmp_path):
    monkeypatch.setattr(ms, "STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setattr(ms, "AUDIO_DIR", str(tmp_path / "store" / "audio"))
    monkeypatch.setattr(ms, "MANIFEST_PATH", str(tmp_path / "store" / "manifest.json"))
    monkeypatch.setattr(ms, "TELEMETRY_PATH", str(tmp_path / "store" / "reuse_telemetry.jsonl"))


def _key():
    return ms.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id="m", canonical_text="The shop opens at nine.")


def _write_manifest(tmp_path, entry_extra):
    k = _key()
    wav = tmp_path / "store" / "audio" / "m.wav"
    wav.parent.mkdir(parents=True, exist_ok=True)
    wav.write_bytes(b"RIFF....WAVE")
    entry = {"audio_path": str(wav), "key": k.as_dict(), "created_at": "2026-01-01T00:00:00",
             "qa_evidence": {"sha256": "x", "asr_verified": True, "asr_text": None, "disfluency_checked": True, "disfluency_evidence": None},
             "audio_classification": None, "scg_result": None}
    entry.update(entry_extra)
    with open(tmp_path / "store" / "manifest.json", "w", encoding="utf-8") as f:
        json.dump({k.master_audio_id(): entry}, f)
    return k


def _boom(_p):
    raise AssertionError("generate_fn must not be called on reuse")


def test_master_store_reuses_old_manifest_entry_without_new_keys(monkeypatch, tmp_path):
    _point_store(monkeypatch, tmp_path)
    k = _write_manifest(tmp_path, {})
    assert "asr_judgement" not in json.load(open(tmp_path / "store" / "manifest.json", encoding="utf-8"))[k.master_audio_id()]
    r = ms.get_or_generate(k, str(tmp_path / "out" / "x.wav"), _boom)
    assert r["status"] == "OK" and r["reused"] is True
    assert "asr_judgement_inherited" not in r            # 旧entryに新キーはなく、勝手に生成もされない
    assert r["asr_verified"] is True and r["disfluency_checked"] is True   # 旧qa_evidenceは従来どおり復元


def test_master_store_new_manifest_key_is_additive(monkeypatch, tmp_path):
    _point_store(monkeypatch, tmp_path)
    aj = {"state": "PASS_WITH_WARNING", "lang": "en", "primary": {"passed": False, "text": "The shop opens at nine."},
          "secondary": {"text": "The shop opens at nine."}, "reason_code": "secondary_confirmed"}
    k = _write_manifest(tmp_path, {"asr_judgement": aj})
    r = ms.get_or_generate(k, str(tmp_path / "out" / "y.wav"), _boom)
    assert r["status"] == "OK" and r["reused"] is True
    assert r["asr_judgement_inherited"] == aj
    assert r["asr_verified"] is True and r["master_audio_key"] == k.as_dict()


# ---------------------------------------------------------------- Assemble Gate の entry単位reader(tmpにwavが無い場合のblock理由に左右されない直接比較)
@pytest.mark.parametrize("p", OLD_FILES + NEW_FILES)
def test_assemble_segment_gate_status_same_with_and_without_new_keys(p):
    doc = _load(p)
    n = 0
    for name, e in _entries(doc):
        a = asm._segment_gate_status(e, name, {})
        b = asm._segment_gate_status(_strip(e), name, {})
        assert a == b
        assert a in ("VALIDATED", "UNVALIDATED", "STOPPED", "HUMAN_APPROVED")
        assert asm._segment_missing_mandatory_disfluency_qa(name, e, "A2") == asm._segment_missing_mandatory_disfluency_qa(name, _strip(e), "A2")
        n += 1
    assert n > 0
