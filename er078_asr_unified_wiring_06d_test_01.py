# AUW 委任_06d: legacy A(er003_v1_n3_01_tts_generate.py main())のcost logger install是正のtest。全てmock・API呼出0・費用JPY0。
# 背景(06c IMPLEMENTATION §4-2 / 06 D1): legacy A本番入口はcost loggerを一度もinstallしておらず、統一judgeのSecondary(Azure)呼出後の
# `cl.record`が`init_logger()が呼ばれていません`のRuntimeErrorで停止(設定不備として再送出)し、Azureは課金されるのに費用が記録されなかった。
import os
import sys
import wave

import pytest

import er003_v1_n3_01_tts_generate as n3
import er005_cost_logger as cl
import er006_secondary_asr_01 as sec

CANON = "Ottoni and colleagues published a study."
PRIMARY_NG = "A Tony and colleagues published a study."


def _wav(tmp_path, name="a.wav", seconds=1, rate=8000):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(b"\x00" * (rate * seconds))
    return str(p)


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    sec.reset_secondary_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(cl, "_LOG_PATH", None)         # 既定=未install(旧legacy Aと同じ状態)
    monkeypatch.setattr(cl, "_INSTALLED", True)        # SDK patchは本番プロセスでのみ。testでは二重patchしない(init_loggerだけ作用)
    yield
    sec.reset_secondary_cache()


def test_e_cost_logger_not_installed_record_raises_runtimeerror_before_fix():
    """是正前の状態の再現(Secondary呼出後のcl.recordが設定不備のRuntimeErrorになる)。"""
    with pytest.raises(RuntimeError, match="init_logger"):
        cl.record({"provider": "azure"})


def test_e_main_installs_cost_logger_per_theme(tmp_path, monkeypatch):
    seen = []
    t1 = {"theme_id": "t1", "out_dir": str(tmp_path / "t1")}
    t2 = {"theme_id": "t2", "out_dir": str(tmp_path / "t2")}
    monkeypatch.setattr(n3.gen, "THEMES", [t1, t2])
    monkeypatch.setattr(n3, "run_theme", lambda theme: seen.append((theme["theme_id"], cl._LOG_PATH)))
    monkeypatch.setattr(sys, "argv", ["er003_v1_n3_01_tts_generate.py"])
    n3.main()
    assert seen == [("t1", f"{t1['out_dir']}/raw_usage_log.jsonl"), ("t2", f"{t2['out_dir']}/raw_usage_log.jsonl")]
    assert os.path.exists(f"{t1['out_dir']}/raw_usage_log.jsonl") and os.path.exists(f"{t2['out_dir']}/raw_usage_log.jsonl")


def test_e_secondary_call_records_cost_and_does_not_runtimeerror_after_install(tmp_path, monkeypatch):
    """main()と同じinstall後は、Secondary(Azure)呼出が`cl.record`で費用を記録し、RuntimeErrorで停止しない(統一judgeがPASS_WITH_WARNINGまで進む)。"""
    out_dir = tmp_path / "theme"
    t = {"theme_id": "t", "out_dir": str(out_dir)}
    monkeypatch.setattr(n3.gen, "THEMES", [t])
    wav = _wav(tmp_path)
    box = {}

    def azure(wav_path, language="en-US", phrases=None, **kw):
        # 本物の get_full_text_via_azure_stt_with_phrase_list と同じく、呼出後に cl.record で費用を記録する
        cl.record({"provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list", "model_id": "azure-speech-stt", "locale": language,
                   "attempt_number": 1, "success": True, "elapsed_seconds": 0.1, "usage_source": "LOCAL_WAV_HEADER_EXACT",
                   "audio_duration_submitted_seconds": 1.0, "phrase_list_size": len(phrases or [])})
        return CANON, None
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", azure)

    def run_theme(theme):
        box["d"] = sec.evaluate_attempt_with_cascade_detail(CANON, PRIMARY_NG, [], wav, language="en-US", cascade_enabled=True,
                                                            attempt_ctx={"slot": 1, "is_last_slot": False})
    monkeypatch.setattr(n3, "run_theme", run_theme)
    monkeypatch.setattr(sys, "argv", ["er003_v1_n3_01_tts_generate.py"])
    n3.main()
    d = box["d"]
    assert d["verified"] is True and d["asr_judgement"]["state"] == "PASS_WITH_WARNING"
    assert d["asr_judgement"]["secondary"]["called"] is True and not d["asr_judgement"]["secondary"].get("unavailable")
    lines = open(f"{out_dir}/raw_usage_log.jsonl", encoding="utf-8").read().strip().splitlines()
    assert len(lines) == 1 and '"provider": "azure"' in lines[0] and "LOCAL_WAV_HEADER_EXACT" in lines[0]


def test_e_no_new_pricing_entries_added():
    """新単価は追加しない(既存pricing_snapshotを使う)。pricing_snapshot.jsonがこの委任で変更されていないこと(git diff空)。"""
    import subprocess
    r = subprocess.run(["git", "diff", "--stat", "--", "er005_output/cost_baseline_01/pricing_snapshot.json"], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.abspath(__file__)))
    assert r.stdout.strip() == ""
