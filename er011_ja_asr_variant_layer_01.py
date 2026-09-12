# ============================================================
# er011_ja_asr_variant_layer_01.py
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01
# ============================================================
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01(初回+修正1回目+
# 修正2回目、closeout: VALIDATED)で検証されたCandidate B(形態素解析
# ベース読み一致、fugashi+unidic-lite)/Candidate C(カタカナ語末長音符・
# 助数詞「ヶ月/ヵ月/カ月」表記の正規化)/Candidate D-1(漢数字の位取り
# [十/百/千/万]を含む一般正規化)/Candidate D-2(voicing許容Cascade
# [ASR_VALIDATION_UNCERTAIN、根拠がphonetic_uncertainのみ]の厳密一致
# 引き上げ)を、Production moduleとして昇格したもの。
#
# ユーザー正式決定(2026-09-12、OPEN-145): 「#11 A-Family / Discovery /
# A2 日本語ASR表記ゆれ一般化対策のProduction採用」を`APPROVED_FOR_
# PRODUCTION`として承認。
#
# 設計原則(Trial REPORTの配線案どおり、追加型=additive):
#   - 既存のpykakasiベース判定(_reading_equal / _reading_equal_allowing_
#     voicing)・Cascade・数字/否定保護・entity_like判定は一切変更しない。
#     この層は「既存判定がまだ解決していない場合」にのみ、既存Resolver
#     (LLM)呼び出しの直前でもう1段の追加チェックとして働く
#     (try_rescue_before_resolver、er007_ja_asr_validator_01.py内から
#     呼ぶ)。既に確定した判定には一切触れないため、regressionが構造的に
#     発生しない(Trial実測でも161件中0件)。
#   - Candidate D-2(voicing許容Cascadeの厳密一致引き上げ)だけは例外的に
#     「既存関数の呼び出し元」でのpost-processingとして配線する
#     (try_upgrade_voicing_cascade、er007_ja_secondary_asr_01.py内の
#     Cascade呼び出し元から呼ぶ)。理由: classify_ja_asr_match()自身の
#     ASR_VALIDATION_UNCERTAINという返り値の意味(Cascade対象)は変更せず、
#     Cascade呼び出し元の判断に委ねる既存設計を壊さないため
#     (Trial REPORT「修正2回目」節§6参照)。
#
# Trial専用ファイル(er011_ja_asr_variant_trial_01*.py)からは一切import
# しない。ロジックはこのファイルへ移設・統合済み(Trialファイル自体は
# 過去の証跡・再現用としてそのまま残す)。
#
# feature flag: FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED
#   既定True(2026-09-12ユーザー正式決定 APPROVED_FOR_PRODUCTIONにより
#   既定ON、OFFにすれば追加層なしの旧挙動へ即座に戻せる)。
#   fugashi/unidic-liteのimportに失敗した場合は、このモジュールの
#   import時点でこのflagを強制的にFalseへ落とし、warnings.warnで警告を
#   出す(fail-safe、判定は既存旧挙動のまま継続する。既存Productionを
#   止めない)。
from __future__ import annotations

import re
import unicodedata
import warnings

import er003_audio_tts_asr_safety as safety  # 読み取り専用の再利用(変更しない)

FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = True

try:
    import fugashi
    import jaconv
    _MORPH_IMPORT_ERROR: Exception | None = None
except Exception as _exc:  # pragma: no cover - fail-safeパス(依存未導入環境)
    fugashi = None  # type: ignore[assignment]
    jaconv = None  # type: ignore[assignment]
    _MORPH_IMPORT_ERROR = _exc

if _MORPH_IMPORT_ERROR is not None:
    FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = False
    warnings.warn(
        "er011_ja_asr_variant_layer_01: fugashi/unidic-liteのimportに失敗したため、"
        "JA ASR表記ゆれ追加層(Candidate B/C/D)を無効化しました(fail-safe、既存の"
        f"pykakasiベース判定のみで継続します): {_MORPH_IMPORT_ERROR!r}",
        RuntimeWarning,
        stacklevel=2,
    )

_tagger = None


def _get_tagger():
    global _tagger
    if _tagger is None:
        _tagger = fugashi.Tagger()
    return _tagger


# ------------------------------------------------------------
# Candidate B: 形態素解析ベース読みエンジン(fugashi + unidic-lite)。
# ------------------------------------------------------------
def morph_kana_reading(text: str) -> str:
    """fugashi(unidic-lite)による形態素解析ベースの読み(カタカナ)を返す。
    pykakasiの「1文字ずつ機械的に漢字の読みを合成する」方式と異なり、
    形態素(単語)単位で辞書引きするため、複合的な訓読み(例:「経つ」)も
    正しく引ける。kana素性が無い場合(記号・数字・未知語等)はpronへ、
    それも無ければsurfaceへfallbackする(fail-safe、読みを捏造しない)。"""
    if not text:
        return ""
    out = []
    for word in _get_tagger()(text):
        kana = getattr(word.feature, "kana", None)
        if kana is None:
            kana = getattr(word.feature, "pron", None)
        if kana is None:
            kana = word.surface
        out.append(kana)
    return "".join(out)


def morph_hira_reading(text: str) -> str:
    """比較の安定性のため、ひらがなへ統一する(jaconv、濁点比較はNFDで別途行う)。"""
    return jaconv.kata2hira(morph_kana_reading(text))


def _reading_equal_morph(a: str, b: str) -> bool:
    if a == b:
        return True
    if not a or not b:
        return False
    try:
        ra = morph_hira_reading(a)
        rb = morph_hira_reading(b)
    except Exception:
        return False
    return ra == rb


def _strip_voicing_marks(s: str) -> str:
    nfd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfd if not unicodedata.combining(ch))


