# -*- coding: utf-8 -*-
"""P2(有料・少額): (a)実TTSが綴りどおりの語をどう読むか(各語2サンプル) (b)制御読み(合理的な読み1+明確な誤発音2)を3語。
TTS=gemini-3.8-flash-lite-tts(Charon。現行Family Xの標準モデル。呼出は低水準callのみ=Review Lock/Master Audio Storeを経由しない)、TTS_EXECUTION_MODE=STANDARD同期。
ASR=Production Primary(routing.transcribe)・Azure(p4)・ローカルWhisper small/medium。判定は replay の EXT/V4 の許可集合を再利用(Trial内比較のみ)。
費用は paid_calls.jsonl に追記(単価の出典つき。出典未確認の単価は上限見積とし明記)。再実行しない。"""
import json, os, sys, time
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_replay as RP
import er100_pnps_stage2_trial_01_attempts_lib as AL   # 共通: Whisper遅延ロード

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p7a_audio as p7a
import er003_b1_p9a_audio as p9a
import er003_b1_p4_audio as p4
import er006_asr_provider_routing_01 as routing

import er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1 as ST1
import er033_tts_flash_lite_family_x_styles_01 as FXS
MODEL = "gemini-3.8-flash-lite-tts"
STYLE = FXS.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]
VOICE = "Charon"
P2DIR = Path(OUT) / "p2_audio"
LEDGER = Path(OUT) / "paid_calls.jsonl"
# 単価(USD)。出典: pricing_snapshot.json(gemini-3.8-flash-lite-tts text入力0.5/M tokens, 音声出力6.0/M tokens[25 tokens/sec]); Azure STT $1.0/audio_hour(同snapshot, Azure Retail Prices API)
# gpt-4o-mini-transcribe は snapshotがtoken単価(入力1.25/出力5.0 per M)のみで音声1秒当たりtoken数が未確認 -> 秒数ベースの上限見積 USD0.006/min を使用(whisper-1公表単価。未確認につき『上限見積』)
USD_JPY = 160.0
SENT = {
    "khaite": "Khaite is a luxury fashion label known for its elevated basics.",
    "meink": "Troy Meink is the United States Secretary of the Air Force.",
    "altuzarra": "Joseph Altuzarra launched his brand, Altuzarra, back in 2008.",
}
CONTROLLED = {   # word -> [(tag, respelled_text)]
    "khaite": [("reasonable", "Kate is a luxury fashion label known for its elevated basics."), ("wrong1", "Kite is a luxury fashion label known for its elevated basics."), ("wrong2", "Kay-tee is a luxury fashion label known for its elevated basics.")],
    "meink": [("reasonable", "Troy Meenk is the United States Secretary of the Air Force."), ("wrong1", "Troy Mink is the United States Secretary of the Air Force."), ("wrong2", "Troy May-ink is the United States Secretary of the Air Force.")],
    "altuzarra": [("reasonable", "Joseph Ahl-too-ZAH-rah launched his brand, Ahl-too-ZAH-rah, back in 2008."), ("wrong1", "Joseph Al-tuh-ZAIR-ah launched his brand, Al-tuh-ZAIR-ah, back in 2008."), ("wrong2", "Joseph Alt-oo-zarr launched his brand, Alt-oo-zarr, back in 2008.")],
}


def ledger_add(rec):
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def tts(text, out_wav, tts_call):
    prompt = text   # Family X現行経路と同じ: 本文verbatim + speech_metadata.style(FULL_STORY)
    t0 = time.time()
    raw = tts_call(text, STYLE)
    samples, _sr, _hdr = ST1.decode_audio_bytes_defensive(raw)
    trimmed, info = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.EN_TRIM_SAFETY_MARGIN_SECONDS)
    use = trimmed if trimmed is not None else samples
    common.write_wav_float(str(out_wav), use, common.SAMPLE_RATE, 1)
    sec = len(use) / common.SAMPLE_RATE
    out_tokens = len(samples) / common.SAMPLE_RATE * 25
    in_tokens = max(1, int(len(prompt) / 4))
    usd = (in_tokens * 0.5 + out_tokens * 6.0) / 1e6
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "p2_tts", "model": MODEL, "voice": VOICE, "wav": str(out_wav), "sec": round(sec, 2), "est_in_tokens": in_tokens, "est_out_tokens": round(out_tokens),
                "cost_jpy": round(usd * USD_JPY, 4), "basis": "pricing_snapshot.json gemini-3.8-flash-lite-tts 0.5/6.0 USD per M tokens(25 tok/s); in_tokens=len/4の概算", "fx": "USD_JPY=160(project default)", "elapsed_s": round(time.time() - t0, 1)})
    return sec


