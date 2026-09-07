# ============================================================
# er011_transcript_style_normalization_trial_01.py
# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01
# ============================================================
# 隔離Trial(Lane A、ユーザー承認2026-09-07、新規仕様候補)。
# Production Validator(er006_preprod_hardening_01_validation.py)は
# HEAD版のまま一切変更せず、importして「包む」ラッパーのみをこの
# ファイル内に実装する(既存normalize_text/tokenize/classify_asr_match
# は無変更)。Production採用・Key Phraseへの展開・既存normalize_textの
# 大規模再設計はいずれも本Trialの範囲外(提案のみ、実装しない)。
#
# 目的: 音声内容は正しいのにASRの表記スタイル差(標準contraction・
# punctuation・tokenization・"wanna"等の口語縮約)だけでValidatorが
# false rejectする問題(OPEN-123、OPEN-122とは別failure mode)を、
# 安全性(true content mismatchを誤acceptしない)を最優先に評価する。
#
# 書き込み範囲: 本ファイル(root)、
# er011_output/transcript_style_normalization_trial_01/ 配下のみ。
# Git操作は一切行わない(Fableが統合)。

from __future__ import annotations

import copy
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er003_b1_p9a_audio as p9a
import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as asr_routing
import er006_secondary_asr_01 as secondary_asr
import er006_preprod_hardening_01_validation as en_validator  # HEAD版、無変更でimportのみ
import er008_disfluency_qa_18 as disfluency_qa

OUT_DIR = "er011_output/transcript_style_normalization_trial_01"
AUDIO_DIR = f"{OUT_DIR}/audio"
RESULTS_DIR = f"{OUT_DIR}/results"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"

TRIAL08_EVIDENCE_PATH = ("er012_output/editorial_b_voices_trial_08_audio/p3/b1b/"
                          "audit/stopped_audio_evidence/point_two_result.json")
OPEN122_TRIAL01_MANIFEST_PATH = ("er011_output/connected_speech_equivalence_layer_trial_01/"
                                  "results/manifest.json")
FIXTURE_TEST_MODULE_PATH = "er006_preprod_hardening_01_validation_test.py"

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 500.0

for d in (OUT_DIR, AUDIO_DIR, RESULTS_DIR, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)


def log(msg):
    print(msg, flush=True)


# ============================================================
# Part 0: コスト計測(er011_connected_speech_equivalence_layer_trial_02の
# 既存パターンを再利用、Azure呼び出しはcost_logger.install()自動記録の
# 対象外のため、本Trialで独自にrecord()して累積コストへ含める)
# ============================================================
def _load_pricing():
    prices = json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter)
    return price


