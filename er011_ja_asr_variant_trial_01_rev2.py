# ============================================================
# er011_ja_asr_variant_trial_01_rev2.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 修正2回目
# ============================================================
# Fable差し戻し指示(2回目): 修正1回目で残った自作82件中2件
# (「頃/ころ」「十件/10件」)について、なぜ現行の候補B+Cで解消しないかを
# failure mode単位で構造的に特定し、個別語テーブルではなく一般的な追加型
# (additive)修正で閉じる。
#
# 本ファイルは新規追加ファイルであり、修正1回目の成果物
# (er011_ja_asr_variant_trial_01_rev1.py)・初回成果物
# (er011_ja_asr_variant_trial_01.py)・Production関数
# (er007_ja_asr_validator_01.py / er011_a2_reading_resolver_01.py /
# er003_audio_tts_asr_safety.py)は一切変更しない(importして再利用する
# だけ)。
from __future__ import annotations

import re

import er003_audio_tts_asr_safety as safety  # 読み取り専用の再利用(変更しない)
import er007_ja_asr_validator_01 as javal  # 読み取り専用の再利用(変更しない)
import er011_ja_asr_variant_trial_01 as candidate_b  # Trial専用、初回成果物(変更しない)
import er011_ja_asr_variant_trial_01_rev1 as candidate_bc  # Trial専用、修正1回目成果物(変更しない)

# ============================================================
# 構造診断(実測で確認した結果、詳細はREPORTの「修正2回目」節に記載)
# ============================================================
# failure mode 1: 「頃/ころ」— 数詞処理でも辞書未登録読みでもなく、
#   「比較アルゴリズム(候補B+Cの適用範囲)」の問題だった。
#   実測: baseline classify_ja_asr_match()は、この入力に対し既に
#   ASR_VALIDATION_UNCERTAIN(既存のvoicing許容Cascade機構、「頃」を
#   pykakasiが文脈依存で連濁形「ごろ」と読んでしまうことへの既存の
#   安全側フォールバック、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B)を
#   返している。修正1回目のcandidate B(classify_with_candidate_
#   additive())は「baseline.classification == TRUE_CONTENT_MISMATCHの
#   場合のみ追加チェックを試みる」設計のため、この時点で早期リターン
#   (tag="unchanged")し、fugashi/unidic-lite形態素読みエンジンには
#   一切到達しない。ところが実際にfugashi/unidic-liteで厳密(濁点許容
#   なし)の読み一致を確認すると、"ゆうがたころにえきへつくよてい"同士で
#   **完全一致**する(形態素辞書ベースの読みエンジンは、pykakasiのような
#   文脈依存の連濁推定を行わず、単語単位で「頃」を正しく「ころ」と
#   引けるため)。つまり、既存のCascade機構が"不確実"と判断したケースの
#   一部は、別の読みエンジンで独立に「本当は完全に同じ読みである」ことを
#   確認できる。既存判定を弱める(Cascade対象を丸ごとPASSにする)のでは
#   なく、「Cascade対象の中でも、形態素読みエンジンが厳密一致を確認できた
#   ものだけ」を追加でPHONETIC_MATCHへ引き上げることで、既存の安全性
#   (「柿/鍵」のように清音化後にのみ偶然一致する別の実在語は、形態素
#   読みエンジンでも厳密不一致のままなのでCascade対象のまま=誤PASSしない)
#   を壊さずに一般的に解消できる(実測で確認、下記参照)。
#
# failure mode 2: 「十件/10件」— 数詞処理(漢数字→算用数字変換の対象
#   範囲)の問題だった。既存Production(er003_audio_tts_asr_safety.py
#   normalize_kanji_counter_numerals_ja())は、閉じた助数詞リスト
#   (つ/泊/回/件/年/時間/か月/週/歳)の直前に来る単独漢数字「一〜九」
#   (1桁)だけを算用数字へ変換しており、「十」(10)・「百」・「千」・
#   「万」といった位取りを持つ漢数字は対象外だった。「十件」はどの正規化
#   ステージでも算用数字化されないため、"じゅうけん"(漢数字側の読み)と
#   "10けん"(ASR側、"10"は形態素解析エンジンでもpykakasiでも音声化
#   されず文字通り"10"のまま残る)の読み比較が一致せず、TRUE_CONTENT_
#   MISMATCHのまま候補B・候補Cのどちらでも解消しなかった。
# ============================================================