def _reading_equal_allowing_voicing_morph(a: str, b: str) -> bool:
    if not a or not b:
        return False
    try:
        ra = morph_hira_reading(a)
        rb = morph_hira_reading(b)
    except Exception:
        return False
    return _strip_voicing_marks(ra) == _strip_voicing_marks(rb)


# ------------------------------------------------------------
# Candidate C: 正規化層(個別語テーブルではなく、いずれも構造的な範囲
# 限定ルール)。
# ------------------------------------------------------------
# (a) カタカナ語の語末長音符(「ー」)の省略差。カタカナ(+長音符)の
#     連続塊全体が4文字以上、かつ連続塊の最後の1文字が長音符の場合に
#     限り、末尾の1文字だけを取り除く(JIS Z 8301が慣用として認める
#     「3モーラ以上の外来語は語末長音符を省略してよい」という一般
#     ルールの実装。4文字未満の短い外来語は対象外、連続塊途中の長音符も
#     対象外)。
_KATAKANA_RUN_RE = re.compile(r"[ァ-ヴー]+")
_MIN_RUN_LEN_FOR_CHOONPU_STRIP = 4


def _strip_trailing_choonpu_in_run(run: str) -> str:
    if len(run) >= _MIN_RUN_LEN_FOR_CHOONPU_STRIP and run.endswith("ー"):
        return run[:-1]
    return run


def normalize_katakana_trailing_choonpu(text: str) -> str:
    if not text:
        return text
    return _KATAKANA_RUN_RE.sub(lambda m: _strip_trailing_choonpu_in_run(m.group(0)), text)


# (b) 助数詞「ヶ月/ヵ月/カ月」を、既存Production(safety._CLOSED_
#     COUNTERS_JA)が既に認識する表記「か月」へ統一してから、既存
#     Production関数normalize_kanji_counter_numerals_ja()(無変更、
#     再利用のみ)を再適用する。対象範囲は「月」のみ(他の助数詞は対象外)。
_MONTH_COUNTER_VARIANT_RE = re.compile(r"[ヶヵカ]月")


def normalize_month_counter_variants(text: str) -> str:
    if not text:
        return text
    t = _MONTH_COUNTER_VARIANT_RE.sub("か月", text)
    t = safety.normalize_kanji_counter_numerals_ja(t)
    return t