def compute_cost_jpy_so_far():
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider == "gemini" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("gemini", model, "input_tokens") / 1e6 \
                        + out_tok * price("gemini", model, "output_tokens") / 1e6
                elif provider == "openai_asr" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("openai_asr", model, "input_tokens") / 1e6 \
                        + out_tok * price("openai_asr", model, "output_tokens") / 1e6
                elif provider == "azure":
                    dur_s = rec.get("audio_duration_submitted_seconds") or 0.0
                    usd = (dur_s / 3600.0) * price(
                        "azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note=""):
    jpy, by = compute_cost_jpy_so_far()
    log(f"  [budget] so far {jpy:.2f} JPY (cap {BUDGET_JPY_CAP}) breakdown={by} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.1f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


def record_azure_call(path, duration_seconds, api="get_full_text_via_azure_stt_with_phrase_list"):
    cost_logger.record({
        "provider": "azure", "api": api, "model_id": "azure-speech-stt",
        "locale": "en-US", "success": True,
        "audio_duration_submitted_seconds": duration_seconds,
        "usage_source": "LOCAL_WAV_HEADER_EXACT_MANUAL_RECORD_OPEN123_TRIAL01",
    })


# ============================================================
# Part 1: Transcript Style Normalization候補(Trial限定、Production未配線)
# ============================================================
# 安全設計の核心: 以下の各expand_*()は、「既にその表記スタイルで書かれて
# いる側」には一切作用しない(該当パターンが無ければ置換されない)。
# classify_with_style_normalization()は、正規化後に両テキストが完全に
# token一致した(=classify_asr_match()がEXACT_MATCH/NORMALIZED_MATCH等
# should_pass=Trueになった)場合のみoverrideする。これにより、
# 「'sをisと解釈すべきかhasと解釈すべきか」のような曖昧性があっても、
# 誤った解釈をした場合は単純に一致しないままなので安全側(false acceptに
# ならない、その代わりrescueできないだけ)に倒れる(詳細はReport参照)。

# (i) 標準contraction展開テーブル(否定反転を一切含まない安全集合)。
# 否定を保持したまま縮約⇔展開するペアのみを含み("do not"⇔"don't"は
# どちらも否定)、"can"⇔"can't"のような意味反転(肯定⇔否定)は絶対に
# 含めない。縮約形(小文字・straight apostrophe)→展開後の完全形、の
# 一方向テーブルだが、canonical/asr双方に適用するため実質双方向として
# 機能する(どちらの側が縮約形でも、その側だけが展開されてもう一方の
# 完全形と一致する)。
_NEGATION_CONTRACTIONS = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    "can't": "cannot", "won't": "will not", "wouldn't": "would not",
    "shouldn't": "should not", "couldn't": "could not",
    "mustn't": "must not", "needn't": "need not", "shan't": "shall not",
}

# 非否定の標準contraction(be/have/will/would系)。's/'dは意味的に
# 曖昧(is/has、would/had)だが、上記の安全設計により誤った解釈を
# 選んでも false accept にはならない(不一致のまま残るだけ)ため、
# 最も頻度の高い解釈(is/would)をデフォルトとして採用する。
_NON_NEGATION_CONTRACTIONS = {
    "i'm": "i am", "you're": "you are", "we're": "we are", "they're": "they are",
    "he's": "he is", "she's": "she is", "it's": "it is", "that's": "that is",
    "there's": "there is", "who's": "who is", "what's": "what is", "here's": "here is",
    "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have",
    "i'll": "i will", "you'll": "you will", "he'll": "he will", "she'll": "she will",
    "we'll": "we will", "they'll": "they will", "it'll": "it will",
    "i'd": "i would", "you'd": "you would", "he'd": "he would", "she'd": "she would",
    "we'd": "we would", "they'd": "they would",
    "let's": "let us",
}

_ALL_STANDARD_CONTRACTIONS = {**_NEGATION_CONTRACTIONS, **_NON_NEGATION_CONTRACTIONS}
_CONTRACTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(_ALL_STANDARD_CONTRACTIONS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE)


def expand_contractions(text: str) -> str:
    """標準contraction(否定保持・非否定とも)を完全形へ展開する。
    アポストロフィのUnicode異体(curly/straight)を先にstraightへ統一
    してからマッチする。既存Production normalize_text()より前の、
    生テキスト段階で行う前処理(既存関数は一切変更しない)。"""
    if not text:
        return text
    t = text.replace("’", "'").replace("‘", "'")

    def _sub(m):
        return _ALL_STANDARD_CONTRACTIONS[m.group(1).lower()]
    return _CONTRACTION_RE.sub(_sub, t)


# (iv) 口語的縮約(want to→wanna 等)。standard contractionとは異なり
# 2語→1語のtoken数変化を伴う。false accept riskが高いため、
# 既定では"never"(適用しない)。"unconditional"/"corroborated"は
# 比較評価のためだけに用意する(いずれもProduction採用候補ではない、
# 詳細はReport参照)。
_COLLOQUIAL_CONTRACTIONS = {
    "wanna": "want to", "gonna": "going to", "gotta": "got to",
}
_COLLOQUIAL_RE = re.compile(
    r"\b(" + "|".join(_COLLOQUIAL_CONTRACTIONS) + r")\b", re.IGNORECASE)


def expand_colloquial(text: str) -> str:
    if not text:
        return text

    def _sub(m):
        return _COLLOQUIAL_CONTRACTIONS[m.group(1).lower()]
    return _COLLOQUIAL_RE.sub(_sub, text)


def classify_with_style_normalization(canonical_text: str, asr_text: str,
                                       secondary_text: str | None = None,
                                       local_text: str | None = None,
                                       wanna_mode: str = "b") -> dict:
    """既存classify_asr_match()(HEAD、無変更)をそのまま最初に呼び、
    should_pass=Falseの場合のみ、Transcript Style Normalization候補を
    段階的に試す。いずれかの段階で正規化後に既存Validatorが
    should_pass=Trueへ変わった場合のみ、Trial限定分類
    "TRANSCRIPT_STYLE_NORMALIZED_MATCH"としてoverrideする(既存
    VALID_CLASSIFICATIONSへは追加しない、Trial内部の表現のみ)。

    wanna_mode: "b"(適用しない、既定)/"a"(無条件適用)/
    "c"(Secondary・localのいずれかがcanonical側を独立に支持した場合のみ
    適用、Equivalence Layer[OPEN-122]と同じcorroboration必須設計を踏襲)。
    """
    baseline = en_validator.classify_asr_match(canonical_text, asr_text)
    result = {
        "baseline_classification": baseline.classification,
        "baseline_should_pass": baseline.should_pass,
        "baseline_reason": baseline.reason,
        "style_normalized_classification": baseline.classification,
        "style_normalized_should_pass": baseline.should_pass,
        "applied_rules": [],
        "wanna_mode": wanna_mode,
    }
    if baseline.should_pass:
        return result  # 既存Validatorで既にPASSなら手を加える必要が無い

    # Step 1: 標準contraction展開のみ
    canon_c = expand_contractions(canonical_text)
    asr_c = expand_contractions(asr_text)
    if canon_c != canonical_text or asr_c != asr_text:
        cand = en_validator.classify_asr_match(canon_c, asr_c)
        if cand.should_pass:
            result["style_normalized_classification"] = "TRANSCRIPT_STYLE_NORMALIZED_MATCH"
            result["style_normalized_should_pass"] = True
            result["applied_rules"].append("contraction_expansion")
            result["style_normalized_reason"] = (
                f"標準contraction展開後にPASS(内部classification={cand.classification})")
            return result

    # Step 2: 口語的縮約(wanna/gonna/gotta)。wanna_modeに応じて適用要否を決める。
    if wanna_mode != "b":
        canon_cc = expand_colloquial(canon_c)
        asr_cc = expand_colloquial(asr_c)
        if canon_cc != canon_c or asr_cc != asr_c:
            cand2 = en_validator.classify_asr_match(canon_cc, asr_cc)
            if cand2.should_pass:
                if wanna_mode == "a":
                    result["style_normalized_classification"] = "TRANSCRIPT_STYLE_NORMALIZED_MATCH"
                    result["style_normalized_should_pass"] = True
                    result["applied_rules"].append("colloquial_expansion_unconditional")
                    result["style_normalized_reason"] = (
                        f"口語的縮約展開後にPASS、無条件採用(内部classification={cand2.classification})")
                    return result
                elif wanna_mode == "c":
                    corroborated_by = []
                    for label, other in (("secondary", secondary_text), ("local", local_text)):
                        if other:
                            other_c = expand_contractions(other)
                            other_res = en_validator.classify_asr_match(canon_c, other_c)
                            if other_res.should_pass:
                                corroborated_by.append(label)
                    if corroborated_by:
                        result["style_normalized_classification"] = "TRANSCRIPT_STYLE_NORMALIZED_MATCH"
                        result["style_normalized_should_pass"] = True
                        result["applied_rules"].append("colloquial_expansion_corroborated")
                        result["corroborated_by"] = corroborated_by
                        result["style_normalized_reason"] = (
                            f"口語的縮約展開後にPASS、独立ASR({corroborated_by})の裏付けありのため採用"
                            f"(内部classification={cand2.classification})")
                        return result
                    else:
                        result["colloquial_candidate_rejected_no_corroboration"] = True

    return result


# ============================================================
# Part 2: 既存Regression fixtureでの無回帰確認(ER-006-POOL-PREPROD-
# HARDENING-01、POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28=59件、API課金なし・
# テキストのみ)。Step 1(contraction_expansion)適用時、既存fixtureの
# 誰も判定が安全でない方向へ変化しないことを確認する。
# ============================================================
def sha256_of(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_existing_fixture_regression():
    log("\n=== 既存Regression fixture(er006_preprod_hardening_01_validation_test.py、59件)無回帰確認 ===")
    import importlib.util
    spec = importlib.util.spec_from_file_location("_er006_fixtures", FIXTURE_TEST_MODULE_PATH)
    fixmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixmod)

    results = {"positive": [], "ambiguous": [], "negative": []}
    fail_count = 0

    for fx in fixmod.POSITIVE_FIXTURES:
        wrapped = classify_with_style_normalization(fx["canonical"], fx["asr"], wanna_mode="b")
        ok = wrapped["style_normalized_should_pass"] or not en_validator.classify_asr_match(
            fx["canonical"], fx["asr"]).should_retry
        if not ok:
            fail_count += 1
        results["positive"].append({"name": fx["name"], "ok": ok,
                                     "baseline": wrapped["baseline_classification"],
                                     "wrapped": wrapped["style_normalized_classification"],
                                     "applied_rules": wrapped["applied_rules"]})
        log(f"  [{'OK' if ok else 'FAIL'}] POSITIVE {fx['name']}: baseline={wrapped['baseline_classification']} "
            f"wrapped={wrapped['style_normalized_classification']} applied={wrapped['applied_rules']}")

    for fx in fixmod.AMBIGUOUS_FIXTURES:
        wrapped = classify_with_style_normalization(fx["canonical"], fx["asr"], wanna_mode="b")
        # AMBIGUOUS fixtureは「元のclassificationが変化しない」ことのみ確認
        # (contraction展開がこのfixture群の意図[数字ゲート等]と無関係なため)。
        ok = (wrapped["style_normalized_classification"] == fx["expected"]) or \
             (wrapped["applied_rules"] == [] and wrapped["baseline_classification"] == fx["expected"])
        if not ok:
            fail_count += 1
        results["ambiguous"].append({"name": fx["name"], "ok": ok,
                                      "expected": fx["expected"],
                                      "baseline": wrapped["baseline_classification"],
                                      "wrapped": wrapped["style_normalized_classification"]})
        log(f"  [{'OK' if ok else 'FAIL'}] AMBIGUOUS {fx['name']}: expected={fx['expected']} "
            f"baseline={wrapped['baseline_classification']} wrapped={wrapped['style_normalized_classification']}")

    for fx in fixmod.NEGATIVE_FIXTURES:
        wrapped = classify_with_style_normalization(fx["canonical"], fx["asr"], wanna_mode="b")
        # NEGATIVE fixtureはtrue content mismatchのはずなので、
        # 正規化後もPASSしてはいけない(=最重要の安全性回帰チェック)。
        ok = not wrapped["style_normalized_should_pass"]
        if not ok:
            fail_count += 1
        results["negative"].append({"name": fx["name"], "ok": ok,
                                     "baseline": wrapped["baseline_classification"],
                                     "wrapped": wrapped["style_normalized_classification"],
                                     "applied_rules": wrapped["applied_rules"]})
        log(f"  [{'OK' if ok else 'FAIL'}] NEGATIVE {fx['name']}: baseline={wrapped['baseline_classification']} "
            f"wrapped={wrapped['style_normalized_classification']} applied={wrapped['applied_rules']}")

    total = len(fixmod.POSITIVE_FIXTURES) + len(fixmod.AMBIGUOUS_FIXTURES) + len(fixmod.NEGATIVE_FIXTURES)
    log(f"\n  Regression結果: {total - fail_count}/{total} OK, {fail_count} FAIL")
    results["summary"] = {"total": total, "fail_count": fail_count}
    return results


# ============================================================
# Part 3: 実例の再利用(追加課金なし)
# ============================================================
def load_trial08_p3_voiceb_evidence():
    """Lane B Trial-08 p3 Voice B(point_two、三人称版)の3回のSTOPPED
    attemptsを再利用する。canonical_textは`point_two_result.json`の
    `canonical_text`、asr_textは各attemptの`asr_text`。"""
    log("\n=== 実例1: Trial-08 p3 Voice B(point_two、3回STOPPED)再利用 ===")
    if not os.path.exists(TRIAL08_EVIDENCE_PATH):
        log(f"  !! 見つかりません: {TRIAL08_EVIDENCE_PATH}")
        return []
    data = json.load(open(TRIAL08_EVIDENCE_PATH, encoding="utf-8"))
    canonical = data["canonical_text"]
    out = []
    for att in data["attempts_log"]:
        item_id = f"trial08_p3_voiceb_attempt{att['attempt']}"
        asr_text = att["asr_text"]
        wrapped_contraction = classify_with_style_normalization(canonical, asr_text, wanna_mode="b")
        out.append({
            "id": item_id, "source": "EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-PERSON-CHECK-01(p3 Voice B)",
            "canonical_text": canonical, "asr_text": asr_text,
            "audio_path": att.get("attempt_audio_path"),
            "original_audio_classification": att.get("audio_classification"),
            "wrapped": wrapped_contraction,
        })
        log(f"  {item_id}: baseline={wrapped_contraction['baseline_classification']} "
            f"wrapped={wrapped_contraction['style_normalized_classification']} "
            f"applied={wrapped_contraction['applied_rules']}")
    return out


def load_open122_wanna_and_asked_evidence():
    """OPEN-122 Trial-01の実測音声(追加課金なし、保存済みmanifest.json
    再利用)から、"want to"→"wanna"(P6_dont_you)、"asked"→"asks"
    (P1_asked_them、Negative Control再利用)を取り出す。"""
    log("\n=== 実例2: OPEN-122 Trial-01実測(P6_dont_you=wanna、P1_asked_them/N3=asked/asks再利用) ===")
    if not os.path.exists(OPEN122_TRIAL01_MANIFEST_PATH):
        log(f"  !! 見つかりません: {OPEN122_TRIAL01_MANIFEST_PATH}")
        return []
    m = json.load(open(OPEN122_TRIAL01_MANIFEST_PATH, encoding="utf-8"))
    by_id = {r["id"]: r for r in m.get("positive_results", [])}
    by_id.update({r["id"]: r for r in m.get("negative_results", [])})

    out = []
    for item_id, note in (("P6_dont_you", "want_to_to_wanna(OPEN-122で個別調査済み、B対象)"),
                           ("P1_asked_them", "asked_to_asks(Negative Control再利用、C対象、正規化してはいけない)"),
                           ("N3_asks_not_asked", "asked_to_asks陰性対照(Negative Control再利用、C対象)")):
        r = by_id.get(item_id)
        if r is None:
            log(f"  !! {item_id} が見つかりません")
            continue
        canonical = r["claimed_canonical"]
        primary = r.get("primary_asr_text") or ""
        secondary = r.get("secondary_asr_text") or ""
        local = r.get("local_asr_text") or ""
        entry = {"id": item_id, "note": note, "canonical_text": canonical,
                  "actually_spoken_text": r.get("actually_spoken_text"),
                  "primary_asr_text": primary, "secondary_asr_text": secondary, "local_asr_text": local,
                  "audio_path": r.get("audio_path")}
        for mode in ("b", "a", "c"):
            entry[f"wrapped_wanna_mode_{mode}"] = classify_with_style_normalization(
                canonical, primary, secondary_text=secondary, local_text=local, wanna_mode=mode)
        out.append(entry)
        for mode in ("b", "a", "c"):
            w = entry[f"wrapped_wanna_mode_{mode}"]
            log(f"  {item_id} [wanna_mode={mode}]: baseline={w['baseline_classification']} "
                f"wrapped={w['style_normalized_classification']} applied={w['applied_rules']}")
    return out


# ============================================================
# Part 4: 新規Standard TTS実測セット
# ============================================================
def local_verbatim_text(path):
    words = disfluency_qa.transcribe_verbatim(path, language="en", model_size="small")
    return " ".join(w["text"].strip() for w in words).strip()


def generate_and_evaluate(item_id, canonical_text, spoken_text, category, note=None):
    """spoken_textを実際にTTSへ渡し、Primary/Secondary/Local ASRを実行、
    canonical_textとの対比を既存Validator(baseline)と各wanna_mode
    ラッパーで評価する。canonical_text != spoken_textの場合は
    意図的な陰性対照(実際の内容不一致)を意味する。"""
    out_path = f"{AUDIO_DIR}/{item_id}.wav"
    log(f"\n--- {item_id} ({category}) ---")
    log(f"  canonical: {canonical_text!r}")
    if spoken_text != canonical_text:
        log(f"  actually_spoken(陰性対照): {spoken_text!r}")

    if os.path.exists(out_path):
        log(f"  [reuse] {out_path}既存のためTTS再生成をスキップ(二重課金防止)")
    else:
        gen = p9a.generate_narration_snippet(spoken_text, "en", out_path)
        assert_budget_ok(f"after TTS {item_id}")
        if gen.get("status") != "OK":
            log(f"  !! TTS generation failed: {gen.get('reason')}")
            return {"id": item_id, "status": "TTS_FAILED", "reason": gen.get("reason"), "category": category}

    primary_text, primary_err = asr_routing.transcribe(out_path, language="en")
    assert_budget_ok(f"after PrimaryASR {item_id}")

    import soundfile as sf
    dur = sf.info(out_path).duration
    secondary_text, secondary_err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
        out_path, language="en-US", phrases=None)
    record_azure_call(out_path, dur)
    assert_budget_ok(f"after SecondaryASR {item_id}")

    local_text = local_verbatim_text(out_path)

    result = {
        "id": item_id, "status": "OK", "category": category, "note": note,
        "canonical_text": canonical_text, "actually_spoken_text": spoken_text,
        "is_negative_control": spoken_text != canonical_text,
        "audio_path": out_path, "audio_sha256": sha256_of(out_path), "duration_seconds": round(dur, 3),
        "primary_asr_text": primary_text, "primary_asr_error": primary_err,
        "secondary_asr_text": secondary_text, "secondary_asr_error": secondary_err,
        "local_asr_text": local_text,
    }
    for engine_label, engine_text in (("primary", primary_text), ("secondary", secondary_text), ("local", local_text)):
        for mode in ("b", "a", "c"):
            key = f"wrapped_{engine_label}_wanna_mode_{mode}"
            if engine_text is None:
                result[key] = None
                continue
            result[key] = classify_with_style_normalization(
                canonical_text, engine_text, secondary_text=secondary_text, local_text=local_text, wanna_mode=mode)
    log(f"  primary_asr={primary_text!r}")
    log(f"  secondary_asr={secondary_text!r}")
    log(f"  local_asr={local_text!r}")
    wb = result["wrapped_primary_wanna_mode_b"]
    log(f"  [primary] baseline={wb['baseline_classification']} wrapped(b)={wb['style_normalized_classification']} "
        f"applied={wb['applied_rules']}")
    return result


