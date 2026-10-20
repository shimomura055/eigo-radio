# -*- coding: utf-8 -*-
"""1回限りのDEV確認script: Production関数(er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list)経由の
Azure呼出1回で、SDK診断ログ上の送信JSON dgi.bias が AZURE_PHRASE_LIST_WEIGHT(2.0)になることを確認する(約JPY1)。
Production関数は無改変で呼び、SpeechConfigにSpeech_LogFilenameだけ外から付与する(production codeへ診断を入れない)。"""
import argparse, json, os, sys
sys.path.insert(0, os.getcwd())
import azure.cognitiveservices.speech as speechsdk
import er005_cost_logger as cl
import er006_secondary_asr_01 as sec
import er084_azure_phraselist_weight_trial_01_lib as lib

ap = argparse.ArgumentParser()
ap.add_argument("--wav", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
log = os.path.join(os.environ.get("TEMP", "."), "plwp1_sdk_wire.log")
if os.path.exists(log):
    os.remove(log)
_orig = speechsdk.SpeechConfig
def _cfg(*args, **kw):
    c = _orig(*args, **kw)
    c.set_property(speechsdk.PropertyId.Speech_LogFilename, log)
    return c
speechsdk.SpeechConfig = _cfg
cl.init_logger(os.path.join(os.path.dirname(a.out), "wire_evidence_cost_log.jsonl"))
phrases = ["Melos"]
text, err = sec.get_full_text_via_azure_stt_with_phrase_list(a.wav, language="en-US", phrases=phrases)
ev = lib.extract_weight_evidence(log)
res = {"function": "er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list", "wav": a.wav,
       "phrases": phrases, "AZURE_PHRASE_LIST_WEIGHT": sec.AZURE_PHRASE_LIST_WEIGHT, "text_head": (text or "")[:120], "err": err,
       "sdk_prop_weight": ev.get("prop_weight"), "wire_bias": ev.get("wire_bias"), "wire_has_dgi": ev.get("wire_has_dgi"),
       "hits_head": ev.get("hits_head"), "PASS": [float(x) for x in (ev.get("wire_bias") or [])] == [float(sec.AZURE_PHRASE_LIST_WEIGHT)]}
json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("sdk_prop_weight", "wire_bias", "wire_has_dgi", "PASS", "err")}, ensure_ascii=False))
