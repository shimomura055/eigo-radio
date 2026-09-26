# ============================================================
# er021_en_asr_semantic_equivalence_trial_01.py
# EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01(Phase A+B、Trial、Production非配線)
# ============================================================
# 性質: Trial実装+検証(ユーザーTrial承認2026-09-26)。Production採用ではない。
# 前提Recon: docs/pm/recon_en_asr_semantic_equivalence_01.md /
#            recon_en_asr_semantic_equivalence_02_tier2_tier3.md
#            EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md Part 2(推奨最終
#            仕様Phase A/B)。承認範囲はPhase A(数値等価・観測性)+Phase B
#            (規則的複数形・固有名詞ASR表記差のcorroboration付き救済、
#            ASR_VALIDATION_UNCERTAINのsub-reason)。Phase C(wanna/gonna等
#            Tier2)は対象外、実装しない。
#
# Production安全性: 本ファイルはer006_preprod_hardening_01_validation.py
# (classify_asr_match/tokenize/capitalized_flags等)を一切変更せず、
# read-onlyでimportして「外側から包む」新規Trial moduleのみを追加する。
# er006_secondary_asr_01.py/er020_tts_retry_local_rewrite_01.py/
# er003_*/er011_*等の既存Production moduleも無変更(このファイルは
# それらをimportして評価専用に呼び出すだけで、cool-down/Local Rewrite/
# Human Review Lockのいずれも発火させない——本Trialは判定層のみを検証する)。
#
# Tier 1(数値/通貨/%/年/時刻/分数/ローマ数字/略語の値等価)は、既存
# normalize_numeric()とは完全に独立した新規パーサとしてこのファイル内に
# 実装する(Fable最終レビューの推奨配置: 「classify_asr_matchラッパー
# 前段のearly-exit、normalize_numeric()本体は無改変」)。値比較は
# fractions.Fraction(有理数の厳密演算、Decimal由来の入力から構築するため
# 2.3や1/3のような値も丸め誤差なく比較できる)を用いる。
#
# 書き込み範囲: 本ファイル(root)+
# er021_output/en_asr_semantic_equivalence_trial_01/ 配下のみ。
# Git操作はこのファイル自身は行わない(Fableが統合)。

from __future__ import annotations

import copy
import difflib
import hashlib
import json
import os
import re
import sys
import time
from decimal import Decimal
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Production Validator(HEAD版、無変更でimportのみ)。
import er006_preprod_hardening_01_validation as val

OUT_DIR = "er021_output/en_asr_semantic_equivalence_trial_01"
RESULTS_DIR = f"{OUT_DIR}/results"
AUDIT_DIR = f"{OUT_DIR}/audit"
AUDIO_DIR = f"{OUT_DIR}/audio"
CORPUS_PATH = f"{OUT_DIR}/corpus.jsonl"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
OBSERVABILITY_LOG_PATH = f"{AUDIT_DIR}/observability_ng_log.jsonl"

FIXTURE_TEST_MODULE_PATH = "er006_preprod_hardening_01_validation_test.py"
EXISTING_PROBE_PATH = "er020_output/tts_local_rewrite_production_wiring_01/a2/comment_test2_probe.json"

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 30.0  # ユーザー指定Guardrail(超えそうなら中断報告)

for _d in (OUT_DIR, RESULTS_DIR, AUDIT_DIR, AUDIO_DIR):
    os.makedirs(_d, exist_ok=True)


def log(msg):
    print(msg, flush=True)


