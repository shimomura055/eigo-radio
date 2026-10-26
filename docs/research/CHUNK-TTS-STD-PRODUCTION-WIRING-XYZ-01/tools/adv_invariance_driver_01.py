# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02 R4(b): Adv(b1b)のgenerate+assembleをmock生成器で実行し、
results json(正規化)・narration wav・合成wavのsha256を書き出す。旧commit(bb578265c)と現ツリーの両方で同一driverを走らせ、バイト一致を比較する。
API 0(外部接続はsetUpModuleで遮断)。使い方: .venv/Scripts/python.exe adv_invariance_driver_01.py --repo <tree root> --out <json>
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zlib
from unittest import mock

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
REPO = os.path.abspath(a.repo)
OUT = os.path.abspath(a.out)
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "netblock_harness_01"))
sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

VOLATILE = re.compile(r"(elapsed|_at$|^ts$|timestamp|created|duration_wall|started|finished|time$|date)", re.I)


def norm(obj, roots):
    if isinstance(obj, dict):
        return {k: norm(v, roots) for k, v in sorted(obj.items()) if not VOLATILE.search(k)}
    if isinstance(obj, list):
        return [norm(v, roots) for v in obj]
    if isinstance(obj, str):
        for r_ in roots:
            obj = obj.replace(r_, "<ROOT>").replace(r_.replace("\\", "/"), "<ROOT>")
        return obj
    return obj


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hj(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def seed_of(name):
    return zlib.crc32(name.encode("utf-8")) & 0xFFFFFFFF


def write_wav(path, name, n=3000):
    import er117_chunk_tts_production_01 as core
    rng = np.random.default_rng(seed_of(name))
    core.write_pcm16(path, (rng.normal(0, 0.05, n) * 32767).astype(np.int16))


# 外部接続を最初に遮断する(driverは実APIを呼ばない。初版でKP解説LLMが1回実呼出された教訓: 委任_02 COST_01参照)
import er121_family_y_runner_01_test_01 as yt  # noqa: E402
yt.setUpModule()

report = {"repo": REPO, "x_adv": {}, "y_adv": {}}

# ---------------------------------------------------------------- X Adv: generate + load/gain/timeline/assemble
import er003_v1_n3_01_assemble as asm  # noqa: E402
import er019_family_x_audio_production_runner_01 as runner  # noqa: E402

P1 = "Para one is short here.\n\nPara two has some more words in it.\n\nPara three ends the first part."
P2 = "Only one paragraph in the second part, so it is not split at all."
P3 = "Third part first paragraph here.\n\nThird part second paragraph here."
PARTS = {"title": "Sample Title", "title_tts": "Sample Title", "part1": P1, "part2": P2, "part3": P3, "in_one_line": "One line."}
SUPPORT = {"preview": "Preview text.", "comment_1": "Comment one.", "comment_2": "Comment two.", "comment_3": "Comment three.", "comment_4": "Comment four."}

tmp = tempfile.mkdtemp(prefix="advinv_x_")
d = os.path.join(tmp, "b1b")
os.makedirs(os.path.join(d, "narration"), exist_ok=True)
os.makedirs(os.path.join(d, "key_phrases"), exist_ok=True)
json.dump(PARTS, open(os.path.join(d, "parts.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(SUPPORT, open(os.path.join(d, "b1_support_texts.json"), "w", encoding="utf-8"))
json.dump({"items": []}, open(os.path.join(d, "key_phrases", "keywords_canonicalized.json"), "w"))


def wide(text, out, **k):
    name = os.path.basename(out)[:-4]
    write_wav(out, name)
    return {"status": "OK", "text": text, "path": out, "asr_verified": True, "voice": "Aoede", "tts_model_id": "m", "model": "m",
            "tts_backend": k.get("tts_backend"), "style_prefix": k.get("style_prefix_override") or "",
            "instruction_type": "english_style_prefix_wide_margin", "sha256": sha(out), "disfluency_checked": True}


def charon(text, out, **k):
    write_wav(out, os.path.basename(out)[:-4])
    return {"status": "OK", "canonical_text": text, "disfluency_checked": True, "text": text}


with mock.patch.object(runner.pnap_hooks.pnap, "is_enabled", return_value=False), \
     mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1", return_value={}), \
     mock.patch.object(runner.voice01, "generate_charon_english", side_effect=charon), \
     mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations", return_value={"items": {}, "audit": {"mock": True}}),      mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin", side_effect=wide):
    runner.generate_family_x_b1_segments(tmp, tts_backend="speech_metadata_flash_lite")

for nm in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five"):
    write_wav(f"{d}/narration/{nm}_charon.wav", nm)
res = json.load(open(f"{d}/audit/tts_generation_results.json", encoding="utf-8"))
rng = np.random.default_rng(7)
st = lambda n=48000: {"samples": rng.normal(0, 0.05, (n, 2))}
fixed = [st(), st(), st()]
with mock.patch.object(runner.asm, "verify_episode_audio_validation_gate", return_value=None), \
     mock.patch.object(runner.p9a, "load_and_resample_to_target", side_effect=fixed):
    src = runner.load_family_x_b1_sources(tmp)
parts = runner.apply_family_x_b1_gain(src)
seq = runner.build_family_x_b1_timeline(parts)
result = asm.assemble_with_timeline(seq)
ev_path = f"{d}/audit/chunk_tts_evidence_b1b.json"
report["x_adv"] = {
    "results_json_normalized_sha256": hj(norm(res, [tmp])),
    "results_json_normalized": norm(res, [tmp]),
    "narration_wav_sha256": {f: sha(f"{d}/narration/{f}") for f in sorted(os.listdir(f"{d}/narration"))},
    "chunk_plan_sha256": sha(f"{d}/audit/chunk_plan_b1b.json") if os.path.exists(f"{d}/audit/chunk_plan_b1b.json") else None,
    "chunk_tts_evidence_normalized_sha256": hj(norm(json.load(open(ev_path, encoding="utf-8")), [tmp])) if os.path.exists(ev_path) else None,
    "gain_report_sha256": hj(parts["gain_report"]),
    "assembled_sha256": hashlib.sha256(np.ascontiguousarray(result["assembled"]).tobytes()).hexdigest(),
    "assembled_shape": list(result["assembled"].shape),
    "timeline_sha256": hj(result["timeline"]),
}
shutil.rmtree(tmp, ignore_errors=True)

# ---------------------------------------------------------------- Y Adv: 正式runner(mock)で tts_b1b + assemble(1段落=不発火 / 複数段落=発火)
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_mock_01 as mk  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402

V2 = ("I wait all morning for the bell to ring, but the van never comes at that hour.\n\n"
      "When it finally comes, I am already late for work and I cannot open the door in time.")
CLOSING3 = ("Maybe the fee is only one small lever in a much larger system.\n\n"
            "Who decides when a parcel arrives, and who can really change that choice?\n\n"
            "What would you want from the service if you were the one waiting?")


@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def run_y(multi):
    root = tempfile.mkdtemp(prefix="advinv_y_")
    ctx = yt._ctx(root)
    with quiet():
        r.run_stages(ctx, ["seed_check", "text", "translate", "support"])
        yt._declare(ctx)
        r.run_stages(ctx, ["kp"])
    out = ctx.out_dir
    b = f"{out}/b1b"
    api = mk.MockApi(out)
    with mk.fake_tts(api), quiet():
        r.run_stages(ctx, ["tts_b1b"])
    if multi:
        pj = f"{b}/parts.json"
        parts = json.load(open(pj, encoding="utf-8"))
        parts["segments"]["y_voice_2"] = V2
        parts["segments"]["y_closing"] = CLOSING3
        json.dump(parts, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        for p_ in (f"{b}/audit/tts_generation_results.json", f"{b}/audit/chunk_plan_b1b.json"):
            if os.path.exists(p_):
                os.remove(p_)
        for sid in ys.Y_SEGMENT_IDS:
            w = f"{b}/narration/{sid}.wav"
            if os.path.exists(w):
                os.remove(w)
        with mk.fake_tts(mk.MockApi(out)), quiet():
            ya.generate_y_b1_segments(out, style_profile=r.STYLE_PROFILE)
    with open(r._level_text_path(ctx, "b1b"), encoding="utf-8") as f:
        article = ys.canonical_body(f.read())
    summ = {}
    try:
        with mk.fake_tts(mk.MockApi(out)), quiet():
            summ = ya.assemble_level(out, "b1b", style_profile=r.STYLE_PROFILE, slug="mock_slug", article_text=article)
    except Exception as exc:   # 旧/新で同じ例外になることも比較対象にする
        summ = {"status": "EXC:" + type(exc).__name__ + ":" + str(exc)[:200]}
    resj = json.load(open(f"{b}/audit/tts_generation_results.json", encoding="utf-8"))
    dec = json.load(open(f"{b}/audit/chunk_tts_decision.json", encoding="utf-8"))
    nd = f"{b}/narration"
    rec = {
        "assemble_status": summ.get("status"),
        "results_json_normalized_sha256": hj(norm(resj, [root, out])),
        "results_json_normalized": norm(resj, [root, out]),
        "narration_wav_sha256": {f: sha(f"{nd}/{f}") for f in sorted(os.listdir(nd)) if f.endswith(".wav")},
        "assembled_wav_sha256": sha(summ["out_path"]) if summ.get("out_path") and os.path.exists(summ["out_path"]) else None,
        "chunk_tts_decision": norm(dec, [root, out]),
        "gain_report_sha256": hj(norm(json.load(open(f"{b}/audit/gain_report.json", encoding="utf-8")), [root, out])) if os.path.exists(f"{b}/audit/gain_report.json") else None,
        "timeline_sha256": hj(norm(json.load(open(f"{b}/audit/timeline.json", encoding="utf-8")), [root, out])) if os.path.exists(f"{b}/audit/timeline.json") else None,
        "chunk_plan_sha256": sha(f"{b}/audit/chunk_plan_b1b.json") if os.path.exists(f"{b}/audit/chunk_plan_b1b.json") else None,
    }
    shutil.rmtree(root, ignore_errors=True)
    return rec


report["y_adv"]["single_paragraph"] = run_y(False)
report["y_adv"]["multi_paragraph"] = run_y(True)
json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("WROTE", OUT)
