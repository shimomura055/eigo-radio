# ============================================================
# er011_connected_speech_equivalence_layer_production_01.py
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# ============================================================
# CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01/02(VALIDATED、
# `CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-0{1,2}_REPORT.md`)
# で検証済みの判定ロジック(ARPAbet音韻環境カテゴリA〜G+多証拠
# corroboration)を、Productionへ無変更で移植したモジュール。
#
# ユーザー正式承認(2026-09-07、APPROVED_FOR_PRODUCTION): 適用範囲は
# **A2/B1英語本文segmentのProduction正式ASR/Validator経路のみ**。
# Key Phrase・日本語segment・Trial専用path・他用途は対象外(この制約は
# 呼び出し側[er006_secondary_asr_01.py]の明示的なopt-inフラグで担保する。
# 本モジュール自体はどこからも自動発火しない、純粋な判定ロジックのみ)。
#
# 既存Production Connected Speech Validator(er011_b1_connected_speech_
# validator_01.py、OPEN-107/OPEN-110、3パターン限定)は無変更のまま
# 最初に呼び出し、その判定(ACCEPT/RESEGMENTATION)を上書きしない
# (Trial-01/02と同じregression-safeな設計)。
#
# 安全設計(Trialのゲート条件を維持、単一Secondaryのみでの無条件accept
# を許さない):
#   (1) 音韻環境(ARPAbet)が既知カテゴリA〜Gに該当
#   (2) 独立ASR(Secondary Azure / local faster-whisper)の少なくとも1つが
#       diff位置でcanonical側を支持(corroboration)
#   の両方が揃った場合のみACCEPT/PASS_WITH_WARNING候補とする。
#   corroboration 0件 -> INSUFFICIENT_EVIDENCE(acceptしない)
#   独立ASR同士が食い違う -> MIXED_EVIDENCE_INSUFFICIENT(acceptしない)
#   corroboration>=1件かつカテゴリA/B/C -> ACCEPT
#   corroboration>=1件かつカテゴリD/E/F/G -> PASS_WITH_WARNING(記録付き)

from __future__ import annotations

import er011_b1_connected_speech_validator_01 as csv3

try:
    import pronouncing
    _PRONOUNCING_AVAILABLE = True
except ImportError:
    _PRONOUNCING_AVAILABLE = False

# ============================================================
# Part 1: ARPAbet音韻特徴テーブル + Connected Speechカテゴリ(A〜G)分類
# (Trial-01/02から無変更で移植)
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
# 追加検出する。Trial-01/02から無変更で移植)
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
# Part 3: 多証拠Equivalence Layer本体(Trial-01/02から無変更で移植)
# ============================================================
def _word_at_diff_matches_canonical(canonical_text: str, other_text: str | None, diff: dict) -> bool | None:
    """other_text(Secondary ASRやlocal ASRの書き起こし)が、diff位置で
    canonical側の語を支持しているかを判定する。position-based(diffの
    index位置の単語を直接比較)で判定する。
      True  -> 支持(corroboration、その位置でcanonical語と一致)
      False -> 支持しない(reduced/altered形と一致、またはさらに別の語)
      None  -> other_textが与えられていない、位置がother_text長を超える等
    既知の限界(Trialで記録済み): canonical/other_text間でdiff位置より
    手前に語数のずれ(挿入・脱落)がある場合、position-based比較がずれる
    可能性がある。"""
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

    secondary_asr_text/local_asr_textをNoneのまま呼ぶと、corroboration
    判定に進む前の「音韻環境が既知カテゴリに該当するか」だけを、追加の
    ASR API呼び出し無しで安価に判定できる(呼び出し側のeligibility事前
    チェック用途、常にEQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE以下の
    corroboration無し判定にしかならず、絶対にacceptしない)。
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


# 呼び出し側(er006_secondary_asr_01.py)が「この判定はacceptまで
# 到達しうる候補か」を判定するための定数(secondary/local無しで呼んだ
# 際、これらの場合は絶対にacceptに届かないため追加ASR呼び出しをしない)。
NEVER_ELIGIBLE_JUDGMENTS = (
    "NO_DELETION_SHAPED_DIFF", "NOT_A_PHONEME_PREFIX_DROP", "NO_KNOWN_CATEGORY_MATCH",
)
ACCEPT_JUDGMENTS = ("EQUIVALENCE_LAYER_ACCEPT", "EQUIVALENCE_LAYER_PASS_WITH_WARNING")
