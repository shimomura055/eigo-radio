# ============================================================
# er011_connected_speech_equivalence_layer_trial_02.py
# CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02
# ============================================================
# 隔離Trial(Lane A、ユーザー承認2026-09-07、OPEN-122の追加検証)。
# Trial-01(`er011_connected_speech_equivalence_layer_trial_01.py`)を
# コピーして作成した独立ファイル。Trial-01自体は無変更のまま保持し、
# 本ファイルは以下を追加する:
#   1. Trial-01で発見された2件の未分類ケース("asked"→"asks"、
#      "want to"→"wanna")の個別調査(新規API呼び出しなし、Trial-01の
#      保存済みmanifest.jsonを再利用)
#   2. カテゴリA〜Gを広げた新規positiveテストセット(4件×7カテゴリ=28件)
#      +既存3パターン・Equivalence Layーいずれもfalse acceptしないことを
#      狙った新規negativeテストセット(7件、各カテゴリ最低1件)
#   3. 既存Production本文音声履歴(rerun-02・Trial-13・No.18等)からの
#      無料ASR差分マイニング
#
# 既存Production Connected Speech Validator(er011_b1_connected_speech_
# validator_01.py、OPEN-107/OPEN-110、3パターン限定でPRODUCTION_WIRED)・
# ASR routing・retry・Cost Guard・Human Review方針は一切変更しない。
#
# 安全設計: 新規カテゴリ判定は「(1)phonetic environmentが既知カテゴリに
# 該当」AND「(2)独立ASR(Secondary Azure / local faster-whisper)の
# 少なくとも1つがcanonical側を支持」の両方が揃った場合のみACCEPT
# 候補とする。単一証拠(diffの見た目だけ)では絶対にacceptしない。
#
# 書き込み範囲: 本ファイル(root)、er011_output/
# connected_speech_equivalence_layer_trial_02/ 配下のみ。Git操作なし。

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er003_b1_p9a_audio as p9a
import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as asr_routing
import er006_secondary_asr_01 as secondary_asr
import er006_preprod_hardening_01_validation as en_validator
import er008_disfluency_qa_18 as disfluency_qa
import er011_b1_connected_speech_validator_01 as csv3

try:
    import pronouncing
    _PRONOUNCING_AVAILABLE = True
except ImportError:
    _PRONOUNCING_AVAILABLE = False

OUT_DIR = "er011_output/connected_speech_equivalence_layer_trial_02"
AUDIO_DIR = f"{OUT_DIR}/audio"
RESULTS_DIR = f"{OUT_DIR}/results"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"

RERUN02_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02"
SHOWED_DIAG_DIR = f"{RERUN02_DIR}/audit/point_two_showed_show_diag"

# Trial-01の既存出力(読み取り専用、再利用のみ・追加課金なし)
TRIAL01_MANIFEST_PATH = "er011_output/connected_speech_equivalence_layer_trial_01/results/manifest.json"

# 既存Production本文音声履歴(無料マイニング対象、読み取り専用)。
# er011_output配下の全attempts_log(tts_generation_results.json)を対象に、
# 英語segmentでasr_textがcanonical_textと食い違う記録(かつ単純な句読点
# 正規化=EXACT_MATCH/NORMALIZED_MATCHではないもの)を無料で抽出する。
PRODUCTION_HISTORY_GLOB = "er011_output/**/tts_generation_results.json"

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 800.0

for d in (OUT_DIR, AUDIO_DIR, RESULTS_DIR, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)


def log(msg):
    print(msg, flush=True)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ============================================================
# Part 0: コスト計測(既存pricing_snapshot.json基準。azure Secondary ASR
# 呼び出しは既存er005_cost_logger._patch_azure()の対象外(別関数)の
# ため、本Trialで独自にrecord()して累積コストへ含める)
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
        "usage_source": "LOCAL_WAV_HEADER_EXACT_MANUAL_RECORD_TRIAL01",
    })


# ============================================================
# Part 1: ARPAbet音韻特徴テーブル + Connected Speechカテゴリ(A〜G)分類
# ============================================================
# manner, place, voiced
CONSONANT_FEATURES = {
    "P": ("stop", "bilabial", False), "B": ("stop", "bilabial", True),
    "T": ("stop", "alveolar", False), "D": ("stop", "alveolar", True),
    "K": ("stop", "velar", False), "G": ("stop", "velar", True),
    "CH": ("affricate", "postalveolar", False), "JH": ("affricate", "postalveolar", True),
    "F": ("fricative", "labiodental", False), "V": ("fricative", "labiodental", True),
    "TH": ("fricative", "dental", False), "DH": ("fricative", "dental", True),
    "S": ("fricative", "alveolar", False), "Z": ("fricative", "alveolar", True),
    "SH": ("fricative", "postalveolar", False), "ZH": ("fricative", "postalveolar", True),
    "HH": ("fricative", "glottal", False),
    "M": ("nasal", "bilabial", True), "N": ("nasal", "alveolar", True), "NG": ("nasal", "velar", True),
    "L": ("liquid", "alveolar", True), "R": ("liquid", "alveolar", True),
    "Y": ("glide", "palatal", True), "W": ("glide", "labiovelar", True),
}
SIBILANT_ARPABET = {"S", "Z", "SH", "ZH", "CH", "JH"}


def _strip_stress(ph: str) -> str:
    return "".join(c for c in ph if not c.isdigit())


def word_phones(word: str) -> list[str] | None:
    """CMU辞書(pronouncing、既存homophone_enと同じライブラリ)から代表
    (先頭)発音のARPAbet音素列を返す。辞書に無ければNone。"""
    if not _PRONOUNCING_AVAILABLE:
        return None
    w = word.lower().strip(".,!?;:\"'")
    variants = pronouncing.phones_for_word(w)
    if not variants:
        return None
    return [_strip_stress(p) for p in variants[0].split()]


