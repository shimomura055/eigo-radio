# ============================================================
# er006_preprod_hardening_01_validation.py
# ER-006-POOL-PREPROD-HARDENING-01: ASR比較の正規化+6分類+Protected Check
# ============================================================
# ER-006-POOL-PILOT-COST-ROOTFIX-01で確認した「9件のSTOPPEDは全てSurface-only
# mismatch」という知見をもとに、canonical textとASR transcriptを単語単位で
# 整列(word-level diff)し、各差分を
#   (a) 表記正規化で説明できる差(発音区別符号・ハイフン・複合語分かち書き・
#       序数・ダッシュ種別・英米綴り)
#   (b) 数字・年・日付の差
#   (c) 否定語の有無の差
#   (d) それ以外の内容語(content word)の置換・欠落・追加
# へ分類する。(b)(c)(d)が1件でもあれば、全体の類似度がどれだけ高くても
# 自動PASSしない(TRUE_CONTENT_MISMATCH)。(a)のみで説明できる場合のみ
# NORMALIZED_MATCHとして扱う。
#
# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01で、英語(language=="en")の
# retry loop(voice01.py::generate_charon_english、news_tail_fix.py、
# point_headings_aoede.py、repro01.py::generate_narration_snippet_verified_
# strict/generate_key_phrase_component_verified、crosslevel_audio_02_
# common.py::generate_english_segment_with_fallback)へ配線済み(下記の
# evaluate_attempt()がその統一エントリポイント)。これらは全テーマ
# (hanshin/health/household含む)で共有される既存モジュール。日本語
# (language=="ja")の経路は既存のphonetic_verdict方式のまま未変更
# (このvalidatorは英語専用のため)。
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field

# ------------------------------------------------------------
# 正規化(ER-006-POOL-PILOT-COST-ROOTFIX-01のer006_cost_rootfix_01_text_
# normalize.pyを土台に、word-level diff用へ拡張)
# ------------------------------------------------------------
BR_AM_SPELLING_PAIRS = [
    ("cancelling", "canceling"), ("cancelled", "canceled"),
    ("colour", "color"), ("favourite", "favorite"), ("centre", "center"),
    ("organise", "organize"), ("organised", "organized"),
    ("realise", "realize"), ("realised", "realized"),
    ("travelled", "traveled"), ("travelling", "traveling"),
    ("labelled", "labeled"), ("modelling", "modeling"),
]

# ER-006-ASR-VALIDATION-RESIDUAL-02: 英語の住所・地理表現でよく使われる
# 標準的な省略形(USPSの通り種別略語に代表される、閉じた既知の集合)。
# ASRが"street"を"St."のように省略形へ書き起こすことが実際に複数回
# (street furniture、full_story_part1等)観測されている。この略語class
# 自体は一般的でよく知られたものであり、個別記事・個別語の特例
# (whitelist)ではない。normalize_text()内でBR_AM_SPELLING_PAIRSと同じ
# 方式(両側を同じ正規化関数へ通す)で吸収するため、「canonical側が
# 完全形streetで、ASR側だけがst.と省略した」場合に両者が同じ正規化後
# トークンへ揃う。"St."は"Saint"の略でもあり得るが、その場合はcanonical
# 側が"saint"であって"street"ではなく、このmapはstreet→st方向にしか
# 定義していないため誤って吸収されない(Saint側の語がstへ変換される
# ことはない)。
_STREET_SUFFIX_EXPANSIONS = [
    ("street", "st"), ("avenue", "ave"), ("road", "rd"), ("boulevard", "blvd"),
    ("drive", "dr"), ("lane", "ln"), ("court", "ct"), ("place", "pl"),
    ("square", "sq"), ("terrace", "terr"), ("highway", "hwy"), ("parkway", "pkwy"),
]
_STREET_SUFFIX_RES = [(full, re.compile(r"\b" + abbr + r"\b")) for full, abbr in _STREET_SUFFIX_EXPANSIONS]

