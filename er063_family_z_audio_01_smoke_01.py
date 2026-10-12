# -*- coding: utf-8 -*-
"""er063 smoke(実TTS、上限JPY3): Dialogue Voice切替確認として Advanced narrator 1 clip(Aoede, PD8)
+ dialogue(king=dionysius, Charon) 1 clip を短文で生成し、voice/modelが想定どおりかを実測する。
証跡: er063_output/family_z_audio_01/smoke_01/ (summary.json, cost_log.jsonl, mp3)。
TTS_EXECUTION_MODE=STANDARD(Standard同期)。.envは本script内でのみload_dotenv。"""
from __future__ import annotations

import glob
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er063_family_z_audio_01 as z  # noqa: E402

BUDGET_JPY = 3.0
OUT_ROOT = "er063_output/family_z_audio_01/smoke_01"
RUN = f"{OUT_ROOT}/melos/run_smoke"
NARRATOR_TEXT = "The sun was low in the sky, and Melos began to run toward the city."
KING_TEXT = '"You will never come back," said the king.'


def _summarize_existing_narrator(spec) -> dict:
    import soundfile as sf
    nd = z.narration_dir_for(RUN, "b1b")
    metas = []
    for p in sorted(glob.glob(f"{nd}/attempts/{spec.clip_id}_attempt*.json")):
        m = json.load(open(p, encoding="utf-8"))
        metas.append({k: m.get(k) for k in ("model", "voice", "tts_execution_mode", "tts_backend", "loop_attempt_index",
                                           "verified", "audio_classification", "asr_text")})
    lr = None
    for p in glob.glob("er011_output/local_rewrite_recovery/run_smoke/b1b/local_rewrite_recovery_full_story_part1_c1.json"):
        d = json.load(open(p, encoding="utf-8"))
        lr = {"status": d["status"], "ng_span": d["ng_span"]["canonical_span_with_context"], "asr_span": d["ng_span"]["asr_span_with_context"],
              "rewritten": d["selection"]["selected"]["rewritten_segment"]}
    wav = f"{nd}/{spec.clip_id}.wav"
    data, sr = sf.read(wav)
    mp3 = f"{OUT_ROOT}/narrator.mp3"
    sf.write(mp3, data, sr, format="MP3")
    return {"clip_id": spec.clip_id, "source": "existing artifacts of run 1", "voice_expected": spec.voice,
            "style_label": z.FAMILY_Z_ROLE_STYLE[spec.role_key]["style_label"],
            "style_prefix_sha256": z.style_prefix_sha256(z.style_text_for(spec)), "attempt_files_meta": metas,
            "local_rewrite": lr, "duration_seconds": round(len(data) / sr, 3), "mp3": mp3, "wav": wav}


def main() -> None:
    import soundfile as sf
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as x_runner  # compute_cost_jpy_so_far(読み取り専用)

    os.makedirs(OUT_ROOT, exist_ok=True)
    cost_log = f"{OUT_ROOT}/cost_log.jsonl"
    cl.install(cost_log)
    level = "b1b"
    plans = {
        "narrator": [z.ClipSpec("full_story_part1_c1", level, "narrator", NARRATOR_TEXT, voice=z.resolve_dialogue_voice("narrator"),
                                speaker="narrator", role_key=z.role_key_for("narrator", level), part=1)],
        "king": [z.ClipSpec("full_story_part1_c2", level, "dialogue", KING_TEXT, voice=z.resolve_dialogue_voice("dionysius"),
                            speaker="dionysius", role_key=z.role_key_for("dialogue", level), part=1)],
    }
    summary = {"budget_jpy": BUDGET_JPY, "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"), "clips": {}}
    for name, plan in plans.items():
        if name == "narrator" and "--narrator-from-artifacts" in sys.argv:
            # 1回目の実行でnarratorは生成済み(後続のLocal Rewrite再検証フックの不具合でresults保存前に停止)。
            # 再生成による追加課金を避け、既存artifact(attempts/*.json, LR json, cost_log)から証跡を集約する。
            summary["clips"][name] = _summarize_existing_narrator(plan[0])
            continue
        spent, _ = x_runner.compute_cost_jpy_so_far(cost_log)
        if spent >= BUDGET_JPY - 0.5:
            summary["clips"][name] = {"skipped": f"budget guard (spent={spent:.2f})"}
            continue
        # smoke専用: 原稿全文=この1文。Local Rewrite再検証はsmokeではmock(PASS)。実er061 anchorsは文単位smokeに不適
        out = z.run_tts_stage(RUN, level, plan, article_text=plan[0].text,
                              revalidate_fn=lambda text_before, text_after: {"verdict": "PASS", "note": "smoke-mock"})
        res = json.load(open(out["results_path"], encoding="utf-8"))
        e = res["segments"][plan[0].clip_id]
        wav = f"{z.narration_dir_for(RUN, level)}/{plan[0].clip_id}.wav"
        mp3 = f"{OUT_ROOT}/{name}.mp3"
        data, sr = sf.read(wav)
        sf.write(mp3, data, sr, format="MP3")
        attempt_meta = []
        for p in sorted(glob.glob(f"{z.narration_dir_for(RUN, level)}/attempts/{plan[0].clip_id}_attempt*.json")):
            m = json.load(open(p, encoding="utf-8"))
            attempt_meta.append({k: m.get(k) for k in ("model", "voice", "tts_execution_mode", "loop_attempt_index",
                                                       "verified", "audio_classification", "asr_text")})
        summary["clips"][name] = {
            "clip_id": plan[0].clip_id, "status": e["status"], "z_adoption": e["z_adoption"], "voice_expected": plan[0].voice,
            "voice_in_entry": e["voice"], "model_ids_measured_entry": e["model_ids_measured"], "style_label": e["style"]["instruction_label"],
            "style_prefix_sha256": e["style"]["style_prefix_sha256"], "fallback_used": e["style"]["fallback_used"],
            "attempts": len(e["attempts"]), "attempt_files_meta": attempt_meta, "asr_text": e.get("asr_text"),
            "duration_seconds": e.get("duration_seconds"), "mp3": mp3, "wav": wav,
            "cooldown_occurred": e["cooldown_occurred"], "local_rewrite": e["audio_text_deviation"]}
    spent, by_provider = x_runner.compute_cost_jpy_so_far(cost_log)
    models = {}
    if os.path.exists(cost_log):
        for line in open(cost_log, encoding="utf-8"):
            r = json.loads(line)
            key = f"{r.get('provider')}:{r.get('model_id') or r.get('model')}:seg={r.get('segment')}"
            models[key] = models.get(key, 0) + 1
    summary["cost_jpy_total"] = round(spent, 3)
    summary["cost_by_provider_jpy"] = {k: round(v, 3) for k, v in by_provider.items()}
    summary["cost_log_calls_by_model_segment"] = models
    with open(f"{OUT_ROOT}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if spent > BUDGET_JPY:
        print("BUDGET EXCEEDED", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