def phonetic_environment_categories(final_phoneme: str | None, initial_phoneme: str | None) -> list[dict]:
    """語末で脱落した(と疑われる)音素と、次語頭の音素から、Connected
    Speechカテゴリ(A〜G)候補を返す(複数該当しうる、best-effort)。
    ユーザー指示のA〜G分類に対応:
      A: 語末子音の弱化・無開放(final stop weakening/unreleased)
      B: /t,d/の弱化・脱落的知覚(alveolar stop reduction、Aの下位)
      C: 語境界での同一・類似子音の融合(homorganic fusion)
      D: assimilation(調音位置同化)
      E: coalescence(/t,d/+/j/の破擦音化、don't you/did you型)
      F: glottalization / flapping
      G: resyllabification(語境界の曖昧化、子音+母音の連結)
    """
    cats = []
    f_feat = CONSONANT_FEATURES.get(final_phoneme) if final_phoneme else None
    i_feat = CONSONANT_FEATURES.get(initial_phoneme) if initial_phoneme else None

    if f_feat is not None and i_feat is not None:
        f_manner, f_place, f_voiced = f_feat
        i_manner, i_place, i_voiced = i_feat

        if f_manner == "stop":
            cats.append({"category": "A", "rule": "final_stop_weakening_unreleased",
                         "detail": f"語末の破裂音({final_phoneme})が、後続子音({initial_phoneme})の前で"
                                   "無開放・弱化しやすい環境。"})
            if final_phoneme in ("T", "D"):
                cats.append({"category": "B", "rule": "alveolar_stop_reduction",
                             "detail": "歯茎破裂音(/t/または/d/)は特に脱落的に知覚されやすい。"})

        if f_place == i_place:
            cats.append({"category": "C", "rule": "homorganic_consonant_fusion",
                         "detail": f"語末({final_phoneme}, {f_place})と次語頭({initial_phoneme}, {i_place})が"
                                   "同じ調音位置のため、境界で融合・区別困難になりやすい。"})

        if final_phoneme in ("N", "T", "D") and i_place not in (None, "alveolar"):
            cats.append({"category": "D", "rule": "place_assimilation",
                         "detail": f"歯茎音({final_phoneme})が、後続子音の調音位置({i_place})へ同化しやすい。"})

        if final_phoneme in ("T", "D") and initial_phoneme == "Y":
            cats.append({"category": "E", "rule": "coalescence_yod",
                         "detail": "/t,d/+/j/がchurch/judge系の破擦音へ融合しやすい(don't you/did you型)。"})

        if final_phoneme == "T":
            cats.append({"category": "F", "rule": "glottalization_candidate",
                         "detail": "語末/t/は後続子音の前で声門閉鎖化しやすい。"})

    elif f_feat is not None and i_feat is None:
        # 次語頭が母音(resyllabification / 母音間ならflapping)
        cats.append({"category": "G", "rule": "resyllabification_liaison",
                     "detail": f"語末子音({final_phoneme})が次語頭の母音へ連結し、音節の切れ目が"
                               "語境界とずれる。"})
        if final_phoneme in ("T", "D"):
            cats.append({"category": "F", "rule": "flapping_intervocalic",
                         "detail": "母音に挟まれた/t,d/はアメリカ英語でflap化しやすい。"})

    return cats


# ============================================================
# Part 2: Deletion-shaped diffの一般化検出(ARPAbet音素prefix比較。
# 既存csv3.final_ed_sound/final_s_sound(綴り規則ベース、-s/-es/-ed
# 限定)を置き換えず、その外側(任意の語末子音脱落)を音素ベースで
# 追加検出する)
# ============================================================
def phoneme_prefix_drop(canonical_word: str, asr_word: str) -> dict | None:
    """asr_wordの音素列がcanonical_wordの音素列の"先頭部分"と完全一致し、
    canonical側に1〜2音素だけ多い(=語末が脱落したように見える)場合、
    脱落した音素のリストを返す。一致しなければNone(false accept防止:
    語幹自体が異なる場合や母音が変わっている場合はNoneになる)。"""
    c_phones = word_phones(canonical_word)
    a_phones = word_phones(asr_word)
    if not c_phones or not a_phones:
        return None
    if len(c_phones) <= len(a_phones):
        return None
    if c_phones[:len(a_phones)] != a_phones:
        return None
    dropped = c_phones[len(a_phones):]
    if len(dropped) > 2:
        return None
    if not all(p in CONSONANT_FEATURES for p in dropped):
        return None  # 母音の脱落は対象外(安全側)
    return {"canonical_phones": c_phones, "asr_phones": a_phones, "dropped_phonemes": dropped}


def phoneme_final_place_substitution(canonical_word: str, asr_word: str) -> dict | None:
    """Assimilation(カテゴリD)は脱落ではなく、語末子音が後続語頭の
    調音位置へ"置き換わる"形で現れる(例: ten -> tem)。canonical/asrの
    音素列が最終音素以外すべて一致し、最終音素どうしがmanner・voicingは
    同じでplaceだけ異なる場合のみ、assimilationの候補として検出する
    (安全側: manner/voicingが変わる場合は語幹自体の置換とみなし対象外)。"""
    c_phones = word_phones(canonical_word)
    a_phones = word_phones(asr_word)
    if not c_phones or not a_phones or len(c_phones) != len(a_phones) or len(c_phones) < 1:
        return None
    if c_phones[:-1] != a_phones[:-1]:
        return None
    c_final, a_final = c_phones[-1], a_phones[-1]
    if c_final == a_final:
        return None
    c_feat, a_feat = CONSONANT_FEATURES.get(c_final), CONSONANT_FEATURES.get(a_final)
    if c_feat is None or a_feat is None:
        return None
    c_manner, c_place, c_voiced = c_feat
    a_manner, a_place, a_voiced = a_feat
    if c_manner != a_manner or c_voiced != a_voiced or c_place == a_place:
        return None
    return {"canonical_phones": c_phones, "asr_phones": a_phones,
            "canonical_final_phoneme": c_final, "asr_final_phoneme": a_final,
            "assimilated_to_place": a_place}


# ============================================================
# Part 3: 多証拠Equivalence Layer本体
# ============================================================
def _word_at_diff_matches_canonical(canonical_text: str, other_text: str, diff: dict) -> bool | None:
    """other_text(Secondary ASRやlocal ASRの書き起こし)が、diff位置で
    canonical側の語を支持しているかを判定する。position-based(diffの
    index位置の単語を直接比較)で判定する(word_diff()の"最初の食い違い"
    方式だと、diff位置より後ろの箇所で別の食い違いがある場合に誤って
    判定不能になってしまうため、直接position比較を用いる)。
      True  -> 支持(corroboration、その位置でcanonical語と一致)
      False -> 支持しない(reduced/altered形と一致、またはさらに別の語)
      None  -> other_textが与えられていない、位置がother_text長を超える等
    既知の限界: canonical/other_text間でdiff位置より手前に語数のずれ
    (挿入・脱落)がある場合、position-based比較がずれる可能性がある
    (今回のテストデータでは発生しなかったことを確認済み、Report参照)。
    """
    if not other_text:
        return None
    c_words = csv3.tokenize(canonical_text)
    o_words = csv3.tokenize(other_text)
    idx = diff.get("index")
    c_word = diff.get("canonical_word")
    if idx is None or c_word is None or idx >= len(o_words) or idx >= len(c_words):
        return None
    o_word = o_words[idx]
    return o_word.lower().rstrip(".,!?;:\"'") == c_word.lower().rstrip(".,!?;:\"'")


