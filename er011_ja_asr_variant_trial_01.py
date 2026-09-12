# ============================================================
# er011_ja_asr_variant_trial_01.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01
# ============================================================
# Trial専用の並行実装。Production関数(er007_ja_asr_validator_01.py /
# er011_a2_reading_resolver_01.py)は一切変更しない。
#
# Candidate B(形態素解析ベース読みエンジン、fugashi+unidic-lite)を、
# 既存のclassify_ja_asr_match()パイプライン(数字/否定保護・
# entity_like・phonetic_uncertain・whole_text_reading救済・Reading
# Resolver呼び出し判断)へ、読み一致判定プリミティブ(_reading_equal /
# _reading_equal_allowing_voicing)だけを差し替えて評価する。
#
# 差し替えはPython関数の「呼び出し時にモジュールのglobalsから名前解決
# する」性質を利用した、呼び出し1回だけのin-process monkeypatch(直後に
# 必ず元へ戻す、try/finally)。ファイルは一切書き換えない。この手法は
# 既存の同codebase内テスト(er011_no18_connected_speech_reading_
# resolver_wiring_08_test.pyのcall_resolver差し替え等)と同じ設計思想。
#
# Reading Resolver(LLM)は、Candidate Bでは一切呼び出さない(¥0が
# Candidate Bの狙い)。Resolverが実際に必要になる件数だけを、
# call_resolverをoffline stubへ差し替えて「呼ばれた回数」だけ数える
# dry-run方式で計測する(本Trialの禁止事項=API支出禁止を厳守)。
from __future__ import annotations

import re
import unicodedata

import fugashi
import jaconv

import er007_ja_asr_validator_01 as javal  # 読み取り専用の再利用(変更しない)
import er011_a2_reading_resolver_01 as reading_resolver  # 読み取り専用の再利用(変更しない)

# Trial専用フラグ(既定OFF、production側のFEATURE_FLAG_A2_READING_RESOLVER_ENABLEDとは別物)
FEATURE_FLAG_TRIAL_MORPH_ENGINE_ENABLED = False

_tagger = None


def _get_tagger():
    global _tagger
    if _tagger is None:
        _tagger = fugashi.Tagger()
    return _tagger


def morph_kana_reading(text: str) -> str:
    """fugashi(unidic-lite)による形態素解析ベースの読み(カタカナ)を返す。
    pykakasiの「1文字ずつ機械的に漢字の読みを合成する」方式と異なり、
    形態素(単語)単位で辞書引きするため、「経つ」のような複合的な訓読みも
    正しく引ける(辞書がunidicで別物のため、kanwadictに無い読みでも
    unidic側に登録されていれば解決できる)。kana素性が無い場合
    (記号・数字・未知語等)はpronフォールバック、それも無ければsurfaceを
    そのまま使う(fail-safe、無理に読みを捏造しない)。"""
    if not text:
        return ""
    out = []
    for word in _get_tagger()(text):
        # unidic-liteの補助記号(句読点等)は kana="" (空文字列、意図的に
        # 「読み無し=無音」を表す)を持つ。ここでNoneと区別せず素直に
        # 空文字列を使う(pykakasiが記号を無音として扱う挙動に合わせる)。
        # 未知語等でkana自体が取得できない(属性が無い/None)場合のみ
        # pron、それも無ければsurfaceへfallbackする(無理に読みを捏造
        # しない、fail-safe)。
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


def classify_with_candidate_morph(canonical_text: str, asr_text: str):
    """production の classify_ja_asr_match() を、読みエンジンだけ
    fugashi/unidic-liteベースへ差し替えて呼び出す(呼び出し1回限りの
    monkeypatch、直後に必ず元へ戻す)。Reading Resolver(LLM)は呼ばない
    (candidate Bは¥0)。"""
    orig_reading_equal = javal._reading_equal
    orig_reading_equal_voicing = javal._reading_equal_allowing_voicing
    orig_flag = javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED
    try:
        javal._reading_equal = _reading_equal_morph
        javal._reading_equal_allowing_voicing = _reading_equal_allowing_voicing_morph
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
        return javal.classify_ja_asr_match(canonical_text, asr_text)
    finally:
        javal._reading_equal = orig_reading_equal
        javal._reading_equal_allowing_voicing = orig_reading_equal_voicing
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = orig_flag