# ------------------------------------------------------------
# Candidate D-1: 漢数字(一〜九/十/百/千/万の位取りを含む)の一般正規化。
# ------------------------------------------------------------
# 既存Production(safety._CLOSED_COUNTERS_JA)と**同じ閉じた助数詞リスト**
# だけをトリガー文脈として再利用する(「日」「人」等の不規則読みリスクが
# 既に実証されている助数詞は対象に含めない、範囲拡大はしていない)。
# 変更するのは「その助数詞の直前に来る漢数字を、1桁(一〜九)だけでなく
# 位取り表記(十/百/千/万)を含めて一般的に算用数字へ変換できるようにする」
# ことだけであり、対象となる助数詞の集合自体は既存Productionの承認済み
# リストのまま変更していない。
_KANJI_DIGIT_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
}
_KANJI_UNIT_MAP = {"十": 10, "百": 100, "千": 1000}
_KANJI_BIG_UNIT_MAP = {"万": 10000}
_KANJI_NUMERAL_CHARS = "".join(_KANJI_DIGIT_MAP) + "".join(_KANJI_UNIT_MAP) + "".join(_KANJI_BIG_UNIT_MAP)

# 既存Production(er003_audio_tts_asr_safety._CLOSED_COUNTERS_JA)を
# 読み取り専用でそのまま再利用する(範囲を独自に広げない)。
_GENERAL_KANJI_NUMERAL_RUN_RE = re.compile(
    r"[" + _KANJI_NUMERAL_CHARS + r"]+(?=(?:" + "|".join(safety._CLOSED_COUNTERS_JA) + r"))"
)


def kanji_numeral_run_to_int(run: str) -> int | None:
    """一般的な漢数字(一〜九/十/百/千/万の位取り表記)を整数へ変換する。
    構文として不正な並び(例: 位取りの大小関係が単調減少でない「十千」、
    数字が連続する「一一」)を検知した場合はNoneを返す(fail-safe、
    無理に値を捏造しない)。この変換は常に「同じ数値表記同士だけが同じ
    文字列に正規化される」性質を持つため(異なる数量を同じ値へ変換する
    ことは構造的に起こらない)、負例(数量そのものが異なるケース)を
    誤ってPASSさせるリスクを生まない。"""
    total = 0
    section = 0
    digit = 0
    last_unit_value = None
    for ch in run:
        if ch in _KANJI_DIGIT_MAP:
            if digit != 0:
                return None  # 数字が連続("一一"等)する構文異常
            digit = _KANJI_DIGIT_MAP[ch]
        elif ch in _KANJI_UNIT_MAP:
            unit_value = _KANJI_UNIT_MAP[ch]
            if last_unit_value is not None and unit_value >= last_unit_value:
                return None  # 位取りの大小関係が単調減少でない構文異常
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
    """既存Productionの閉じた助数詞リスト(safety._CLOSED_COUNTERS_JA、
    読み取り専用で再利用・範囲拡大なし)の直前に来る漢数字を、1桁(一〜九)
    だけでなく位取り表記(十/百/千/万)を含めて一般的に算用数字へ変換する。
    構文的に解釈できない並びはfail-safeで無変換のまま返す(誤変換により
    無関係な値を作り出さない)。"""
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
    """Candidate D-1の正規化パイプライン(実測で発見した順序依存の副作用を
    回避する版)。

    実装中に実測で発見した副作用: 既存Production
    (er007_ja_asr_validator_01.normalize_ja()内でsafety.normalize_kanji_
    counter_numerals_ja()を呼んでいる)は、閉じた助数詞の直前に来る
    「単独の1桁の漢数字(一〜九)」だけを算用数字へ変換する。この既存処理を
    先に通してから複合漢数字(位取りを含む)へ一般正規化を試みると、
    例えば「十五件」の末尾の1文字「五」だけが既存Productionの処理で先に
    "5"へ変換されてしまい、"十5件"という漢数字と算用数字が混在した文字列に
    なる。この時点でCandidate D-1の正規表現(漢数字の連続塊+直後に助数詞)は
    "十"の直後が"5"(算用数字、文字クラス外)になるため塊が寸断され、
    "十"単体では直後が助数詞ではなくなり一致条件を満たさず、結果的に
    「十五件」が「15件」へ変換されない(実測で確認、REPORT参照)。
    この副作用を避けるため、Candidate D-1は**既存Productionの正規化
    (javal.normalize_ja())を通す前の生テキスト**に対して先に複合漢数字の
    一般正規化を適用する(この時点では漢数字は漢字のまま連続しているため
    正しく塊として認識できる)。生テキストの時点で既に漢数字が算用数字へ
    変換されているため、その後にjaval.normalize_ja()を通しても、既存
    Productionの単独1桁変換は対象(漢数字)が既に残っていないため単純に
    素通りするだけで、既存Productionの処理内容・出力を一切変更しない
    (副作用なし、読み取り専用の再利用のまま)。

    追加で実測して発見した同種の副作用(2件目): 助数詞「ヶ月/ヵ月/カ月」
    表記(Candidate C、rev1)と複合漢数字が同時に発生するケース(例:
    「十五ヶ月」)。Candidate Cの表記統一(ヶ月->か月)より先に一般漢数字
    正規化を行うと、まだ「か月」に統一されていない「ヶ月」の直前では
    「か月」の助数詞パターンにマッチせず変換されない。そのため、まず
    Candidate C由来の「ヶ月/ヵ月/カ月->か月」の文字置換**だけ**
    (safety.normalize_kanji_counter_numerals_ja()の呼び出しはまだ行わない、
    複合漢数字が漢字のまま残っている状態を保つ)を先に適用し、そのあとで
    一般漢数字正規化を適用する(この時点で「か月」に統一済みのため、
    複合漢数字も正しく塊として認識できる)。"""
    # 1. 助数詞のヶ月表記差(ヶ/ヵ/カ)月 -> か月 の文字置換だけを先に適用
    #    する(rev1のCandidate C正規表現を読み取り専用で再利用。rev1の
    #    normalize_month_counter_variants()自体は呼ばない、それは内部で
    #    safety.normalize_kanji_counter_numerals_ja()も呼んでしまうため、
    #    複合漢数字がまだ漢字のまま残っている状態を保てなくなるのを避ける)。
    t = candidate_bc._MONTH_COUNTER_VARIANT_RE.sub("か月", raw_text)
    # 2. 漢数字(位取りを含む)の一般正規化。ここで初めて助数詞直前の複合
    #    漢数字を安全に塊として認識できる(既存Productionの単独1桁変換も
    #    Candidate Cのヶ月統一も、まだ複合漢数字を寸断していないため)。
    t = normalize_general_kanji_counter_numerals_ja(t)
    # 3. 既存Production(句読点除去・NFKC・単独1桁漢数字変換)。ここに来る
    #    時点で助数詞直前の漢数字は既に全て算用数字化済みのため、既存の
    #    単独1桁変換は対象が残っておらず単純に素通りする(副作用なし)。
    t = javal.normalize_ja(t)
    # 4. カタカナ語末長音符の正規化(Candidate C、rev1関数をそのまま再利用)。
    #    ヶ月表記は手順1で既に統一済みのため、Candidate Cの月表記正規化を
    #    再度呼んでも冪等(無害、対象が残っていないため何もしない)。
    t = candidate_bc.normalize_candidate_c(t)
    return t