def classify_connected_speech_equivalence(canonical_text: str, asr_text: str,
                                           secondary_asr_text: str | None = None,
                                           local_asr_text: str | None = None) -> dict:
    """既存3パターン(csv3.classify_connected_speech)をまず無変更で呼び、
    ACCEPT/RESEGMENTATIONならそのまま返す(既存挙動を一切変えない)。
    UNCLASSIFIEDの場合のみ、一般化Equivalence Layer(音素prefix脱落検出
    + phonetic environmentカテゴリA〜G + 独立ASR corroboration)を適用する。
    """
    existing = csv3.classify_connected_speech(canonical_text, asr_text)
    if existing["new_judgment"] in ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION"):
        return {
            "layer_judgment": existing["new_judgment"],
            "source": "existing_3_pattern_unchanged",
            "existing_result": existing,
            "equivalence_layer_info": None,
        }

    diff = existing.get("diff")
    if diff is None or diff.get("canonical_word") is None or diff.get("asr_word") is None:
        return {"layer_judgment": "NO_DELETION_SHAPED_DIFF", "source": "equivalence_layer",
                "existing_result": existing, "equivalence_layer_info": None}

    c_word, a_word, next_word = diff["canonical_word"], diff["asr_word"], diff["next_word"]
    next_phones = word_phones(next_word) if next_word else None
    initial_phoneme = next_phones[0] if next_phones else None

    drop_info = phoneme_prefix_drop(c_word, a_word)
    subst_info = None
    if drop_info is not None:
        diff_shape = "deletion"
        final_dropped = drop_info["dropped_phonemes"][-1]
        categories = phonetic_environment_categories(final_dropped, initial_phoneme)
    else:
        subst_info = phoneme_final_place_substitution(c_word, a_word)
        if subst_info is None:
            return {"layer_judgment": "NOT_A_PHONEME_PREFIX_DROP", "source": "equivalence_layer",
                    "existing_result": existing, "equivalence_layer_info": None,
                    "diff": diff}
        diff_shape = "place_substitution"
        final_dropped = subst_info["canonical_final_phoneme"]
        categories = phonetic_environment_categories(final_dropped, initial_phoneme)
        # assimilation(カテゴリD)は「置換先の音素placeが、実際に次語頭の
        # placeと一致する」場合のみ候補にする(単なる語幹置換の誤検出防止)
        i_feat = CONSONANT_FEATURES.get(initial_phoneme) if initial_phoneme else None
        assimilated_ok = i_feat is not None and i_feat[1] == subst_info["assimilated_to_place"]
        categories = [c for c in categories if c["category"] == "D"] if assimilated_ok else []

    info = {
        "diff": diff, "diff_shape": diff_shape, "drop_info": drop_info, "substitution_info": subst_info,
        "final_dropped_phoneme": final_dropped,
        "next_word_initial_phoneme": initial_phoneme, "categories_matched": categories,
    }

    if not categories:
        return {"layer_judgment": "NO_KNOWN_CATEGORY_MATCH", "source": "equivalence_layer",
                "existing_result": existing, "equivalence_layer_info": info}

    secondary_support = _word_at_diff_matches_canonical(canonical_text, secondary_asr_text, diff)
    local_support = _word_at_diff_matches_canonical(canonical_text, local_asr_text, diff)
    info["secondary_asr_supports_canonical"] = secondary_support
    info["local_asr_supports_canonical"] = local_support

    corroboration_count = sum(1 for v in (secondary_support, local_support) if v is True)
    contradiction_count = sum(1 for v in (secondary_support, local_support) if v is False)
    info["corroboration_count"] = corroboration_count
    info["contradiction_count"] = contradiction_count

    cat_labels = {c["category"] for c in categories}
    high_confidence_cats = cat_labels & {"A", "B", "C"}

    if corroboration_count == 0:
        judgment = "EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE"
    elif contradiction_count > 0:
        # 独立ASR同士が食い違う(一方はcanonicalを支持、一方は否定) ->
        # 安全側でwarning止まり、blockingしない扱いにはしない
        judgment = "EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT"
    elif high_confidence_cats:
        judgment = "EQUIVALENCE_LAYER_ACCEPT"
    else:
        judgment = "EQUIVALENCE_LAYER_PASS_WITH_WARNING"

    return {"layer_judgment": judgment, "source": "equivalence_layer",
            "existing_result": existing, "equivalence_layer_info": info}


# ============================================================
# Part 4: テストセット定義
# ============================================================
# Positive(Trial-02新規、Trial-01の9件とは別文): カテゴリA〜G各4件
# (計28件)、B1/A2の実運用に近い長さ・語彙の文。各文はカテゴリ判定用
# bigramを事前に`phonetic_environment_categories()`で検証済み(script外の
# 検証で確認、Reportに記載)。複数カテゴリに同時該当する文は実際の英語
# 音韻現象として自然なため、Trial-01同様category_expectedに複数ラベルを
# 許容する。
POSITIVE_ITEMS = [
    # --- Category A(語末破裂音の弱化・無開放、非alveolar中心) ---
    {"id": "T2A1_shop_closes", "category_expected": "A",
     "canonical": "The shop closes early on weekends, so plan your visit."},
    {"id": "T2A2_stop_watching", "category_expected": "A",
     "canonical": "Officials plan to stop watching the market so closely."},
    {"id": "T2A3_drug_store", "category_expected": "A",
     "canonical": "The city will renovate the old drug store downtown."},
    {"id": "T2A4_bike_path", "category_expected": "A",
     "canonical": "Runners often use the new bike path near the river."},
    # --- Category B(alveolar/t,d/の弱化、Aの下位) ---
    {"id": "T2B1_worked_hard", "category_expected": "A/B/D/F",
     "canonical": "She worked hard to finish the report on time."},
    {"id": "T2B2_packed_bags", "category_expected": "A/B/D/F",
     "canonical": "He packed bags for the long business trip."},
    {"id": "T2B3_picked_books", "category_expected": "A/B/D/F",
     "canonical": "The clerk picked books from the top shelf."},
    {"id": "T2B4_planned_carefully", "category_expected": "A/B/D",
     "canonical": "Volunteers planned carefully before the charity event."},
    # --- Category C(語境界での同一・類似子音の融合) ---
    {"id": "T2C1_trip_plan", "category_expected": "A/C",
     "canonical": "A good trip plan should include enough rest days."},
    {"id": "T2C2_grab_bag", "category_expected": "A/C",
     "canonical": "Each visitor received a small grab bag of gifts."},
    {"id": "T2C3_job_market", "category_expected": "A/C",
     "canonical": "The company's job market report surprised analysts."},
    {"id": "T2C4_quick_glance", "category_expected": "A/C",
     "canonical": "A quick glance at the schedule showed no changes."},
    # --- Category D(assimilation、調音位置同化) ---
    {"id": "T2D1_turn_back", "category_expected": "D",
     "canonical": "Traffic slowed until drivers could turn back safely."},
    {"id": "T2D2_run_fast", "category_expected": "D",
     "canonical": "The runner tried to run fast down the steep hill."},
    {"id": "T2D3_sun_barely", "category_expected": "D",
     "canonical": "The sun barely rose over the quiet hills this morning."},
    {"id": "T2D4_win_big", "category_expected": "D",
     "canonical": "The team hoped to win big at the tournament."},
    # --- Category E(coalescence、/t,d/+you型) ---
    {"id": "T2E1_could_you", "category_expected": "A/B/D/E",
     "canonical": "Could you send the report before noon?"},
    {"id": "T2E2_did_you", "category_expected": "A/B/D/E",
     "canonical": "Did you remember to lock the front door?"},
    {"id": "T2E3_would_you", "category_expected": "A/B/D/E",
     "canonical": "Would you mind checking the numbers again?"},
    {"id": "T2E4_meet_you", "category_expected": "A/B/D/E/F",
     "canonical": "I promise I will meet you at the station."},
    # --- Category F(glottalization/flapping、語末/t/中心) ---
    {"id": "T2F1_not_bad", "category_expected": "A/B/D/F",
     "canonical": "That was not bad for a first attempt."},
    {"id": "T2F2_great_job", "category_expected": "A/B/D/F",
     "canonical": "It was a great job by the whole team."},
    {"id": "T2F3_light_switch", "category_expected": "A/B/C/F",
     "canonical": "Please turn off the light switch before leaving."},
    {"id": "T2F4_quiet_place", "category_expected": "A/B/D/F",
     "canonical": "The old library was always a quiet place to study."},
    # --- Category G(resyllabification、語末子音+次語頭母音) ---
    {"id": "T2G1_an_apple", "category_expected": "G",
     "canonical": "Doctors say an apple a day helps overall health."},
    {"id": "T2G2_good_idea", "category_expected": "G/F",
     "canonical": "That was such a good idea for the festival."},
    {"id": "T2G3_made_it", "category_expected": "G/F",
     "canonical": "The mistake made it hard to trust the final results."},
    {"id": "T2G4_quick_answer", "category_expected": "G",
     "canonical": "A quick answer is not always the right one."},
]