# ============================================================
# Part 0: コスト計測(既存Trialパターン[er011_transcript_style_
# normalization_trial_01.py]を再利用、Azure呼び出しはcost_logger.install()
# 自動記録の対象外のため独自にrecord()する)
# ============================================================
def _load_pricing():
    prices = json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]

    def price(provider, model, meter, tier="Standard"):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == tier)
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
                if provider == "openai_asr" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("openai_asr", model, "input_tokens") / 1e6 \
                        + out_tok * price("openai_asr", model, "output_tokens") / 1e6
                elif provider == "azure":
                    dur_s = rec.get("audio_duration_submitted_seconds") or 0.0
                    usd = (dur_s / 3600.0) * price(
                        "azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
                elif provider in ("gemini", "gemini_batch") and model:
                    tier = "Batch" if provider == "gemini_batch" else "Standard"
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("gemini", model, "input_tokens", tier) / 1e6 \
                        + out_tok * price("gemini", model, "output_tokens", tier) / 1e6
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


def record_azure_call(duration_seconds, api="get_full_text_via_azure_stt_with_phrase_list"):
    import er005_cost_logger as cost_logger
    cost_logger.record({
        "provider": "azure", "api": api, "model_id": "azure-speech-stt",
        "audio_duration_submitted_seconds": duration_seconds,
    })


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================
# Part 1: Tier 1 数値/通貨/%/年/時刻/分数/ローマ数字/略語 値パーサ
# ============================================================
# 安全設計の核心(Fable最終レビュー準拠): 両側を同一の意味値へ「パース」し、
# 値が完全一致した場合のみ等価とする(文字列正規化の拡張ではない)。
# パース失敗・非対応構文は「等価でない」扱い(best-effort禁止、常に安全側)。
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90}
_MULTI_SCALE_WORDS = {"thousand": 1000, "million": 10 ** 6, "billion": 10 ** 9, "trillion": 10 ** 12}
_SCALE_WORDS = {"hundred": 100, **_MULTI_SCALE_WORDS}
_NUMBER_VOCAB = set(_ONES) | set(_TENS) | set(_SCALE_WORDS) | {"and"}

# ローマ数字: 安全のため単独の"I"(代名詞"I"と衝突するため)は意図的に
# 対象から除外する(閉じた集合をII〜Xに限定、Fable批判レビュー#10相当の
# 追加安全策——仕様の範囲を「狭める」方向の変更のみであり、既存の
# 「安全性を落とす」変更ではないためTrial実装判断として妥当と考える)。
_ROMAN_SAFE = {"II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}

_CURRENCY_SYMBOLS = {"$": "USD", "£": "GBP", "€": "EUR"}
_CURRENCY_WORDS = {"dollar": "USD", "dollars": "USD", "pound": "GBP", "pounds": "GBP",
                    "euro": "EUR", "euros": "EUR"}

_FRACTION_PHRASES = {
    ("a", "half"): Fraction(1, 2), ("one", "half"): Fraction(1, 2),
    ("a", "third"): Fraction(1, 3), ("one", "third"): Fraction(1, 3),
    ("two", "thirds"): Fraction(2, 3),
    ("a", "quarter"): Fraction(1, 4), ("one", "quarter"): Fraction(1, 4),
    ("three", "quarters"): Fraction(3, 4),
}

_NUMSTR_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")
_FRACTION_DIGIT_RE = re.compile(r"(\d+)/(\d+)")
_TOKEN_RE = re.compile(
    r"[$£€]\d[\d,]*(?:\.\d+)?"
    r"|\d{1,2}:\d{2}"
    r"|\d+/\d+"
    r"|\d[\d,]*(?:\.\d+)?%"
    r"|\d[\d,]*(?:\.\d+)?"
    r"|[A-Za-z']+"
    # ER021-SAFETY: 上記いずれにも一致しない文字(上付き指数記号
    # ¹⁶・数式記号×÷等、空白でない1文字)を、黙って消える(=情報が
    # 消失し値が変わって見えてしまう)のではなく、必ず1文字ずつの
    # literal atomとして残す。これにより指数表記("10¹⁶"のような
    # Tier1対象外の構文)が誤って"10"と等価扱いされる(false accept)
    # ことを防ぐ(既存fixtureで実測して発見・修正)。
    r"|[^\s]"
)


def _preprocess_raw(text: str) -> str:
    """記号レベルの閉じた対応(&⇔and、No.⇔number、minus⇔-)を、大文字小文字
    情報(ローマ数字判定に必要)を保ったまま適用する。"""
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"\bNo\.\s*(?=\d)", "number ", text)
    # 語と語の間のハイフン(twenty-eight/ninety-nine等)は、語を分かつ
    # 空白と同じ扱いにする(production側_convert_cardinal_words()と同型の
    # 対策)。数字の直前のマイナス記号(下記)とは別の構文のため、先に
    # 処理する。
    text = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", text)
    # マイナス記号(数字の直前、直前の文字が数字でない場合のみ)。
    # "10-20"のような範囲表現(直前が数字)は対象外(等価にしない)。
    text = re.sub(r"(?<![\d])-(?=\d)", " minus ", text)
    return text


def _to_fraction(numstr: str) -> Fraction:
    return Fraction(Decimal(numstr.replace(",", "")))


def _mk_number(value: Fraction, currency: str | None = None, percent: bool = False) -> dict:
    return {"kind": "number", "value": value, "currency": currency, "percent": percent}


