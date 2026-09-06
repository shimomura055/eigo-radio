# ============================================================
# er011_kp_en_asr_false_rejection_cascade_trial_01.py
# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01
# ============================================================
# 目的(隔離Trial、Production変更なし): 短い英語Key Phraseに対して
# Primary ASR(OpenAI gpt-4o-mini-transcribe、language="en")が非ラテン
# 文字(CJK等)を主体とする意味変換出力を返した場合に、正しい英語音声を
# 誤ってfalse rejectしないための一般的な仕組みの候補を比較検証する。
#
# 対象Production実装(read-onlyで再利用、無変更):
#   - er003_v1_repro01_main_generate.generate_key_phrase_component_verified /
#     generate_narration_snippet_verified_strict (Cascade呼び出し元)
#   - er006_secondary_asr_01.evaluate_attempt_with_cascade_detail
#     (既存Cascade: entity_like/homophone_candidateのASR_VALIDATION_
#     UNCERTAINにのみ発動、TTS_FAILURE/TRUE_CONTENT_MISMATCHには発動しない)
#   - er006_preprod_hardening_01_validation.classify_asr_match
#     (tokenize()が[^a-z0-9]+をスペース化するため、CJK等の非ASCII文字は
#     比較前に消える。ASR側がCJKのみを返すと類似度がほぼ0になり、
#     TTS_FAILUREへ分類される。事実確認: KEYPHRASE-EN-TTS-ROOTCAUSE-
#     DIAGNOSTIC-01_REPORT.md参照)
#   - er006_asr_provider_routing_01.transcribe (Primary ASR呼び出し、
#     promptパラメータは現在渡していない)
#
# 本Trialモジュールは、これら既存関数を呼び出す/re-classifyするだけで、
# 上記のいずれも書き換えない(Trial条件はこのファイル内だけで完結する)。
#
# 条件:
#   (a) Primary ASR出力が英語canonicalに対して非ラテン文字主体の場合、
#       classify_asr_matchの結果(TTS_FAILURE/TRUE_CONTENT_MISMATCH問わず)
#       に関わらずSecondary ASR(Azure en-US、既存
#       er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list
#       をそのまま再利用)で確認し、Secondaryがclassify_asr_matchで
#       should_pass=Trueならその時点でverified扱いにする(Trial限定の
#       追加分岐、既存Cascadeの発動条件[entity_like/homophone_candidate]
#       は一切変更しない)。
#   (b) OpenAI ASR呼び出しへ、英語のまま逐語で書き起こし翻訳・意味変換
#       しない旨のprompt引数を追加する(routing.transcribeは無変更、
#       Trial専用の別関数として実装)。
#   (c) (a)+(b)併用: (b)のprompt付きPrimary結果に対して(a)の非ラテン
#       文字判定+Secondary Cascadeを適用する。
#
# 非ラテン文字判定(この関数のみで完結する、Production非導入):
#   ラテン文字(基本ラテン+主要発音区別符号)とCJK/かな/ハングル文字を
#   それぞれ数え、(CJK系文字数)/(ラテン文字数+CJK系文字数) >= 0.5
#   (両方0の場合はFalse)を「非ラテン文字主体」と判定する。適用範囲は
#   Key Phrase Component呼び出し(generate_key_phrase_component_verified
#   が扱う独立した短い英語segment)のASR出力全体であり、segment内の
#   部分文字列やそれ以外のsegment種別(Full Story本文等)へは適用しない
#   (Key Phrase呼び出しに限定したTrialのため)。

from __future__ import annotations

import json
import os
import re

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr

OUT_DIR = "er011_output/kp_en_asr_false_rejection_cascade_trial_01"
AUDIO_DIR = f"{OUT_DIR}/audio"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

ASR_MODEL = "gpt-4o-mini-transcribe"  # Production Primary ASRと同一モデル(routing.ASR_ROUTING["en"])

# ------------------------------------------------------------
# 非ラテン文字主体判定(Trial専用、Production非導入)
# ------------------------------------------------------------
_LATIN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")
_CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿가-힣]")
NON_LATIN_DOMINANT_THRESHOLD = 0.5