# Negative controls(Trial-02新規、7件、各カテゴリ最低1件): claimed_
# canonicalとは本当に異なる内容(時制)を実際にTTSへ渡し、独立ASR
# (Secondary/local)も実発話どおり一致する設計。いずれも
# `phoneme_prefix_drop()`が検出する"語尾脱落"と全く同じ音素形をもつ
# 最も厳しい敵対的対照(script外で事前検証、Reportに記載): 複数主語+
# 現在形(3人称単数の-sを要しない)にすることで、時制を変えても両方とも
# 文法的に正しい文になるよう設計した。
NEGATIVE_ITEMS = [
    {"id": "T2N1_pack_not_packed", "category_expected": "A/B/D/F",
     "claimed_canonical": "The workers packed bags for the long delivery route.",
     "actually_spoken": "The workers pack bags for the long delivery route.",
     "note": "T2B2との最小対(packed/pack)、時制の真の内容不一致"},
    {"id": "T2N2_plan_not_planned", "category_expected": "A/B/D",
     "claimed_canonical": "Volunteers planned carefully before the charity event.",
     "actually_spoken": "Volunteers plan carefully before the charity event.",
     "note": "T2B4との最小対(planned/plan)、時制の真の内容不一致"},
    {"id": "T2N3_open_not_opened", "category_expected": "A/B/C",
     "claimed_canonical": "These old gates opened slowly during the ceremony.",
     "actually_spoken": "These old gates open slowly during the ceremony.",
     "note": "OPEN-107型(opened/open)の新規陰性対照、時制の真の内容不一致"},
    {"id": "T2N4_turn_not_turned", "category_expected": "D",
     "claimed_canonical": "The cars turned back before reaching the bridge.",
     "actually_spoken": "The cars turn back before reaching the bridge.",
     "note": "T2D1との最小対(turned/turn)、時制の真の内容不一致"},
    {"id": "T2N5_help_not_helped", "category_expected": "A/B/D/E/F",
     "claimed_canonical": "The staff helped you with every step of registration.",
     "actually_spoken": "The staff help you with every step of registration.",
     "note": "E環境(help/helped+you)の陰性対照、時制の真の内容不一致"},
    {"id": "T2N6_open_it_not_opened_it", "category_expected": "G/F",
     "claimed_canonical": "Technicians opened it immediately after the alarm sounded.",
     "actually_spoken": "Technicians open it immediately after the alarm sounded.",
     "note": "G環境(opened/open+it)の陰性対照、時制の真の内容不一致"},
    {"id": "T2N7_watch_not_watched", "category_expected": "A/B/D/F",
     "claimed_canonical": "The guards watched closely during the entire event.",
     "actually_spoken": "The guards watch closely during the entire event.",
     "note": "T2F系との最小対(watched/watch)、時制の真の内容不一致"},
]

# Regression: 既存3パターンのfixture(er011_no18_connected_speech_
# reading_resolver_wiring_08_test.pyより、テキストのみ再利用、無変更)
EXISTING_PATTERN_REGRESSION = [
    {"id": "R1_studies_suggest_PatternA",
     "canonical": "The studies suggest that a phone can affect attention even when you do not check it.",
     "asr": "The study suggests that a phone can affect attention even when you do not check it.",
     "expect": "CONNECTED_SPEECH_ACCEPT"},
    {"id": "R2_opened_to_PatternB",
     "canonical": "Your phone does not have to be opened to become part of the task.",
     "asr": "Your phone does not have to be open to become part of the task.",
     "expect": "CONNECTED_SPEECH_ACCEPT"},
    {"id": "R3_survey_suggest_PatternC",
     "canonical": "The studies and the survey suggest that a phone can affect people even when they do not check it.",
     "asr": "The studies and the surveys suggest that a phone can affect people even when they do not check it.",
     "expect": "CONNECTED_SPEECH_RESEGMENTATION"},
    {"id": "R4_unrelated_mismatch",
     "canonical": "The report shows a clear increase in visits.",
     "asr": "The report shows a clear decrease in visits.",
     "expect": "UNCLASSIFIED"},
]


# ============================================================
# Part 4b: Rule-engine単体sanity check(合成diff、実音声ではない)
# ============================================================
# 実測(P1〜P9の実TTS+実ASR)では、カテゴリC〜Gの環境そのものは正しく
# 音声化されたが、Primary ASRが実際に脱落型の誤りを再現しなかった
# (Reportの§5参照)。ルールエンジン自体がカテゴリB/C/D/E/Fを正しく
# 判定し、かつcorroboration有無で挙動が正しく変わることを、audio非依存の
# 合成diff(実際の音声・実ASR呼び出しではない、テキストのみ、追加課金
# 無し)で個別に確認する。これは「実音声でのfalse reject発生頻度」の
# 証拠ではなく、「ルールが設計どおり動くか」の単体確認である。
SYNTHETIC_RULE_CHECKS = [
    # "ten"の同化先("tem")はCMU辞書に実在しない綴りのため使えない。
    # sun/sum(いずれもCMU辞書に実在する語)で、後続語頭が両唇音の場合の
    # 歯茎鼻音->両唇鼻音同化(教科書的なplace assimilationの例、
    # "green paper"型と同型)を検証する。
    {"id": "SYN_D_sun_sum_assimilation", "category": "D", "diff_shape": "place_substitution",
     "canonical": "The sun barely rose over the hills.",
     "asr_reduced": "The sum barely rose over the hills.",
     "corroborating_text": "The sun barely rose over the hills.",  # 支持あり(独立ASRはsunのまま)
     "contradicting_text": "The sum barely rose over the hills."},  # 支持なし(独立ASRもsum)
]


