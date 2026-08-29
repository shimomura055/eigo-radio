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

import er008_asr_variant_hardening_15_homophone_en as homophone_en

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

# ============================================================
# ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01: 数値正規化の一般化
# ============================================================
# 従来は2〜12の単語のみをbareで算用数字へ変換していた(ER-006-ASR-
# VALIDATION-RESIDUAL-02)。実際にPublic Benches Boavida segmentで
# "28"(canonical)と"twenty-eight"(Azure ASR)という、値は同じだが
# 表記が異なるだけの差でsegment全体がTRUE_CONTENT_MISMATCHになる
# 事例を確認したため、cardinal numberの綴り⇔算用数字変換を一般化する。
#
# 安全設計の核心: 「表記が違うだけで値(意味)が同じ」場合のみ吸収し、
# 「表記は数字っぽいが値や意味が違う」場合は絶対に吸収しない。
#   - 桁が変わる(three→3:00)・単位が付く(5→5%, 5→$5)・序数と基数が
#     入れ替わる(28→28th)場合は、後段の`_is_number()`が別トークンだと
#     判定できるよう、値の変換とは別に区別可能な形へ正規化する
#     (%/$/小数点は英数字マーカーへ変換して残し、後段の記号除去で
#     消えないようにする。詳細はnormalize_numeric()内のコメント参照)。
#   - 序数語(third)は基数(3)ではなく序数表記(3rd)へ変換し、基数と
#     混同しない。
#   - 日付の序数接尾辞除去(March 4th→March 4)は、月名が直前にある
#     場合のみに限定する(過去は"28th"のようにmonth文脈でなくても
#     一律で"28"へ変換されてしまっており、"28 ≠ 28th"という意味の
#     違いを見逃す実バグだった。今回修正)。
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000}
_NUM_WORD_VOCAB = set(_ONES) | set(_TENS) | set(_SCALES) | {"and"}

# "first"・"second"は、序数(「1番目」)としてだけでなく、"may first run"
# (=「まず最初に」という副詞)・discourse connector("first, ...second, ...")
# のような、数とは無関係な非常に高頻度な用法があるため、意図的に対象から
# 除外する(実際に"a company...may first run at a loss"という副詞用法が、
# 誤って"May 1st"と一致してしまう実回帰を検出したため)。third以降は
# 副詞的用法の頻度が大きく下がるため対象に含める。
_ORDINAL_WORDS = {
    "third": "3rd", "fourth": "4th", "fifth": "5th",
    "sixth": "6th", "seventh": "7th", "eighth": "8th", "ninth": "9th", "tenth": "10th",
    "eleventh": "11th", "twelfth": "12th", "thirteenth": "13th", "fourteenth": "14th",
    "fifteenth": "15th", "sixteenth": "16th", "seventeenth": "17th", "eighteenth": "18th",
    "nineteenth": "19th", "twentieth": "20th", "thirtieth": "30th",
}
_ORDINAL_WORD_RE = re.compile(r"\b(" + "|".join(_ORDINAL_WORDS.keys()) + r")\b", re.IGNORECASE)

# ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(2026-08-27)で発見: 複合序数
# ("twenty eighth"/"twenty-eighth"のような、十の位の単語+一の位の序数語)
# は、上記_ORDINAL_WORDS(単純序数のみ)にも_convert_cardinal_words()
# (cardinal語のみ、"eighth"はvocabに含まれない)にも属さないため、
# 単独では変換されない。normalize_numeric()の既存の順序(cardinal変換
# [手順3]が先、ordinal変換[手順7]が後)では、"twenty"だけがcardinal変換で
# 独立して"20"へ変換され、残った"eighth"がordinal変換で独立して"8th"へ
# 変換され、"20 8th"という2つの無関係なtokenへ分裂してしまう実バグを、
# No.5(pool_n5_cafes)B1 full_story_part2の日付発話形修正で発見した。
# OPEN-58(複合基数のハイフン誤変換)と同じ教訓("tts_safe_number_words_
# en()のような既存共有regexへの機械的な追加は事故を招きやすい")を踏まえ、
# 汎用的な書き換えはせず、"十の位の単語+一の位の序数語"という閉じた
# 具体的パターンのみを対象にした専用ステップを追加する(既存の
# _DATE_ORDINAL_RE等、他の狭いスコープの日付・数値パターンと同じ設計
# 方針)。"first"/"second"は_ORDINAL_WORDS側では副詞的用法との曖昧さを
# 理由に除外されているが、"twenty first"のような複合形での副詞的誤用は
# 実質的に存在しないため、この専用パターンでは含める。
_ORDINAL_ONES = {
    "first": ("1", "st"), "second": ("2", "nd"), "third": ("3", "rd"),
    "fourth": ("4", "th"), "fifth": ("5", "th"), "sixth": ("6", "th"),
    "seventh": ("7", "th"), "eighth": ("8", "th"), "ninth": ("9", "th"),
}
_COMPOUND_ORDINAL_RE = re.compile(
    r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[\s-]+"
    r"(" + "|".join(_ORDINAL_ONES.keys()) + r")\b", re.IGNORECASE)