# --- テストセット定義 ---
# A: 標準contraction・punctuation/comma/em dash/hyphen/apostrophe
STYLE_A_ITEMS = [
    ("a01_does_not", "The office manager does not answer emails during the weekend.", "A_contraction_negation"),
    ("a02_are_not", "They are not available for the interview this week.", "A_contraction_negation"),
    ("a03_will_not", "The team will not finish the project before the deadline.", "A_contraction_negation"),
    ("a04_cannot", "The client cannot access the shared folder from home.", "A_contraction_negation"),
    ("a05_i_am", "I am certain the results are accurate this quarter.", "A_contraction_non_negation"),
    ("a06_they_are_it_is", "The client said they are happy with the change, and it is already working well.",
     "A_contraction_non_negation"),
    ("a07_we_will", "We will update the schedule once the report is ready.", "A_contraction_non_negation"),
    # 縮約形を「そのまま台本(canonical)」として使う逆方向のケース
    ("a08_contracted_script_1", "I'm not sure it's the right approach for this project.",
     "A_contraction_reverse_direction"),
    ("a09_contracted_script_2", "They're planning to visit the new office next week.",
     "A_contraction_reverse_direction"),
    ("a10_contracted_script_3", "We'll need more time to finish the review, and it isn't easy to rush it.",
     "A_contraction_reverse_direction"),
    # punctuation/comma/em dash/hyphenの確認(既存で吸収済みのはずの再確認)
    ("a11_em_dash", "The manager needs a quiet space—or at least a quieter desk—for the afternoon calls.",
     "A_punctuation_em_dash"),
    ("a12_comma_heavy", "The team met, discussed the results, and agreed on next steps.", "A_punctuation_comma"),
    ("a13_hyphenated_compound", "The client uses a well-known scheduling tool for the project.",
     "A_tokenization_hyphen"),
]