def normalize_candidate_c(text: str) -> str:
    t = normalize_katakana_trailing_choonpu(text)
    t = normalize_month_counter_variants(t)
    return t


# ------------------------------------------------------------
# Candidate D-1: 漢数字(一〜九/十/百/千/万の位取りを含む)の一般正規化。
# ------------------------------------------------------------
# 既存Production(safety._CLOSED_COUNTERS_JA)と同じ閉じた助数詞リスト
# だけをトリガー文脈として再利用する(対象助数詞の集合自体は拡大しない、
# 「日」「人」等の不規則読みリスクがある助数詞は引き続き対象外)。
_KANJI_DIGIT_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
}
_KANJI_UNIT_MAP = {"十": 10, "百": 100, "千": 1000}
_KANJI_BIG_UNIT_MAP = {"万": 10000}
_KANJI_NUMERAL_CHARS = "".join(_KANJI_DIGIT_MAP) + "".join(_KANJI_UNIT_MAP) + "".join(_KANJI_BIG_UNIT_MAP)

_GENERAL_KANJI_NUMERAL_RUN_RE = re.compile(
    r"[" + _KANJI_NUMERAL_CHARS + r"]+(?=(?:" + "|".join(safety._CLOSED_COUNTERS_JA) + r"))"
)


def kanji_numeral_run_to_int(run: str) -> int | None:
    """一般的な漢数字(一〜九/十/百/千/万の位取り表記)を整数へ変換する。
    構文として不正な並びを検知した場合はNoneを返す(fail-safe)。この
    変換は常に「同じ数値表記同士だけが同じ文字列に正規化される」性質を
    持つため、負例(数量そのものが異なるケース)を誤ってPASSさせるリスク
    を生まない。"""
    total = 0
    section = 0
    digit = 0
    last_unit_value = None
    for ch in run:
        if ch in _KANJI_DIGIT_MAP:
            if digit != 0:
                return None
            digit = _KANJI_DIGIT_MAP[ch]
        elif ch in _KANJI_UNIT_MAP:
            unit_value = _KANJI_UNIT_MAP[ch]
            if last_unit_value is not None and unit_value >= last_unit_value:
                return None
            last_unit_value = unit_value
            section += (digit or 1) * unit_value
            digit = 0
        elif ch in _KANJI_BIG_UNIT_MAP:
            unit_value = _KANJI_BIG_UNIT_MAP[ch]
            if last_unit_value is not None and unit_value >= last_unit_value:
                return None
            last_unit_value = unit_value
            section += digit
            total += section * unit_value
            section = 0
            digit = 0
        else:
            return None
    total += section + digit
    return total


def normalize_general_kanji_counter_numerals_ja(text: str) -> str:
    if not text:
        return text

    def _sub(m: re.Match) -> str:
        run = m.group(0)
        value = kanji_numeral_run_to_int(run)
        if value is None:
            return run
        return str(value)

    return _GENERAL_KANJI_NUMERAL_RUN_RE.sub(_sub, text)


def prepare_text_for_candidate_d1(raw_text: str) -> str:
    """Candidate D-1の正規化パイプライン(順序依存の副作用を回避する版、
    詳細はTrial REPORT「修正2回目」節参照)。生テキストに対し先に複合
    漢数字の一般正規化を適用してから、既存Production
    (javal.normalize_ja())・Candidate Cを通す(この順序でないと、既存
    Productionの単独1桁変換が先に走り複合漢数字の文字列を寸断してしまう
    副作用が実測で確認されている)。javalは循環import回避のため遅延
    importする。"""
    import er007_ja_asr_validator_01 as javal  # 遅延import(循環import回避)

    # 1. 助数詞のヶ月表記差(ヶ/ヵ/カ)月 -> か月 の文字置換だけを先に適用
    #    する(safety.normalize_kanji_counter_numerals_ja()の呼び出しは
    #    まだ行わない、複合漢数字が漢字のまま残っている状態を保つ)。
    t = _MONTH_COUNTER_VARIANT_RE.sub("か月", raw_text)
    # 2. 漢数字(位取りを含む)の一般正規化。
    t = normalize_general_kanji_counter_numerals_ja(t)
    # 3. 既存Production(句読点除去・NFKC・単独1桁漢数字変換)。この時点で
    #    助数詞直前の漢数字は既に全て算用数字化済みのため、既存の単独
    #    1桁変換は対象が残っておらず単純に素通りする(副作用なし)。
    t = javal.normalize_ja(t)
    # 4. カタカナ語末長音符の正規化(Candidate C)。ヶ月表記は手順1で
    #    既に統一済みのため、月表記正規化を再度呼んでも冪等(無害)。
    t = normalize_candidate_c(t)
    return t


