# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: ¥0 evidence(API・生成なし)。
(1) Family X defaultのprofile選択: 新規out_dir(記録なし・CLI指定なし・run stateなし)で `--stage plan --dry-run`
    を実行し、style_profile.json / entry_point.json のprofileがn01に解決されること(Opus必須6: default選択はtestと¥0 dry-runで確認)。
    既存out_dir(run state有り・記録なし)でCLI未指定が課金前にSTOPすること、`--style-profile default`で従来どおりになること。
(2) Family Z mock: 新規run dirでnarrator styleがN01に解決・記録され、既存Z run dir(Melos run_e2e_02、読取りのみ)は
    narrator style label不一致で課金前STOPとなること(`inspect_run_narrator_style`、書込みなし)。
出力: er071_output/m2p0_n01_production_wiring_01/dry_run_default_profile_02.json, z_mock_check_02.json
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_n01_dryrun_and_z_mock_evidence_01.py"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import er019_family_x_style_profile_01 as sp  # noqa: E402
import er063_family_z_audio_01 as z  # noqa: E402

OUT = "er071_output/m2p0_n01_production_wiring_01"


def main():
    res = {"purpose": "defaultのprofile選択(新規out_dir->n01)の¥0確認", "cases": {}}
    tmp = tempfile.mkdtemp()
    env = dict(os.environ, PYTHONUTF8="1", TTS_EXECUTION_MODE="STANDARD")
    base = [sys.executable, "er019_family_x_audio_production_runner_01.py", "--slug", "coffee_prices", "--run", "run_v5_ms_01",
            "--stage", "plan", "--dry-run", "--budget-jpy", "80"]
    # case 1: 新規out_dir + 承認済みbackend + CLI未指定
    o1 = f"{tmp}/new_default"
    r = subprocess.run(base + ["--out-dir", o1, "--tts-backend", "speech_metadata_flash_lite"], capture_output=True, text=True, env=env)
    ep = json.load(open(f"{o1}/entry_point.json", encoding="utf-8"))
    rec = json.load(open(sp.record_path(o1), encoding="utf-8"))
    res["cases"]["new_out_dir_cli_unspecified"] = {"rc": r.returncode, "style_profile": ep.get("style_profile"),
                                                   "source": ep.get("style_profile_source"), "record_profile": rec["profile_id"],
                                                   "full_story_sha256": rec["roles"]["FULL_STORY"]["sha256"], "api_cost_jpy": 0}
    # case 2: 既存run state有り(記録なし) + CLI未指定 -> 課金前STOP
    o2 = f"{tmp}/old_run"
    os.makedirs(f"{o2}/a2/audit")
    open(f"{o2}/a2/audit/tts_generation_results.json", "w").write("{}")
    r = subprocess.run(base + ["--out-dir", o2, "--tts-backend", "speech_metadata_flash_lite"], capture_output=True, text=True, env=env)
    res["cases"]["existing_run_state_cli_unspecified"] = {"rc": r.returncode, "stopped_before_any_write": not os.path.exists(sp.record_path(o2)),
                                                          "stderr_tail": r.stderr.strip().splitlines()[-1][:300] if r.stderr.strip() else None}
    # case 3: 同上 + --style-profile default 明示 -> 従来どおり
    r = subprocess.run(base + ["--out-dir", o2, "--tts-backend", "speech_metadata_flash_lite", "--style-profile", "default"],
                       capture_output=True, text=True, env=env)
    ep3 = json.load(open(f"{o2}/entry_point.json", encoding="utf-8"))
    res["cases"]["existing_run_state_explicit_default"] = {"rc": r.returncode, "style_profile_key_absent_in_entry_point": "style_profile" not in ep3,
                                                           "record_created": os.path.exists(sp.record_path(o2))}
    # case 4: legacy backend(未指定)+ 新規out_dir -> default(N01はflash-lite必須)
    o4 = f"{tmp}/legacy"
    r = subprocess.run(base + ["--out-dir", o4], capture_output=True, text=True, env=env)
    ep4 = json.load(open(f"{o4}/entry_point.json", encoding="utf-8"))
    res["cases"]["new_out_dir_legacy_backend"] = {"rc": r.returncode, "style_profile_key_absent_in_entry_point": "style_profile" not in ep4,
                                                  "tts_backend": ep4.get("tts_backend")}
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump(res, open(f"{OUT}/dry_run_default_profile_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))

    # ---- Family Z mock(読取りのみ・生成なし) ----
    zres = {"purpose": "Family Z narrator N01配線のmock(課金0・生成なし・Z記事再生成STOP維持)", "z_style_table": {}, "melos_run_e2e_02_readonly": {}}
    rep = z.assert_style_table_integrity()
    zres["z_style_table"] = {"N01_sha256": rep["N01"], "NARRATOR_FULL_STORY_ADV": z.expected_narrator_style("b1b"),
                             "NARRATOR_FULL_STORY_STD": z.expected_narrator_style("a2"),
                             "std_text_contains_a2_slow_instruction": "Speak at a slightly slower" in z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"]}
    base_dir = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
    for level in ("a2", "b1b"):
        ld = f"{base_dir}/{level}"
        cached = z.load_results(ld)
        info = z.inspect_run_narrator_style(ld, level, cached)
        zres["melos_run_e2e_02_readonly"][level] = {"status": info["status"], "n_mismatch": len(info.get("mismatches", [])),
                                                    "sample": info.get("mismatches", [])[:2]}
    json.dump(zres, open(f"{OUT}/z_mock_check_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(zres, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