def _split_into_two_digit_groups(words: list[str]) -> list[int] | None:
    """"nineteen ninety-nine"(年のペア読み)のような、桁を連結する2桁
    グループへ分割できるかを判定する。同時に、単独の一桁数字語の連続
    ("one two three"のような桁ごとの読み上げ)を1つの数へ合成しない
    (7桁以上の数字列・単独数字語の連続は合成しない、という安全側の
    制約)。"""
    groups = []
    i, n = 0, len(words)
    while i < n:
        w = words[i]
        if w in _TENS:
            if i + 1 < n and words[i + 1] in _ONES and 1 <= _ONES[words[i + 1]] <= 9:
                groups.append(_TENS[w] + _ONES[words[i + 1]])
                i += 2
            else:
                groups.append(_TENS[w])
                i += 1
        elif w in _ONES:
            v = _ONES[w]
            if v >= 10:
                groups.append(v)
                i += 1
            else:
                if n == 1:
                    groups.append(v)
                    i += 1
                else:
                    return None  # 単独一桁数字語の連続 -> 合成しない(安全側)
        else:
            return None
    return groups


def _words_to_number_scale(words: list[str]) -> int | None:
    total, current, seen = 0, 0, False
    for w in words:
        if w == "and":
            continue
        if w in _ONES:
            current += _ONES[w]
            seen = True
        elif w in _TENS:
            current += _TENS[w]
            seen = True
        elif w == "hundred":
            current = (current if current else 1) * 100
            seen = True
        elif w in _MULTI_SCALE_WORDS:
            scale = _MULTI_SCALE_WORDS[w]
            total += (current if current else 1) * scale
            current = 0
            seen = True
        else:
            return None
    if not seen:
        return None
    return total + current


def _parse_bare_number_run(words: list[str]) -> int | None:
    if any(w in _SCALE_WORDS for w in words):
        return _words_to_number_scale(words)
    groups = _split_into_two_digit_groups([w for w in words if w != "and"])
    if groups is None:
        return None
    if len(groups) == 1:
        return groups[0]
    if len(groups) == 2:
        # 年のペア読み(nineteen ninety-nine=1999、twenty twenty-six=2026等)。
        # スケール語が無い場合のみ、2つの2桁グループを百の位で連結する
        # (加算ではない、通常の基数読みとは異なる文法)。
        return groups[0] * 100 + groups[1]
    return None


def _consume_number_word_run(words: list[str], i: int):
    n = len(words)
    j = i
    while j < n and words[j].lower() in _NUMBER_VOCAB:
        j += 1
    integer_words = [w.lower() for w in words[i:j]]
    if not integer_words:
        return None
    int_value = _parse_bare_number_run(integer_words)
    if int_value is None:
        return None
    value = Fraction(int_value)
    k = j
    if k < n and words[k].lower() == "point":
        k2 = k + 1
        frac_digits = []
        while k2 < n and words[k2].lower() in _ONES and _ONES[words[k2].lower()] < 10:
            frac_digits.append(_ONES[words[k2].lower()])
            k2 += 1
        if frac_digits:
            frac_str = "0." + "".join(str(d) for d in frac_digits)
            value = value + Fraction(Decimal(frac_str))
            k = k2
    return value, k


def _try_fraction_phrase(words: list[str], i: int):
    if i + 1 >= len(words):
        return None
    key = (words[i].lower(), words[i + 1].lower())
    if key in _FRACTION_PHRASES:
        return _FRACTION_PHRASES[key], 2
    return None


def _try_minute(words: list[str], j: int):
    """時刻の分部分(2桁グループ、"thirty"/"fifteen"/"forty five"等)。
    ちょうど1つの2桁グループとして解釈でき、値が0〜59の範囲に収まる
    場合のみ返す(それ以外はNone、安全側)。"""
    n = len(words)
    for length in (2, 1):
        if j + length <= n:
            candidate = [w.lower() for w in words[j:j + length]]
            if all(w in _ONES or w in _TENS for w in candidate):
                groups = _split_into_two_digit_groups(candidate)
                if groups and len(groups) == 1 and 0 <= groups[0] <= 59:
                    return groups[0], j + length
    return None


