# ============================================================
# er011_open121_tts_repetition_general_qa_trial_01.py
# OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01
# ============================================================
# 隔離Trial(Lane A、ユーザー承認2026-09-07)。Production Validator/QA/
# retry/Cost Guard/TTS Prompt/適用範囲は一切変更しない。既存Production
# 関数(er003_b1_p9a_audio.generate_narration_snippet / er006_asr_
# provider_routing_01.transcribe / er008_disfluency_qa_18の関数群)を
# 無変更のまま呼び出すだけの、独立したTrialモジュール。
#
# 目的: TTSの句・文単位の言い直し/再読(repetition hallucination)を、
# 既存ASR平滑化・既存disfluency QA(隣接単語のみ)がすり抜ける前提で、
# 「異常音声をProductionへ流出させない一般QA」を設計・比較検証する。
#
# 書き込み範囲: 本ファイル(root)、er011_output/
# open121_tts_repetition_general_qa_trial_01/ 配下のみ。Git操作なし。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import sys
import time

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as asr_routing
import er008_disfluency_qa_18 as dq18

RERUN02 = "er011_output/open112_trend_theme2_b_final_audio_rerun_02"
OUT_DIR = "er011_output/open121_tts_repetition_general_qa_trial_01"
TEST_SET_DIR = f"{OUT_DIR}/test_set"
RESULTS_DIR = f"{OUT_DIR}/results"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 800.0

MANIFEST_PATH = f"{TEST_SET_DIR}/manifest.json"


def log(msg):
    print(msg, flush=True)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_wav(path):
    data, sr = sf.read(path, always_2d=False)
    return data, sr


def write_wav(path, data, sr):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, data, sr, subtype="PCM_16")


def to_mono(data):
    if data.ndim == 1:
        return data.astype(np.float64)
    return data.mean(axis=1).astype(np.float64)


def duration_seconds(path):
    data, sr = load_wav(path)
    return round(len(data) / sr, 3)


# ============================================================
# コスト集計(既存pricing_snapshot.json、公式ソース参照。推測priceは使わない)
# ============================================================
def _load_pricing():
    prices = json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter)
    return price


def compute_cost_jpy_so_far():
    """AUDIT_DIR/raw_usage_log.jsonl(このTrial専用のcost_logger出力)から
    累積コストをJPY換算で計算する。Production側のraw_usage_log.jsonlには
    一切触れない(init_logger()でこのTrial専用パスへ切り替え済み)。"""
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
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note=""):
    jpy, _ = compute_cost_jpy_so_far()
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.1f} JPY > cap {BUDGET_JPY_CAP} JPY. "
                            f"Stopping ({note}).")
    return jpy


# ============================================================
# Phase 1: テストセット構築(実在陽性のコピー + manifest雛形)
# ============================================================
# A2 parts.json(canonical text SSOT、rerun-02生成時に確定した原稿)から
# 読み取った既存canonicalテキスト(このTrialでは一切変更しない、読み取りのみ)。
A2_CANON = {
    "point_two_body": ("Young travelers are not one single market. Women aged 29 and under "
                        "still showed strong interest in famous tourist places, at about 45%. "
                        "Gourmet travel was even higher, at about 52%. This is not the same "
                        "picture as the male interest in solo and hobby-based trips. The useful "
                        "lesson is not that sightseeing is ending. Different young travelers may "
                        "be looking for different kinds of value from the same holiday."),
    "in_one_line": ("The direction is visible in several surveys, but it is still a change in "
                     "what young travelers want—not proof that long, slow stays have become "
                     "the new normal."),
    "point_one_body": ("Slow travel may be less about adding nights and more about choosing how "
                        "to use the day. Among men aged 29 and under, solo travel was about 25%, "
                        "and hobby-focused travel was about 24%. A separate survey found that "
                        "about 90% of Gen Z respondents wanted free time inside an overseas tour. "
                        "About 80% wanted at least half a day. A short trip can still feel more "
                        "personal when the traveler has room to choose."),
    "part1": ("As of September 2026, a quiet split appears in travel surveys in Japan. Young "
              "people are showing more interest in trips at their own pace. They want room for "
              "personal interests and free time. But the trips they plan are still often short. "
              "This is the interesting part: wanting slower travel does not yet mean a long stay. "
              "When people imagined getting a full month off, the most common answer was a trip "
              "of about one week. It was chosen by 24.1%. This shows that many people can imagine "
              "giving travel more time when the chance exists."),
    "part2": ("But a different autumn survey looked at people who were planning a trip. Their "
              "planned hotel stays averaged 1.8 nights, with a median of 2 nights. The two "
              "pictures do not fully match. One shows a wish for more time. The other shows short "
              "plans. Japan’s Tourism White Paper also says that making stays longer is still "
              "a policy task. So the evidence does not show a complete move from famous "
              "sightseeing to slow travel. It shows a growing wish for a more personal trip, "
              "while long stays have not yet become normal."),
    "topic_intro": "Today's topic is Young Japan Wants Slower Trips. The Plans Are Still Short.",
    "kp1_en": "at one's own pace",
    "kp2_en": "a full month off",
    "kp3_en": "hobby-focused travel",
    "kp4_en": "median",
    "kp5_en": "the new normal",
}

# 日本語(既存a2_support_texts.json / meaning群、読み取りのみ)
A2_CANON_JA = {
    "preview": ("日本の若い世代には、旅先で"
                "自分らしく過ごしたいという"
                "思いが見られます。いくつか"
                "の調査を通して、旅行の楽し"
                "み方がどう変わっているのか"
                "を考えます。"),
}