# ER-006-ASR-VALIDATION-RESIDUAL-02: 小さな数(2〜12)の綴り⇔算用数字の
# 表記差を吸収する。tts_generate.py::tts_safe_number_words_en()が既に
# TTS入力側だけ算用数字("two"→"2")へ変換しているのは、Azure ASRが
# 口頭の小さな数を算用数字へ書き起こす傾向を前提にした対策だった。
# 実際にPilotで確認したところ、OpenAI gpt-4o-mini-transcribeは逆に
# 綴りのまま("2"と発話された内容を"two"と)書き起こすことがあり
# (実例: Public Benches B1 comment_3、"two more angles"→TTS入力"2 more
# angles"→OpenAI ASR "two more angles"で、canonical側の"2"とASR側の
# "two"がprotected_checkの数字チェックで不一致判定されていた)、
# ASRプロバイダ次第でどちらの表記になるか変わる。値そのものが変わって
# いない限り、2〜12の綴り/算用数字は同じ数として吸収してよい
# (逆に"three"→"3:00"のような桁区切り記号混入は、正規化後も
# トークン数が変わる(3 00の2トークン)ため、この吸収の対象にならず
# 引き続きnumber_mismatchとして検出される)。
_EN_NUMBER_WORDS = {
    "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}
_EN_NUMBER_WORD_RE = re.compile(r"\b(" + "|".join(_EN_NUMBER_WORDS.keys()) + r")\b", flags=re.IGNORECASE)


_NEGATION_WORDS = {
    "not", "no", "never", "none", "nobody", "nothing", "nowhere", "neither", "nor",
    "cannot", "cant", "wont", "isnt", "arent", "wasnt", "werent", "doesnt", "dont",
    "didnt", "hasnt", "havent", "hadnt", "wouldnt", "shouldnt", "couldnt", "without",
}

_ORDINAL_RE = re.compile(r"\b(\d+)(st|nd|rd|th)\b")


def strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_text(text: str) -> str:
    """発音上区別できない表記差、および閉じた既知集合の標準的な省略形
    (通り種別略語等、_STREET_SUFFIX_EXPANSIONS参照)のみを吸収する。
    任意の単語の置き換えは行わない(BR_AM_SPELLING_PAIRS・略語展開とも、
    どちらも「同じ語の別表記」という閉じた既知集合に限定している点で
    従来方針を維持している)。"""
    t = (text or "").lower()
    t = strip_diacritics(t)
    for br, am in BR_AM_SPELLING_PAIRS:
        t = t.replace(br, am)
    t = t.replace("—", "-").replace("–", "-")
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = _ORDINAL_RE.sub(r"\1", t)
    t = _EN_NUMBER_WORD_RE.sub(lambda m: _EN_NUMBER_WORDS[m.group(1).lower()], t)
    for full, abbr_re in _STREET_SUFFIX_RES:
        t = abbr_re.sub(full, t)
    t = re.sub(r"[^a-z0-9]+", " ", t)  # ハイフン/複合語分かち書き差もここで吸収
    t = re.sub(r"\s+", " ", t).strip()
    return t


def tokenize(text: str) -> list[str]:
    return normalize_text(text).split()


def despaced(text: str) -> str:
    """複合語の分かち書き差(blitzscaling/blitz scaling/blitz-scaling等)を
    吸収するため、正規化後さらに空白も除去した比較用文字列。"""
    return normalize_text(text).replace(" ", "")


# \w相当だがUnicode文字(Malmöのö等)も含めて1語として拾う必要があるため、
# ASCIIの[A-Za-z]ではなくUnicodeの文字クラスを使う([^\W\d_]は「非単語文字でも
# 数字でも_でもない」= Unicodeの文字)。
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def capitalized_flags(text: str) -> set[str]:
    """原文で大文字始まりだったトークン(正規化後の小文字形)の集合。
    固有名詞らしさの粗い判定に使う。

    ER-006-AUDIO-RETRY-CASCADE-PROD-01(2026-08-22)で修正: 従来は
    「文頭(語index 0)の大文字化は情報にならない」として一律除外していたが、
    実際のfailure実例("Ottoni and colleagues' 2016 study..."のように、
    引用の学術者名がsegmentの先頭に来るケース)で、この一律除外により
    真正の固有名詞がentity_tokensへ入らず、TRUE_CONTENT_MISMATCH(retry
    対象)のまま扱われてしまう不具合を確認した。文頭語のうち、小文字化
    した形が既知の一般語(_STOPWORDS、"The"/"It"/"This"等)である場合のみ
    除外し、それ以外の文頭大文字語(固有名詞である可能性が高い)は通常
    位置の語と同様にentity候補として扱う。個別固有名詞のwhitelistでは
    なく、既存の_STOPWORDS(閉じた既知集合)を再利用した一般対策。"""
    words = _WORD_RE.findall(text)
    flags = set()
    for i, w in enumerate(words):
        if not w[0].isupper():
            continue
        if i == 0 and w.lower() in _STOPWORDS:
            continue  # 文頭の一般語(The/It/This等)は大文字化が情報にならない
        flags.add(strip_diacritics(w.lower()))
    return flags


# ------------------------------------------------------------
# Protected check: 数字・否定・内容語の欠落/追加/置換を検出する
# ------------------------------------------------------------
@dataclass
class ProtectedCheckResult:
    passed: bool
    number_mismatches: list[tuple[str, str]] = field(default_factory=list)
    negation_mismatches: list[tuple[str, str]] = field(default_factory=list)
    content_word_diffs: list[dict] = field(default_factory=list)  # {"type": replace/delete/insert, "canonical": ..., "asr": ...}


_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "is", "are", "was", "were", "be", "been", "being", "it", "its", "this", "that",
    "these", "those", "as", "by", "with", "from", "so", "than", "then", "there",
}