# B: 口語的縮約(want to/wanna, going to/gonna, got to/gotta)
STYLE_B_ITEMS = [
    ("b01_want_to", "Do you want to join the meeting this afternoon?", "B_colloquial_want_to"),
    ("b02_want_to_2", "I want to check the numbers again before we submit them.", "B_colloquial_want_to"),
    ("b03_going_to", "The team is going to release the update next week.", "B_colloquial_going_to"),
    ("b04_got_to", "I have got to check the schedule again before Friday.", "B_colloquial_got_to"),
    ("b05_wanna_script", "I wanna check the numbers again before we submit them.", "B_colloquial_reverse_direction"),
]

# C: 正規化してはいけないNegative control(内容そのものの差)
STYLE_C_ITEMS = [
    ("c01_tense_change", "The manager explained the new policy in detail.",
     "The manager explains the new policy in detail.", "C_negative_tense_inflection"),
    ("c02_content_swap", "The team increased the budget for next quarter.",
     "The team decreased the budget for next quarter.", "C_negative_content_word_swap"),
    ("c03_can_cant_negation_reversal", "You can access the file from any device.",
     "You can't access the file from any device.", "C_negative_negation_reversal"),
    ("c04_will_wont_negation_reversal", "The store will open on Monday.",
     "The store won't open on Monday.", "C_negative_negation_reversal"),
    ("c05_tense_change_2", "She finished the report earlier than expected.",
     "She finishes the report earlier than expected.", "C_negative_tense_inflection"),
    ("c06_content_swap_2", "Customers can return the item within thirty days.",
     "Customers can exchange the item within thirty days.", "C_negative_content_word_swap"),
]