def run_synthetic_rule_checks():
    """全パイプライン(word_diff経由)の合成diffテスト(音素prefix脱落
    ではなくplace substitution=assimilationの検出、実音声ではない)。"""
    log("\n=== Rule-engine単体sanity check A: 合成diff(place substitution/assimilation、実音声ではない、追加課金なし) ===")
    results = []
    for case in SYNTHETIC_RULE_CHECKS:
        with_support = classify_connected_speech_equivalence(
            case["canonical"], case["asr_reduced"],
            secondary_asr_text=case["corroborating_text"], local_asr_text=None)
        without_support = classify_connected_speech_equivalence(
            case["canonical"], case["asr_reduced"],
            secondary_asr_text=case["contradicting_text"], local_asr_text=None)
        info = with_support.get("equivalence_layer_info") or {}
        matched_cats = {c["category"] for c in info.get("categories_matched", [])}
        ok_category = case["category"] in matched_cats
        ok_gate = (with_support["layer_judgment"] in
                   ("EQUIVALENCE_LAYER_ACCEPT", "EQUIVALENCE_LAYER_PASS_WITH_WARNING")) and \
                  (without_support["layer_judgment"] == "EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE")
        log(f"  [{'OK' if (ok_category and ok_gate) else 'FAIL'}] {case['id']}: "
            f"matched_categories={sorted(matched_cats)} "
            f"with_support={with_support['layer_judgment']} without_support={without_support['layer_judgment']}")
        results.append({
            "id": case["id"], "expected_category": case["category"],
            "matched_categories": sorted(matched_cats), "category_ok": ok_category,
            "with_support_judgment": with_support["layer_judgment"],
            "without_support_judgment": without_support["layer_judgment"],
            "gate_ok": ok_gate,
        })

    # ------------------------------------------------------------
    # sanity check B: phonetic_environment_categories()単体(音素環境の
    # 分類ロジックのみを直接検証。coalescence(E)/flapping(F)は、
    # ASRが実際にそれらしい綴りで書き起こすことがほぼ無い[標準綴りへ
    # 正規化されるため]、text-diff経由での合成テストが非現実的なので、
    # 分類サブ関数を直接呼ぶunit testとする)。
    # ------------------------------------------------------------
    log("\n=== Rule-engine単体sanity check B: phonetic_environment_categories()直接呼び出し(音素環境分類のみ、実音声ではない) ===")
    direct_cases = [
        {"id": "SYN_E_direct_dont_you", "final": "T", "initial": "Y", "expect_category": "E"},
        {"id": "SYN_F_direct_get_it", "final": "T", "initial": None, "expect_category": "F"},
        {"id": "SYN_G_direct_an_apple", "final": "N", "initial": None, "expect_category": "G"},
        {"id": "SYN_C_direct_big_cat", "final": "G", "initial": "K", "expect_category": "C"},
    ]
    for case in direct_cases:
        cats = phonetic_environment_categories(case["final"], case["initial"])
        labels = {c["category"] for c in cats}
        ok = case["expect_category"] in labels
        log(f"  [{'OK' if ok else 'FAIL'}] {case['id']}: final={case['final']} initial={case['initial']} "
            f"-> matched={sorted(labels)} (expect {case['expect_category']} included)")
        results.append({"id": case["id"], "expected_category": case["expect_category"],
                        "matched_categories": sorted(labels), "category_ok": ok,
                        "with_support_judgment": "N/A_DIRECT_UNIT_TEST", "without_support_judgment": "N/A",
                        "gate_ok": None})
    return results


# ============================================================
# Part 5: 実行(TTS生成+複数ASR経路+判定)
# ============================================================
def local_verbatim_text(path):
    words = disfluency_qa.transcribe_verbatim(path, language="en", model_size="small")
    return " ".join(w["text"].strip() for w in words).strip()


def generate_and_evaluate(item_id, canonical_text, spoken_text, category_expected=None, note=None):
    """spoken_text(実際にTTSへ渡すテキスト)を生成し、Primary/Secondary/
    Local ASRを実行、Equivalence Layerで判定する。canonical_text!=
    spoken_textの場合は陰性対照(意図的な内容不一致)を意味する。"""
    out_path = f"{AUDIO_DIR}/{item_id}.wav"
    log(f"\n--- {item_id} ---")
    log(f"  claimed_canonical: {canonical_text!r}")
    if spoken_text != canonical_text:
        log(f"  actually_spoken (陰性対照、実際にTTSへ渡すテキスト): {spoken_text!r}")

    if os.path.exists(out_path):
        log(f"  [reuse] {out_path}既存のためTTS再生成をスキップ(既に同一Trial内で生成済み、二重課金防止)")
        gen = {"status": "OK", "reused": True}
    else:
        gen = p9a.generate_narration_snippet(spoken_text, "en", out_path)
        assert_budget_ok(f"after TTS {item_id}")
        if gen.get("status") != "OK":
            log(f"  !! TTS generation failed: {gen.get('reason')}")
            return {"id": item_id, "status": "TTS_FAILED", "reason": gen.get("reason")}

    primary_text, primary_err = asr_routing.transcribe(out_path, language="en")
    assert_budget_ok(f"after PrimaryASR {item_id}")

    import soundfile as sf
    dur = sf.info(out_path).duration
    secondary_text, secondary_err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
        out_path, language="en-US", phrases=None)
    record_azure_call(out_path, dur)
    assert_budget_ok(f"after SecondaryASR {item_id}")

    local_text = local_verbatim_text(out_path)

    equiv = classify_connected_speech_equivalence(
        canonical_text, primary_text or "", secondary_text, local_text)

    existing_en_validator = en_validator.classify_asr_match(canonical_text, primary_text or "")

    result = {
        "id": item_id, "status": "OK", "category_expected": category_expected, "note": note,
        "claimed_canonical": canonical_text, "actually_spoken_text": spoken_text,
        "is_negative_control": spoken_text != canonical_text,
        "audio_path": out_path, "audio_sha256": sha256_of(out_path), "duration_seconds": round(dur, 3),
        "primary_asr_text": primary_text, "primary_asr_error": primary_err,
        "secondary_asr_text": secondary_text, "secondary_asr_error": secondary_err,
        "local_asr_text": local_text,
        "existing_en_validator_classification": existing_en_validator.classification,
        "existing_en_validator_should_pass": existing_en_validator.should_pass,
        "equivalence_layer_result": equiv,
    }
    log(f"  primary_asr={primary_text!r}")
    log(f"  secondary_asr={secondary_text!r}")
    log(f"  local_asr={local_text!r}")
    log(f"  existing_en_validator: {existing_en_validator.classification} (should_pass={existing_en_validator.should_pass})")
    log(f"  equivalence_layer: {equiv['layer_judgment']}")
    return result


def run_existing_pattern_regression():
    log("\n=== 既存3パターンRegression(fixture再利用、テキストのみ・API課金なし) ===")
    results = []
    for case in EXISTING_PATTERN_REGRESSION:
        equiv = classify_connected_speech_equivalence(case["canonical"], case["asr"])
        ok = (equiv["layer_judgment"] == case["expect"]) or \
             (case["expect"] == "UNCLASSIFIED" and equiv["layer_judgment"] not in
              ("EQUIVALENCE_LAYER_ACCEPT", "EQUIVALENCE_LAYER_PASS_WITH_WARNING",
               "CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION"))
        log(f"  [{'OK' if ok else 'FAIL'}] {case['id']}: expect={case['expect']} got={equiv['layer_judgment']}")
        results.append({"id": case["id"], "expect": case["expect"], "got": equiv["layer_judgment"],
                        "pass": ok, "full_result": equiv})
    return results


