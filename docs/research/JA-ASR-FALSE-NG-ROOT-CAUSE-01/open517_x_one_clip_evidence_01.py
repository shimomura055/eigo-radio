# OPEN-517 F1+F2 正式runtime発火証拠(Family X・日本語1〜2 clip)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_10 (ii)。
# Xの正式Production経路(er019 `_generate_or_reuse` + `n3_tts.generate_a2_japanese_with_reading_safety`[backend=speech_metadata_flash_lite、
# style=FAMILY_X_ROLE_STYLE_JA、X runnerのpreview/comment生成と同一引数] + secondary_run_scope + er109 family_scope("X"))で日本語clipを実生成し、
# judge artifact(asr_judgement)にF1/F2/R-5が残ることを確認する。runner全体は回さない。専用dir(--out-dir)にのみ書く。
# 実行: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_x_one_clip_evidence_01.py --out-dir er078_output/open517_runtime_evidence_01/x_one_clip_01 --approved-budget-jpy 5
import argparse, datetime, json, os, subprocess, sys

sys.path.insert(0, ".")

# 過去のX正式run(part2_hr_evidence_01__run_r2)で primary.equivalence_basis=READING_MATCH となった comment_3 / comment_2 の原稿(同一文面)
CLIPS = [
    ("ja_asr_ev_x_comment_3", "ここまでで、関税が始まる前から、豆不足と豆の価格上昇が起きていたことが分かりました。夏に始まった関税も、豆の価格を押し上げました。続いて、それぞれが店頭の値上がりにどう関わったのかを聞いていきましょう。"),
    ("ja_asr_ev_x_comment_2", "店のコーヒーの値上がりには、夏の関税より前に始まった豆不足が関係していました。では、そのころ豆の市場では何が起きていたのでしょうか。"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--approved-budget-jpy", type=float, default=5.0)
    ap.add_argument("--max-clips", type=int, default=1)
    a = ap.parse_args()
    started = datetime.datetime.now().astimezone()
    out = a.out_dir.replace("\\", "/")
    import er062_family_z_structure_01 as st
    st.check_stop_sentinel("open517_x_one_clip:start", out)
    st.record_launch_and_check_storm(out, sys.argv)
    st.acquire_run_lock(out, sys.argv)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
        import er005_cost_logger as cl
        cost_log = f"{out}/cost_log.jsonl"
        cl.install(cost_log)
        st.install_api_stop_guard()
        import er019_family_x_audio_production_runner_01 as xr
        import er003_v1_n3_01_tts_generate as n3_tts
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        import er078_secondary_run_scope_01 as sec_scope
        import er109_xz_scope_01 as er109_scope
        backend = xr.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND
        nd = f"{out}/a2/narration"
        os.makedirs(nd, exist_ok=True)
        os.makedirs(f"{out}/a2/audit", exist_ok=True)
        segments = {}
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

        @sec_scope.with_secondary_run
        @er109_scope.family_scope("X")
        def run_clips():
            for clip_id, text in CLIPS[: a.max_clips]:
                spent = xr.compute_cost_jpy_so_far(cost_log)[0]
                if spent >= a.approved_budget_jpy:
                    print(f"BUDGET_STOP spent={spent}")
                    break
                st.check_stop_sentinel(f"open517_x_one_clip:{clip_id}", out)
                wav = f"{nd}/{clip_id}.wav"
                with cl.segment_context(clip_id):
                    res = xr._generate_or_reuse(
                        None, clip_id, wav,
                        lambda text=text, wav=wav: n3_tts.generate_a2_japanese_with_reading_safety(
                            text, wav, n3_tts.expected_substring_ja(text),
                            style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA, tts_backend=backend), expected_text=text)
                segments[clip_id] = res
                aj = res.get("asr_judgement") if isinstance(res, dict) else None
                print(clip_id, res.get("status") if isinstance(res, dict) else None, (aj or {}).get("state"), (aj or {}).get("reason_code"),
                      ((aj or {}).get("primary") or {}).get("equivalence_basis"), "r5" in (aj or {}), "spent", xr.compute_cost_jpy_so_far(cost_log)[0])
                json.dump({"segments": segments, "management_id": "JA-ASR-FALSE-NG-ROOT-CAUSE-01", "level": "a2"},
                          open(f"{out}/a2/audit/tts_generation_results.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        run_clips()
        summary = {"started_at": started.isoformat(), "pid": os.getpid(), "git_head": head, "argv": sys.argv, "clips": [c[0] for c in CLIPS[: a.max_clips]],
                   "spent_jpy": xr.compute_cost_jpy_so_far(cost_log)[0], "finished_at": datetime.datetime.now().astimezone().isoformat()}
        json.dump(summary, open(f"{out}/evidence_summary.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        st.release_run_lock(out)


if __name__ == "__main__":
    main()