def _try_spoken_time(words: list[str], i: int):
    """"three thirty pm"/"six oh five am"のような話し言葉の時刻表現。
    誤爆(単なる基数の並びを時刻と誤認)を避けるため、am/pmが直後に
    続く場合のみ時刻として認識する(Fable最終レビュー: 時刻はh:mm⇔語+
    am/pmの閉じた対応のみ)。"""
    n = len(words)
    hour_word = words[i].lower()
    if hour_word not in _ONES or not (1 <= _ONES[hour_word] <= 12):
        return None
    hour = _ONES[hour_word]
    j = i + 1
    minute = None
    if (j < n and words[j].lower() == "oh" and j + 1 < n
            and words[j + 1].lower() in _ONES and _ONES[words[j + 1].lower()] < 10):
        minute = _ONES[words[j + 1].lower()]
        j += 2
    else:
        m = _try_minute(words, j)
        if m is not None:
            minute, j = m
    if minute is None:
        return None
    if j < n and words[j].lower() in ("am", "pm"):
        meridiem = words[j].lower()
        j += 1
    else:
        return None  # am/pmが無い場合は時刻として確定させない(安全側)
    return {"kind": "time", "value": Fraction(hour * 100 + minute), "meridiem": meridiem}, j


def _apply_suffixes(atom: dict, words: list[str], idx: int) -> int:
    """数値atom生成直後に、続く語がscale語(hundred/thousand/million/
    billion/trillion)・"percent"・通貨語(dollars等)であれば併合する。
    digit形式・語形式のどちらから来たatomにも同じロジックを適用する。"""
    if atom["kind"] != "number":
        return idx
    n = len(words)
    if idx < n and words[idx].lower() in _SCALE_WORDS:
        atom["value"] = atom["value"] * _SCALE_WORDS[words[idx].lower()]
        idx += 1
    if idx < n:
        w = words[idx].lower()
        if w == "percent" and not atom["percent"]:
            atom["percent"] = True
            idx += 1
        elif w in _CURRENCY_WORDS and atom["currency"] is None:
            atom["currency"] = _CURRENCY_WORDS[w]
            idx += 1
    return idx


def _tier1_atoms(text: str) -> list[dict]:
    if not text:
        return []
    raw = _preprocess_raw(text)
    words = _TOKEN_RE.findall(raw)
    atoms: list[dict] = []
    i, n = 0, len(words)
    while i < n:
        w = words[i]
        if w and w[0] in _CURRENCY_SYMBOLS and _NUMSTR_RE.fullmatch(w[1:]):
            atoms.append(_mk_number(_to_fraction(w[1:]), currency=_CURRENCY_SYMBOLS[w[0]]))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        m = _TIME_RE.fullmatch(w)
        if m:
            hour, minute = int(m.group(1)), int(m.group(2))
            meridiem, consumed = None, 1
            if i + 1 < n and words[i + 1].lower() in ("am", "pm"):
                meridiem = words[i + 1].lower()
                consumed = 2
            atoms.append({"kind": "time", "value": Fraction(hour * 100 + minute), "meridiem": meridiem})
            i += consumed
            continue
        m = _FRACTION_DIGIT_RE.fullmatch(w)
        if m:
            num, den = int(m.group(1)), int(m.group(2))
            if den != 0:
                atoms.append(_mk_number(Fraction(num, den)))
                i += 1
                i = _apply_suffixes(atoms[-1], words, i)
                continue
        if w.endswith("%") and _NUMSTR_RE.fullmatch(w[:-1]):
            atoms.append(_mk_number(_to_fraction(w[:-1]), percent=True))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        if _NUMSTR_RE.fullmatch(w):
            bare = w.replace(",", "")
            if "," not in w and "." not in w and len(bare) >= 7:
                # 7桁以上の生の数字列(電話番号・ID等) -> 値化せず桁完全一致のみ
                atoms.append({"kind": "literal", "word": w})
                i += 1
                continue
            atoms.append(_mk_number(_to_fraction(w)))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        if w in _ROMAN_SAFE:
            atoms.append(_mk_number(Fraction(_ROMAN_SAFE[w])))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        frac = _try_fraction_phrase(words, i)
        if frac is not None:
            value, consumed = frac
            atoms.append(_mk_number(value))
            i += consumed
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        spoken_time = _try_spoken_time(words, i)
        if spoken_time is not None:
            atom, next_i = spoken_time
            atoms.append(atom)
            i = next_i
            continue
        lw = w.lower()
        if lw in _NUMBER_VOCAB:
            parsed = _consume_number_word_run(words, i)
            if parsed is not None:
                value, next_i = parsed
                atoms.append(_mk_number(value))
                i = next_i
                i = _apply_suffixes(atoms[-1], words, i)
                continue
        atoms.append({"kind": "literal", "word": lw.strip("'")})
        i += 1
    return atoms