def _copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def build_test_set():
    os.makedirs(TEST_SET_DIR, exist_ok=True)
    manifest = []

    # ---- 陽性(実在、確認済み) ----
    pos_real = [
        dict(item_id="real_point_two_buggy",
             src=f"{RERUN02}/audit/duplication_diagnosis_review_fix_02/"
                 "2_a2_point_two_narration_BUGGY_UNFIXED_pending_human_review.wav",
             canonical_text=A2_CANON["point_two_body"], language="en",
             label="positive", source="real_confirmed",
             note="Trial-13時点のGemini TTS生成そのもののhallucination。冒頭2文が"
                  "まるごと1回逐語反復(offset≈9.63秒、OPEN-112-THEME2-AUDIO-"
                  "REVIEW-FIX-02_REPORT.md §1確認済み)。既存Human Review Cost Guardに"
                  "より現在もHUMAN_REVIEW_LOCKED状態で未修正のまま。"),
        dict(item_id="real_in_one_line_buggy",
             src=f"{RERUN02}/audit/duplication_diagnosis_review_fix_02/"
                 "3_a2_in_one_line_narration_BEFORE_FIX_buggy.wav",
             canonical_text=A2_CANON["in_one_line"], language="en",
             label="positive", source="real_confirmed",
             note="同上failure mode。主節全体が1回逐語反復(offset≈8.2秒)。"
                  "現在は修正済み音声がProductionへ反映済み(このwavは修正前の原本コピー)。"),
    ]
    for item in pos_real:
        dst = f"{TEST_SET_DIR}/positives_real/{item['item_id']}.wav"
        _copy(item["src"], dst)
        item["path"] = dst
        item["sha256"] = sha256_of(dst)
        item["duration_seconds"] = duration_seconds(dst)
        del item["src"]
        manifest.append(item)

    # ---- 陰性(既存Production PASS済み音声の再利用、読み取りコピー) ----
    neg_reused = [
        ("a2_comment_1", f"{RERUN02}/a2/narration/comment_1.wav", None, "ja"),
        ("a2_comment_2", f"{RERUN02}/a2/narration/comment_2.wav", None, "ja"),
        ("a2_comment_3", f"{RERUN02}/a2/narration/comment_3.wav", None, "ja"),
        ("a2_comment_4", f"{RERUN02}/a2/narration/comment_4.wav", None, "ja"),
        ("a2_meaning_1", f"{RERUN02}/a2/narration/meaning_1.wav", None, "ja"),
        ("a2_meaning_2", f"{RERUN02}/a2/narration/meaning_2.wav", None, "ja"),
        ("a2_meaning_3", f"{RERUN02}/a2/narration/meaning_3.wav", None, "ja"),
        ("a2_meaning_4", f"{RERUN02}/a2/narration/meaning_4.wav", None, "ja"),
        ("a2_meaning_5", f"{RERUN02}/a2/narration/meaning_5.wav", None, "ja"),
        ("a2_preview", f"{RERUN02}/a2/narration/preview.wav", A2_CANON_JA["preview"], "ja"),
        ("a2_japanese_title", f"{RERUN02}/a2/narration/japanese_title.wav", None, "ja"),
        ("a2_topic_intro", f"{RERUN02}/a2/narration/topic_intro.wav", A2_CANON["topic_intro"], "en"),
        ("a2_kp1_en", f"{RERUN02}/a2/narration/kp1_en.wav", A2_CANON["kp1_en"], "en"),
        ("a2_kp2_en", f"{RERUN02}/a2/narration/kp2_en.wav", A2_CANON["kp2_en"], "en"),
        ("a2_kp3_en", f"{RERUN02}/a2/narration/kp3_en.wav", A2_CANON["kp3_en"], "en"),
        ("a2_kp4_en", f"{RERUN02}/a2/narration/kp4_en.wav", A2_CANON["kp4_en"], "en"),
        ("a2_kp5_en", f"{RERUN02}/a2/narration/kp5_en.wav", A2_CANON["kp5_en"], "en"),
        ("a2_point_one_clean", f"{RERUN02}/a2/narration/point_one.wav", A2_CANON["point_one_body"], "en"),
        ("a2_full_story_part1_clean", f"{RERUN02}/a2/narration/full_story_part1.wav", A2_CANON["part1"], "en"),
        ("a2_full_story_part2_clean", f"{RERUN02}/a2/narration/full_story_part2.wav", A2_CANON["part2"], "en"),
        ("a2_in_one_line_fixed_clean", f"{RERUN02}/a2/narration/in_one_line.wav", A2_CANON["in_one_line"], "en"),
        ("b1b_kp1_en", f"{RERUN02}/b1b/narration/kp1_en.wav", None, "en"),
        ("b1b_kp2_en", f"{RERUN02}/b1b/narration/kp2_en.wav", None, "en"),
        ("b1b_comment_1", f"{RERUN02}/b1b/narration/comment_1.wav", None, "ja"),
        ("b1b_comment_2", f"{RERUN02}/b1b/narration/comment_2.wav", None, "ja"),
        ("b1b_in_one_line", f"{RERUN02}/b1b/narration/in_one_line.wav", None, "en"),
        ("b1b_full_story_intro_charon", f"{RERUN02}/b1b/narration/full_story_intro_charon.wav", None, "en"),
    ]
    for item_id, src, canon, lang in neg_reused:
        if not os.path.exists(src):
            log(f"  [skip, missing] {item_id}: {src}")
            continue
        dst = f"{TEST_SET_DIR}/negatives_reused/{item_id}.wav"
        _copy(src, dst)
        manifest.append(dict(
            item_id=item_id, path=dst, sha256=sha256_of(dst), duration_seconds=duration_seconds(dst),
            canonical_text=canon, language=lang, label="negative", source="reused_production_pass",
            note="rerun-02 Production PASS済み音声の読み取りコピー(既存Validator合格済み)。"))

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log(f"build_test_set: {len(manifest)} items -> {MANIFEST_PATH}")
    return manifest


# ============================================================
# Phase 2: 合成陽性(clean音声を編集して人工的な重複を作る)
# ============================================================
def _get_word_timestamps(wav_path):
    words = dq18.transcribe_verbatim(wav_path, language="en", model_size="small")
    return words


def _splice_repeat(data, sr, src_start_s, src_end_s, insert_at_s, gap_before_s=0.18):
    """[src_start_s, src_end_s)の音声を、insert_at_s の位置へ複製挿入する
    (元のsrc区間はそのまま残す。insert_at_s以降の音声は後ろへ押し出される)。
    実在した重複(直前まで読んだ内容を、少し後の時点で読み直す)と同じ形。"""
    span = data[int(round(src_start_s * sr)):int(round(src_end_s * sr))]
    gap = np.zeros(int(round(gap_before_s * sr)), dtype=data.dtype)
    insert_idx = int(round(insert_at_s * sr))
    insert_idx = min(insert_idx, len(data))
    out = np.concatenate([data[:insert_idx], gap, span, data[insert_idx:]])
    return out, len(span) / sr