def _convert_compound_ordinal_words(text: str) -> str:
    """"twenty eighth"/"twenty-eighth" -> "28th"のような、十の位+一の位
    序数語の複合形だけを対象にした変換(_convert_cardinal_words()・
    _convert_ordinal_words()より先に呼ぶことで、両者が独立に一部だけ
    変換してしまう分裂を防ぐ)。"""
    def _repl(m: "re.Match") -> str:
        tens_val = _TENS[m.group(1).lower()]
        ones_digit, suffix = _ORDINAL_ONES[m.group(2).lower()]
        return f"{tens_val + int(ones_digit)}{suffix}"
    return _COMPOUND_ORDINAL_RE.sub(_repl, text)

_MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
           "september", "october", "november", "december")
_DATE_ORDINAL_RE = re.compile(r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2})(st|nd|rd|th)\b", re.IGNORECASE)

# ============================================================
# ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01: 数式表記の正規化
# ============================================================
# No.6 A2 Point One("2 × 10⁻¹⁶"のような科学的記数法)で、TTS音声自体は
# 正しく("2 times 10 to the minus 16th")読み上げているにもかかわらず、
# canonical側のUnicode上付き文字(⁻¹⁶等)がnormalize_text()の一般記号
# 除去([^a-z0-9]+のスペース化)で情報ごと失われ(桁・符号が消える)、
# ASR側の綴り("...to the minus 16th")と比較不能になっていた実例を
# 確認した。安全設計の核心は数値正規化と同じ: 「表記が違うだけで意味
# (底・符号・指数の値)が同じ」場合のみ吸収し、指数の桁・符号が異なる
# 場合は絶対に吸収しない。xdollarx等と同じマーカー方式で、底(base)と
# 指数の符号・値を独立したtokenとして保持したまま比較する。
_SUPERSCRIPT_TRANSLATE = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7",
    "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+",
})
# "10⁻¹⁶"・"10¹⁶"のような、数字に直接続くUnicode上付き文字列(符号+桁)。
_SUPERSCRIPT_EXPONENT_RE = re.compile(r"(\d+)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)")
# "10^-16"・"10^16"のような、ASCII表記のキャレット指数(ASRが記号のまま
# 書き起こす場合が実際に観測されている)。
_CARET_EXPONENT_RE = re.compile(r"(\d+)\^(-?)(\d+)")
# 話し言葉側: "10 to the minus/negative 16(th)?"(負の指数)。"minus"/
# "negative"どちらの語も同じ意味で使われる(実際のASR書き起こしで両方
# 観測済み)。序数接尾辞の有無を問わず、底と指数の桁だけを取り出す。
_SPOKEN_NEGATIVE_EXPONENT_RE = re.compile(
    r"\b(\d+)\s+to\s+the\s+(?:minus|negative)\s+(\d+)(?:st|nd|rd|th)?\b", re.IGNORECASE)
# 話し言葉側: "10 to the 16th"のような正の指数(minusを伴わない)。
# 上のnegative版を先に適用してから使うため、ここへ到達する時点でminus
# 付きは既にマーカー化済み。
_SPOKEN_POSITIVE_EXPONENT_RE = re.compile(
    r"\b(\d+)\s+to\s+the\s+(\d+)(?:st|nd|rd|th)?\b", re.IGNORECASE)


def _normalize_superscript_exponents_early(text: str) -> str:
    """canonical/ASR両側で使われる記号ベースの指数表記(Unicode上付き文字、
    ASCIIキャレット"^")を、xexpx(正)/xexpnegx(負)マーカーへ変換する。
    **normalize_text()のstrip_diacritics()より前に呼ぶこと**:
    strip_diacritics()のNFKD分解は上付き数字を通常の数字へ分解してしまい
    (例: "10⁻¹⁶"→"10−16")、「元々上付きだった」という情報(=指数で
    あるという情報)自体が失われ、この関数が呼ばれる前にもう検出できなく
    なる実バグを確認したため、あえてstrip_diacritics()より前段の専用
    ステップとして分離した(キャレット表記はASCII文字でNFKD分解の影響を
    受けないが、実装を1箇所にまとめるため同じ関数・同じタイミングで
    処理する)。マーカーはxdollarx等と同じ設計思想で、底・符号・桁を
    独立したtokenとして保持したまま比較する(10⁻¹⁶と10⁻⁶・10¹⁶を
    区別可能なまま残す)。"""
    def _repl_superscript(m: "re.Match") -> str:
        base = m.group(1)
        ascii_sup = m.group(2).translate(_SUPERSCRIPT_TRANSLATE)
        neg = ascii_sup.startswith("-")
        digits = ascii_sup.lstrip("+-")
        if not digits.isdigit():
            return m.group(0)  # 数字化できない場合は変更しない(安全側)
        marker = "xexpnegx" if neg else "xexpx"
        return f"{base}{marker}{digits}"

    def _repl_caret(m: "re.Match") -> str:
        base, sign, digits = m.group(1), m.group(2), m.group(3)
        marker = "xexpnegx" if sign == "-" else "xexpx"
        return f"{base}{marker}{digits}"

    text = _SUPERSCRIPT_EXPONENT_RE.sub(_repl_superscript, text)
    text = _CARET_EXPONENT_RE.sub(_repl_caret, text)
    return text