def asr_all(wav, sec):
    out = {}
    pt, perr = routing.transcribe(str(wav), "en-US")
    out["primary"] = pt
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "p2_asr_openai", "model": "gpt-4o-mini-transcribe", "wav": str(wav), "sec": round(sec, 2), "cost_jpy": round(sec / 60 * 0.006 * USD_JPY, 4), "basis": "上限見積 USD0.006/min(単価未確認につき上限)", "err": perr})
    at, aerr = p4.get_full_text_via_azure_stt_continuous(str(wav), language="en-US", timeout_seconds=90)
    out["azure"] = at
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "p2_asr_azure", "wav": str(wav), "sec": round(sec, 2), "cost_jpy": round(sec / 3600 * 1.0 * USD_JPY, 5), "basis": "pricing_snapshot Azure STT S1 $1.0/audio_hour", "err": aerr})
    for sz in ("small", "medium"):
        out["whisper_" + sz] = AL.whisper(sz, str(wav))
    return out


def verdict(word, canon, asr, arm_sets):
    res = {}
    for arm, accset in arm_sets.items():
        obs = []
        for k, txt in asr.items():
            sp = asr_span(canon, txt, word)
            lab, det = RP.obs_verdict(word, sp, accset)
            obs.append((k, lab, det))
        prod = [l for k, l, _ in obs if k in ("primary", "azure")]
        if not accset:
            v = "HR_MAINTAINED(推定不成立)"
        elif prod and all(l in ("MATCH", "EXACT") for l in prod) and "MATCH" in prod:
            v = "PASS_WITH_WARNING"
        elif "MISMATCH" in prod and "OOV" not in prod:
            v = "NG"
        else:
            v = "HR_MAINTAINED(判定不能)"
        res[arm] = {"verdict": v, "obs": obs}
    return res


def main():
    est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
    r0 = json.load(open(f"{OUT}/r0_extractions.json", encoding="utf-8"))
    S = RP.build_sets(est, r0)
    A = {w: RP.accepted(w, S[w]) for w in TARGETS}
    P2DIR.mkdir(parents=True, exist_ok=True)
    tts_call = ST1.make_tts_call_fn(MODEL, VOICE)
    items = []
    # (a) 綴りどおり x 2サンプル(7語)
    for w in TARGETS:
        sent = est[w]["sentence"]
        for n in (1, 2):
            items.append({"set": "a_natural", "word": w, "tag": f"natural{n}", "tts_text": sent, "canon": sent})
    # (b) 制御読み
    for w, lst in CONTROLLED.items():
        for tag, text in lst:
            items.append({"set": "b_controlled", "word": w, "tag": tag, "tts_text": text, "canon": SENT[w]})
    for it in items:
        wav = P2DIR / f"{it['set']}_{it['word']}_{it['tag']}.wav"
        sec = tts(it["tts_text"], wav, tts_call)
        asr = asr_all(wav, sec)
        it.update(wav=str(wav), sec=round(sec, 2), asr=asr, verdicts=verdict(it["word"], it["canon"], asr, {"V4": A[it["word"]]["V4"], "EXT": A[it["word"]]["EXT"], "DIAG_UNION": A[it["word"]]["DIAG_UNION"]}))
        print(it["set"], it["word"], it["tag"], {k: v["verdict"] for k, v in it["verdicts"].items()}, {k: v for k, v in asr.items()}, flush=True)
        json.dump(items, open(f"{OUT}/p2_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = sum(json.loads(l)["cost_jpy"] for l in open(LEDGER, encoding="utf-8") if l.strip() and "cost_jpy" in json.loads(l))
    print("paid_calls total jpy (cumulative incl. E3)", round(total, 3))


if __name__ == "__main__":
    main()