# ------------------------------------------------------------
# 統合エントリポイント1: Candidate B -> C -> D-1。
# er007_ja_asr_validator_01.classify_ja_asr_match()内、既存Resolver
# (LLM)呼び出し直前の1箇所からだけ呼ぶ(既にnon_cascade_diffsが残り、
# 既存のwhole_text読み一致でも説明できなかった場合、すなわち既存判定が
# まだ何も確定させていない場合にのみ到達する)。
# ------------------------------------------------------------
def try_rescue_before_resolver(canonical_text: str, asr_text: str,
                                c_norm: str, a_norm: str, ratio: float, protected):
    """既存判定(pykakasiベース)がこの時点でまだ解決していない場合にのみ
    呼ばれる想定。解決できればClassificationResultJAを返し、呼び出し元は
    それをそのまま返してResolver(LLM)を呼ばずに済ませる。解決できなければ
    Noneを返し、呼び出し元は既存どおりResolverへfall throughする。"""
    if not FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED:
        return None

    import er007_ja_asr_validator_01 as javal  # 遅延import(循環import回避)

    def _pass(classification: str, reason: str):
        return javal.ClassificationResultJA(
            classification, ratio, protected, should_pass=True, should_retry=False, reason=reason)

    def _cascade(reason: str):
        return javal.ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False, reason=reason)

    # --- Candidate B: 形態素解析ベース全文読み一致 ---
    if _reading_equal_morph(c_norm, a_norm):
        return _pass("PHONETIC_MATCH",
                     "(JA ASR Variant Layer/Candidate B)pykakasiベースの読み判定では一致しなかったが、"
                     "fugashi/unidic-lite形態素解析ベースの全文読みが完全一致")
    if _reading_equal_allowing_voicing_morph(c_norm, a_norm):
        return _cascade("(JA ASR Variant Layer/Candidate B)形態素解析ベースの読みが濁点/半濁点の有無を"
                         "除き一致(Cascade対象、即PASSにはしない)")

    # --- Candidate C: カタカナ語末長音符・助数詞ヶ月表記の正規化 ---
    c_norm2 = normalize_candidate_c(c_norm)
    a_norm2 = normalize_candidate_c(a_norm)
    if c_norm2 == a_norm2:
        return _pass("NORMALIZED_MATCH",
                     "(JA ASR Variant Layer/Candidate C)カタカナ語末長音符の省略差・助数詞表記"
                     "(ヶ月/ヵ月/カ月->か月)の正規化後に文字列として完全一致")
    if _reading_equal_morph(c_norm2, a_norm2):
        return _pass("PHONETIC_MATCH",
                     "(JA ASR Variant Layer/Candidate C)正規化後、fugashi/unidic-lite形態素解析"
                     "ベースの読みが完全一致")
    if _reading_equal_allowing_voicing_morph(c_norm2, a_norm2):
        return _cascade("(JA ASR Variant Layer/Candidate C)正規化後、形態素解析ベースの読みが"
                         "濁点/半濁点の有無を除き一致(Cascade対象、即PASSにはしない)")

    # --- Candidate D-1: 漢数字位取り(十/百/千/万)の一般正規化 ---
    c_norm_d = prepare_text_for_candidate_d1(canonical_text)
    a_norm_d = prepare_text_for_candidate_d1(asr_text)
    if c_norm_d == a_norm_d:
        return _pass("NORMALIZED_MATCH",
                     "(JA ASR Variant Layer/Candidate D-1)漢数字(十/百/千/万の位取りを含む)・"
                     "カタカナ語末長音符・助数詞表記の正規化後に文字列として完全一致")
    if _reading_equal_morph(c_norm_d, a_norm_d):
        return _pass("PHONETIC_MATCH",
                     "(JA ASR Variant Layer/Candidate D-1)漢数字一般正規化後、fugashi/unidic-lite"
                     "形態素解析ベースの読みが完全一致")
    if _reading_equal_allowing_voicing_morph(c_norm_d, a_norm_d):
        return _cascade("(JA ASR Variant Layer/Candidate D-1)漢数字一般正規化後、形態素解析ベースの"
                         "読みが濁点/半濁点の有無を除き一致(Cascade対象、即PASSにはしない)")

    return None