_DIGIT_X_DIGIT_RE = re.compile(r"(?<=\d)\s*x\s*(?=\d)", re.IGNORECASE)


def _normalize_spoken_exponents(text: str) -> str:
    """ASR側(話し言葉)の"N to the (minus/negative) M(th)?"を、
    _normalize_superscript_exponents_early()と同じxexpx/xexpnegx
    マーカーへ変換する。cardinal/ordinal語の変換より後に呼ぶことで、
    "ten to the minus sixteenth"のように綴られた場合も、先に数字化
    されてから拾える。さらに、数式でよく使われる記号を、ASR側の話し言葉
    と綴りが揃うよう共通の語へ変換する:
      "×" / 数字に挟まれた"x"(掛け算記号のASR書き起こしとして実際に
        観測された) -> " times "
      "="(等号) / "is equal to" -> "equals"
      "<"(不等号) -> " less than "、">"(不等号) -> " greater than "
    (これをしないと、例えば"*b* = 0.90"の"="は後段の記号除去でただ
    消えるだけなのに対し、ASR側の"b equals 0.90"は"equals"という語が
    残ってしまい、意味が同じでも一致しなくなる。"<"/">"も同様)。"""
    text = _SPOKEN_NEGATIVE_EXPONENT_RE.sub(r"\1xexpnegx\2", text)
    text = _SPOKEN_POSITIVE_EXPONENT_RE.sub(r"\1xexpx\2", text)
    text = text.replace("×", " times ")
    text = _DIGIT_X_DIGIT_RE.sub(" times ", text)
    text = re.sub(r"\b(?:is|was)\s+equal\s+to\b", "equals", text)
    text = text.replace("=", " equals ")
    text = text.replace("<", " less than ")
    text = text.replace(">", " greater than ")
    return text


def _words_to_number(words: list[str]) -> int | None:
    """word列(小文字、"and"含む)を1つの整数へ変換する。数値語列として
    不正な場合はNoneを返す(呼び出し側は元の語をそのまま残すこと)。"""
    total = 0
    current = 0
    seen_any = False
    for w in words:
        if w == "and":
            continue
        if w in _ONES:
            current += _ONES[w]
            seen_any = True
        elif w in _TENS:
            current += _TENS[w]
            seen_any = True
        elif w == "hundred":
            current = current * 100 if current else 100
            seen_any = True
        elif w in ("thousand", "million"):
            scale = _SCALES[w]
            total += (current if current else 1) * scale
            current = 0
            seen_any = True
        else:
            return None
    return total + current if seen_any else None


def _convert_cardinal_words(text: str) -> str:
    """text中のcardinal number word列(2語以上の組み合わせ、または
    hundred/thousand/millionを含む1語)を算用数字へ変換する。
    "one"は代名詞("the right one"等)としての使用頻度が高く曖昧なため、
    単独で出現した場合は変換しない(2語以上の並びの一部としてのみ変換
    対象、例: "one hundred")。"""
    text = re.sub(r"(?<=[a-zA-Z])-(?=[a-zA-Z])", " ", text)
    tokens = text.split()
    lower_tokens = [t.lower() for t in tokens]
    out = []
    i = 0
    while i < len(tokens):
        if lower_tokens[i] in _NUM_WORD_VOCAB:
            j = i
            while j < len(tokens) and lower_tokens[j] in _NUM_WORD_VOCAB:
                j += 1
            seq = lower_tokens[i:j]
            if len(seq) == 1 and seq[0] == "one":
                out.append(tokens[i])
                i += 1
                continue
            val = _words_to_number(seq)
            if val is None or (len(seq) == 1 and val < 2):
                out.append(tokens[i])
                i += 1
                continue
            out.append(str(val))
            i = j
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


