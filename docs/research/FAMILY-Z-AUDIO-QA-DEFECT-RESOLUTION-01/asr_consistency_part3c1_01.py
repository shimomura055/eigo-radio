# 委任_01: 既存wavに対する既存ASR経路のみの再転写(新規TTS 0 / LLM 0)。1回起動のみ。
#  Primary=er006_asr_provider_routing_01.transcribe(OpenAI gpt-4o-mini-transcribe, prompt無し) を各wav1回
#  Secondary=er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list を PhraseListあり(Production同条件=Ledger canonical_spelling) 3wav各1回
#            + PhraseListなし 1wav(att2)1回(PhraseListの効果切り分け)
# 費用: Azure=pricing_snapshot.json(USD1.0/audio hour, 160JPY/USD) x 実音声秒数(推定値、実請求は未確認)。OpenAIは別途概算を記載。
# 実行: .venv\Scripts\python.exe -X utf8 <this file> --out <json>   (cwd=repo root)
import sys, os, json, argparse, hashlib, re
sys.path.insert(0, os.getcwd())
import soundfile as sf
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er006_pronunciation_ledger_01 as pl
import er005_cost_logger
er005_cost_logger.init_logger('docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/asr_consistency_part3c1_01_cost_log.jsonl')  # 実費記録は本調査専用ログ(run cost_logを汚さない)
B = "er026_output/family_z_production_e2e_01/melos"
WAVS = {
 "run04_att2": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt2_customa3c4625e.wav",
 "run04_att3": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt3_minimalfallback.wav",
 "run03_att1_PASS_pre_slowdown": f"{B}/run_e2e_03/a2/narration/attempts/full_story_part3_c1_attempt1_customa3c4625e.wav",
}
CANON = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
         "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
         "then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword "
         "was already raised above his friend.")
AZ_PL_RUNS = ["run04_att2", "run04_att3", "run03_att1_PASS_pre_slowdown"]
AZ_NOPL_RUNS = ["run04_att2"]
USD_PER_HOUR, JPY_PER_USD = 1.0, 160.0
def name_window(t):
    m = re.search(r"rock\.\s*(.{0,28})", t or "")
    return m.group(1) if m else None
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
phrases = [h["canonical_spelling"] for h in pl.get_hint_for_text(CANON, min_confidence="low")]
out = {"phrase_list_used_in_PL_runs": phrases, "runs": {}}
cost_s = 0.0
for k, p in WAVS.items():
    dur = sf.info(p).duration
    rec = {"path": p, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(), "duration_s": round(dur, 2)}
    t, err = routing.transcribe(p, language="en-US"); rec["primary_openai"] = {"text_name_window": name_window(t), "text": t, "err": err}
    if k in AZ_PL_RUNS:
        t, err = sec.get_full_text_via_azure_stt_with_phrase_list(p, language="en-US", phrases=phrases)
        rec["azure_with_phraselist"] = {"name_window": name_window(t), "text": t, "err": err}; cost_s += dur
    if k in AZ_NOPL_RUNS:
        t, err = sec.get_full_text_via_azure_stt_with_phrase_list(p, language="en-US", phrases=None)
        rec["azure_no_phraselist"] = {"name_window": name_window(t), "text": t, "err": err}; cost_s += dur
    out["runs"][k] = rec
    print(k, "OpenAI:", rec["primary_openai"]["text_name_window"], "| AzurePL:", (rec.get("azure_with_phraselist") or {}).get("name_window"), "| AzureNoPL:", (rec.get("azure_no_phraselist") or {}).get("name_window"))
out["cost"] = {"azure_audio_seconds": round(cost_s, 2), "azure_jpy_estimate": round(cost_s / 3600 * USD_PER_HOUR * JPY_PER_USD, 3),
               "openai_calls": len(WAVS), "openai_jpy_estimate": "約0.1/call(トークン実測245in/82out=run_04 cost_log行196、pricing_snapshot 1.25/5.0 USD per 1M tokens x160=約0.1)",
               "source": "er005_output/cost_baseline_01/pricing_snapshot.json (azure USD1.0/audio hour; openai gpt-4o-mini-transcribe tokens)", "note": "推定。実請求は未確認"}
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["cost"])