# ------------------------------------------------------------
# 統合エントリポイント2: Candidate D-2(voicing許容Cascadeの厳密一致
# 引き上げ)。er007_ja_secondary_asr_01.py(A2 Cascade呼び出し元)側で、
# classify_ja_asr_match()の戻り値がASR_VALIDATION_UNCERTAINだった直後に
# だけ呼ぶ(既存関数自体の返り値の意味は変更しない、呼び出し元での
# post-processing)。
# ------------------------------------------------------------
def _is_pure_phonetic_uncertain_cascade(result) -> bool:
    """baselineの分類がASR_VALIDATION_UNCERTAINで、かつその根拠が
    「濁点/半濁点の有無だけが異なる読みゆれ(phonetic_uncertain)」のみで
    構成されている(固有名詞らしさ[entity_like]起因の差が1件も混ざって
    いない)場合にのみTrueを返す。固有名詞ゆれは本層のスコープ外
    (Human Review温存)のため対象から明示的に除外する。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_diffs
    return bool(diffs) and all(d["phonetic_uncertain"] and not d["entity_like"] for d in diffs)


def try_upgrade_voicing_cascade(canonical_text: str, asr_text: str, result):
    """既存のCascade判定(ASR_VALIDATION_UNCERTAIN、濁点/半濁点の有無だけが
    異なる読みゆれと判定されたケース)に限り、fugashi/unidic-lite形態素
    読みエンジンで「厳密一致(濁点許容なし)」を再確認する。厳密一致すれば
    PHONETIC_MATCHへ引き上げたClassificationResultJAを返す。それ以外
    (対象外・厳密不一致・flag OFF)はNoneを返す(呼び出し元は元のresultを
    そのまま使うこと)。「柿/鍵」のように清音化後にのみ偶然一致する別の
    実在語は、形態素読みエンジンでも厳密不一致のままのためNoneを返し、
    既存のCascade対象のまま維持される(誤PASSを生まない)。"""
    if not FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED:
        return None
    if not _is_pure_phonetic_uncertain_cascade(result):
        return None

    import er007_ja_asr_validator_01 as javal  # 遅延import(循環import回避)

    c_norm = javal.normalize_ja(canonical_text)
    a_norm = javal.normalize_ja(asr_text)
    if not _reading_equal_morph(c_norm, a_norm):
        return None
    return javal.ClassificationResultJA(
        "PHONETIC_MATCH", result.similarity_ratio, result.protected,
        should_pass=True, should_retry=False,
        reason="(JA ASR Variant Layer/Candidate D-2)既存pykakasiは濁点/半濁点の有無だけが"
               "異なる読みとしてCascade対象にしたが、fugashi/unidic-lite形態素解析ベースの"
               "厳密な(濁点許容なしの)読みが完全一致したため、読み違いではなく完全に同じ"
               "読みであると判断しPHONETIC_MATCHへ引き上げる")