def _atoms_equal(a: dict, b: dict) -> bool:
    if a["kind"] != b["kind"]:
        return False
    if a["kind"] == "literal":
        return a["word"] == b["word"]
    if a["kind"] == "number":
        return a["value"] == b["value"] and a["currency"] == b["currency"] and a["percent"] == b["percent"]
    if a["kind"] == "time":
        return a["value"] == b["value"] and a["meridiem"] == b["meridiem"]
    return False


def _atoms_public(atoms: list[dict]) -> list[dict]:
    out = []
    for a in atoms:
        pub = dict(a)
        if isinstance(pub.get("value"), Fraction):
            pub["value"] = str(pub["value"])
            pub["value_float"] = float(a["value"])
        out.append(pub)
    return out


def tier1_numeric_equivalence(canonical: str, asr: str) -> dict | None:
    """Tier 1 early-exit。両側の値パース列が完全一致した場合のみdictを
    返す(等価でなければNone、呼び出し側はStep 2へフォールバックする)。"""
    try:
        ca = _tier1_atoms(canonical)
        aa = _tier1_atoms(asr)
    except Exception:
        return None  # パース例外は非等価扱い(安全側、best-effort禁止)
    if len(ca) != len(aa):
        return None
    if not any(a["kind"] != "literal" for a in ca):
        return None  # 数値的内容が無い(Tier1の対象外、Step2へ委ねる)
    for a, b in zip(ca, aa):
        if not _atoms_equal(a, b):
            return None
    return {"canonical_atoms": ca, "asr_atoms": aa}