def _convert_ordinal_words(text: str) -> str:
    """序数の綴り(third)を算用数字+序数接尾辞(3rd)へ変換する。基数(3)
    へは変換しない(序数と基数を混同すると"28 ≠ 28th"の区別が壊れる)。"""
    return _ORDINAL_WORD_RE.sub(lambda m: _ORDINAL_WORDS[m.group(0).lower()], text)


def normalize_numeric(text: str) -> str:
    """数値表記の意味同一な差(綴り⇔算用数字・桁区切りカンマ・小数点・
    パーセント・通貨・序数)を吸収する一方、桁や単位が変わる差は区別
    可能なまま残す。戻り値はさらにnormalize_text()の一般記号除去
    ([^a-z0-9]+をスペース化)を通ることを前提とする。%/$/小数点は、
    その除去ステップで消えてしまわないよう英数字のみのマーカー文字列
    (xdollarx/xpercentx/xdecimalpointx)へ変換しておく(除去後も
    "5"と"5xdollarx"のように異なるtokenのまま残り、5≠$5を保つ)。"""
    t = text.lower()
    # 0. 単語末尾に直接くっついた句読点(three.やfive,のような、文末や
    #    読点で頻発する形)を切り離す。_convert_cardinal_words()は
    #    空白区切りでtokenを取るため、句読点が単語へ付着したままだと
    #    "three."が語彙辞書の"three"と一致せず、数値語の並びが途中で
    #    途切れてしまう実バグがあった(例: "two thousand twenty-three."が
    #    "2020 three."になってしまっていた)。数字と数字の間の"."(小数点)
    #    は対象外にする(それは後段のstep 5で別途処理する)。
    t = re.sub(r"(?<=[a-z])([.,;:!?])", r" \1", t)
    # 1. 通貨記号(前置$)を、後段の通貨語処理と同じ形へ寄せる。
    t = re.sub(r"\$\s*(\d+(?:\.\d+)?)", r"\1 dollars", t)
    # 2. 桁区切りカンマの除去(1,000 -> 1000。3桁区切りの位置のみ対象、
    #    誤って無関係な数字列を結合しないよう桁数を限定する)。
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    # 2.5. 複合序数("twenty eighth"/"twenty-eighth"型)を、後続のcardinal/
    #      ordinal変換(手順3・7)が独立に分裂させる前に1トークンへ変換する
    #      (ER-010-DATE-SPOKEN-FORM-POINT-FIX-01)。
    t = _convert_compound_ordinal_words(t)
    # 3. cardinal数値語 -> 算用数字。
    t = _convert_cardinal_words(t)
    # 4. 通貨語(N dollars/dollar) -> マーカー。
    t = re.sub(r"\b(\d+(?:\.\d+)?)\s+dollars?\b", r"\1xdollarx", t)
    t = re.sub(r"\$\s*(\d+(?:\.\d+)?)", r"\1xdollarx", t)
    # 5. 小数点(digit point digit / digit.digit) -> マーカー。
    t = re.sub(r"\b(\d+)\s+point\s+(\d+)\b", r"\1xdecimalpointx\2", t)
    t = re.sub(r"(\d+)\.(\d+)", r"\1xdecimalpointx\2", t)
    # 6. パーセント(N percent / N%) -> マーカー。
    t = re.sub(r"\b(\d+(?:xdecimalpointx\d+)?)\s*(?:percent|per cent)\b", r"\1xpercentx", t)
    t = re.sub(r"(\d+(?:xdecimalpointx\d+)?)\s*%", r"\1xpercentx", t)
    # 7. 序数語 -> 算用数字+序数接尾辞(基数へは変換しない)。
    t = _convert_ordinal_words(t)
    # 8. 日付文脈(月名直後)の序数接尾辞のみ除去。月名が無い"28th"等は
    #    そのまま残り、"28"(基数)と区別され続ける。
    t = _DATE_ORDINAL_RE.sub(r"\1 \2", t)
    # 9. 数式の指数表記(ASR側の"to the (minus) N(th)?"という話し言葉、
    #    および"×"記号)を、底・符号・桁を保ったままマーカー化する。
    #    cardinal/ordinal語の変換(手順3・7)より後に置くことで、
    #    "ten to the minus sixteenth"のように綴られた場合も先に数字化
    #    されてから拾える。canonical側のUnicode上付き文字は、strip_diacritics()
    #    によるNFKD分解で情報が失われる前に、normalize_text()の先頭で
    #    既にマーカー化済み(_normalize_superscript_exponents_early参照)。
    t = _normalize_spoken_exponents(t)
    return t


