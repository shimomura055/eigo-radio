# OPEN-517 F1+F2 正式runtime発火証拠(Family Z・日本語1〜2 clip)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_09 (ii)。
# 目的: Zの正式Production経路(er063 `generate_or_reuse_z` + `real_generators()` -> er003 `generate_a2_japanese_with_reading_safety` -> er007 adapter -> er078 unified judge)で
#       日本語clipを実生成し、そのjudge artifact(asr_judgement)にF1/F2/R-5の記録が残ることを確認する。runner全体(Writer/KP/assemble等)は回さない。
# 範囲: 専用dir(--out-dir)だけに書く。他agentのrun dirには書かない。有料=TTS(Gemini) + ASR(OpenAI Primary)、必要時のみAzure Secondary。上限は--approved-budget-jpy(既定20円)。
# STOP: 起動前にstop_scope_check(別途)・STOPセンチネル確認・launch storm/RUN_LOCK(Zと同じ)。HR Lockに当たっても approved_by="user" は付けない(事実として記録)。
# 実行: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_z_one_clip_evidence_01.py --out-dir er078_output/open517_runtime_evidence_01/z_one_clip --approved-budget-jpy 20
import argparse, datetime, json, os, subprocess, sys, time

sys.path.insert(0, ".")

CLIPS = [
    ("ja_asr_ev_comment_1", "comment", "メロスは三日の期限までに、二十キロの道を走り抜きました。"),
    ("ja_asr_ev_comment_2", "comment", "王は八千人の民の前で、三人の約束を聞きました。"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--approved-budget-jpy", type=float, default=20.0)
    ap.add_argument("--max-clips", type=int, default=2)
    a = ap.parse_args()
    started = datetime.datetime.now().astimezone()
    out = a.out_dir.replace("\\", "/")
    import er062_family_z_structure_01 as st
    import er063_family_z_audio_01 as a63
    st.check_stop_sentinel("open517_z_one_clip:start", out)
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
        import er019_family_x_audio_production_runner_01 as x_runner
        gens = a63.real_generators()
        level = "a2"
        nd = a63.narration_dir_for(out, level)
        os.makedirs(nd, exist_ok=True)
        os.makedirs(f"{out}/{level}/audit", exist_ok=True)
        segments = {}
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        for clip_id, kind, text in CLIPS[: a.max_clips]:
            spent = x_runner.compute_cost_jpy_so_far(cost_log)[0]
            if spent >= a.approved_budget_jpy:
                print(f"BUDGET_STOP spent={spent} >= {a.approved_budget_jpy}")
                break
            st.check_stop_sentinel(f"open517_z_one_clip:{clip_id}", out)
            spec = a63.ClipSpec(clip_id=clip_id, level=level, kind=kind, text=text, voice="Aoede", speaker="narrator",
                                role_key=a63.role_key_for(kind, level), language="ja")
            wav = f"{nd}/{spec.wav_name()}"
            res = a63.generate_or_reuse_z(None, spec, wav, lambda s=spec, w=wav: gens[s.kind](s, w))
            entry = a63.build_entry(spec, wav, res)
            segments[clip_id] = entry
            aj = res.get("asr_judgement") if isinstance(res, dict) else None
            print(clip_id, res.get("status") if isinstance(res, dict) else None, (aj or {}).get("state"), (aj or {}).get("reason_code"),
                  "r5" in (aj or {}), "spent", x_runner.compute_cost_jpy_so_far(cost_log)[0])
            json.dump({"segments": segments, "management_id": "JA-ASR-FALSE-NG-ROOT-CAUSE-01", "level": level},
                      open(f"{out}/{level}/audit/tts_generation_results.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        summary = {"started_at": started.isoformat(), "pid": os.getpid(), "git_head": head, "argv": sys.argv, "clips": [c[0] for c in CLIPS[: a.max_clips]],
                   "spent_jpy": x_runner.compute_cost_jpy_so_far(cost_log)[0], "finished_at": datetime.datetime.now().astimezone().isoformat()}
        json.dump(summary, open(f"{out}/evidence_summary.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        st.release_run_lock(out)


if __name__ == "__main__":
    main()
