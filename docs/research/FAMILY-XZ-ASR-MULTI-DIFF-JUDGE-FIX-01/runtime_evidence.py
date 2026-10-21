"""FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01 S5 runtime evidence (有料・最小、TTS生成なし)。
既存wavのコピー(隔離dir)に対し、Production判定関数 evaluate_attempt_with_cascade を Production既定
(force_secondary なし)で実ASR呼出して1回実行し、転写と判定ラベルをそのまま記録する。
隔離: wavは隔離dirへコピー(元の成果物dirのattempt_history等を変更しない)。human_review_queue/Ledger research/
semantic telemetryは隔離dirへ向ける(Production tracked fileを変更しない)。
使い方: .venv/Scripts/python.exe docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/runtime_evidence.py <x|z> <iso_dir>"""
import json, os, shutil, sys, time
sys.path.insert(0, os.getcwd())
which, iso = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(iso, exist_ok=True)
import er005_cost_logger as cl
cl.install(os.path.join(iso, "raw_usage_log.jsonl"))
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as s2
import er006_pronunciation_ledger_01 as pronun_ledger
import er021_en_asr_semantic_equivalence_production_01 as se
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er078_asr_unified_attempt_ctx_01 as attempt_ctx_mod
import er011_human_review_lock_01 as review_lock

s2.HUMAN_REVIEW_LOG_PATH = os.path.join(iso, "human_review_queue_isolated.jsonl")
captured_tel = []
se.append_telemetry_log = lambda rec: captured_tel.append(rec)
s2._resolve_unresolved_entity_for_review = lambda span: None  # 隔離: Ledger research(有料・永続化)を行わない

if which == "x":
    res = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json"
    src_wav = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/narration/attempts/full_story_part1_attempt1_englishstyleprefixwidemargin.wav"
    sid = "full_story_part1"
    canonical = json.load(open(res, encoding="utf8"))["segments"][sid]["canonical_text"]
    language, seg_arg = "en-US", sid
else:
    res = "er026_output/family_z_production_e2e_01/melos/run_e2e_06/b1b/audit/tts_generation_results.json"
    sid = "full_story_part1_c1"
    d = json.load(open(res, encoding="utf8"))["segments"][sid]
    canonical, src_wav = d["canonical_text"], d["path"] if os.path.exists(d["path"]) else "er026_output/family_z_production_e2e_01/melos/run_e2e_06/b1b/narration/%s.wav" % sid
    language, seg_arg = "en-US", None  # Family Z (er012) は segment_id を渡さない(既存呼出と同一)
wav = os.path.join(iso, os.path.basename(src_wav))
shutil.copyfile(src_wav, wav)

t0 = time.time()
max_len = len(canonical) + 15
asr_text, err = routing.transcribe(wav, language=language, prompt=None)
ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(canonical, min_confidence="low")]
detail = {}
cs_enabled = retry_primitive.connected_speech_enabled_for(sid)
verified_content, stop_retrying, cls = s2.evaluate_attempt_with_cascade(
    canonical, asr_text, [], wav, language=language, ledger_phrases=ledger_phrases,
    cascade_enabled=s2.FEATURE_FLAG_SECONDARY_ASR_ENABLED, enable_connected_speech_equivalence_layer=cs_enabled,
    detail_out=detail, segment_id=seg_arg,
    attempt_ctx=attempt_ctx_mod.build_attempt_ctx(1, review_lock.PRODUCTION_MAX_TTS_ATTEMPTS, max_len=max_len))
aj = detail.get("asr_judgement") or {}
out = dict(path=which, segment=sid, src_wav=src_wav, force_secondary=False, cascade_enabled=s2.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
           connected_speech_enabled=cs_enabled, primary_asr_error=err, primary_transcript=asr_text,
           verified_content=verified_content, stop_retrying=stop_retrying, classification=cls.classification,
           content_word_diffs=cls.protected.content_word_diffs, asr_judgement=aj, cascade_layers=(aj.get("adapter") or {}).get("layers"),
           ledger_phrases=ledger_phrases, elapsed_s=round(time.time() - t0, 1), telemetry_records=len(captured_tel))
json.dump(out, open(os.path.join(iso, "runtime_evidence_%s.json" % which), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("path", "classification", "verified_content", "stop_retrying", "cascade_layers", "elapsed_s")}, ensure_ascii=False))
print("PRIMARY:", asr_text)
print("STATE:", aj.get("state"), aj.get("reason_code"), "primary_label=", (aj.get("primary") or {}).get("label"),
      "secondary_called=", (aj.get("secondary") or {}).get("called"))
