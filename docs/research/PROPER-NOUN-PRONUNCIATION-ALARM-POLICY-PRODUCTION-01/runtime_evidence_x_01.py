# -*- coding: utf-8 -*-
"""PNAP 委任_02 runtime evidence (X): Family X正式runnerのTTS段関数 generate_family_x_b1_segments を、新run dir・--only-segments相当
(_ONLY_SEGMENTS)で**1回だけ**実行する。runner mainのscaffold/RF(Risk Flagger)/assembleは費用・副作用(review_queue書込)回避のため含めない
(RF/scaffoldは固有名詞アラームと無関係)。TTS段の関数・decorator(secondary_run_scope/in_one_line_scope/pnap_hooks.family_scope)・
Production判定器・Master Audio Store・Ledgerは全て正式のもの。再起動なし。
使い方: python runtime_evidence_x_01.py <out_dir> <segments(カンマ区切り)>"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from dotenv import load_dotenv

load_dotenv()
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import er005_cost_logger as cl
import er019_family_x_audio_production_runner_01 as r
import er103_proper_noun_alarm_policy_01 as pnap

out_dir = sys.argv[1]
segs = {s.strip() for s in sys.argv[2].split(",") if s.strip()}
r._ONLY_SEGMENTS = segs
pid, src = r.style_profile_mod.resolve_run_profile(out_dir, None, write=False, tts_backend=r.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND)
r.style_profile_mod.assert_profile_backend(pid, r.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND)
pid, src = r.style_profile_mod.resolve_run_profile(out_dir, None, write=True, tts_backend=r.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND)
print("style_profile", pid, src, "pnap_enabled", pnap.is_enabled(), "scope_before", pnap.current_scope(), flush=True)
cl.install(f"{out_dir}/raw_usage_log.jsonl")
with cl.logging_context("pnap_evidence_01", "tts"):
    res = r.generate_family_x_b1_segments(out_dir, tts_backend=r.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND, style_profile=pid)
print(json.dumps(res, ensure_ascii=False, indent=1))
print("scope_after", pnap.current_scope())
final_jpy, by_provider = r.compute_cost_jpy_so_far(f"{out_dir}/raw_usage_log.jsonl")
print("cost_jpy", round(final_jpy, 2), by_provider)
