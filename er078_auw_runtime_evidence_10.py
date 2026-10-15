# -*- coding: utf-8 -*-
"""AUW 委任_10: U1是正(JA C1固有名詞差・類似度<0.4の事前除外撤廃)のRegression実音声evidence。

  saved_azure : 保存済みwav(reuse)に対し、保存済みPrimary転写(reuse)+live Azure(fresh)で統一JA adapter
                (er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail)を実行する。TTS・OpenAIは呼ばない。
  neg_control : 誤った文面をTTS(synthetic)→live Primary(OpenAI)→live Azure→統一JA adapterを、正しい原稿に対して実行する。
                期待=全件NG(PASS/PASS_WITH_WARNINGが1件でも出れば条件付きSTOP s1)。

有料APIは --execute 指定時のみ。1partにつき1回のみ実行(再起動・自動再試行・監督ループなし)。
Guardrail: --budget-jpy(ledger累計の見積費用がこれを超える見込みなら新規API呼出をせず停止)。STOP: <out>/STOP と stop_scope_check_01。
書込先: <out> 配下のみ(隔離)。shared state(下記)はrun前後のsha256を記録して差分を報告する。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_10.py <saved_azure|neg_control> --out <dir> --budget-jpy 12 [--execute]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

MANAGED_ID = "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01"
AZURE_JPY_PER_SEC = 1.0 / 3600.0 * 160.0      # $1.0/hour x 160 JPY/USD(秒切上げ)
TTS_JPY_PER_CLIP = 0.062                        # RUNTIME_EVIDENCE_06.md:113,320
OPENAI_ASR_JPY_PER_SEC = 0.003 / 60.0 * 160.0   # 概算(gpt-4o-mini-transcribe $0.003/min)

SHARED_STATE = [
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er011_output/attempt_history.jsonl",
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    "er007_output/ja_asr_cascade_01/human_review_queue.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
]

# ---- saved_azure の対象(保存wav + 保存Primary転写 + 原稿)。before=保存時のjudge状態 ----
M = "er026_output/family_z_production_e2e_01/melos"
E6B = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/ja_hr/run/a2/narration/attempts"
SAVED = [
    dict(id="S1_melos_title_hangul_a3", wav=f"{M}/run_e2e_01/a2/narration/attempts/japanese_title_attempt3_customb8f0ff16.wav",
         canon="走れメロス", primary="시리에 매우스", before="NG_EXCLUDED(similarity_lt_0.4:0.0)", u1="A5", s2=True),
    dict(id="S2_melos_title_hangul_c5bk", wav=f"{M}/cs_audit_01/pre_regen_c5_backup/attempts_all_pre/japanese_title_attempt1_customb8f0ff16.wav",
         canon="走れメロス", primary="가시 레메로스", before="NG_EXCLUDED(similarity_lt_0.4:0.0)", u1="A5", s2=True),
    dict(id="S3_akb48_title", wav="er005_output/cost_baseline_01/akb48/a2/narration/japanese_title.wav",
         canon="AKB48の新曲『好きish』、伊藤百花が2作連続センター、近藤沙樹が初選抜",
         primary="AKB48の新曲「月光シッシュ」伊藤ひょうかが2作連続センター。近藤さやかが初選抜。", before="NG_EXCLUDED(A6_C1_PROPER_NOUN_DIFF)", u1="A6"),
    dict(id="S4_hr_comment1_minfb_a3", wav=f"{E6B}/comment_1_attempt3_minimalfallback.wav",
         canon="合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。",
         primary="合い言葉は、ブルルクル、グロルップ、ブンムプ、フヌクです。", before="NG_EXCLUDED(A6_C1_PROPER_NOUN_DIFF entity_like)", u1="A6"),
    dict(id="S5_hr_comment1_a1", wav=f"{E6B}/comment_1_attempt1_custom99dc82e9.wav",
         canon="合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。",
         primary="合言葉は、ブルルクルグルルプ、ブンムプフヌクです。", before="ASR_VALIDATION_UNCERTAIN(Primary NG, P3 Secondary)", u1="-"),
    dict(id="S6_hr_comment1_a2", wav=f"{E6B}/comment_1_attempt2_custom99dc82e9.wav",
         canon="合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。",
         primary="合い言葉は、ブルルクル、グロルプ、ブンムプ、フヌクです。", before="ASR_VALIDATION_UNCERTAIN(Primary NG, P3 Secondary)", u1="-"),
    dict(id="S7_melos_title_pass_a2", wav=f"{M}/run_e2e_01/a2/narration/attempts/japanese_title_attempt2_customb8f0ff16.wav",
         canon="走れメロス", primary="走れメロス", before="PASS(Primary EXACT)", u1="-"),
    dict(id="S8_melos_title_c5bk_a2", wav=f"{M}/cs_audit_01/pre_regen_c5_backup/attempts_all_pre/japanese_title_attempt2_customb8f0ff16.wav",
         canon="走れメロス", primary="はしれメロス", before="PHONETIC_MATCH(Primary PASS)", u1="-"),
]

# ---- neg_control: (id, 原稿(正), TTSで読ませる誤文面, expected_readings, 狙い) ----
NEG = [
    ("N1_gas_to_kasu", "ガス会社に連絡してください。", "カス会社に連絡してください。", None, "カタカナ1字(ガス→カス)=entity_like解放クラス"),
    ("N2_meta_spelled", "Metaが新しい発表をしました。", "エムイーティーエーが新しい発表をしました。", {"meta": "メタ"}, "辞書登録Latin語の綴り読み=A7"),
    ("N3_meta_methane", "Metaが新しい発表をしました。", "メタンが新しい発表をしました。", {"meta": "メタ"}, "辞書登録Latin語の別語=A7"),
    ("N4_short_word", "橋を渡ります。", "箸を渡ります。", None, "短語の別語(同音異義の別語)"),
    ("N5_name_one_char", "走れメロス", "走れメロン", None, "固有名詞の一文字違い"),
    ("N6_person_name", "山田太郎さんが来ました。", "山田次郎さんが来ました。", None, "人名の一文字違い"),
    ("N7_number", "店は午後三時に開きます。", "店は午後五時に開きます。", None, "数値差=P1維持の確認"),
    ("N8_negation", "これは安全ではありません。", "これは安全です。", None, "否定差=P1維持の確認"),
]


def sha256_file(p):
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def wav_seconds(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


class Ledger:
    def __init__(self, out, budget):
        self.path = os.path.join(out, "cost", "spend_ledger.jsonl")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.budget, self.total, self.out = budget, 0.0, out

    def check(self, est, what):
        if os.path.exists(os.path.join(self.out, "STOP")):
            raise SystemExit(f"STOP sentinel present: {self.out}/STOP (新規API呼出なし)")
        if self.total + est > self.budget:
            raise SystemExit(f"Guardrail JPY {self.budget} 超過見込み({self.total:.3f}+{est:.3f}) before {what}: 新規API呼出なしで停止")

    def add(self, kind, jpy, **kw):
        self.total += jpy
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind, "est_jpy": round(jpy, 4),
                                "cum_jpy": round(self.total, 4), **kw}, ensure_ascii=False) + "\n")


def stop_scope_check(out):
    p = os.path.join(out, "stop_check.json")
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", out, "--out", p])
    if r.returncode != 0:
        raise SystemExit(f"stop_scope_check rc={r.returncode}: 新規API呼出をせず停止")


def snap_shared():
    return {p: sha256_file(p) for p in SHARED_STATE}


def init_cost_logger(out):
    import er005_cost_logger as cl
    cl.init_logger(os.path.join(out, "cost", "usage_log.jsonl"))


def judge_one(canon, primary, wav, expected_readings=None):
    import er007_ja_secondary_asr_01 as ja
    d = ja.evaluate_attempt_ja_with_cascade_detail(canon, primary, wav, cascade_enabled=True, length_ok=True,
                                                   expected_readings=expected_readings,
                                                   attempt_ctx={"slot": 1, "is_last_slot": False, "segment_key": os.path.basename(wav)})
    aj = d.get("asr_judgement") or {}
    sec = aj.get("secondary") or {}
    return {"state": aj.get("state"), "reason_code": aj.get("reason_code"), "exclusion_rule": aj.get("exclusion_rule"),
            "verified": bool(d.get("verified")), "warnings": aj.get("warnings"), "secondary_called": bool(sec.get("called")),
            "secondary_text": sec.get("text"), "secondary_label": sec.get("label"), "secondary_error": sec.get("error"),
            "technical_stop": d.get("technical_stop"), "scg_result": d.get("scg_result"),
            "azure_real_calls": (aj.get("adapter") or {}).get("azure_real_calls"),
            "final_status": d.get("final_status")}


def run_saved_azure(out, execute, budget):
    os.makedirs(out, exist_ok=True)
    stop_scope_check(out)
    led = Ledger(out, budget)
    plan = []
    for s in SAVED:
        ok = os.path.exists(s["wav"])
        plan.append({"id": s["id"], "wav": s["wav"], "exists": ok, "sec": round(wav_seconds(s["wav"]), 2) if ok else None,
                     "est_azure_jpy_max": round(math.ceil(wav_seconds(s["wav"])) * AZURE_JPY_PER_SEC, 4) if ok else None})
    res = {"part": "saved_azure", "execute": execute, "budget_jpy": budget, "plan": plan, "rows": []}
    print(json.dumps(plan, ensure_ascii=False, indent=1))
    if not execute:
        json.dump(res, open(os.path.join(out, "result_dry.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return
    init_cost_logger(out)
    before = snap_shared()
    trans = 0
    for s in SAVED:
        sec_s = wav_seconds(s["wav"])
        led.check(math.ceil(sec_s) * AZURE_JPY_PER_SEC, s["id"])
        r = judge_one(s["canon"], s["primary"], s["wav"])
        if r["secondary_called"]:
            led.add("azure_stt", math.ceil(sec_s) * AZURE_JPY_PER_SEC, id=s["id"])
        trans_flag = (r["state"] == "NG_SECONDARY_UNAVAILABLE") and s["before"].startswith("NG_EXCLUDED")
        trans += int(trans_flag)
        row = {"id": s["id"], "u1_class": s["u1"], "canon": s["canon"], "primary_text": s["primary"], "before": s["before"],
               "after": r, "ng_excluded_to_unavailable": trans_flag, "wav_sha256": sha256_file(s["wav"]), "wav_sec": round(sec_s, 2)}
        res["rows"].append(row)
        print(s["id"], r["state"], r["reason_code"], "| sec:", r["secondary_text"], "| label:", r["secondary_label"])
    after = snap_shared()
    res.update(ng_excluded_to_secondary_unavailable_count=trans, spend_jpy=round(led.total, 4),
               shared_state_diff={k: (before[k], after[k]) for k in before if before[k] != after[k]},
               stop_file_present=os.path.exists(os.path.join(out, "STOP")))
    json.dump(res, open(os.path.join(out, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("spend_jpy", res["spend_jpy"], "transitions", trans, "shared_state_diff", res["shared_state_diff"])


def synth(text, out_path):
    """Production JA TTS方式(Gemini flash-lite speech_metadata backend、STANDARD)で1clip生成。"""
    import er002_common as common
    import er003_b1_p4c_audio as p4c
    import er003_b1_p9a_audio as p9a
    import er006_batch_tts_wiring_01 as batch_wiring
    import er033_tts_flash_lite_backend_wiring_01 as flw
    call_fn, prompt = flw.resolve_tts_call_and_prompt(
        text, p9a.JAPANESE_STYLE_PREFIX, p9a.JAPANESE_MODEL_NAME, p9a.VOICE_NAME, out_path,
        tts_backend="speech_metadata_flash_lite", build_tts_prompt=p4c.build_tts_prompt,
        make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
    pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"ok": False, "error": str(err)}
    with open(out_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm))
    return {"ok": True, "retries": retries}


def run_neg_control(out, execute, budget):
    os.makedirs(os.path.join(out, "clips"), exist_ok=True)
    stop_scope_check(out)
    led = Ledger(out, budget)
    res = {"part": "neg_control", "execute": execute, "budget_jpy": budget,
           "t2_check": {"diff_regen_possible": "N/A(新規synthetic文面のみ。既存wavの差分再生成対象なし)", "audio_cache": "なし(synthetic誤文面は再利用元が存在しない)",
                        "budget_flag": f"--budget-jpy {budget}", "unexpected_full_regen": "なし(8 clip x TTS 1回、再試行なし)"},
           "cases": [dict(id=i, canon=c, spoken=sp, expected_readings=er, aim=a) for i, c, sp, er, a in NEG], "rows": []}
    if not execute:
        print(json.dumps(res["cases"], ensure_ascii=False, indent=1))
        return
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    init_cost_logger(out)
    import er006_asr_provider_routing_01 as routing
    before = snap_shared()
    pass_count = 0
    for i, canon, spoken, er, aim in NEG:
        wav = os.path.join(out, "clips", f"{i}.wav")
        led.check(TTS_JPY_PER_CLIP + 0.1 + 0.5, i)
        t = synth(spoken, wav)
        led.add("tts", TTS_JPY_PER_CLIP, id=i, ok=t["ok"])
        if not t["ok"]:
            res["rows"].append({"id": i, "tts_error": t.get("error")})
            continue
        sec = wav_seconds(wav)
        ptext, perr = routing.transcribe(wav, language="ja-JP", timeout_seconds=90.0)
        led.add("openai_asr", math.ceil(sec) * OPENAI_ASR_JPY_PER_SEC, id=i, err=perr)
        led.check(math.ceil(sec) * AZURE_JPY_PER_SEC, i + "_azure")
        r = judge_one(canon, ptext, wav, expected_readings=er)
        if r["secondary_called"]:
            led.add("azure_stt", math.ceil(sec) * AZURE_JPY_PER_SEC, id=i)
        passed = r["state"] in ("PASS", "PASS_WITH_WARNING")
        pass_count += int(passed)
        row = {"id": i, "canon": canon, "spoken": spoken, "aim": aim, "wav_sec": round(sec, 2), "wav_sha256": sha256_file(wav),
               "primary_text": ptext, "primary_error": perr, "after": r, "false_accept": passed}
        res["rows"].append(row)
        print(i, r["state"], r["reason_code"], "| primary:", ptext, "| azure:", r["secondary_text"])
    after = snap_shared()
    res.update(false_accept_count=pass_count, spend_jpy=round(led.total, 4),
               shared_state_diff={k: (before[k], after[k]) for k in before if before[k] != after[k]},
               stop_file_present=os.path.exists(os.path.join(out, "STOP")))
    json.dump(res, open(os.path.join(out, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("false_accept_count", pass_count, "spend_jpy", res["spend_jpy"], "shared_state_diff", res["shared_state_diff"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["saved_azure", "neg_control"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    (run_saved_azure if a.part == "saved_azure" else run_neg_control)(a.out, a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