def load_showed_strong_flagship_evidence():
    """既存OPEN-112 Theme2 Point Two診断(2026-09-07実施、
    er011_open112_theme2_point_two_showed_show_diag_02.py)の実データを
    再利用する(新規TTS/ASR課金なし)。attempt1(Primary ASRが"show"と
    誤認識した実例)にEquivalence Layerを適用する。"""
    log("\n=== Flagship実例: A2 Point Two 'showed strong' (既存診断データ再利用、追加課金なし) ===")
    raw_path = f"{SHOWED_DIAG_DIR}/diag_raw_evidence.json"
    nobias_path = f"{SHOWED_DIAG_DIR}/secondary_asr_no_phrase_bias.json"
    if not os.path.exists(raw_path):
        log(f"  !! 既存診断データが見つかりません: {raw_path}")
        return None
    raw = json.load(open(raw_path, encoding="utf-8"))
    nobias = json.load(open(nobias_path, encoding="utf-8")) if os.path.exists(nobias_path) else []

    # word_diff()はindex 0から位置合わせして最初の食い違いを探すため、
    # windowed(文の途中から始まる)clipではなく、canonical全文と3経路とも
    # full clipの書き起こしを使う(語の位置が正しく揃う)。windowedの
    # no-phrase-bias Secondary結果("Still showed strong interest.")は
    # 補足証拠として別途記録するのみで、判定入力には使わない。
    canonical_snippet = raw["canonical_text"]
    primary_attempt1 = next(
        r["asr_text"] for r in raw["production_asr_full_noprompt"] if r["label"] == "attempt1")
    secondary_full_attempt1 = next(
        r["asr_text"] for r in raw["secondary_asr_full"] if r["label"] == "attempt1")
    local_attempt1 = next(
        r["transcript"] for r in raw["local_verbatim_full"] if r["label"] == "attempt1")
    secondary_nobias_windowed_attempt1 = next(
        (r["asr_text"] for r in nobias if r["label"] == "attempt1_tight"), None)

    log(f"  canonical(先頭140字): {canonical_snippet[:140]!r}...")
    log(f"  primary_asr full clip(実データ): {primary_attempt1[:140]!r}...")
    log(f"  secondary_asr full clip(実データ、phrase_list=['showed']付与): {secondary_full_attempt1[:140]!r}...")
    log(f"  local_asr full clip(実データ): {local_attempt1[:140]!r}...")
    log(f"  [補足] secondary_asr windowed no-phrase-bias(実データ): {secondary_nobias_windowed_attempt1!r}")

    equiv = classify_connected_speech_equivalence(
        canonical_snippet, primary_attempt1, secondary_full_attempt1, local_attempt1)
    log(f"  equivalence_layer: {equiv['layer_judgment']}")

    return {
        "id": "FLAGSHIP_showed_strong_attempt1", "source": "既存Production診断データ再利用(追加課金なし)",
        "canonical_snippet": canonical_snippet,
        "primary_asr_text": primary_attempt1,
        "secondary_asr_text_full_clip_phrase_biased": secondary_full_attempt1,
        "secondary_asr_text_windowed_no_phrase_bias_supplementary": secondary_nobias_windowed_attempt1,
        "local_asr_text": local_attempt1,
        "existing_3pattern_replay": raw.get("connected_speech_validator_replay"),
        "equivalence_layer_result": equiv,
    }


# ============================================================
# Part 6: Trial-01の2件("asked"→"asks"、"want to"→"wanna")の個別調査
# (新規API呼び出しなし、Trial-01保存済みmanifest.jsonを再利用のみ)
# ============================================================
def investigate_trial01_unclassified_cases():
    """Trial-01のP1_asked_them("asked"→"asks")・P6_dont_you("want to"→
    "wanna")について、canonical/Primary/Secondary/local ASR・既存
    Validator結果・Equivalence Layer結果を突き合わせ、Connected Speechの
    一種として吸収すべきか、別failure modeとして分離すべきかを判定する。
    """
    log("\n=== Trial-01の2件の個別調査(保存済みmanifest.json再利用、追加課金なし) ===")
    if not os.path.exists(TRIAL01_MANIFEST_PATH):
        log(f"  !! Trial-01 manifestが見つかりません: {TRIAL01_MANIFEST_PATH}")
        return None
    m = json.load(open(TRIAL01_MANIFEST_PATH, encoding="utf-8"))
    by_id = {r["id"]: r for r in m.get("positive_results", [])}

    investigations = {}
    for item_id, label in (("P1_asked_them", "tense_substitution_asked_to_asks"),
                            ("P6_dont_you", "wanna_normalization_want_to_to_wanna")):
        r = by_id.get(item_id)
        if r is None:
            log(f"  !! {item_id} がTrial-01 manifestに見つかりません")
            continue
        existing = r["equivalence_layer_result"]["existing_result"]
        diff = existing.get("diff") or {}
        c_word, a_word = diff.get("canonical_word"), diff.get("asr_word")

        drop_info = phoneme_prefix_drop(c_word, a_word) if c_word and a_word else None
        subst_info = phoneme_final_place_substitution(c_word, a_word) if c_word and a_word else None
        c_phones = word_phones(c_word) if c_word else None
        a_phones = word_phones(a_word) if a_word else None

        # 3経路(Primary/Secondary/local)がdiff位置でどの語形を支持したか
        secondary_supports_canonical = _word_at_diff_matches_canonical(
            r["claimed_canonical"], r["secondary_asr_text"], diff)
        local_supports_canonical = _word_at_diff_matches_canonical(
            r["claimed_canonical"], r["local_asr_text"], diff)

        # 分類判定(ロジック上の理由を機械的に記録、実装はしない):
        #   - phoneme_prefix_drop/phoneme_final_place_substitutionのいずれも
        #     Noneなら、既存Equivalence Layer(カテゴリA〜G)の対象外
        #     (diff形状がConnected Speechの音素的部分集合[脱落/置換]と
        #     一致しない)
        if drop_info is None and subst_info is None:
            shape_verdict = "NOT_A_CONNECTED_SPEECH_PHONEME_SHAPE"
            reason = ("canonical語とASR語の音素列が、末尾1〜2音素のみ脱落 "
                       "(phoneme_prefix_drop)、または末尾音素のみ調音位置が "
                       "異なる(phoneme_final_place_substitution、manner/voicing "
                       "は同一)、のいずれの形にも一致しない。すなわち、"
                       "「語末の弱化・脱落・同化」という物理的に連続的な "
                       "音韻現象では説明できない、語幹自体が別の語(または "
                       "別の屈折形)に置き換わった形のdiffである。")
        else:
            shape_verdict = "MATCHES_CONNECTED_SPEECH_PHONEME_SHAPE_BUT_UNTESTED"
            reason = "音素形はConnected Speechの脱落/置換パターンに一致する。"

        investigations[item_id] = {
            "label": label,
            "canonical_text": r["claimed_canonical"],
            "primary_asr_text": r["primary_asr_text"],
            "secondary_asr_text": r["secondary_asr_text"],
            "local_asr_text": r["local_asr_text"],
            "diff": diff,
            "canonical_word": c_word, "asr_word": a_word,
            "canonical_word_phones": c_phones, "asr_word_phones": a_phones,
            "phoneme_prefix_drop_result": drop_info,
            "phoneme_final_place_substitution_result": subst_info,
            "diff_shape_verdict": shape_verdict,
            "diff_shape_reason": reason,
            "secondary_asr_supports_canonical": secondary_supports_canonical,
            "local_asr_supports_canonical": local_supports_canonical,
            "existing_3pattern_new_judgment": existing.get("new_judgment"),
            "existing_en_validator_classification": r["existing_en_validator_classification"],
            "equivalence_layer_result_in_trial01": r["equivalence_layer_result"]["layer_judgment"],
        }
        log(f"  --- {item_id} ({label}) ---")
        log(f"    canonical_word={c_word!r} asr_word={a_word!r}")
        log(f"    canonical_word_phones={c_phones} asr_word_phones={a_phones}")
        log(f"    phoneme_prefix_drop={drop_info} phoneme_final_place_substitution={subst_info}")
        log(f"    diff_shape_verdict={shape_verdict}")
        log(f"    secondary_supports_canonical={secondary_supports_canonical} local_supports_canonical={local_supports_canonical}")
        log(f"    existing_3pattern={existing.get('new_judgment')} existing_en_validator={r['existing_en_validator_classification']}")

    # ------------------------------------------------------------
    # 個別の分類考察(機械的なverdictに加え、正直な人間可読の考察を記録。
    # 新しいValidatorロジックはここでは一切実装しない、分類・命名の
    # 提案のみ)
    # ------------------------------------------------------------
    notes = {}
    asked = investigations.get("P1_asked_them")
    if asked:
        # asked(AE1 S K T)→asks(AE1 S K S): 末尾音素がTとSでmanner
        # (stop vs fricative)が異なるため、phoneme_final_place_
        # substitution()の条件(manner/voicing同一・placeのみ異なる)にも
        # 一致しない。すなわち音素的に「連続変化」では説明できない、
        # 動詞の時制/人称語尾(-ed→-s)まるごとの置換。
        notes["P1_asked_them"] = {
            "classification_label": "ASR_TENSE_AGREEMENT_SUBSTITUTION(語幹自体の屈折形置換、"
                                      "Connected Speechの音素的部分集合ではない)",
            "primary_category_bucket": "morphology/tense normalization(Connected Speechではない)",
            "explanation": (
                "canonical\"asked\"(過去形、ARPAbet AE1 S K T)とPrimary ASR\"asks\""
                "(3人称単数現在形、AE1 S K S)は、末尾音素がT(破裂音)とS(歯擦音)で"
                "manner自体が異なる。Trial-01/02のEquivalence Layerが定義する"
                "「語末子音の脱落(prefix drop)」「語末子音のplace置換のみ"
                "(manner/voicing同一)」のいずれの音素形にも一致しない。"
                "Secondary(Azure)・local(faster-whisper)はいずれも\"asked\"(canonical)"
                "と一致しており、TTSが\"asks\"と発話した証拠はない。これは"
                "「TTSが物理的に語尾子音を弱化・脱落・同化させた」のではなく、"
                "「OpenAI Primary ASR(gpt-4o-mini-transcribe)が言語モデル的な"
                "事前分布に基づき、過去形を(統計的に馴染みのある)現在形へ"
                "置換した」可能性が高い、ASR側の文法正規化(grammatical "
                "normalization/regularization)候補。既存Connected Speech "
                "Validator(3パターン)・本Equivalence Layer(カテゴリA〜G)の"
                "いずれの対象にもならず、正しく`NOT_A_PHONEME_PREFIX_DROP`/"
                "`TRUE_CONTENT_MISMATCH`のまま既存判定を維持している"
                "(false acceptしていない、安全側)。1件のみの観測であり、"
                "TTS発話自体が非決定的に\"asks\"寄りに聞こえた可能性"
                "(酸素的に近い/sk/クラスタ)を完全には排除できないため、"
                "断定的な原因確定ではない。"
            ),
            "recommend_new_failure_mode_name": "候補名(実装なし、命名提案のみ): "
                "\"ASR Verb-Inflection Normalization\"(既存OPEN-103[default単語"
                "誤発音、TTS側]・OPEN-110[単数/複数取り違え、TTS側]とは異なり、"
                "TTS発話ではなくASR側の文法正規化が疑われる点で区別すべき)。",
        }
    wanna = investigations.get("P6_dont_you")
    if wanna:
        notes["P6_dont_you"] = {
            "classification_label": "ASR_TRANSCRIPT_STYLE_NORMALIZATION(口語短縮形の表記正規化、"
                                      "Connected Speechの音韻現象自体は自然だが、既存diffモデルの"
                                      "対象外の理由が異なる)",
            "primary_category_bucket": "transcript style normalization(Connected Speechの実在現象"
                                        "に起因するが、既存の1語対1語diffモデルでは表現できない)",
            "explanation": (
                "canonical\"want to\"(2語)とPrimary ASR\"wanna\"(1語)は、"
                "英語の口語的短縮(coalescence、want+to→wanna)として音韻的には"
                "よく知られた自然な現象。しかしEquivalence Layer/既存3パターン"
                "はいずれも1語対1語のword_diff()を前提としており、2語→1語の"
                "縮約は`phoneme_prefix_drop()`(同一語数、末尾音素のみ脱落)にも"
                "`phoneme_final_place_substitution()`(同一語数、末尾音素のみ"
                "置換)にも一致しない(語数自体が変わるため)。Secondary"
                "(Azure)・local(faster-whisper)はいずれも\"want to\"(canonical、"
                "正書法的な表記)と一致しており、TTSが物理的に短縮形を発話した"
                "のか、正規形を発話しつつPrimary ASRが口語表記へ変換したのか"
                "は、本調査(既存音声データのみの再利用)だけでは音響的に"
                "断定できない。Secondary/localが正書法表記を返す一方で"
                "Primaryのみ口語表記を返す非対称性は、「ASR側の書き起こし"
                "スタイル(orthographic normalization)の違い」を強く示唆する"
                "(Primary=口語表記を許容するモデル、Secondary/local=正書法"
                "正規化する傾向、という説明が最も整合的)。"
            ),
            "recommend_new_failure_mode_name": "候補名(実装なし、命名提案のみ): "
                "\"ASR Transcript Style Normalization (Contraction Spelling)\""
                "(Connected Speechの物理現象自体は否定しないが、既存の1語対1語"
                "diffモデルの外側にあるため、モデル拡張[N-gram/多語diff対応]が"
                "必要になる、本Equivalence Layerの現行実装の範囲外の課題)。",
        }

    return {"investigations": investigations, "notes": notes}