def classify_with_baseline(canonical_text: str, asr_text: str):
    """production既定動作の再現。ただしResolverはoffline(候補なし扱いに
    はしない、実際にcall_resolverが呼ばれる回数だけをoffline stubで
    数える)。stub自体は例外を送出するだけでネットワークへは一切出ない。"""
    calls = {"n": 0}
    orig_call_resolver = reading_resolver.call_resolver
    orig_flag = javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED

    def _stub_call_resolver(full_text_context, target_word, candidates):
        calls["n"] += 1
        raise RuntimeError("dry-run stub: 本TrialではAPI支出禁止のためLLM呼び出しを行わない")

    try:
        reading_resolver.call_resolver = _stub_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = True
        result = javal.classify_ja_asr_match(canonical_text, asr_text)
    finally:
        reading_resolver.call_resolver = orig_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = orig_flag
    return result, calls["n"]


def classify_with_candidate_additive(canonical_text: str, asr_text: str):
    """『置き換え』ではなく『追加』方式のCandidate B。既存のpykakasiベース
    読み判定(_reading_equal等)は一切変更せず、Production既定のResolver
    呼び出し地点(非cascade diffが残り、pykakasiベースの全文読み一致でも
    説明できない場合)の直前に、fugashi/unidic-liteベースの全文読み一致
    チェックをもう1段追加するだけの設計。
    既存判定で既にPASS/Cascade対象になったケースは一切変更しない
    (regressionが原理的に発生しない、既存チェックを完全に温存するため)。
    fugashiベースでも一致しない場合のみ、既存どおりResolver(LLM)へ
    fall throughする(このTrial関数自体はResolverを呼ばない、dry-run
    カウントのみ行う)。"""
    orig_call_resolver = reading_resolver.call_resolver
    orig_flag = javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED
    calls = {"n": 0}

    def _stub_call_resolver(full_text_context, target_word, candidates):
        calls["n"] += 1
        raise RuntimeError("dry-run stub: 本TrialではAPI支出禁止のためLLM呼び出しを行わない")

    try:
        reading_resolver.call_resolver = _stub_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = True
        baseline_result = javal.classify_ja_asr_match(canonical_text, asr_text)
    finally:
        reading_resolver.call_resolver = orig_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = orig_flag

    if baseline_result.classification != "TRUE_CONTENT_MISMATCH":
        # 既存チェックで既にPASS/Cascade対象になっている(=Resolverの出番
        # ではない)。追加チェックは一切適用せず既存結果をそのまま返す。
        return baseline_result, calls["n"], "unchanged"

    c_norm = javal.normalize_ja(canonical_text)
    a_norm = javal.normalize_ja(asr_text)
    if _reading_equal_morph(c_norm, a_norm):
        rescued = javal.ClassificationResultJA(
            "PHONETIC_MATCH", baseline_result.similarity_ratio, baseline_result.protected,
            should_pass=True, should_retry=False,
            reason="(Candidate B追加チェック)pykakasiベースの読み判定では一致しなかったが、"
                   "fugashi/unidic-lite形態素解析ベースの全文読みが完全一致")
        return rescued, calls["n"], "rescued_by_morph_exact"
    if _reading_equal_allowing_voicing_morph(c_norm, a_norm):
        rescued = javal.ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", baseline_result.similarity_ratio, baseline_result.protected,
            should_pass=False, should_retry=False,
            reason="(Candidate B追加チェック)形態素解析ベースの読みが濁点/半濁点の有無を除き一致"
                   "(Cascade対象、即PASSにはしない)")
        return rescued, calls["n"], "rescued_to_cascade_by_morph_voicing"
    return baseline_result, calls["n"], "unresolved"


def candidate_a_dry_candidate_check(kanji_char: str, expected_reading_hira: str) -> dict:
    """Candidate A(kanwadictに無い読みのための閉じた補完テーブル)の
    「そもそも候補に正解が存在するか」だけをoffline(pykakasi辞書引きの
    み、LLMは一切呼ばない)で確認する。Resolverは「候補から選ぶ」設計の
    ため、候補に無ければLLMをどれだけ呼んでも解決不可能(fail-safe設計
    そのものの再確認)。"""
    candidates = reading_resolver.single_char_candidates(kanji_char)
    return {
        "kanji": kanji_char, "expected_reading": expected_reading_hira,
        "candidates": candidates,
        "expected_in_candidates": expected_reading_hira in candidates,
    }