# ============================================================
# Part 2: Tier 3(sub_reason判定 + corroboration救済)
# ============================================================
def _singularize_simple(word: str) -> str | None:
    """`_is_benign_plural_pair`相当(er006本体、L514-522の同型実装。
    Production本体は変更しないため、観測性用にこのTrial module内で
    独立に再実装する)。"""
    if len(word) > 4 and word.endswith("es") and word[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return word[:-2]
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return None


def _is_benign_plural_pair(a: str, b: str) -> bool:
    if a == b:
        return True
    return _singularize_simple(a) == b or _singularize_simple(b) == a


def _locate_single_token_diff(canonical: str, asr: str) -> dict | None:
    """非等価opcodeがちょうど1件、かつ1トークン対1トークンのreplaceの
    場合のみ位置情報を返す(それ以外はNone、救済対象を狭く限定する)。"""
    canon_tokens = val.tokenize(canonical)
    asr_tokens = val.tokenize(asr)
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if len(ops) != 1:
        return None
    tag, i1, i2, j1, j2 = ops[0]
    if tag != "replace" or i2 - i1 != 1 or j2 - j1 != 1:
        return None
    return {"index": i1, "canonical_word": canon_tokens[i1], "asr_word": asr_tokens[j1]}


def _corroboration_supports(canon_tokens: list[str], idx: int, other_text: str | None) -> bool | None:
    """OPEN-122の`_word_at_diff_matches_canonical`相当(同型実装、
    position-basedでcanonical語をother_text[Secondary/Local ASR]が
    支持しているかを判定する)。"""
    if not other_text:
        return None
    other_tokens = val.tokenize(other_text)
    if idx >= len(other_tokens) or idx >= len(canon_tokens):
        return None
    return other_tokens[idx] == canon_tokens[idx]


def _determine_sub_reason(baseline: "val.ClassificationResult", canonical: str, asr: str):
    """ASR_VALIDATION_UNCERTAIN/TRUE_CONTENT_MISMATCHの内訳をobservability
    用に細分化する(既存ラベル自体は変更しない、新規フィールドのみ)。"""
    if baseline.should_pass:
        return "none", None
    if baseline.classification == "TTS_FAILURE":
        # ASR自体が取得できなかった(asr_text is None)、または類似度が
        # 著しく低くTTS生成自体の異常が疑われるケース。sub_reasonの
        # 既定8分類のどれにも該当しないため、observability上は
        # "content_word"へ丸めず区別できるよう素直にラベルを返す
        # (呼び出し側のsub_reason集合はTrialの観測目的であり、既存
        # ClassificationResultのclassification自体で判別可能なため、
        # このsub_reason文字列自体は既存の8分類の外側にある拡張)。
        return "tts_failure", None
    diffs = baseline.protected.content_word_diffs
    if baseline.classification == "TRUE_CONTENT_MISMATCH":
        if baseline.protected.number_mismatches:
            return "protected_number", None
        if baseline.protected.negation_mismatches:
            return "protected_negation", None
        return "content_word", None
    if baseline.classification == "ASR_VALIDATION_UNCERTAIN":
        if diffs and all(d["entity_like"] for d in diffs):
            loc = _locate_single_token_diff(canonical, asr)
            return "entity_only", loc
        if diffs and all(d["homophone_candidate"] and not d["entity_like"] for d in diffs):
            return "homophone_only", None
        if not diffs:
            loc = _locate_single_token_diff(canonical, asr)
            if loc and _is_benign_plural_pair(loc["canonical_word"], loc["asr_word"]):
                return "plural_only", loc
            return "low_ratio", None
    return "content_word", None


# ============================================================
# Part 3: classify_semantic_equivalence() 統一エントリ
# ============================================================
def classify_semantic_equivalence(canonical: str, asr: str | None, *,
                                   secondary_text: str | None = None,
                                   local_text: str | None = None) -> dict:
    """Trial判定層(Production非配線)。ClassificationResult互換の
    should_pass/should_retry/classification/reasonに加え、観測性用の
    sub_reason/diff_spans/tier_applied/observability_recordを持つdictを
    返す。

    Step 1: Tier 1数値等価のearly-exit(既存classify_asr_matchは呼ばず、
            独立した値パースのみで判定)。
    Step 2: 既存classify_asr_match()をそのまま呼ぶ(結果を改変しない)。
    Step 3: baselineがASR_VALIDATION_UNCERTAINで、diffが規則的複数形
            のみ/固有名詞のみ(1トークン差)の場合のみ、Secondary/Local
            ASRのcorroborationを確認しPASS_WITH_WARNING相当で救済する。
    Step 4: 観測性(sub_reason/diff_spans/observability_record)を付与。
    """
    if asr is not None:
        tier1 = tier1_numeric_equivalence(canonical, asr)
        if tier1 is not None:
            return {
                "classification": "NUMERIC_EQUIVALENCE_MATCH",
                "should_pass": True, "should_retry": False,
                "reason": "Tier 1(数値/通貨/%/年/時刻/分数/ローマ数字/略語)の値パースが両側で完全一致",
                "sub_reason": "numeric_only", "tier_applied": "tier1_numeric",
                "diff_spans": {"canonical_atoms": _atoms_public(tier1["canonical_atoms"]),
                               "asr_atoms": _atoms_public(tier1["asr_atoms"])},
                "baseline_classification": None, "corroborated_by": [],
                "observability_record": None,
            }

    baseline = val.classify_asr_match(canonical, asr)
    sub_reason, diff_loc = _determine_sub_reason(baseline, canonical, asr)

    result = {
        "classification": baseline.classification,
        "should_pass": baseline.should_pass,
        "should_retry": baseline.should_retry,
        "reason": baseline.reason,
        "sub_reason": sub_reason,
        "tier_applied": "baseline",
        "diff_spans": diff_loc,
        "baseline_classification": baseline.classification,
        "corroborated_by": [],
        "observability_record": None,
    }

    if baseline.should_pass:
        return result

    if (baseline.classification == "ASR_VALIDATION_UNCERTAIN"
            and sub_reason in ("plural_only", "entity_only") and diff_loc):
        canon_tokens = val.tokenize(canonical)
        corroborated_by = []
        for label, other_text in (("secondary", secondary_text), ("local", local_text)):
            supports = _corroboration_supports(canon_tokens, diff_loc["index"], other_text)
            if supports is True:
                corroborated_by.append(label)
        if corroborated_by:
            result["classification"] = "SECONDARY_ASR_CORROBORATED_MATCH"
            result["should_pass"] = True
            result["should_retry"] = False
            result["tier_applied"] = "tier3_corroboration"
            result["corroborated_by"] = corroborated_by
            result["reason"] = (f"Tier3救済(sub_reason={sub_reason}): 独立ASR({corroborated_by})が"
                                 f"diff位置でcanonical語'{diff_loc['canonical_word']}'を支持")
            return result

    if not result["should_pass"]:
        result["observability_record"] = {
            "canonical": canonical, "asr": asr, "classification": result["classification"],
            "sub_reason": sub_reason, "diff_spans": diff_loc,
        }
    return result


def append_observability_log(result: dict, path: str = OBSERVABILITY_LOG_PATH) -> None:
    """NG時のcanonical/ASR/diff/sub_reasonをJSONLへ追記する(Phase Aの
    観測性修正、挙動変更なし)。"""
    rec = result.get("observability_record")
    if not rec:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