# ============================================================
# Part 7: 既存Production本文音声履歴からの無料ASR差分マイニング
# (新規API呼び出しなし、既存tts_generation_results.jsonの再利用のみ)
# ============================================================
def mine_production_history_asr_diffs():
    """er011_output配下の既存Production本文音声履歴(rerun-02・Trial-13・
    No.18等)から、英語segmentでasr_textがcanonical_textと食い違う記録
    (単純な句読点正規化=EXACT_MATCH/NORMALIZED_MATCHは除く)を無料で
    抽出する。新規TTS/ASR呼び出しは一切行わない。"""
    log("\n=== 既存Production本文音声履歴からの無料ASR差分マイニング(追加課金なし) ===")
    import glob as _glob
    TRIVIAL = {"EXACT_MATCH", "NORMALIZED_MATCH", None}
    found = []
    for path in _glob.glob(PRODUCTION_HISTORY_GLOB, recursive=True):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for group_name in ("segments", "key_phrases"):
            group = data.get(group_name)
            if not isinstance(group, dict):
                continue
            for seg_id, seg in group.items():
                if seg.get("language") != "en":
                    continue
                canonical = seg.get("canonical_text") or seg.get("text")
                for a in (seg.get("attempts_log") or []):
                    cls = a.get("audio_classification")
                    if cls in TRIVIAL:
                        continue
                    asr = a.get("asr_text")
                    if not asr:
                        continue
                    found.append({
                        "source_file": path, "group": group_name, "seg_id": seg_id,
                        "attempt": a.get("attempt"), "canonical_text": canonical,
                        "asr_text": asr, "audio_classification": cls,
                    })
    log(f"  抽出件数(非trivialな英語ASR差分レコード): {len(found)}")
    for f in found:
        log(f"    {f['source_file']} / {f['seg_id']} attempt{f['attempt']}: {f['audio_classification']}")
    return found


