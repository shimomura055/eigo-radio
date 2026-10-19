"""FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02 ③ 正式経路検証(offline、新規TTS 0)。

run_e2e_04 Std part3_c1 の『LR版(Melos->He)・減速前wav』を一時dirへcopyし、**修正後の正式関数**
`er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess`(ffmpeg 6%減速 -> 統一judgeで再検証)をそのまま実行する。
- 比較A(修正後=正式経路): result に LR採用記録を載せた状態 -> 書換え後の実送信文で照合されるはず(期待: PASS相当)。
- 比較B(修正前相当): result から LR記録を外した状態 -> 旧原稿(Melos入り)で照合される(旧実装と同じ参照先。期待: STOPPED)。
ASRは、減速後wavのsha256が実run(AH行15175)の減速後wavと一致する場合に限り、実runが保存済みの転写を再利用する(API 0)。
shaが一致しない場合のみ本物のASR(OpenAI、1呼出)を使い、その旨と概算費用を記録する(上限JPY10)。Azure呼出は遮断(呼ばれたら例外)。
本体run dir(--src-run)は読取のみ。HR Lock(review_lock_state.json)には触れない。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er006_asr_provider_routing_01 as routing  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402
import er003_v1_n3_01_tts_generate as tg  # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cached_post_slowdown(clip):
    path = "er011_output/attempt_history.jsonl"
    last = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if '"A2_SLOWDOWN_REVERIFY"' not in line or f"{clip}.wav" not in line or "run_e2e_04/a2" not in line:
                continue
            last = json.loads(line)
    return last


def run_case(label, work_root, clip, src_wav_original, result, cached_text, expected_slowed_sha):
    narr = os.path.join(work_root, label, "a2", "narration")
    os.makedirs(narr, exist_ok=True)
    wav = os.path.join(narr, f"{clip}.wav")
    shutil.copyfile(src_wav_original, wav)          # 減速前(LR版)をcopy。以降の減速・上書きは全てwork dir内
    api = {"openai_asr_calls": 0, "cached_transcript_used": False, "azure_calls": 0}

    def transcribe(path, language="en-US", **kw):
        got = sha(path)
        if got == expected_slowed_sha and cached_text:
            api["cached_transcript_used"] = True
            return cached_text, None
        api["openai_asr_calls"] += 1
        return routing.transcribe(path, language=language, **kw)

    def no_azure(*a, **k):
        api["azure_calls"] += 1
        raise RuntimeError("Azure call blocked by verify script")

    tg.routing.transcribe = transcribe
    sec.get_full_text_via_azure_stt_with_phrase_list = no_azure
    seen = []
    real = sec.evaluate_attempt_with_cascade_detail

    def spy(expected, *a, **k):
        seen.append(expected)
        return real(expected, *a, **k)

    sec.evaluate_attempt_with_cascade_detail = spy
    try:
        out = tg.apply_a2_slowdown_postprocess(clip, narr.replace("\\", "/"), result["canonical_text_before_local_rewrite"]
                                               if result.get("local_rewrite_recovery") else result["_canonical"], result)
    finally:
        sec.evaluate_attempt_with_cascade_detail = real
    return {
        "label": label, "status": out.get("status"), "asr_verified": out.get("asr_verified"),
        "post_slowdown_classification": out.get("post_slowdown_classification"),
        "post_slowdown_final_classification": out.get("post_slowdown_final_classification"),
        "post_slowdown_expected_text_source": out.get("post_slowdown_expected_text_source"),
        "expected_text_passed_to_judge": seen[0] if seen else None,
        "post_slowdown_asr_text": out.get("post_slowdown_asr_text"),
        "slowed_wav_sha256": sha(wav), "slowed_sha_equals_run04_wav": sha(wav) == expected_slowed_sha,
        "slowdown_info": out.get("slowdown_info"), "api": api,
        "asr_judgement_state": (out.get("asr_judgement") or {}).get("state"),
        "reason": out.get("reason"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-run", required=True)
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--clip", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    # Production stateを汚さない(telemetry no-op。Trial scriptの先例=er065_*と同じ方法)
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: None
    review_lock.append_attempt_history_event = lambda *x, **k: None

    src_narr = os.path.join(a.src_run, "a2", "narration")
    src_orig = os.path.join(src_narr, f"{a.clip}_original.wav")
    src_slow = os.path.join(src_narr, f"{a.clip}.wav")
    lock_path = os.path.join(a.src_run, "a2", "audit", "review_lock_state.json")
    before = {p: sha(p) for p in (src_orig, src_slow, lock_path)}

    run_name = os.path.basename(a.src_run.rstrip("/\\"))
    rec_path = f"er011_output/local_rewrite_recovery/{run_name}/a2/local_rewrite_recovery_{a.clip}.json"
    rec = json.load(open(rec_path, encoding="utf-8"))
    canonical = rec["canonical_text"]
    rewritten = rec["selection"]["selected"]["rewritten_segment"]
    cached = load_cached_post_slowdown(a.clip)
    cached_text = cached["post_slowdown_asr_text"] if cached else None
    slowed_sha = before[src_slow]

    lr_result = {"status": "OK", "text": rewritten, "sha256": None, "duration_seconds": 23.12,
                 "local_rewrite_recovery": rec, "canonical_text_before_local_rewrite": canonical, "fallback_used": True}
    base_result = {"status": "OK", "text": canonical, "sha256": None, "duration_seconds": 23.12, "_canonical": canonical}

    cases = [
        run_case("fixed_formal_path", a.work_dir, a.clip, src_orig, lr_result, cached_text, slowed_sha),
        run_case("pre_fix_equivalent_canonical_reference", a.work_dir, a.clip, src_orig, base_result, cached_text, slowed_sha),
    ]
    after = {p: sha(p) for p in before}
    fixed, prefix = cases
    verdict = {
        "fixed_passes_against_rewritten_text": fixed["status"] == "OK" and fixed["post_slowdown_expected_text_source"] == "local_rewrite_text",
        "pre_fix_equivalent_fails_against_canonical": prefix["status"] == "STOPPED",
        "run04_source_files_unchanged": before == after,
    }
    res = {
        "management_id": "FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02", "clip": a.clip,
        "canonical_text": canonical, "rewritten_text_actually_sent": rewritten,
        "cached_transcript_source": ("er011_output/attempt_history.jsonl A2_SLOWDOWN_REVERIFY(行15175相当)" if cached else None),
        "cases": cases, "verdict": verdict, "source_sha256_before": before, "source_sha256_after": after,
        "hr_lock_untouched": before[lock_path] == after[lock_path],
        "new_tts_calls": 0,
        "cost_note": "OpenAI ASR呼出数は cases[*].api.openai_asr_calls を参照(0ならAPI費用0)。Azure呼出は遮断(0)。",
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({"verdict": verdict, "fixed": {k: fixed[k] for k in ("status", "post_slowdown_classification", "post_slowdown_expected_text_source", "api")},
                      "pre_fix": {k: prefix[k] for k in ("status", "post_slowdown_classification", "api")}}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