def _is_number(tok: str) -> bool:
    return tok.isdigit()


def protected_check(canonical_tokens: list[str], asr_tokens: list[str],
                     entity_tokens: set[str] | None = None) -> ProtectedCheckResult:
    entity_tokens = entity_tokens or set()
    result = ProtectedCheckResult(passed=True)
    sm = difflib.SequenceMatcher(None, canonical_tokens, asr_tokens, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        canon_span = canonical_tokens[i1:i2]
        asr_span = asr_tokens[j1:j2]

        canon_numbers = [t for t in canon_span if _is_number(t)]
        asr_numbers = [t for t in asr_span if _is_number(t)]
        if canon_numbers != asr_numbers and (canon_numbers or asr_numbers):
            result.number_mismatches.append((" ".join(canon_numbers), " ".join(asr_numbers)))
            result.passed = False

        canon_neg = [t for t in canon_span if t in _NEGATION_WORDS]
        asr_neg = [t for t in asr_span if t in _NEGATION_WORDS]
        if bool(canon_neg) != bool(asr_neg):
            result.negation_mismatches.append((" ".join(canon_neg), " ".join(asr_neg)))
            result.passed = False

        canon_content = [t for t in canon_span if t not in _STOPWORDS and not _is_number(t) and t not in _NEGATION_WORDS]
        asr_content = [t for t in asr_span if t not in _STOPWORDS and not _is_number(t) and t not in _NEGATION_WORDS]
        if canon_content or asr_content:
            if canon_content != asr_content:
                # canonical側の内容語が全て「原文で大文字始まりだった語(固有名詞らしい語)」
                # なら entity_like=True とする(ASR側がどう書き起こすかは問わない。
                # 固有名詞の音訳は元々ASR側が正しい表記を持たないことが前提のため)。
                # 固有名詞の音訳差(Triangeln→Triangle等)はASR_VALIDATION_UNCERTAIN
                # (retry停止・Review対象)の候補にする一方、通常の内容語(動詞・形容詞・
                # 名詞)の置換/欠落/追加はentity_like=Falseとし、一致率が高くても
                # TRUE_CONTENT_MISMATCH(retry対象)のままにする
                # ("increase"→"decrease"のような対義語誤りを見逃さないため)。
                entity_like = bool(canon_content) and set(canon_content).issubset(entity_tokens)
                result.content_word_diffs.append({
                    "type": tag, "canonical": " ".join(canon_content), "asr": " ".join(asr_content),
                    "entity_like": entity_like,
                })
    return result


# ------------------------------------------------------------
# 分類本体
# ------------------------------------------------------------
VALID_CLASSIFICATIONS = (
    "EXACT_MATCH", "NORMALIZED_MATCH", "HIGH_SIMILARITY_SAFE",
    "ASR_VALIDATION_UNCERTAIN", "TRUE_CONTENT_MISMATCH", "TTS_FAILURE",
)


@dataclass
class ClassificationResult:
    classification: str
    normalized_ratio: float
    protected: ProtectedCheckResult
    should_pass: bool
    should_retry: bool
    reason: str


def classify_asr_match(canonical_text: str, asr_text: str,
                        high_similarity_threshold: float = 0.98,
                        uncertain_threshold: float = 0.85,
                        tts_failure_threshold: float = 0.4) -> ClassificationResult:
    if asr_text is None:
        return ClassificationResult("TTS_FAILURE", 0.0, ProtectedCheckResult(passed=False),
                                     should_pass=False, should_retry=True, reason="ASR書き起こし自体が取得できなかった")

    if canonical_text.strip() == asr_text.strip():
        return ClassificationResult("EXACT_MATCH", 1.0, ProtectedCheckResult(passed=True),
                                     should_pass=True, should_retry=False, reason="完全一致")

    canon_tokens = tokenize(canonical_text)
    asr_tokens = tokenize(asr_text)
    ratio = difflib.SequenceMatcher(None, canon_tokens, asr_tokens, autojunk=False).ratio()

    if canon_tokens == asr_tokens:
        return ClassificationResult("NORMALIZED_MATCH", 1.0, ProtectedCheckResult(passed=True),
                                     should_pass=True, should_retry=False,
                                     reason="表記正規化(発音区別符号/ハイフン/序数/英米綴り等)後に一致")

    # 複合語の分かち書き差(blitzscaling/blitz scaling等)は、語単位のtoken列では
    # 一致しないが、空白を除去した文字列としては一致する。短いKey Phrase等で
    # word-level ratioが不安定になりやすいため、先に判定する。
    if despaced(canonical_text) == despaced(asr_text):
        return ClassificationResult("NORMALIZED_MATCH", 1.0, ProtectedCheckResult(passed=True),
                                     should_pass=True, should_retry=False,
                                     reason="複合語の分かち書き・ハイフン位置の差のみ(空白除去後に一致)")

    # 冠詞等のstopwordを除いた内容語だけを despace して比較する版。
    # 短いKey Phrase(例: canonical="a wide-scale empirical study" vs
    # asr="Widescale empirical study.")でstopwordの有無自体が表記差の対象外
    # であるケースを吸収する。
    canon_content_only = [t for t in tokenize(canonical_text) if t not in _STOPWORDS]
    asr_content_only = [t for t in tokenize(asr_text) if t not in _STOPWORDS]
    if "".join(canon_content_only) == "".join(asr_content_only) and canon_content_only:
        return ClassificationResult("NORMALIZED_MATCH", 1.0, ProtectedCheckResult(passed=True),
                                     should_pass=True, should_retry=False,
                                     reason="冠詞等を除いた内容語の複合語分かち書き差のみ(空白除去後に一致)")

    entity_tokens = capitalized_flags(canonical_text)
    protected = protected_check(canon_tokens, asr_tokens, entity_tokens=entity_tokens)

    if not protected.passed:
        return ClassificationResult("TRUE_CONTENT_MISMATCH", ratio, protected,
                                     should_pass=False, should_retry=True,
                                     reason=f"数字/否定の不一致を検出: numbers={protected.number_mismatches} negation={protected.negation_mismatches}")

    if ratio < tts_failure_threshold:
        return ClassificationResult("TTS_FAILURE", ratio, protected,
                                     should_pass=False, should_retry=True,
                                     reason="全体類似度が著しく低く、TTS生成自体の異常(hallucination/missing speech)が疑われる")

    non_entity_diffs = [d for d in protected.content_word_diffs if not d["entity_like"]]
    entity_only_diffs = [d for d in protected.content_word_diffs if d["entity_like"]]

    if non_entity_diffs:
        # 固有名詞以外の内容語(動詞・形容詞・名詞等)の置換/欠落/追加は、
        # 一致率が高くても自動PASSさせず、retry対象のTRUE_CONTENT_MISMATCHのままにする
        # (例: "increase"→"decrease"、重要語の欠落を見逃さないため)。
        return ClassificationResult("TRUE_CONTENT_MISMATCH", ratio, protected,
                                     should_pass=False, should_retry=True,
                                     reason=f"固有名詞以外の内容語に差がある(内容誤りの可能性): {non_entity_diffs}")

    if entity_only_diffs:
        return ClassificationResult("ASR_VALIDATION_UNCERTAIN", ratio, protected,
                                     should_pass=False, should_retry=False,
                                     reason=f"固有名詞らしき語にのみ音訳差がある(retryでは解決しない可能性が高い): {entity_only_diffs}")

    if ratio >= high_similarity_threshold:
        return ClassificationResult("HIGH_SIMILARITY_SAFE", ratio, protected,
                                     should_pass=True, should_retry=False,
                                     reason="内容語の差は無く、表記のみの軽微な揺れ")

    return ClassificationResult("ASR_VALIDATION_UNCERTAIN", ratio, protected,
                                 should_pass=False, should_retry=False,
                                 reason="内容語の差は検出されないが、一致率がPASS基準に届かない")


# ------------------------------------------------------------
# Retry Guardrail: 同一signatureが連続した場合の打ち切り判定
# ------------------------------------------------------------
def signature(canonical_text: str, asr_text: str) -> str:
    """同一失敗パターンの検出用キー(正規化済みASR text)。"""
    return normalize_text(asr_text or "")


def should_stop_retrying(attempt_results: list[ClassificationResult], max_same_signature: int = 3) -> bool:
    """直近max_same_signature件が全てASR_VALIDATION_UNCERTAIN/TRUE_CONTENT_MISMATCH
    以外へ進展しておらず、かつ正規化後のASR textがほぼ同一(signature一致)なら、
    これ以上retryしても改善しないと判断して打ち切る。
    TRUE_CONTENT_MISMATCH/TTS_FAILUREは対象外(retryで直る可能性があるため)。"""
    if len(attempt_results) < max_same_signature:
        return False
    recent = attempt_results[-max_same_signature:]
    if any(r.classification in ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE") for r in recent):
        return False
    if any(r.should_pass for r in recent):
        return False  # 通常は呼ばれる前にPASS確定しているはずだが念のため
    return True


# ------------------------------------------------------------
# Production wiring用ヘルパー(ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01で
# 実際のretry loopへ配線した際に使う統一エントリポイント)
# ------------------------------------------------------------
def evaluate_attempt(canonical_text: str, asr_text: str, prior_results: list,
                      max_same_signature: int = 3) -> tuple[bool, bool, "ClassificationResult"]:
    """1回のTTS attemptの評価結果を返す。
    prior_resultsは呼び出し側がループの外で初期化し、毎回このリストへ
    追記していく(同一segment内の履歴、standard/fallback別に分けて渡すこと)。

    戻り値: (verified, stop_retrying, classification)
      verified=True        → このattemptをそのまま採用してよい(retry不要)
      stop_retrying=True   → PASSはしないが、これ以上retryしても改善しない
                              (ASR_VALIDATION_UNCERTAIN、同一signatureが
                              max_same_signature回連続)。直前に書き込み済みの
                              audioをそのまま採用し、STATUS="ASR_VALIDATION_
                              UNCERTAIN"として返すこと(STOPPEDとは区別する)。
      それ以外              → 通常通りretryを継続する。
    """
    result = classify_asr_match(canonical_text, asr_text)
    prior_results.append(result)
    if result.should_pass:
        return True, False, result
    if not result.should_retry and should_stop_retrying(prior_results, max_same_signature=max_same_signature):
        return False, True, result
    return False, False, result