def non_latin_dominance_info(text: str | None) -> dict:
    text = text or ""
    latin_n = len(_LATIN_RE.findall(text))
    cjk_n = len(_CJK_RE.findall(text))
    total = latin_n + cjk_n
    ratio = (cjk_n / total) if total > 0 else 0.0
    is_dominant = total > 0 and cjk_n > 0 and ratio >= NON_LATIN_DOMINANT_THRESHOLD
    return {"latin_chars": latin_n, "cjk_chars": cjk_n, "ratio_cjk": round(ratio, 3),
            "is_non_latin_dominant": is_dominant, "threshold": NON_LATIN_DOMINANT_THRESHOLD}


# ------------------------------------------------------------
# (b) prompt付きOpenAI ASR呼び出し(Trial専用、routing.transcribeは無変更)
# ------------------------------------------------------------
EN_ASR_NO_TRANSLATE_PROMPT = (
    "The audio is spoken in English. Transcribe it verbatim in English, exactly "
    "as spoken, using English spelling. Do not translate it, and do not write it "
    "in Japanese, Chinese, or any other language or script."
)

_openai_client_trial = None


def _get_openai_client_trial():
    global _openai_client_trial
    if _openai_client_trial is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        _openai_client_trial = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client_trial


def transcribe_openai_with_prompt(wav_path: str, prompt_text: str) -> tuple[str | None, str | None]:
    client = _get_openai_client_trial()
    try:
        with open(wav_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=ASR_MODEL, file=f, language="en", prompt=prompt_text)
        return resp.text, None
    except Exception as exc:
        return None, str(exc)[:500]


# ------------------------------------------------------------
# TTS生成(Standard同期、Production Key Phrase経路と同一のvoice/model/
# instruction文言。cascade wrapperは経由せず、単発生成+単発ASRのみを行う
# 単純化版[retry loopなし]。理由: 本Trialは「1回のASR出力に対する事後の
# 再判定ロジック」を比較するのが目的であり、TTS自体のretry構成は対象外)
# ------------------------------------------------------------
def generate_english_key_phrase_style_audio(text: str, out_name: str) -> dict:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}.wav"
    prompt = p4c.build_tts_prompt(text, repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"TTS失敗: {err}", "text": text}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした", "text": text}
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        return {"status": "STOPPED", "reason": anomaly["reason"], "duration_anomaly": anomaly, "text": text}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    return {"status": "OK", "text": text, "path": out_path, "language": "en",
            "instruction": "KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX (Production同一文言)",
            "call_count": 1 + retries, "retry_count": retries, "sha256": p8a.sha256_file(out_path),
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4)}