def run_new_tts_test_set():
    results = {"A": [], "B": [], "C": []}
    for item_id, text, category in STYLE_A_ITEMS:
        results["A"].append(generate_and_evaluate(item_id, text, text, category))
    for item_id, text, category in STYLE_B_ITEMS:
        results["B"].append(generate_and_evaluate(item_id, text, text, category))
    for item_id, canonical, spoken, category in STYLE_C_ITEMS:
        results["C"].append(generate_and_evaluate(item_id, canonical, spoken, category))
    return results


# ============================================================
# Part 5: player.html(file:///形式試聴用)
# ============================================================
def build_player_html(new_results, manifest_path):
    rows = []
    for cat in ("A", "B", "C"):
        for r in new_results.get(cat, []):
            if r.get("status") != "OK":
                continue
            wb = r["wrapped_primary_wanna_mode_b"]
            wa = r["wrapped_primary_wanna_mode_a"]
            wc = r["wrapped_primary_wanna_mode_c"]
            rows.append(
                f"<tr><td>{r['id']}</td><td>{r['category']}</td>"
                f"<td>canonical: {r['canonical_text']}<br>spoken: {r['actually_spoken_text']}</td>"
                f"<td><audio controls src='audio/{r['id']}.wav'></audio></td>"
                f"<td>Primary: {r['primary_asr_text']}<br>Secondary: {r['secondary_asr_text']}<br>"
                f"Local: {r['local_asr_text']}</td>"
                f"<td>baseline={wb['baseline_classification']}</td>"
                f"<td>mode_b={wb['style_normalized_classification']}<br>"
                f"mode_a={wa['style_normalized_classification']}<br>"
                f"mode_c={wc['style_normalized_classification']}</td></tr>")
    html = ("<html><head><meta charset='utf-8'><title>OPEN-123 Transcript Style Normalization Trial 01</title>"
            "<style>table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:4px;"
            "font-size:12px;vertical-align:top}</style></head><body>"
            f"<h1>OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01</h1>"
            f"<p>manifest: {manifest_path}</p>"
            "<table><tr><th>id</th><th>category</th><th>text</th><th>audio</th><th>ASR (3経路)</th>"
            "<th>baseline(既存Validator)</th><th>wrapped(candidate methods)</th></tr>"
            + "".join(rows) + "</table></body></html>")
    path = f"{OUT_DIR}/player.html"
    open(path, "w", encoding="utf-8").write(html)
    return path


# ============================================================
# main
# ============================================================
def main():
    cost_logger.install(COST_LOG_PATH)
    log("=== OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01 開始 ===")

    fixture_regression = run_existing_fixture_regression()
    trial08_evidence = load_trial08_p3_voiceb_evidence()
    open122_evidence = load_open122_wanna_and_asked_evidence()
    new_results = run_new_tts_test_set()

    jpy, by_provider = compute_cost_jpy_so_far()

    manifest = {
        "fixture_regression": fixture_regression,
        "trial08_p3_voiceb_evidence": trial08_evidence,
        "open122_wanna_asked_evidence": open122_evidence,
        "new_tts_results": new_results,
        "cost_jpy_total": round(jpy, 2),
        "cost_by_provider_jpy": by_provider,
        "budget_cap_jpy": BUDGET_JPY_CAP,
    }
    manifest_path = f"{RESULTS_DIR}/manifest.json"
    open(manifest_path, "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2))

    player_path = build_player_html(new_results, manifest_path)

    log(f"\n=== 完了 ===")
    log(f"  cost_jpy_total: {jpy:.2f} (cap {BUDGET_JPY_CAP})")
    log(f"  manifest: {manifest_path}")
    log(f"  player: {player_path}")


if __name__ == "__main__":
    main()