_NEGATION_WORDS = {
    "not", "no", "never", "none", "nobody", "nothing", "nowhere", "neither", "nor",
    "cannot", "cant", "wont", "isnt", "arent", "wasnt", "werent", "doesnt", "dont",
    "didnt", "hasnt", "havent", "hadnt", "wouldnt", "shouldnt", "couldnt", "without",
}


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
    # strip_diacritics()のNFKD分解はUnicode上付き数字/マイナスを通常の
    # 数字へ分解してしまい、「上付きだった」という指数情報自体が失われる
    # (例: "10⁻¹⁶"→"10−16")。そうなるとxexpx/xexpnegxマーカーへ変換する
    # 手がかりが消えてしまうため、strip_diacritics()より前のこの時点で
    # 先にマーカー化しておく。
    t = _normalize_superscript_exponents_early(t)
    t = strip_diacritics(t)
    for br, am in BR_AM_SPELLING_PAIRS:
        t = t.replace(br, am)
    t = t.replace("—", "-").replace("–", "-")
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = normalize_numeric(t)
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
    # ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22: normalize_text()の
    # `re.sub(r"[^a-z0-9]+", " ", t)`はアポストロフィも空白へ置換するため、
    # 短縮形("they're"→"they re")は"re"部分だけが独立したtokenとして残る。
    # canonical側が展開形("they are"等)の場合、"are"は既にstopwordだが、
    # ASR側の短縮形の残骸("re")はstopword集合に無いため、内容の変化が
    # 無いのにcontent_word_diffs(TRUE_CONTENT_MISMATCH)として検出されて
    # しまうbugがNo.8 B1 full_story_part2("They are"→TTSが自然に
    # "They're"と発話)で実際に発生した(3回中3回、ASR結果は毎回意味上
    # 完全に同じだが機械的にretryが続き、最終的にSTOPPEDへ到達した)。
    # "re"(are由来)は他の一般的な英単語と衝突する可能性が低いため安全に
    # stopword化できる。"will"/"have"由来の"ll"/"ve"は、"will"/"have"
    # 自体がstopwordではなく実質的な意味を持つ語のため、同じ対策では
    # 直らず("we'll"→"we"+"ll" vs canonical"we"+"will"はreplace型diffに
    # なる)、より広い契約形(contraction)対応の設計が別途必要(本修正の
    # 対象外、実データでの発生は未確認のため今回は見送る)。
    "re",
}


def _is_number(tok: str) -> bool:
    return tok.isdigit()


def _singularize_simple(word: str) -> str | None:
    """規則的な複数形のみを単数形へ変換する(不規則複数形は対象外)。
    誤って無関係な短い語を同一視しないよう、長さと語尾の形を厳格に絞る。
    Noneは「この語は規則複数形として扱えない」を意味する(安全側)。"""
    if len(word) > 4 and word.endswith("es") and word[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return word[:-2]  # matches -> match, boxes -> box
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]  # results -> result
    return None