def build_player_html(all_positive, all_negative, flagship, manifest_path):
    rows = []

    def row(item, label):
        if item.get("status") != "OK":
            return f"<tr><td>{label}</td><td colspan=5>{item.get('status')}: {item.get('reason','')}</td></tr>"
        equiv = item["equivalence_layer_result"]
        audio_rel = os.path.relpath(item["audio_path"], OUT_DIR)
        return (f"<tr><td>{label}</td>"
                f"<td>claimed: {item['claimed_canonical']}<br>spoken: {item['actually_spoken_text']}</td>"
                f"<td><audio controls src='{audio_rel}'></audio></td>"
                f"<td>Primary: {item['primary_asr_text']}<br>Secondary: {item['secondary_asr_text']}<br>Local: {item['local_asr_text']}</td>"
                f"<td>{item['existing_en_validator_classification']}</td>"
                f"<td>{equiv['layer_judgment']}</td></tr>")

    for item in all_positive:
        rows.append(row(item, item.get("id", "?")))
    for item in all_negative:
        rows.append(row(item, item.get("id", "?")))

    flagship_html = ""
    if flagship:
        flagship_html = (f"<h2>Flagship: showed strong (既存診断データ、file:///は元Reportのplayer.html参照)</h2>"
                          f"<p>canonical: {flagship['canonical_snippet'][:200]}...</p>"
                          f"<p>primary_asr(full clip): {flagship['primary_asr_text'][:200]}...</p>"
                          f"<p>secondary_asr(full clip, phrase-biased): {flagship['secondary_asr_text_full_clip_phrase_biased'][:200]}...</p>"
                          f"<p>secondary_asr(windowed, no phrase bias, 補足): {flagship['secondary_asr_text_windowed_no_phrase_bias_supplementary']}</p>"
                          f"<p>local_asr(full clip): {flagship['local_asr_text'][:200]}...</p>"
                          f"<p>equivalence_layer: {flagship['equivalence_layer_result']['layer_judgment']}</p>")

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Connected Speech Equivalence Layer Trial</title></head>
<body>
<h1>Connected Speech Equivalence Layer Generalization Trial 02</h1>
{flagship_html}
<h2>Positive / Negative test items</h2>
<table border="1" cellpadding="4">
<tr><th>id</th><th>text</th><th>audio</th><th>ASR</th><th>existing_en_validator</th><th>equivalence_layer</th></tr>
{''.join(rows)}
</table>
<p>manifest: {os.path.relpath(manifest_path, OUT_DIR)}</p>
</body></html>"""
    path = f"{OUT_DIR}/player.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def main():
    cost_logger.install(COST_LOG_PATH)
    log("=== Connected Speech Equivalence Layer Generalization Trial 02 開始(追加検証+Trial-01の2件調査) ===")

    # 1. 既知failure mode照合はscript外(既存SSOT読み取り)で先に実施済み
    #    (CURRENT_SPEC.md/OPEN_ITEMS.md OPEN-103/106/107/110/119参照、
    #    Reportに記載)。

    # 2. Trial-01の2件の個別調査(追加課金なし)
    trial01_investigation = investigate_trial01_unclassified_cases()

    # 3. 既存3パターンregression + synthetic rule sanity check(再利用)
    regression_results = run_existing_pattern_regression()
    synthetic_rule_results = run_synthetic_rule_checks()

    # 4. Flagship実例(既存診断データ再利用、追加課金なし)
    flagship = load_showed_strong_flagship_evidence()

    # 5. 既存Production本文音声履歴からの無料マイニング
    production_history_mining = mine_production_history_asr_diffs()

    # 6. 新規positive(カテゴリA〜G ×4件=28件)
    positive_results = []
    for item in POSITIVE_ITEMS:
        r = generate_and_evaluate(item["id"], item["canonical"], item["canonical"],
                                   category_expected=item["category_expected"])
        positive_results.append(r)

    # 7. 新規negative(7件、各カテゴリ最低1件)
    negative_results = []
    for item in NEGATIVE_ITEMS:
        r = generate_and_evaluate(item["id"], item["claimed_canonical"], item["actually_spoken"],
                                   category_expected=item.get("category_expected"), note=item["note"])
        negative_results.append(r)

    jpy_total, by_provider = compute_cost_jpy_so_far()

    manifest = {
        "trial01_unclassified_case_investigation": trial01_investigation,
        "flagship": flagship,
        "production_history_mining": production_history_mining,
        "existing_pattern_regression": regression_results,
        "synthetic_rule_engine_checks": synthetic_rule_results,
        "positive_results": positive_results,
        "negative_results": negative_results,
        "cost_jpy_total": round(jpy_total, 2),
        "cost_by_provider_jpy": by_provider,
        "budget_cap_jpy": BUDGET_JPY_CAP,
    }
    manifest_path = f"{RESULTS_DIR}/manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, default=str)

    player_path = build_player_html(positive_results, negative_results, flagship, manifest_path)

    # ------------------------------------------------------------
    # 集計: false reject(positiveでACCEPT/PASS_WITH_WARNINGに届かない)
    # /false accept(negativeでACCEPTしてしまった)、カテゴリ別内訳
    # ------------------------------------------------------------
    def is_accept(equiv):
        return equiv["layer_judgment"] in (
            "CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION",
            "EQUIVALENCE_LAYER_ACCEPT", "EQUIVALENCE_LAYER_PASS_WITH_WARNING")

    def is_exact_match(r):
        return (r.get("primary_asr_text") or "").strip().lower().rstrip(".,!?") == \
               (r.get("claimed_canonical") or "").strip().lower().rstrip(".,!?")

    false_accepts = [r["id"] for r in negative_results
                      if r.get("status") == "OK" and is_accept(r["equivalence_layer_result"])]
    positive_env_matched = [r["id"] for r in positive_results
                             if r.get("status") == "OK"
                             and r["equivalence_layer_result"].get("equivalence_layer_info")
                             and r["equivalence_layer_result"]["equivalence_layer_info"].get("categories_matched")]
    positive_natural_false_reject_rescued = [
        r["id"] for r in positive_results
        if r.get("status") == "OK" and not is_exact_match(r)
        and is_accept(r["equivalence_layer_result"])
        and r["equivalence_layer_result"]["source"] != "existing_3_pattern_unchanged"]
    positive_non_exact = [r["id"] for r in positive_results
                           if r.get("status") == "OK" and not is_exact_match(r)]

    by_category = {}
    for item in POSITIVE_ITEMS:
        cat_key = item["category_expected"]
        r = next((x for x in positive_results if x["id"] == item["id"]), None)
        if r is None or r.get("status") != "OK":
            continue
        by_category.setdefault(cat_key, []).append({
            "id": r["id"], "exact_match": is_exact_match(r),
            "judgment": r["equivalence_layer_result"]["layer_judgment"]})

    log("\n=== 集計 ===")
    log(f"  cost_total_jpy={jpy_total:.2f} (cap={BUDGET_JPY_CAP})")
    log(f"  positive件数={len(positive_results)} negative件数={len(negative_results)}")
    log(f"  positiveでexact matchではなかった(自然にASR差分が発生した)id一覧: {positive_non_exact}")
    log(f"  false_accepts (negativeでACCEPT相当になったもの、0件が必須): {false_accepts}")
    log(f"  positiveでカテゴリA-Gに該当したid一覧: {positive_env_matched}")
    log(f"  自然発生救済例(既存3パターン以外でACCEPT/PASS_WITH_WARNINGに到達): {positive_natural_false_reject_rescued}")
    log(f"  category_breakdown: {json.dumps(by_category, ensure_ascii=False)}")
    log(f"  production_history_mining件数: {len(production_history_mining)}")
    log(f"  manifest: {manifest_path}")
    log(f"  player: {player_path}")
    log("=== 完了 ===")


if __name__ == "__main__":
    main()