def build_synthetic_positives():
    os.makedirs(f"{TEST_SET_DIR}/positives_synthetic", exist_ok=True)
    sources = [
        ("a2_point_one_clean", f"{TEST_SET_DIR}/negatives_reused/a2_point_one_clean.wav", A2_CANON["point_one_body"]),
        ("a2_full_story_part1_clean", f"{TEST_SET_DIR}/negatives_reused/a2_full_story_part1_clean.wav", A2_CANON["part1"]),
        ("a2_full_story_part2_clean", f"{TEST_SET_DIR}/negatives_reused/a2_full_story_part2_clean.wav", A2_CANON["part2"]),
    ]
    manifest = []
    for src_id, src_path, canon in sources:
        words = _get_word_timestamps(src_path)
        data, sr = load_wav(src_path)
        total_dur = len(data) / sr
        log(f"  {src_id}: {len(words)} words, duration={total_dur:.2f}s")

        # 挿入位置: 音声中盤(実在バグと同じく「先ほど話した内容を後で読み直す」形)
        mid_frac = 0.55
        insert_at_s = total_dur * mid_frac
        # 対象spanは音声の先頭付近(実在バグの「冒頭2文がまるごと反復」と同型)
        variants = {
            "word": (1, 1),      # 1 word
            "phrase": (3, 5),    # 3-5 words
            "sentence": (7, 12),  # 7-12 words (ほぼ1文)
        }
        for kind, (nmin, nmax) in variants.items():
            n = min(nmax, max(nmin, len(words) // 6))
            n = max(n, nmin)
            # 先頭寄りの単語列(先頭3語は除いて自然な語境界を選ぶ)
            start_idx = 3 if len(words) > (3 + n) else 0
            span_words = words[start_idx:start_idx + n]
            if not span_words:
                continue
            src_start_s = span_words[0]["start"]
            src_end_s = span_words[-1]["end"]
            repeated_text = " ".join(w["text"] for w in span_words).strip()

            out, span_dur = _splice_repeat(data, sr, src_start_s, src_end_s, insert_at_s)
            item_id = f"synth_{kind}_{src_id}"
            out_path = f"{TEST_SET_DIR}/positives_synthetic/{item_id}.wav"
            write_wav(out_path, out, sr)
            manifest.append(dict(
                item_id=item_id, path=out_path, sha256=sha256_of(out_path),
                duration_seconds=round(len(out) / sr, 3), canonical_text=canon, language="en",
                label="positive", source="synthetic",
                note=(f"clean音声({src_id})を編集し、先頭付近の{kind}-level span "
                      f"({n}語:'{repeated_text}') を音声中盤(t≈{insert_at_s:.2f}s)へ"
                      f"複製挿入(gap0.18秒)。実在バグ(直前までの内容の再読)と同じ形。"),
                synth_info=dict(kind=kind, n_words=n, repeated_text=repeated_text,
                                 src_start_s=round(src_start_s, 3), src_end_s=round(src_end_s, 3),
                                 insert_at_s=round(insert_at_s, 3), src_item_id=src_id)))
            log(f"    -> {item_id}: '{repeated_text}' inserted at {insert_at_s:.2f}s")

    # manifestへ追記
    existing = json.load(open(MANIFEST_PATH, encoding="utf-8")) if os.path.exists(MANIFEST_PATH) else []
    existing = [m for m in existing if not m["item_id"].startswith("synth_")]
    existing.extend(manifest)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    log(f"build_synthetic_positives: {len(manifest)} items")
    return manifest


# ============================================================
# Phase 3: 新規Standard TTS生成(既存Production関数を無変更のまま
# 直接呼び出し。Review Lock/guarded_generateは経由しない=このTrialの
# 生成物はProduction narrationパス規約に従わないため、Review Lock側の
# _has_valid_narration_layout()判定で自動的にbypassされる設計と同じ
# 安全側の扱いにする)。
# ============================================================
INTENTIONAL_REPETITION_TEXTS = {
    "intentional_not_now_later_ever": "Not now. Not later. Not ever. The answer stays the same no matter when you ask.",
    "intentional_stability_control": "One values a steady base. The other values control. Both matter, but they rarely mean the same thing to the same person.",
    "intentional_twice_today": "It happened twice today. Twice. Once in the morning, and once again just before lunch.",
    "intentional_three_hundred": "The price was three hundred dollars. Three hundred dollars for a single night, with breakfast included.",
    "intentional_no_matter": "No matter what. No matter when. No matter who. The rule never changes.",
    "intentional_said_twice": "She said it once, and then she said it again, just to make sure everyone understood.",
}

NATURAL_ATTEMPT_TEXTS = {
    "natural_attempt_weather": ("Local forecasters say the region has seen fewer heavy rain days this year, "
                                 "but the rain that does fall tends to arrive all at once. Farmers say this "
                                 "makes planning harder than a simple drop in total rainfall would. Some are "
                                 "shifting planting schedules by two or three weeks to reduce the risk."),
    "natural_attempt_commute": ("A growing number of office workers are choosing to arrive earlier and leave "
                                 "earlier, aiming to avoid the most crowded trains. Transit officials say this "
                                 "spreads passenger load across a wider window, but peak crowding around the "
                                 "old core hours has not disappeared, it has simply softened at the edges."),
    "natural_attempt_coffee": ("Coffee shop owners in the area report that customers are ordering smaller "
                                "cups more often instead of one large cup in the morning. Some owners see "
                                "this as a sign that coffee is being treated less like a single ritual and "
                                "more like a habit spread across the day."),
    "natural_attempt_remote_work": ("Several companies that once required five days in the office have settled "
                                     "on a three-day minimum instead. Managers say the change came after "
                                     "employees pointed to focused work getting done more easily at home, while "
                                     "team meetings still worked better in person."),
    "natural_attempt_phone_use": ("A recent survey found that most young adults check their phones within five "
                                   "minutes of waking up, but a smaller group has started leaving phones in "
                                   "another room overnight. Sleep researchers say the second group reports "
                                   "falling asleep faster, though the sample size remains small."),
    "natural_attempt_sleep": ("People who track their sleep with a wearable device often discover they wake "
                               "up more times per night than they realized. Doctors note that noticing this "
                               "pattern does not always mean something is wrong, since brief awakenings are a "
                               "normal part of a healthy sleep cycle."),
}


def _standard_tts_generate(text, out_path):
    """Production Standard同期TTS経路(client.models.generate_content、
    Batch APIではない)を無変更のまま呼び出す。p9a.generate_narration_
    snippet()にtts_call_fnを渡さないことで、既定の_make_english_call_fn()
    (Standard同期)が使われる(A2/B1本文と同一voice=Aoede・同一
    style_prefix・同一model)。"""
    import er003_b1_p9a_audio as p9a
    return p9a.generate_narration_snippet(text, "en", out_path)


def generate_new_tts_negatives(cost_log_path=COST_LOG_PATH):
    cost_logger.install(cost_log_path)
    os.makedirs(f"{TEST_SET_DIR}/negatives_new_tts", exist_ok=True)
    manifest_new = []
    with cost_logger.logging_context("OPEN-121-TRIAL", "intentional_repetition_negative"):
        for item_id, text in INTENTIONAL_REPETITION_TEXTS.items():
            assert_budget_ok(f"before {item_id}")
            with cost_logger.segment_context(item_id):
                out_path = f"{TEST_SET_DIR}/negatives_new_tts/{item_id}.wav"
                t0 = time.time()
                r = _standard_tts_generate(text, out_path)
                log(f"  [{item_id}] status={r.get('status')} dur={time.time()-t0:.1f}s")
                if r.get("status") != "OK":
                    log(f"    FAILED: {r}")
                    continue
                manifest_new.append(dict(
                    item_id=item_id, path=out_path, sha256=sha256_of(out_path),
                    duration_seconds=duration_seconds(out_path), canonical_text=text, language="en",
                    label="negative", source="new_standard_tts_intentional_repetition",
                    note="新規Standard同期TTS生成(Aoede、A2/B1本文と同一voice/prompt)。"
                         "台本自体に意図的な反復・言い換えを含む(hallucinationではない)。"))
    with cost_logger.logging_context("OPEN-121-TRIAL", "natural_hallucination_attempt"):
        for item_id, text in NATURAL_ATTEMPT_TEXTS.items():
            assert_budget_ok(f"before {item_id}")
            with cost_logger.segment_context(item_id):
                out_path = f"{TEST_SET_DIR}/negatives_new_tts/{item_id}.wav"
                t0 = time.time()
                r = _standard_tts_generate(text, out_path)
                log(f"  [{item_id}] status={r.get('status')} dur={time.time()-t0:.1f}s")
                if r.get("status") != "OK":
                    log(f"    FAILED: {r}")
                    continue
                manifest_new.append(dict(
                    item_id=item_id, path=out_path, sha256=sha256_of(out_path),
                    duration_seconds=duration_seconds(out_path), canonical_text=text, language="en",
                    label="negative_or_positive_unknown", source="new_standard_tts_natural_attempt",
                    note="新規Standard同期TTS生成。反復を意図しない通常段落(hallucination "
                         "自然発生を狙った試行)。実際にhallucinationが発生していれば陽性、"
                         "していなければ陰性として扱う(後段の生transcript確認で判定)。"))

    existing = json.load(open(MANIFEST_PATH, encoding="utf-8")) if os.path.exists(MANIFEST_PATH) else []
    existing = [m for m in existing if m["source"] not in
                ("new_standard_tts_intentional_repetition", "new_standard_tts_natural_attempt")]
    existing.extend(manifest_new)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    jpy, by_provider = compute_cost_jpy_so_far()
    log(f"generate_new_tts_negatives: {len(manifest_new)} items generated. cost so far: {jpy:.1f} JPY {by_provider}")
    return manifest_new


# ============================================================
# Phase 1b: B1 Full Story Part 1「partial-word false start型」実在陽性の
# 追加(OPEN_ITEMS.md OPEN-121行、2026-09-07ユーザー試聴で確認・
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02サブタスクDのfalsestart_
# characterization診断で特性確認済み)。Point Two/In One Line(語句・
# 文単位のまるごと反復)とは異なる型(語の途中で切れる短い言い直し+
# 再開、"As of Septem, As of September 2026…")であり、既存
# detect_adjacent_word_repetition・本Trialのn-gram法(トークン単位の
# 完全一致を前提)のいずれも原理的に検知できない(word-level timestampの
# 異常な長さ["September"が1.28秒、通常0.5〜0.6秒の2倍以上]として現れる)。
# ============================================================
B1_CANON = {
    "part1_opening": ("As of September 2026, travel surveys in Japan tell a story with two "
                       "different speeds."),
}
FALSESTART_SRC = (f"{RERUN02}/audit/duplication_diagnosis_review_fix_02/b1_fsp1_recheck/"
                   "falsestart_opening_0-3s.wav")


def add_b1_fsp1_falsestart_positive():
    if not os.path.exists(FALSESTART_SRC):
        log(f"  [skip, missing] falsestart source: {FALSESTART_SRC}")
        return None
    item_id = "real_b1_fsp1_falsestart_partial_word"
    dst = f"{TEST_SET_DIR}/positives_real/{item_id}.wav"
    _copy(FALSESTART_SRC, dst)
    item = dict(
        item_id=item_id, path=dst, sha256=sha256_of(dst), duration_seconds=duration_seconds(dst),
        canonical_text=B1_CANON["part1_opening"], language="en", label="positive", source="real_confirmed",
        note="B1 Full Story Part 1冒頭0-3秒抽出。2026-09-07ユーザー試聴で実在確認済みの"
             "partial-word false start型重複(\"As of Septem, As of September 2026…\")。"
             "Point Two/In One Line(語句・文単位のまるごと反復)とは異なる型で、'September'の"
             "word-level timestamp長が1.28秒(通常0.5〜0.6秒の2倍以上)という異常値として現れる"
             "(OPEN_ITEMS.md OPEN-121行、falsestart_characterization_evidence.json参照)。"
             "既存disfluency QA・本Trialのn-gram法(トークン完全一致前提)のいずれも"
             "原理的に検知不能(このTrialではMethod Aの拡張案=語長異常検知で別途検証する)。")
    existing = json.load(open(MANIFEST_PATH, encoding="utf-8")) if os.path.exists(MANIFEST_PATH) else []
    existing = [m for m in existing if m["item_id"] != item_id]
    existing.append(item)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    log(f"add_b1_fsp1_falsestart_positive: added {item_id} ({item['duration_seconds']}s)")
    return item


# ============================================================
# Method A-ext: 単語duration異常検知(falsestart型向け)。faster-whisper
# word-level timestampの長さが、その単語の文字数から予測される典型的な
# 長さと比べて異常に長い場合をflagする。既存disfluency QA/本TrialのMethod
# A(トークン完全一致前提)では検知できないfalsestart型(語の途中で切れて
# 再開し、ASRが1 tokenへ吸収してしまうケース)向けの補完策。
# ============================================================
def detect_word_duration_anomaly(words, z_threshold=2.5, min_ratio=1.8):
    """各wordのduration(秒)を、その単語の文字数に対する線形回帰的な
    目安(全体の秒/文字比の中央値)と比較する。比率がmin_ratio以上、かつ
    zスコアがz_threshold以上のwordを異常として検知する。"""
    if len(words) < 4:
        return {"flagged": False, "anomalies": [], "note": "insufficient words for duration baseline"}
    per_char = []
    for w in words:
        text = dq18._normalize_token(w["text"])
        dur = w["end"] - w["start"]
        if text and dur > 0:
            per_char.append(dur / max(len(text), 1))
    if not per_char:
        return {"flagged": False, "anomalies": [], "note": "no usable words"}
    median_per_char = float(np.median(per_char))
    std_per_char = float(np.std(per_char)) or 1e-6
    anomalies = []
    for w in words:
        text = dq18._normalize_token(w["text"])
        dur = w["end"] - w["start"]
        if not text or dur <= 0:
            continue
        expected = median_per_char * max(len(text), 1)
        ratio = dur / expected if expected > 0 else 0
        z = (dur / max(len(text), 1) - median_per_char) / std_per_char
        if ratio >= min_ratio and z >= z_threshold:
            anomalies.append({"word": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                               "duration_seconds": round(dur, 3), "expected_seconds": round(expected, 3),
                               "ratio": round(ratio, 2), "z_score": round(z, 2)})
    return {"flagged": bool(anomalies), "anomalies": anomalies,
            "median_seconds_per_char": round(median_per_char, 4)}


def build_word_duration_reference(reference_items):
    """clean(陰性)音声集合から、単語文字列(正規化後)ごとの典型duration
    (秒)分布を作る。同一単語同士の比較(同一文字数の他単語との比較ではなく、
    'September'なら過去の'September'の長さと比較する)の方が、"as"/"of"の
    ような短機能語の固定調音コストに引きずられる単純な秒/文字比モデルより
    頑健であることをこのTrialで確認した(v1の秒/文字モデルはfalsestart型を
    検知できなかった、下記run_method_a2_word_duration_anomaly()参照)。"""
    ref = {}
    for path in reference_items:
        words = _get_word_timestamps(path)
        for w in words:
            text = dq18._normalize_token(w["text"])
            dur = w["end"] - w["start"]
            if text and dur > 0:
                ref.setdefault(text, []).append(dur)
    return {k: {"median": float(np.median(v)), "n": len(v), "max": max(v), "min": min(v)}
            for k, v in ref.items()}


def detect_word_duration_anomaly_same_word_ref(words, reference, ratio_threshold=1.8):
    """同一単語(正規化後)の参照durationと比較する版。参照に存在しない
    単語はここでは判定しない(false positiveを避ける安全側の設計、既存
    disfluency QAのdocstringと同じ思想)。"""
    anomalies = []
    for w in words:
        text = dq18._normalize_token(w["text"])
        dur = w["end"] - w["start"]
        ref_entry = reference.get(text)
        if not text or dur <= 0 or ref_entry is None:
            continue
        ratio = dur / ref_entry["median"] if ref_entry["median"] > 0 else 0
        if ratio >= ratio_threshold:
            anomalies.append({"word": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                               "duration_seconds": round(dur, 3), "reference_median_seconds": round(ref_entry["median"], 3),
                               "reference_n": ref_entry["n"], "ratio": round(ratio, 2)})
    return {"flagged": bool(anomalies), "anomalies": anomalies, "method": "same_word_reference"}


# ============================================================
# Method D: 音響self-similarity(OPEN-112診断で使った手法と同一設計、
# b1_fsp1_recheck/recheck_script.pyのspectral_self_similarity()を
# 独立コピーとして再実装。Production/他タスクのファイルは一切変更しない)。
# ============================================================
def spectral_self_similarity(path, frame_ms=25.0, hop_ms=10.0, min_lag_s=1.0, top_k=5):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if np.abs(mono).max() > 0:
        mono = mono / (np.abs(mono).max() + 1e-9)

    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    if n_frames < 2:
        return {"path": path, "sample_rate": sr, "duration_seconds": round(len(mono) / sr, 3), "top_matches": []}

    window = np.hanning(frame_len)
    spec = np.zeros((n_frames, frame_len // 2 + 1))
    for i in range(n_frames):
        start = i * hop_len
        frame = mono[start:start + frame_len]
        if len(frame) < frame_len:
            frame = np.pad(frame, (0, frame_len - len(frame)))
        spec[i] = np.abs(np.fft.rfft(frame * window))

    logspec = np.log1p(spec)
    norms = np.linalg.norm(logspec, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = logspec / norms
    sim = normed @ normed.T

    min_lag_frames = int(min_lag_s * 1000.0 / hop_ms)
    n = sim.shape[0]
    candidates = []
    for i in range(n):
        for j in range(i + min_lag_frames, n):
            candidates.append((sim[i, j], i, j))
    candidates.sort(key=lambda x: -x[0])

    top = []
    seen_pairs = set()
    for score, i, j in candidates:
        key = (i // 20, j // 20)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        top.append({"similarity": round(float(score), 4),
                     "time_a_seconds": round(i * hop_ms / 1000.0, 3),
                     "time_b_seconds": round(j * hop_ms / 1000.0, 3),
                     "lag_seconds": round((j - i) * hop_ms / 1000.0, 3)})
        if len(top) >= top_k:
            break

    run_lengths = []
    for entry in top[:3]:
        i0 = int(round(entry["time_a_seconds"] * 1000.0 / hop_ms))
        lag = int(round(entry["lag_seconds"] * 1000.0 / hop_ms))
        threshold = 0.85
        k = 0
        while (i0 + k < n and i0 + k + lag < n and sim[i0 + k, i0 + k + lag] >= threshold):
            k += 1
        run_lengths.append(round(k * hop_ms / 1000.0, 3))
    for idx, rl in enumerate(run_lengths):
        top[idx]["run_length_seconds_at_thresh_0.85"] = rl

    return {"path": path, "sample_rate": sr, "duration_seconds": round(len(mono) / sr, 3),
            "frame_ms": frame_ms, "hop_ms": hop_ms, "min_lag_seconds": min_lag_s, "top_matches": top}


def run_method_d(manifest=None):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        t0 = time.time()
        sim = spectral_self_similarity(item["path"])
        best_run = max((m.get("run_length_seconds_at_thresh_0.85", 0.0) for m in sim["top_matches"]), default=0.0)
        results[item["item_id"]] = {
            "duration_seconds": sim["duration_seconds"],
            "best_run_length_seconds": best_run,
            "top_matches": sim["top_matches"],
            "elapsed_seconds": round(time.time() - t0, 2),
        }
        log(f"  [MethodD] {item['item_id']}: best_run_length={best_run:.3f}s")
    with open(f"{RESULTS_DIR}/method_d_spectral_self_similarity.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# Method A: 句・文単位n-gram反復検知(既存detect_adjacent_word_
# repetition[隣接1語のみ]の拡張案。canonicalテキスト照合で意図的反復を
# 除外する)。既存er008_disfluency_qa_18.pyは無変更、このTrial専用の
# 新規関数として実装する。
# ============================================================
def _normalize_tokens(text):
    return [dq18._normalize_token(w) for w in text.split()]


def find_repeated_spans(tokens, min_words=1):
    """tokens内で、非隣接も含めた完全一致の反復spanを検出する。各pairに
    ついて最長一致(k)まで貪欲に延長し、既に選ばれたspanと重なる短い
    候補は除外する(最長優先)。"""
    n = len(tokens)
    candidates = []
    for i in range(n):
        if not tokens[i]:
            continue
        for j in range(i + 1, n):
            if tokens[i] != tokens[j]:
                continue
            k = 0
            while i + k < j and j + k < n and tokens[i + k] == tokens[j + k]:
                k += 1
            if k >= min_words:
                candidates.append((i, j, k))
    candidates.sort(key=lambda m: -m[2])
    selected = []
    covered = set()
    for i, j, k in candidates:
        rng = set(range(j, j + k)) | set(range(i, i + k))
        if rng & covered:
            continue
        covered |= rng
        selected.append((i, j, k))
    selected.sort(key=lambda m: m[0])
    return selected


def _canonical_repeat_count(span_tokens, canonical_tokens):
    """span_tokens(反復として検知されたtoken列)が、canonical_text側にも
    複数回出現するか(=台本自体が意図した反復である可能性)を数える。"""
    if not span_tokens or not canonical_tokens:
        return 0
    n, m = len(canonical_tokens), len(span_tokens)
    count = 0
    for i in range(n - m + 1):
        if canonical_tokens[i:i + m] == span_tokens:
            count += 1
    return count


def detect_ngram_repetition(words, canonical_text=None, min_words=3):
    """Trial提案方式(Method A)。wordsはfaster-whisper word-level
    timestamps(dq18.transcribe_verbatim()の戻り値)。min_words=3で
    phrase/sentence-level(3語以上)の非隣接反復を検知し、canonicalへの
    照合で意図的反復(台本に元々複数回同じ語句がある場合)を除外する。"""
    tokens = [dq18._normalize_token(w["text"]) for w in words]
    spans = find_repeated_spans(tokens, min_words=min_words)
    canonical_tokens = _normalize_tokens(canonical_text) if canonical_text else None
    matches = []
    for i, j, k in spans:
        span_tokens = tokens[i:i + k]
        span_text = " ".join(w["text"] for w in words[i:i + k])
        canon_count = _canonical_repeat_count(span_tokens, canonical_tokens) if canonical_tokens is not None else None
        intentional = (canon_count is not None and canon_count >= 2)
        gap_seconds = round(words[j]["start"] - words[i + k - 1]["end"], 3)
        category = "word" if k == 1 else ("phrase" if k <= 4 else "sentence")
        matches.append({
            "span_text": span_text, "n_words": k, "category": category,
            "first_start_s": round(words[i]["start"], 3), "first_end_s": round(words[i + k - 1]["end"], 3),
            "second_start_s": round(words[j]["start"], 3), "second_end_s": round(words[j + k - 1]["end"], 3),
            "gap_seconds": gap_seconds, "canonical_repeat_count": canon_count, "intentional": intentional,
            "flagged": not intentional,
        })
    flagged = [m for m in matches if m["flagged"]]
    return {"matches": matches, "flagged": bool(flagged), "flagged_matches": flagged,
            "word_count": len(words), "canonical_known": canonical_tokens is not None}


def run_method_a_local(manifest=None):
    """faster-whisper local verbatim上で (a)既存dq18(隣接1語のみ、baseline)
    (b)Trial提案のn-gram(min_words>=3、canonical crosscheck付き)の両方を
    実行し比較する。"""
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        if item.get("language") != "en":
            log(f"  [MethodA] skip (language={item.get('language')}): {item['item_id']}")
            continue
        t0 = time.time()
        words = _get_word_timestamps(item["path"])
        baseline = dq18.detect_adjacent_word_repetition(words)
        proposed = detect_ngram_repetition(words, canonical_text=item.get("canonical_text"), min_words=3)
        proposed_min1 = detect_ngram_repetition(words, canonical_text=item.get("canonical_text"), min_words=1)
        results[item["item_id"]] = {
            "word_count": len(words),
            "baseline_dq18_adjacent_word": {"flagged": bool(baseline), "repeats": [
                {"token": r["token"], "first_start_s": round(r["first"]["start"], 3),
                 "second_start_s": round(r["second"]["start"], 3)} for r in baseline]},
            "proposed_ngram_min3_canonical_crosscheck": proposed,
            "proposed_ngram_min1_canonical_crosscheck": proposed_min1,
            "elapsed_seconds": round(time.time() - t0, 2),
        }
        log(f"  [MethodA] {item['item_id']}: baseline_flagged={bool(baseline)} "
            f"proposed_min3_flagged={proposed['flagged']} ({len(proposed['flagged_matches'])} spans) "
            f"proposed_min1_flagged={proposed_min1['flagged']} ({len(proposed_min1['flagged_matches'])} spans)")
    with open(f"{RESULTS_DIR}/method_a_local_verbatim.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# Method C: 窓分割ASR(既存Production Primary ASR = er006_asr_provider_
# routing_01.transcribe()を無変更のまま呼び出す)。全文一括ASR(baseline)
# と、window/hop設定を変えた複数のwindowed ASRを比較する。
# ============================================================
def _cut_clip(data, sr, start_s, end_s):
    return data[int(round(start_s * sr)):int(round(end_s * sr))]


def _text_ngram_repetition(text, canonical_text=None, min_words=3):
    """ASR transcript(word-level timestampなし、空白split)に対する
    Method Aのtext-only版。"""
    if not text:
        return {"matches": [], "flagged": False, "flagged_matches": [], "canonical_known": canonical_text is not None}
    tokens = _normalize_tokens(text)
    spans = find_repeated_spans(tokens, min_words=min_words)
    canonical_tokens = _normalize_tokens(canonical_text) if canonical_text else None
    raw_words = text.split()
    matches = []
    for i, j, k in spans:
        span_tokens = tokens[i:i + k]
        span_text = " ".join(raw_words[i:i + k]) if i + k <= len(raw_words) else " ".join(span_tokens)
        canon_count = _canonical_repeat_count(span_tokens, canonical_tokens) if canonical_tokens is not None else None
        intentional = (canon_count is not None and canon_count >= 2)
        category = "word" if k == 1 else ("phrase" if k <= 4 else "sentence")
        matches.append({"span_text": span_text, "n_words": k, "category": category,
                         "canonical_repeat_count": canon_count, "intentional": intentional,
                         "flagged": not intentional})
    flagged = [m for m in matches if m["flagged"]]
    return {"matches": matches, "flagged": bool(flagged), "flagged_matches": flagged,
            "canonical_known": canonical_tokens is not None}


def run_method_c(manifest=None, window_configs=((8.0, 4.0), (12.0, 6.0)), positive_repeats=2):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    os.makedirs(f"{AUDIT_DIR}/method_c_windows", exist_ok=True)
    cost_logger.install(COST_LOG_PATH)
    results = {}
    for item in manifest:
        if item.get("language") != "en":
            log(f"  [MethodC] skip (language={item.get('language')}): {item['item_id']}")
            continue
        assert_budget_ok(f"before {item['item_id']}")
        data, sr = load_wav(item["path"])
        total_dur = len(data) / sr
        repeats = positive_repeats if item.get("label") in ("positive",) or item.get("source") == "synthetic" else 1
        canon = item.get("canonical_text")

        with cost_logger.logging_context("OPEN-121-TRIAL", "method_c_windowed_asr"), \
                cost_logger.segment_context(item["item_id"]):
            full_calls = []
            for r in range(repeats):
                t0 = time.time()
                text, err = asr_routing.transcribe(item["path"], language="en")
                full_calls.append({"call_index": r + 1, "asr_text": text, "error": err,
                                    "elapsed_seconds": round(time.time() - t0, 2),
                                    "ngram_check": _text_ngram_repetition(text, canon) if text else None})

            windowed_results = {}
            for (win_s, hop_s) in window_configs:
                key = f"win{win_s:g}_hop{hop_s:g}"
                window_texts = []
                w0 = 0.0
                idx = 0
                while w0 < total_dur:
                    w1 = min(w0 + win_s, total_dur)
                    clip = _cut_clip(data, sr, w0, w1)
                    clip_path = f"{AUDIT_DIR}/method_c_windows/{item['item_id']}_{key}_{idx}.wav"
                    write_wav(clip_path, clip, sr)
                    t0 = time.time()
                    text, err = asr_routing.transcribe(clip_path, language="en")
                    window_texts.append({"window_start_s": round(w0, 2), "window_end_s": round(w1, 2),
                                          "asr_text": text, "error": err,
                                          "elapsed_seconds": round(time.time() - t0, 2)})
                    os.remove(clip_path)
                    idx += 1
                    if w1 >= total_dur:
                        break
                    w0 += hop_s
                concat_text = " ".join(w["asr_text"] for w in window_texts if w["asr_text"])
                windowed_results[key] = {
                    "window_seconds": win_s, "hop_seconds": hop_s, "n_windows": len(window_texts),
                    "windows": window_texts, "concatenated_text": concat_text,
                    "ngram_check": _text_ngram_repetition(concat_text, canon),
                }

        results[item["item_id"]] = {"duration_seconds": round(total_dur, 3),
                                     "full_asr_calls": full_calls, "windowed": windowed_results}
        any_full_flagged = any((c.get("ngram_check") or {}).get("flagged") for c in full_calls)
        any_win_flagged = any(v["ngram_check"]["flagged"] for v in windowed_results.values())
        log(f"  [MethodC] {item['item_id']}: full_flagged={any_full_flagged} windowed_flagged={any_win_flagged} "
            f"cost_so_far={compute_cost_jpy_so_far()[0]:.2f}JPY")
        with open(f"{RESULTS_DIR}/method_c_windowed_asr.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# 結果集計 + player.html
# ============================================================
def build_results_table():
    manifest = {m["item_id"]: m for m in json.load(open(MANIFEST_PATH, encoding="utf-8"))}
    method_a = json.load(open(f"{RESULTS_DIR}/method_a_local_verbatim.json", encoding="utf-8")) \
        if os.path.exists(f"{RESULTS_DIR}/method_a_local_verbatim.json") else {}
    method_c = json.load(open(f"{RESULTS_DIR}/method_c_windowed_asr.json", encoding="utf-8")) \
        if os.path.exists(f"{RESULTS_DIR}/method_c_windowed_asr.json") else {}
    method_d = json.load(open(f"{RESULTS_DIR}/method_d_spectral_self_similarity.json", encoding="utf-8")) \
        if os.path.exists(f"{RESULTS_DIR}/method_d_spectral_self_similarity.json") else {}
    method_a_ext = json.load(open(f"{RESULTS_DIR}/method_a_ext_word_duration_same_word_ref.json", encoding="utf-8")) \
        if os.path.exists(f"{RESULTS_DIR}/method_a_ext_word_duration_same_word_ref.json") else {}

    rows = []
    for item_id, item in manifest.items():
        a = method_a.get(item_id)
        c = method_c.get(item_id)
        d = method_d.get(item_id)
        ext = method_a_ext.get(item_id)
        row = {
            "item_id": item_id, "label": item.get("label"), "source": item.get("source"),
            "language": item.get("language"), "duration_seconds": item.get("duration_seconds"),
            "baseline_dq18_flagged": a["baseline_dq18_adjacent_word"]["flagged"] if a else None,
            "method_a_min3_flagged": a["proposed_ngram_min3_canonical_crosscheck"]["flagged"] if a else None,
            "method_a_min1_flagged": a["proposed_ngram_min1_canonical_crosscheck"]["flagged"] if a else None,
            "method_c_full_flagged": (any((cc.get("ngram_check") or {}).get("flagged")
                                       for cc in c["full_asr_calls"]) if c else None),
            "method_c_windowed_flagged": (any(w["ngram_check"]["flagged"] for w in c["windowed"].values())
                                           if c else None),
            "method_d_best_run_length_seconds": d["best_run_length_seconds"] if d else None,
            "method_a_ext_word_duration_flagged": ext["flagged"] if ext else None,
        }
        rows.append(row)
    with open(f"{RESULTS_DIR}/summary_table.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # threshold calibration for Method D (min positive run vs max negative run)
    pos_runs = [r["method_d_best_run_length_seconds"] for r in rows
                if r["label"] == "positive" and r["method_d_best_run_length_seconds"] is not None]
    neg_runs = [r["method_d_best_run_length_seconds"] for r in rows
                if r["label"] in ("negative", "negative_or_positive_unknown")
                and r["method_d_best_run_length_seconds"] is not None]
    calib = {"positive_min_run_length": min(pos_runs) if pos_runs else None,
             "negative_max_run_length": max(neg_runs) if neg_runs else None,
             "n_positive": len(pos_runs), "n_negative": len(neg_runs)}
    with open(f"{RESULTS_DIR}/method_d_threshold_calibration.json", "w", encoding="utf-8") as f:
        json.dump(calib, f, ensure_ascii=False, indent=2)
    log(f"summary_table: {len(rows)} rows. Method D calibration: {calib}")
    return rows


def build_player_html():
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    rows = json.load(open(f"{RESULTS_DIR}/summary_table.json", encoding="utf-8")) \
        if os.path.exists(f"{RESULTS_DIR}/summary_table.json") else []
    by_id = {r["item_id"]: r for r in rows}

    def section(title, items):
        html = [f"<h2>{title}</h2><table border=1 cellpadding=4 style='border-collapse:collapse'>"]
        html.append("<tr><th>item_id</th><th>audio</th><th>lang</th><th>dur(s)</th>"
                     "<th>dq18(baseline)</th><th>MethodA min3</th><th>MethodA min1</th>"
                     "<th>MethodC full</th><th>MethodC windowed</th><th>MethodD run(s)</th>"
                     "<th>MethodA-ext dur.anomaly</th><th>note</th></tr>")
        for item in items:
            r = by_id.get(item["item_id"], {})
            rel = os.path.relpath(item["path"], OUT_DIR).replace("\\", "/")
            html.append("<tr>"
                         f"<td>{item['item_id']}</td>"
                         f"<td><audio controls src='{rel}'></audio></td>"
                         f"<td>{item.get('language')}</td>"
                         f"<td>{item.get('duration_seconds')}</td>"
                         f"<td>{r.get('baseline_dq18_flagged')}</td>"
                         f"<td>{r.get('method_a_min3_flagged')}</td>"
                         f"<td>{r.get('method_a_min1_flagged')}</td>"
                         f"<td>{r.get('method_c_full_flagged')}</td>"
                         f"<td>{r.get('method_c_windowed_flagged')}</td>"
                         f"<td>{r.get('method_d_best_run_length_seconds')}</td>"
                         f"<td>{r.get('method_a_ext_word_duration_flagged')}</td>"
                         f"<td style='max-width:400px;font-size:11px'>{item.get('note', '')}</td>"
                         "</tr>")
        html.append("</table>")
        return "\n".join(html)

    positives_real = [m for m in manifest if m["source"] == "real_confirmed"]
    positives_synth = [m for m in manifest if m["source"] == "synthetic"]
    negatives_reused = [m for m in manifest if m["source"] == "reused_production_pass"]
    negatives_new = [m for m in manifest if m["source"] in
                      ("new_standard_tts_intentional_repetition", "new_standard_tts_natural_attempt")]

    html = ["<html><head><meta charset='utf-8'><title>OPEN-121 Trial player</title></head><body>",
            "<h1>OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01</h1>",
            section("1. 陽性(実在、確認済み)", positives_real),
            section("2. 陽性(合成、clean音声を編集)", positives_synth),
            section("3. 陰性(既存Production PASS音声の再利用)", negatives_reused),
            section("4. 陰性(新規Standard TTS: 意図的反復 / 自然hallucination試行)", negatives_new),
            "</body></html>"]
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    log(f"player.html -> {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["build_test_set", "build_synthetic_positives",
                                           "generate_new_tts_negatives", "run_method_d",
                                           "run_method_a_local", "run_method_c",
                                           "build_results_table", "build_player_html"])
    args = parser.parse_args()
    if args.phase == "build_test_set":
        build_test_set()
    elif args.phase == "build_synthetic_positives":
        build_synthetic_positives()
    elif args.phase == "generate_new_tts_negatives":
        generate_new_tts_negatives()
    elif args.phase == "run_method_d":
        run_method_d()
    elif args.phase == "run_method_a_local":
        run_method_a_local()
    elif args.phase == "run_method_c":
        run_method_c()
    elif args.phase == "build_results_table":
        build_results_table()
    elif args.phase == "build_player_html":
        build_player_html()