def _is_benign_plural_pair(a: str, b: str) -> bool:
    """"result"/"results"のような、規則的な単数形・複数形の揺れのみの語対を
    判定する。ASR側が複数形/単数形をどちらで書き起こすかは意味内容の誤りを
    示さない(cancelling/canceling等の綴り差と同種の、表記上の揺れ)。"""
    if a == b:
        return True
    return _singularize_simple(a) == b or _singularize_simple(b) == a


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
            if (len(canon_content) == len(asr_content)
                    and all(_is_benign_plural_pair(c, a) for c, a in zip(canon_content, asr_content))):
                # 規則的な単数形/複数形の揺れのみ(例: "result"/"results")。
                # BR/AM綴り差等と同種の表記上の揺れとみなし、content_word_diffs
                # へは追加しない(内容誤りではないため、後段のcascade判定を
                # 無関係な複数形差でブロックしない)。
                continue
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
                # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part I/J:
                # 単一語同士の置換差(wait/weight等)で、CMU Pronouncing
                # Dictionaryの発音(ARPAbet)が完全一致する場合のみ
                # homophone_candidateとする(削除/追加[canon_content/
                # asr_contentのどちらかが空]は対象外、entity_likeと同様
                # 比較可能な1語同士のみを対象にする)。
                homophone_candidate = False
                if len(canon_content) == 1 and len(asr_content) == 1:
                    result_h = homophone_en.homophone_arpabet_equivalent(canon_content[0], asr_content[0])
                    homophone_candidate = bool(result_h)
                result.content_word_diffs.append({
                    "type": tag, "canonical": " ".join(canon_content), "asr": " ".join(asr_content),
                    "entity_like": entity_like, "homophone_candidate": homophone_candidate,
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

    # 冠詞(a/an/the)だけを除いた内容語を despace して比較する版。
    # 短いKey Phrase(例: canonical="a wide-scale empirical study" vs
    # asr="Widescale empirical study.")で冠詞の有無自体が表記差の対象外
    # であるケースを吸収する。
    # ER-008-N7-CONTENT-AUDIO-QA-02で発見: ここで_STOPWORDS全体(with/by/
    # from/as等の前置詞も含む)を使うと、"compare poorly with"のような
    # 前置詞で終わる短いKey Phraseで、実際には"with"が欠落した音声
    # ("Compare poorly")が、"with"がstopwordとして両側から消えることで
    # 誤ってNORMALIZED_MATCH判定されてしまう(実際の欠落語を見逃す
    # Validator gap)。この despace shortcutは冠詞のみを対象とし、
    # 意味を持つ前置詞・接続詞は_STOPWORDSに含まれていてもここでは
    # 除去しない(articles_onlyへ限定)。
    articles_only = {"a", "an", "the"}
    canon_content_only = [t for t in tokenize(canonical_text) if t not in articles_only]
    asr_content_only = [t for t in tokenize(asr_text) if t not in articles_only]
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

    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part I/J: homophone_
    # candidate(発音がCMU辞書上完全一致する単一語の置換差、wait/weight
    # 等)も、entity_likeと同様に「即TTS retry」の対象からは除外する
    # (即retryさせると、No.8 wait/weightのように音として正しい可能性が
    # 高い音声を無駄に何度も作り直してしまうため)。
    non_entity_diffs = [d for d in protected.content_word_diffs
                         if not d["entity_like"] and not d["homophone_candidate"]]
    entity_only_diffs = [d for d in protected.content_word_diffs if d["entity_like"]]
    homophone_only_diffs = [d for d in protected.content_word_diffs
                             if d["homophone_candidate"] and not d["entity_like"]]

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

    if homophone_only_diffs:
        return ClassificationResult("ASR_VALIDATION_UNCERTAIN", ratio, protected,
                                     should_pass=False, should_retry=False,
                                     reason=f"発音が完全一致する同音語らしき語にのみ差がある"
                                            f"(retryでは解決しない可能性が高い): {homophone_only_diffs}")

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


# ============================================================
# ER-010-ENTITY-PHONETIC-CORROBORATION-01: 固有名詞ASR表記揺れの
# 軽量音韻類似度チェック
# ============================================================
# 背景(No.5 pool_n5_cafes B1 full_story_part1で発生): entity_only_diffs
# (上記classify_asr_match、固有名詞らしき語のみの音訳差)はASR_VALIDATION_
# UNCERTAIN(should_pass=False、retryしても改善しない)としてHuman Review
# へ回る設計が既にある(is_entity_like_mismatch、er006_secondary_asr_01.py)。
# しかし「自動PASSさせる」設計は無く、実際には正しく発話されている可能性が
# 高い音声(例: "L. Mimoun and A. Gruen"という、英語ASRにとって馴染みの
# 薄い研究者名)が、TTSを何度取り直しても解決しないままHuman Reviewに
# 滞留する。
#
# 新しいresearch工程(発音資料の事前調査)は、全記事・全固有名詞への一律
# コスト増になるため追加しない(過剰実装の回避)。代わりに、実際に
# entity_only_diffsが発生した名前**だけ**を対象に、複数の独立したTTS
# 取り直し(同じ音声の複数回文字起こしではなく、別々に生成されたTTS
# takeそれぞれのASR結果)を比較し、以下の軽量な音韻類似度チェック
# (pure Python、新規外部依存なし、日本語側の_reading_equal_allowing_
# voicing()と同じ発想の英語版)で、明らかに同一固有名詞の音訳揺れだと
# 判定できる場合のみ自動PASS相当として扱う。
#
# 設計上の要点(既存のprotected_check思想[数字/否定/内容語は絶対に
# 見逃さない]を壊さないための保守的な制約):
#   1. 各takeごとにentity_only_diffs(数字・否定・非固有名詞内容語の差が
#      一切無い不一致)かどうかを個別に判定する。数字・否定・非固有名詞
#      内容語の差を含むtakeは、そのtake単体を判断材料から除外するのみで
#      (1回だけの無関係な不具合[語の脱落等]は対象entityの音韻評価とは
#      別問題)、他の独立したtakeがentity-onlyで一貫していれば、その
#      takeの証拠は引き続き使う(全体を一括拒否しない)。
#   2. 同じcanonical entity spanについて、複数の独立したTTS take間で
#      **異なる**ASR書き起こし候補が観測された場合のみ、標準的な閾値
#      (soundex一致+文字列類似度0.5以上+文字数差2以内+語頭一致)で
#      音韻類似度を判定する。同じ誤認識が繰り返し観測される場合は、
#      「ASRのノイズ」ではなく「別の実在する固有名詞として安定して
#      聞こえている」可能性を排除できないため、自動PASSしない
#      (例: "Robert"→"Rupert"のような、無関係だが実在する別人名への
#      置き換わりを拒否するための設計。この2語はsoundexが一致し文字列
#      類似度も高いため、単発の判定だけでは区別できない)。
#   3. 1回しか観測されていないentity spanについては、上記2の「異なる
#      候補の多様性」による裏付けが無いため、より厳しい閾値(文字列
#      類似度0.75以上+文字数差1以内)を要求する。
#   4. 複数語からなるentity span(例: "Ralf Rüller")は、canonical/ASR
#      両方の語数が一致する場合のみ語ごとに判定する(語数が異なる場合
#      [例: "Neukölln"→"new Cologne"]は、既に別の単語への丸ごと置換
#      である可能性が高いため対象外とし、Human Reviewのまま維持する)。
#
# **既知の限界(正直に記録)**: soundexベースの軽量チェックは、
# "Robert"/"Rupert"のように無関係な既存の別名同士でもsoundexコードが
# 一致するケースを完全には排除できない(上記2の多様性要件で緩和して
# いるが、理論的に完全ではない)。本チェックはあくまで「retry・Human
# Review滞留を減らすための補助的な最適化」であり、既存の必須プロセス
# (最終的なユーザー試聴)がこの限界に対する最終的な安全網であり続ける
# (CURRENT_SPEC.md「最終人間試聴」原則は本チェックの追加によっても
# 一切変更しない)。
ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED = "ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED"

_SOUNDEX_CODES = {}
for _ch in "BFPV":
    _SOUNDEX_CODES[_ch] = "1"
for _ch in "CGJKQSXZ":
    _SOUNDEX_CODES[_ch] = "2"
for _ch in "DT":
    _SOUNDEX_CODES[_ch] = "3"
_SOUNDEX_CODES["L"] = "4"
for _ch in "MN":
    _SOUNDEX_CODES[_ch] = "5"
_SOUNDEX_CODES["R"] = "6"


def soundex_en(word: str) -> str:
    """標準的なSoundexアルゴリズム(pure Python、新規外部依存なし)。
    英字以外は無視する(発音区別符号除去後の語を渡すことを想定)。"""
    letters = re.sub(r"[^A-Za-z]", "", (word or "")).upper()
    if not letters:
        return ""
    first = letters[0]
    codes = []
    prev = _SOUNDEX_CODES.get(first, "")
    for ch in letters[1:]:
        code = _SOUNDEX_CODES.get(ch, "")
        if code and code != prev:
            codes.append(code)
        if ch not in "HW":  # H/Wは前の子音との「隣接」を切らない(標準仕様)
            prev = code
    return (first + "".join(codes) + "000")[:4]


def _phonetic_pair_ok(a: str, b: str, *, strict: bool) -> bool:
    """1語同士の音韻類似度判定。strict=Trueは単発観測(裏付け無し)向けの
    厳しい閾値、strict=Falseは複数の異なる候補が観測された場合(多様性
    そのものが裏付けになる)向けの標準閾値。

    ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 D-1で修正: 従来は先頭
    文字の"綴り"が完全一致しない場合に即FAILしていたが(`a[0] != b[0]`)、
    これは"Kristie"(k)と"Christy"(c)のように、綴りは異なっても英語では
    同じ音(/k/)を表す組の実例(No.8監査)を誤って弾いていた。soundex_en()
    が単語の残り部分では既にC/G/J/K/Q/S/X/Zを同じ子音グループ"2"として
    扱っているのと同じ_SOUNDEX_CODESテーブルを、先頭文字の比較にも
    再利用する(新規のテーブルを追加せず、既存の等価グループをそのまま
    拡張する)。母音・H・Wのようにテーブルに無い文字は、`.get(ch, ch)`に
    より従来通り文字そのもので比較され(=綴りが異なれば不一致のまま)、
    無関係な母音同士まで緩めることはない。"""
    a, b = a.lower(), b.lower()
    if a == b:
        return True
    if not a or not b:
        return False
    if _SOUNDEX_CODES.get(a[0].upper(), a[0]) != _SOUNDEX_CODES.get(b[0].upper(), b[0]):
        return False
    # soundex_en()自体は標準Soundex仕様通り先頭文字を常に生の文字で
    # 残す(K623/C623のように、残りが同じ子音コードでも先頭文字の違いで
    # 文字列としては不一致になる)。先頭文字の等価性は直前で確認済みの
    # ため、ここでは残りのコード部分(位置1以降)だけを比較する。
    if soundex_en(a)[1:] != soundex_en(b)[1:]:
        return False
    max_len_diff = 1 if strict else 2
    min_ratio = 0.75 if strict else 0.5
    if abs(len(a) - len(b)) > max_len_diff:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= min_ratio


def _strip_short_tokens(span: str) -> str:
    """"L."のような1〜2文字の頭文字・略語トークンを取り除く。difflibの
    word-level diffは、ASR側で頭文字が直後の固有名詞と融合して書き起こ
    される場合(例: "L. Mimoun"→"Elmi Moon")、canonical側のspan境界に
    その頭文字を含めるかどうかが試行ごとに揺れる(実データで確認済み:
    同じ"L. Mimoun"が、あるtakeでは"mimoun"単独、別のtakeでは"l mimoun"
    という2語spanとして検出された)。この揺れによって同一固有名詞の証拠が
    別々のspan keyへ分裂するのを防ぐため、grouping key算出時に短い
    トークンを取り除く(全て短い場合は元のspanのまま返す=安全側)。"""
    words = [w for w in span.split() if len(w) > 2]
    return " ".join(words) if words else span


def _span_phonetically_ok(canonical_words: list[str], asr_span: str, *, strict: bool) -> bool:
    """canonical_words(既に短いトークンを除去済みの語列)と、ASR候補
    spanの語数が一致する場合のみ語ごとに判定する。語数が一致しない場合は
    「判定不能」を示すNoneではなくFalseを返す(呼び出し側でこの関数を
    使う前に、比較可能なペアかどうかを別途確認すること)。"""
    asr_words = asr_span.split()
    if not canonical_words or len(canonical_words) != len(asr_words):
        return False
    return all(_phonetic_pair_ok(c, a, strict=strict) for c, a in zip(canonical_words, asr_words))


def aggregate_entity_only_phonetic_corroboration(canonical_text: str, asr_texts: list[str]) -> dict:
    """複数の独立したTTS take(asr_texts、それぞれ別のTTS生成に対する
    Primary ASR書き起こし)を、同じcanonical_textに対して再分類し、
    entity_only_diffsだけが原因の不一致が、音韻的に見て「同じ固有名詞の
    ASR書き起こし揺れ」だと判定できるかを集約評価する。

    新規TTS/ASR API呼び出しは一切行わない(既に得られたasr_textsを
    classify_asr_match()で再分類するだけの、ローカルでの後処理)。

    戻り値: {"accept": bool, "reason": str, "spans": {canonical_span: [asr候補,...]}}
    """
    if len(asr_texts) < 1:
        return {"accept": False, "reason": "no attempts provided", "spans": {}}

    spans: dict[str, set[str]] = {}
    skipped_non_entity = 0
    for asr_text in asr_texts:
        cls = classify_asr_match(canonical_text, asr_text)
        if cls.should_pass:
            continue  # このtakeは既に合格しているので集約対象外(問題なし)
        diffs = cls.protected.content_word_diffs
        if not diffs or not all(d["entity_like"] for d in diffs):
            # 固有名詞以外の差(数字・否定・通常内容語)を含むtakeは、この
            # 機構の判断材料としては使わない(そのtakeだけを除外する)。
            # ただし、他の独立したtakeがentity-onlyで一貫していれば、
            # その別の1回の失敗を理由に全体を拒否はしない(1回だけの
            # 無関係な不具合[語の脱落等]は、対象entityの音韻評価とは
            # 別問題であり、そのentity自体の評価を無効にする理由には
            # ならないため)。
            skipped_non_entity += 1
            continue
        for d in diffs:
            key = _strip_short_tokens(d["canonical"])
            spans.setdefault(key, set()).add(d["asr"])

    if not spans:
        return {"accept": False,
                "reason": f"no usable entity-only diffs across the given takes "
                          f"(skipped {skipped_non_entity} take(s) with non entity-only mismatches)",
                "spans": {}}

    for canon_span, guesses in spans.items():
        canon_words = canon_span.split()
        # 頭文字融合等で語数が対応しない候補は「判定不能」として除外する
        # (反証にも証拠にもしない)。全候補が語数不一致なら判断材料無し。
        comparable = [g for g in guesses if len(g.split()) == len(canon_words)]
        if not comparable:
            return {"accept": False,
                    "reason": f"no word-count-comparable candidates for {canon_span!r}: "
                              f"candidates={sorted(guesses)}",
                    "spans": {k: sorted(v) for k, v in spans.items()}}
        strict = len(set(comparable)) < 2  # 単発観測(裏付け無し)は厳しい閾値
        if not all(_span_phonetically_ok(canon_words, g, strict=strict) for g in comparable):
            return {"accept": False,
                    "reason": f"phonetic check failed for {canon_span!r}: candidates={sorted(guesses)}",
                    "spans": {k: sorted(v) for k, v in spans.items()}}

    return {"accept": True,
            "reason": "all entity-only spans are phonetically consistent with the canonical spelling "
                      "across independently generated takes",
            "spans": {k: sorted(v) for k, v in spans.items()}}