def generate_japanese_narration_style_audio(text: str, out_name: str) -> dict:
    """陰性対照(i)用: 日本語TTSでcanonical(英語)に対応する日本語訳語
    (「新常態」「デフォルト」)を発話させる。Production
    generate_narration_snippet()のja分岐(meaning_N narration等と同一の
    JAPANESE_STYLE_PREFIX)をそのまま使う。"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}.wav"
    r = p9a.generate_narration_snippet(text, "ja", out_path)
    return r


# ------------------------------------------------------------
# 評価(4条件: 現行/(a)/(b)/(c))
# ------------------------------------------------------------
def evaluate_item(canonical_text: str, wav_path: str) -> dict:
    result = {"canonical_text": canonical_text, "wav_path": wav_path}

    # --- 現行(Production同一ロジック、単発Primary ASR+classify_asr_match) ---
    primary_text, primary_err = routing.transcribe(wav_path, language="en-US")
    baseline_cls = val.classify_asr_match(canonical_text, primary_text) if primary_text is not None else None
    baseline_classification = baseline_cls.classification if baseline_cls else "TTS_FAILURE"
    baseline_verified = bool(baseline_cls and baseline_cls.should_pass)
    cascade_eligible_in_production = bool(
        baseline_cls and (secondary_asr.is_entity_like_mismatch(baseline_cls)
                           or secondary_asr.is_homophone_candidate_mismatch(baseline_cls)))
    result["baseline"] = {
        "primary_text": primary_text, "primary_error": primary_err,
        "classification": baseline_classification, "verified": baseline_verified,
        "cascade_eligible_in_production": cascade_eligible_in_production,
        "non_latin_info": non_latin_dominance_info(primary_text),
    }

    # --- (a): 現行Primary結果に対し、非ラテン文字主体ならSecondary Azureで再確認 ---
    a = {"invoked": False, "verified": baseline_verified, "final_classification": baseline_classification}
    secondary_text_shared = None
    secondary_cls_shared = None
    if not baseline_verified and result["baseline"]["non_latin_info"]["is_non_latin_dominant"]:
        secondary_text_shared, secondary_err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
            wav_path, language="en-US", phrases=None)
        secondary_cls_shared = val.classify_asr_match(canonical_text, secondary_text_shared) if secondary_text_shared is not None else None
        a_verified = bool(secondary_cls_shared and secondary_cls_shared.should_pass)
        a = {
            "invoked": True, "secondary_text": secondary_text_shared, "secondary_error": secondary_err,
            "secondary_classification": secondary_cls_shared.classification if secondary_cls_shared else "TTS_FAILURE",
            "verified": a_verified,
            "final_classification": (secondary_cls_shared.classification if a_verified else baseline_classification),
        }
    result["condition_a"] = a

    # --- (b): prompt付きPrimary ASR単独 ---
    prompt_text, prompt_err = transcribe_openai_with_prompt(wav_path, EN_ASR_NO_TRANSLATE_PROMPT)
    prompt_cls = val.classify_asr_match(canonical_text, prompt_text) if prompt_text is not None else None
    b_classification = prompt_cls.classification if prompt_cls else "TTS_FAILURE"
    b_verified = bool(prompt_cls and prompt_cls.should_pass)
    result["condition_b"] = {
        "primary_prompt_text": prompt_text, "primary_prompt_error": prompt_err,
        "classification": b_classification, "verified": b_verified,
        "non_latin_info": non_latin_dominance_info(prompt_text),
    }

    # --- (c): (b)のPrimary結果に(a)と同じ非ラテン文字判定+Secondary Cascadeを適用 ---
    c = {"invoked": False, "verified": b_verified, "final_classification": b_classification}
    if not b_verified and result["condition_b"]["non_latin_info"]["is_non_latin_dominant"]:
        # コスト削減のため、(a)で既にSecondary Azureを呼んでいれば同じ音声への
        # 同じ呼び出しを再利用する(同一wav_path・同一language・phrases=Noneの
        # 呼び出しであり、TTSは再生成しない前提と同じ発想でASR呼び出し回数を
        # 節約する)。(a)が発火していなければ(=現行Primaryが非ラテンでなかった
        # 場合)ここで新規にSecondaryを呼ぶ。
        if secondary_cls_shared is not None or secondary_text_shared is not None:
            text_s, cls_s = secondary_text_shared, secondary_cls_shared
            reused = True
        else:
            text_s, err_s = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
                wav_path, language="en-US", phrases=None)
            cls_s = val.classify_asr_match(canonical_text, text_s) if text_s is not None else None
            reused = False
        c_verified = bool(cls_s and cls_s.should_pass)
        c = {
            "invoked": True, "secondary_reused_from_condition_a": reused,
            "secondary_text": text_s, "secondary_classification": cls_s.classification if cls_s else "TTS_FAILURE",
            "verified": c_verified,
            "final_classification": (cls_s.classification if c_verified else b_classification),
        }
    result["condition_c"] = c

    return result


# ------------------------------------------------------------
# テストセット定義
# ------------------------------------------------------------
def run_trial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    items = []

    # --- 陽性(1): new normal、既存保全音声を再利用(新規TTSコストなし) ---
    existing_new_normal = "er011_output/kp_en_tts_rootcause_diagnostic_01/kp2_en_attempt4_english_lock_2_final.wav"
    items.append({"item_id": "pos_new_normal_reused_attempt4", "canonical_text": "new normal",
                  "wav_path": existing_new_normal, "wav_source": "reused_existing (KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01)"})

    # --- 陽性(2): new normal、新規1回生成 ---
    gen = generate_english_key_phrase_style_audio("new normal", "pos_new_normal_fresh")
    items.append({"item_id": "pos_new_normal_fresh", "canonical_text": "new normal",
                  "wav_path": gen.get("path"), "wav_source": "new_tts", "tts_generation": gen})

    # --- 陽性(3): default、既存Mini-Trial-20-R2音声(attempt1、ASR「デフォルト」既知)を再利用 ---
    existing_default = "er010_output/no9_keyphrase_minimal_instruction_minitrial_20_r2/audio/kp2_default_attempt1.wav"
    items.append({"item_id": "pos_default_reused_attempt1", "canonical_text": "default",
                  "wav_path": existing_default, "wav_source": "reused_existing (ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINITRIAL-20-R2)"})

    # --- 陽性(4-7): 日本語で定着した英語表現、新規1回生成 ---
    for text, name in [
        ("work-life balance", "pos_work_life_balance"),
        ("remote work", "pos_remote_work"),
        ("subscription", "pos_subscription"),
        ("cashless", "pos_cashless"),
    ]:
        gen = generate_english_key_phrase_style_audio(text, name)
        items.append({"item_id": f"pos_{name}", "canonical_text": text,
                      "wav_path": gen.get("path"), "wav_source": "new_tts", "tts_generation": gen})

    # --- 陰性対照(i): 日本語TTSで日本語訳語を発話(英語canonicalに対してreject維持が期待) ---
    gen = generate_japanese_narration_style_audio("新常態", "neg_ja_shinjoutai")
    items.append({"item_id": "neg_ja_shinjoutai_vs_new_normal", "canonical_text": "new normal",
                  "wav_path": gen.get("path"), "wav_source": "new_tts", "tts_generation": gen,
                  "kind": "negative", "negative_reason": "日本語TTSで「新常態」を発話(canonical=new normal)"})

    gen = generate_japanese_narration_style_audio("デフォルト", "neg_ja_default")
    items.append({"item_id": "neg_ja_default_vs_default", "canonical_text": "default",
                  "wav_path": gen.get("path"), "wav_source": "new_tts", "tts_generation": gen,
                  "kind": "negative", "negative_reason": "日本語TTSで「デフォルト」を発話(canonical=default)"})

    # --- 陰性対照(ii): 英語で別の語を発話(canonical=new normal、実際はnew formal) ---
    gen = generate_english_key_phrase_style_audio("new formal", "neg_en_new_formal")
    items.append({"item_id": "neg_en_new_formal_vs_new_normal", "canonical_text": "new normal",
                  "wav_path": gen.get("path"), "wav_source": "new_tts", "tts_generation": gen,
                  "kind": "negative", "negative_reason": "英語TTSで別の語「new formal」を発話(canonical=new normal)"})

    for it in items:
        it.setdefault("kind", "positive")
        if it.get("wav_path") and os.path.exists(it["wav_path"]):
            it["evaluation"] = evaluate_item(it["canonical_text"], it["wav_path"])
        else:
            it["evaluation"] = {"error": "wav_pathが存在しません(TTS生成失敗の可能性)",
                                "tts_generation_status": it.get("tts_generation", {}).get("status")}

    # --- 集計 ---
    positives = [it for it in items if it["kind"] == "positive" and "error" not in it["evaluation"]]
    negatives = [it for it in items if it["kind"] == "negative" and "error" not in it["evaluation"]]

    def _rate(items_subset, cond_key):
        n = len(items_subset)
        if n == 0:
            return None
        if cond_key == "baseline":
            rejected = sum(1 for it in items_subset if not it["evaluation"]["baseline"]["verified"])
        else:
            rejected = sum(1 for it in items_subset if not it["evaluation"][cond_key]["verified"])
        return {"n": n, "false_rejections": rejected, "false_rejection_rate": round(rejected / n, 3)}

    def _false_accepts(items_subset, cond_key):
        if cond_key == "baseline":
            return [it["item_id"] for it in items_subset if it["evaluation"]["baseline"]["verified"]]
        return [it["item_id"] for it in items_subset if it["evaluation"][cond_key]["verified"]]

    summary = {
        "positive_false_rejection_rate": {
            "baseline": _rate(positives, "baseline"),
            "condition_a": _rate(positives, "condition_a"),
            "condition_b": _rate(positives, "condition_b"),
            "condition_c": _rate(positives, "condition_c"),
        },
        "negative_false_accepts": {
            "baseline": _false_accepts(negatives, "baseline"),
            "condition_a": _false_accepts(negatives, "condition_a"),
            "condition_b": _false_accepts(negatives, "condition_b"),
            "condition_c": _false_accepts(negatives, "condition_c"),
        },
        "positive_item_ids": [it["item_id"] for it in positives],
        "negative_item_ids": [it["item_id"] for it in negatives],
    }

    output = {
        "non_latin_dominant_threshold": NON_LATIN_DOMINANT_THRESHOLD,
        "en_asr_no_translate_prompt": EN_ASR_NO_TRANSLATE_PROMPT,
        "asr_model": ASR_MODEL,
        "items": items,
        "summary": summary,
    }
    with open(f"{OUT_DIR}/trial_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    return output


if __name__ == "__main__":
    r = run_trial()
    print(json.dumps(r["summary"], ensure_ascii=False, indent=2, default=str))