# ------------------------------------------------------------
# Candidate D-2: 既存のvoicing許容Cascade(ASR_VALIDATION_UNCERTAIN)の
# うち、形態素解析エンジンによる厳密一致(濁点許容なし)で裏付けが取れた
# ものだけを、PHONETIC_MATCHへ引き上げる。
# ------------------------------------------------------------
def _is_pure_phonetic_uncertain_cascade(result) -> bool:
    """baselineの分類がASR_VALIDATION_UNCERTAINで、かつその根拠が
    「濁点/半濁点の有無だけが異なる読みゆれ(phonetic_uncertain)」のみで
    構成されている(固有名詞らしさ[entity_like]起因の差が1件も混ざって
    いない)場合にのみTrueを返す。固有名詞ゆれ(entity_likeを含むケース)
    は本Trialのスコープ外(表記ゆれの一般化ではなく別種の不確実性)の
    ため、対象から明示的に除外する。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_diffs
    return bool(diffs) and all(d["phonetic_uncertain"] and not d["entity_like"] for d in diffs)


def try_upgrade_voicing_cascade_via_exact_morph(canonical_text: str, asr_text: str, result):
    """既存のCascade判定(ASR_VALIDATION_UNCERTAIN、濁点/半濁点の有無だけが
    異なる読みゆれと判定されたケース)に限り、fugashi/unidic-lite形態素
    読みエンジンで「厳密一致(濁点許容なし)」を再確認する。厳密一致すれば、
    pykakasiの文脈依存読み合成(連濁の有無の誤判定)が原因だっただけで、
    実際には完全に同じ読みであると別エンジンで裏付けが取れたと判断し、
    PHONETIC_MATCHへ引き上げる。厳密一致しない場合は一切変更しない
    (Noneを返す)。「柿/鍵」のように清音化後にのみ偶然一致する別の
    実在語は、形態素読みエンジンでも厳密不一致のままのためNoneを返し、
    既存のCascade対象(should_pass=False)のまま維持される
    =誤PASSを生まない(実測で確認、REPORT参照)。"""
    if not _is_pure_phonetic_uncertain_cascade(result):
        return None
    c_norm = javal.normalize_ja(canonical_text)
    a_norm = javal.normalize_ja(asr_text)
    if not candidate_b._reading_equal_morph(c_norm, a_norm):
        return None
    return javal.ClassificationResultJA(
        "PHONETIC_MATCH", result.similarity_ratio, result.protected,
        should_pass=True, should_retry=False,
        reason="(Candidate D-2追加チェック)既存pykakasiは濁点/半濁点の有無だけが"
               "異なる読みとしてCascade対象にしたが、fugashi/unidic-lite形態素解析"
               "ベースの厳密な(濁点許容なしの)読みが完全一致したため、読み違いでは"
               "なく完全に同じ読みであると判断しPHONETIC_MATCHへ引き上げる")


# ------------------------------------------------------------
# 統合エントリポイント: Candidate B -> C -> D(D-1漢数字一般化 / D-2
# voicing Cascade厳密一致引き上げ)の順で、既存の追加方式の原則
# (既に確定した判定は一切変更しない)をそのまま踏襲して重ねる。
# ------------------------------------------------------------
def classify_with_candidate_additive_bcd(canonical_text: str, asr_text: str):
    bc_result, calls, bc_tag = candidate_bc.classify_with_candidate_additive_bc(canonical_text, asr_text)

    if bc_tag == "b:unchanged":
        # baselineがTRUE_CONTENT_MISMATCH以外(既にPASS/Cascade確定)。
        # Candidate D-2: 既存のvoicing許容Cascade(ASR_VALIDATION_
        # UNCERTAIN)のうち、形態素解析エンジンの厳密一致で裏付けが取れた
        # ものだけを追加で引き上げる。それ以外はbc_resultをそのまま返す
        # (既存判定に一切触れない)。
        upgraded = try_upgrade_voicing_cascade_via_exact_morph(canonical_text, asr_text, bc_result)
        if upgraded is not None:
            return upgraded, calls, "rescued_by_exact_morph_from_voicing_cascade_d2"
        return bc_result, calls, bc_tag

    if bc_tag != "unresolved":
        # Candidate B(fugashi全文読み)またはCandidate C(カタカナ長音符・
        # ヶ月表記正規化)が既に確定させた判定には一切触れない。
        return bc_result, calls, bc_tag

    # ここに到達するのは、baselineがTRUE_CONTENT_MISMATCHで、かつ
    # Candidate B・Candidate Cのどちらでも読みが一致しなかった場合のみ。
    # Candidate D-1: 漢数字の位取り一般化(十/百/千/万)を追加で正規化して
    # から、Candidate Cと同じ3段(完全一致->形態素厳密一致->形態素voicing
    # 許容一致)を再度試す。順序依存の副作用を避けるため、生テキストに
    # 先に一般漢数字正規化を適用してからjaval.normalize_ja()を通す
    # (prepare_text_for_candidate_d1()のdocstring参照)。
    c_norm_d = prepare_text_for_candidate_d1(canonical_text)
    a_norm_d = prepare_text_for_candidate_d1(asr_text)

    if c_norm_d == a_norm_d:
        rescued = javal.ClassificationResultJA(
            "NORMALIZED_MATCH", bc_result.similarity_ratio, bc_result.protected,
            should_pass=True, should_retry=False,
            reason="(Candidate D-1追加チェック)漢数字(十/百/千/万の位取りを含む)・"
                   "カタカナ語末長音符・助数詞表記(ヶ月/ヵ月/カ月->か月)の正規化後に"
                   "文字列として完全一致")
        return rescued, calls, "rescued_by_normalization_d1_exact"

    if candidate_b._reading_equal_morph(c_norm_d, a_norm_d):
        rescued = javal.ClassificationResultJA(
            "PHONETIC_MATCH", bc_result.similarity_ratio, bc_result.protected,
            should_pass=True, should_retry=False,
            reason="(Candidate D-1追加チェック)漢数字一般正規化後、fugashi/unidic-lite"
                   "形態素解析ベースの読みが完全一致")
        return rescued, calls, "rescued_by_normalization_d1_then_morph"

    if candidate_b._reading_equal_allowing_voicing_morph(c_norm_d, a_norm_d):
        rescued = javal.ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", bc_result.similarity_ratio, bc_result.protected,
            should_pass=False, should_retry=False,
            reason="(Candidate D-1追加チェック)漢数字一般正規化後、形態素解析ベースの"
                   "読みが濁点/半濁点の有無を除き一致(Cascade対象、即PASSにはしない)")
        return rescued, calls, "rescued_to_cascade_by_normalization_d1_then_morph_voicing"

    return bc_result, calls, "unresolved"
