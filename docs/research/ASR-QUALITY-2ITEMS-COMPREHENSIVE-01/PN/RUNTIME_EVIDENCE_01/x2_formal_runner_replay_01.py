# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS PN 委任_04 X-2(W-07予備策): **正式X runnerのTTS段関数 `generate_family_x_b1_segments`**(PNAP scope+RET構築hookのdecorator付き、`_ONLY_SEGMENTS`指定=`--only-segments`相当)を、
隔離run_dir(本dir配下の新規theme)で実行する。TTS合成のprimitive(`er002_common._call_tts_with_retry`)**だけ**を、保存済みの実誤読wav(pool_n8_airport_line `point_two`=Kristie Tse)の
PCMを返すstubに差し替える(=自然発火の運に依存しない)。それより下流は全て正式経路: 発話区間trim/ASR(OpenAI Primary、実API)/統一judge/Azure Secondary(実API)/cascade/retry/PNAP/RET/results書出/finally報告。
証拠区分=『正式runner関数+生成器(合成primitive)差し替え+実ASR』。CLI入口(`main()`のRisk Flagger等)は通らない(費用・無関係な前段を避けるため関数を直接呼ぶ)。
隔離: Master Audio Store/HR queue/Ledger upsertには書かない(HR queueはstub[件数のみ記録]、Stage1[Perplexity+Ledger upsert]はstub)。実音声は本dir配下theme内のみ。"""
import json
import os
import shutil
import sys
import time
import wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(HERE, "x2_run", "theme_n8")
if os.path.exists(THEME) and "--keep" not in sys.argv:
    shutil.rmtree(THEME)
os.makedirs(os.path.join(THEME, "b1b"), exist_ok=True)

import er005_cost_logger as cl
cl.install(os.path.join(THEME, "raw_usage_log.jsonl"))

import er002_common as common
import er006_secondary_asr_01 as sec
import er019_family_x_audio_production_runner_01 as x
import er103_proper_noun_alarm_policy_01 as pol
import er103_run_entity_table_01 as ret

HR = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
WAV = "er006_output/pool_pilot_01/pool_n8_airport_line/b1b/narration/point_two.wav"
rows = [json.loads(l) for l in open(HR, encoding="utf-8") if l.strip()]
row = next(r for r in reversed(rows) if r["wav_path"].replace(chr(92), "/") == WAV)
canon = row["canonical_text"]
json.dump({"title": "Airport line evidence", "part1": "Placeholder first part is not selected.", "part2": canon, "part3": "Placeholder third part is not selected.",
           "in_one_line": "Placeholder one line is not selected."}, open(os.path.join(THEME, "b1b", "parts.json"), "w", encoding="utf-8"))
json.dump({k: "Placeholder %s text, not selected." % k for k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4")},
          open(os.path.join(THEME, "b1b", "b1_support_texts.json"), "w", encoding="utf-8"))

with wave.open(WAV) as w:
    assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
    PCM = w.readframes(w.getnframes())
tts_calls = []


def stub_tts(call_fn, prompt, max_retry=2, sleep_fn=None, **kw):
    tts_calls.append(len(tts_calls) + 1)
    return PCM, 0, True, None


common._call_tts_with_retry = stub_tts
hr_calls, stage1_calls = [], []
sec._log_human_review = lambda d: hr_calls.append({"segment": d.get("segment_id"), "reason": d.get("reason") or d.get("review_reason")})
sec._resolve_unresolved_entity_for_review = lambda span: stage1_calls.append(span) or {"pronunciation_hint": "(stub: Ledger upsert/Perplexity not executed in isolated run)", "confidence": "stub", "sources": []}

x._ONLY_SEGMENTS = {"full_story_part2"}          # --only-segments full_story_part2 相当(main()と同じ代入)
t0 = time.time()
res = {"evidence_class": "formal_runner_function_with_tts_synthesis_primitive_replaced_by_stored_misread_wav", "wav": WAV, "canonical_text": canon[:200]}
with cl.logging_context("x2_ret_evidence", "tts"):
    out = x.generate_family_x_b1_segments(THEME, tts_backend=x.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND, style_profile="fx_20261017")
res["seconds"] = round(time.time() - t0, 1)
res["tts_stub_calls"] = len(tts_calls)
res["scope_after"] = pol.current_scope()
res["table_holder_after"] = ret.current_table()
tr = json.load(open(os.path.join(THEME, "b1b", "audit", "tts_generation_results.json"), encoding="utf-8"))
seg = tr["segments"]["full_story_part2"]
aj = seg.get("asr_judgement") or {}
res["segment"] = {"status": seg.get("status"), "reason": seg.get("reason"), "attempts": len(seg.get("attempts_log") or seg.get("standard_attempts_log") or []),
                  "final_status": seg.get("final_status"), "asr_state": aj.get("state"), "human_review_required": seg.get("human_review_required")}
pa = aj.get("pronunciation_alarm") or {}
res["pronunciation_alarm"] = {"entity_table": pa.get("entity_table"), "nouns": pa.get("nouns")}
res["alarm_records"] = [{"proper_noun": r.get("proper_noun"), "evidence": r["mismatch"].get("proper_noun_evidence"), "entity_table_basis": r.get("entity_table_basis"),
                        "primary": r["mismatch"].get("asr_primary"), "secondary": r["mismatch"].get("asr_secondary")} for r in aj.get("pronunciation_alarm_records") or []]
res["hr_stub_calls"] = hr_calls
res["stage1_stub_calls"] = stage1_calls
et = os.path.join(THEME, "audit", "entity_table.json")
saved = json.load(open(et, encoding="utf-8")) if os.path.exists(et) else None
res["entity_table_json"] = None if saved is None else {"schema": saved["schema"], "builder_version": saved["builder_version"], "status": saved["status"],
                                                      "raw": saved["raw"], "n_covered": len(saved["covered_text_sha256"]), "builds": saved["builds"]}
rep = os.path.join(THEME, "b1b", "audit", "operator_alarm_report.md")
res["operator_report_excerpt"] = open(rep, encoding="utf-8").read()[:3500] if os.path.exists(rep) else None
res["pronunciation_alarms_json_count"] = json.load(open(os.path.join(THEME, "b1b", "audit", "pronunciation_alarms.json"), encoding="utf-8")).get("count")
res["review_queue"] = "HR queue stubで捕捉した件数=%d(正式HR queueへは書込なし)" % len(hr_calls)
json.dump(res, open(os.path.join(HERE, "x2_formal_runner_replay_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: res[k] for k in ("seconds", "tts_stub_calls", "segment", "pronunciation_alarm", "hr_stub_calls", "stage1_stub_calls")}, ensure_ascii=False, default=str)[:3000])
