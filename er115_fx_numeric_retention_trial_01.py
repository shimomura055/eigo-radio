# -*- coding: utf-8 -*-
"""er115_fx_numeric_retention_trial_01.py  (DEV/Trial専用。Productionに配線されない・既定OFF相当=importしても何も起きない)

FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02。Family X(日本語記事)の「必要な中核数値だけを本文へ残す」ための
DEV合成(O3方式 + Opus条件A必須修正M1〜M5・推奨R1〜R5)。Productionファイル・Prompt・閾値・flagは一切編集しない。
既存Production関数は import して呼ぶだけ(Prompt定数は文字列合成で拡張し、原定数は書き換えない)。

構成(DESIGN_02.md):
  B3 DEV : Production B3(run_storyline_b3)を、clientラッパで「追記ブロック」を足して呼ぶだけ(B3 Prompt本体は不変)。
  M1     : B3直後の決定論検査(Storylineの数値は全て ニュース欄の【中核数値】の同一概念に対応・合計<=2)。違反はB3を1回だけ再実行。
  E      : 必須集合 = Storylineに現れる中核数値の概念(ニュース欄の表記)。ただし年単位(前提)・日付は観察のみ(M2)。
  R4     : 入力側(ニュース欄・「テーマ：」行)の「数字〜数字」だけを「数字から数字」へ決定論正規化(R0_PROMPT本体は不変)。
  Gate   : R0/R1/R2直後に、較正済み照合(M4)でEの保持を検査。本文は自動書換えしない。不足時は段限定再実行(R0/R1/R2各<=2呼出、R2は記号QAと枠共有)。
  計測   : 選定数/必要数/掲載数/不要掲載数、周辺数値混入、誤解表現WARN(観察のみ)。
禁止: Web検索・Research再実行・Production出力dirへの書込み(出力は er115_output/ のみ)。
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import types
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er003_audio_tts_asr_safety as safety   # noqa: E402
import er005_cost_logger as cl   # noqa: E402
import er012_e_family_entertainment_two_level_runner_01 as efam   # noqa: E402
import er019_family_x_entertainment_production_runner_01 as runner   # noqa: E402
import er053_b3_annotation_contract_01 as contract   # noqa: E402
import er053_b3_deterministic_producer_01 as P   # noqa: E402
import er053_cost_aggregate_01 as ca   # noqa: E402
import er053_family_x_factlock_ja_writer_01 as w1   # noqa: E402
import er095_b3_core_number_rounding_01 as rounding   # noqa: E402

jaw = w1.jaw
OUT_ROOT = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01")
TRIAL_TAG = "FX_NUMERIC_RETENTION_TRIAL_01"

# ======================================================================================================
# 定数(文言。Phase 1で1回だけ調整可・調整したらshaを証跡に残す)
# ======================================================================================================
B3_ADDENDUM = (
    "\n\n【追加の指示: 数値の扱い(Storylineを決めた後の手順)】\n"
    "上の1〜5で中心Storylineと採用Factを決めた後、selected_storylineの1行を書くときだけ、次に従ってください。"
    "Storylineの選び方とFactの採否は、数値の有無で変えないでください(Test4のとおり、「数字がある」だけの理由でFactを残さないこと)。\n"
    "- そのStorylineの1行が答える中心的な問いに、台帳のnumeric_value欄にある数値で直接答えられる場合は、その数値を、"
    "numeric_value欄の表記のまま、selected_storylineの1行に含めてください(最大2個)。\n"
    "- その数値の解釈に不可欠な前提(推定・仮定・期間・範囲)がある場合は、前提を示す言葉(「推定」「仮定」など)を含めてください。"
    "前提の数値を含めてよいのは、それが中心的な問いへの答えの一部である場合だけで、上記の最大2個に含みます。\n"
    "- 中心的な問いが数値で答えるものでない場合、または入れると文が不自然になる場合は、数値を入れなくてかまいません。"
    "数値を増やすために無関係な数値を入れないでください。\n"
    "- numeric_value欄にない数値や、他のFactの補足的な数値は、selected_storylineの1行に含めないでください。"
)
# 委任_03 O-1'(Opus OPUS_REVIEW_02): Storylineに入れる数値は「問いへの答えそのものの値」に限る。比較相手(予測値・別の推定・過去の値)は、
# 比較そのものが答えの場合を除き、数値を入れず言葉で述べる。v1(B3_ADDENDUM)はPhase 1の再現性のため不変で残す。
B3_ADDENDUM_V2 = (
    "\n\n【追加の指示: 数値の扱い(Storylineを決めた後の手順)】\n"
    "上の1〜5で中心Storylineと採用Factを決めた後、selected_storylineの1行を書くときだけ、次に従ってください。Storylineの選び方とFactの採否は、数値の有無で変えないでください(Test4のとおり、「数字がある」だけの理由でFactを残さないこと)。\n"
    "- そのStorylineの1行が答える中心的な問いに、台帳のnumeric_value欄にある数値で直接答えられる場合は、問いへの答えそのものの値だけを、numeric_value欄の表記のまま、selected_storylineの1行に含めてください(最大2個)。\n"
    "- 予測値・別の推定・過去の値・基準値など、答えと見比べるための数値(比較相手)は、比較そのものが問いへの答えである場合を除き、selected_storylineの1行に数値で入れず、言葉で述べてください(比較そのものが答えの場合は、比べる2つの値を入れてよい。合わせて最大2個)。\n"
    "- その数値の解釈に不可欠な前提(推定・仮定・期間・範囲)がある場合は、前提を示す言葉(「推定」「仮定」など)を含めてください。前提の数値を含めてよいのは、それが中心的な問いへの答えの一部である場合だけで、上記の最大2個に含みます。\n"
    "- 中心的な問いが数値で答えるものでない場合、または入れると文が不自然になる場合は、数値を入れなくてかまいません。数値を増やすために無関係な数値を入れないでください。\n"
    "- numeric_value欄にない数値や、他のFactの補足的な数値は、selected_storylineの1行に含めないでください。"
)
# 委任_04 R5(Opus OPUS_REVIEW_01 R5: B3の同一呼出のJSONに欄を足す案): v2の本文に、reader_must_hear_numbers欄の指示を足す。
# Production B3 Prompt本体・STORYLINE_B3_JSON_SCHEMA定数は不変(欄の追加はDEV wrapperが送信直前にschemaのコピーへ足す)。
B3_ADDENDUM_V3_FIELD = (
    "\n\n【追加の指示2: reader_must_hear_numbers欄(出力JSONの追加フィールド)】\n"
    "出力JSONのreader_must_hear_numbers(文字列の配列)に、「この記事を聞く人に必ず伝えるべき重要数値」を、台帳のnumeric_value欄にある数値の表記のまま(単位・倍率語を含めて)入れてください(例の形式: 「12.5%」「約3万人」「4.5倍」)。selected_storylineに数値を入れるかどうかとは別に、記事全体として判断します。Storylineの選び方とFactの採否は、この欄のために変えないでください。\n"
    "入れてよいのは、次をすべて満たす数値だけです。重要なほど多く入れるのではなく、本当に必要なものに絞ってください。\n"
    "- その数値がないと、記事の中心的な発見・事実が伝わりにくくなる。\n"
    "- その数値が、記事の驚きや面白さ、論旨や比較の説得力を支えている。\n"
    "- 言葉による説明では十分に代替できない。\n"
    "- その数値を本文に入れても、読みやすさやストーリーの流れが損なわれない。\n"
    "入れない数値: 日付・年・序数、背景や補足の数値、他の数値の言い換えや内訳、比較の相手側の値や付随する条件の数値、台帳に出てくるだけで記事の中心でない数値(比較の結果の倍率や差そのものが記事の中心的な発見なら、その倍率や差は入れてよい)。\n"
    "最大2個です。採用したFact(selected_fact_ids)に含まれる台帳の数値だけを入れてください。必要な数値がない記事は空の配列[]にしてください(無理に入れない)。この欄の数値をselected_storylineの1行に自然に含められる場合は含めてかまいませんが、含めなくてもかまいません。"
)
B3_ADDENDUM_V3 = B3_ADDENDUM_V2 + B3_ADDENDUM_V3_FIELD
# 委任_04 v4(1回だけの指示文修正、PREREGISTERED_CRITERIA_03 追補): v3の判断基準が『すべてを満たす(AND)』と読まれ、ig_nobelで欄が2/2空だったため、
# ユーザー原文§3の5観点を『①〜③のどれか かつ ④⑤』の論理構造に整理。v3は不変で残す。
B3_ADDENDUM_V4_FIELD = (
    "\n\n【追加の指示2: reader_must_hear_numbers欄(出力JSONの追加フィールド)】\n"
    "出力JSONのreader_must_hear_numbers(文字列の配列)に、「この記事を聞く人に必ず伝えるべき重要数値」を、台帳のnumeric_value欄にある数値の表記のまま(単位・倍率語を含めて)入れてください(例の形式: 「12.5%」「約3万人」「4.5倍」)。selected_storylineに数値を入れるかどうかとは別に、記事全体として判断します。Storylineの選び方とFactの採否は、この欄のために変えないでください。\n"
    "次の①〜③のどれかに強く当てはまり、かつ④⑤の問題がない数値だけを入れてください。重要なほど多く入れるのではなく、本当に必要なものに絞ってください。\n"
    "① その数値がないと、記事の中心的な発見・事実が伝わりにくくなる。\n"
    "② その数値が、記事の驚きや面白さを支えている。\n"
    "③ その数値が、論旨や比較の説得力を支えている。\n"
    "④ 言葉による説明だけでは、同じ具体性が出せない(「大きい」「多い」「はるかに」などの言葉では、聞き手が量や程度をつかめない)。\n"
    "⑤ 本文に入れても、読みやすさやストーリーの流れが損なわれない。\n"
    "入れない数値: 日付・年・序数、背景や補足の数値、他の数値の言い換えや内訳、比較の相手側の値や付随する条件の数値、台帳に出てくるだけで記事の中心でない数値(比較の結果の倍率や差そのものが記事の中心的な発見なら、その倍率や差は入れてよい)。\n"
    "最大2個です。採用したFact(selected_fact_ids)に含まれる台帳の数値だけを入れてください。必要な数値がない記事は空の配列[]にしてください(無理に入れない)。この欄の数値をselected_storylineの1行に自然に含められる場合は含めてかまいませんが、含めなくてもかまいません。"
)
B3_ADDENDUM_V4 = B3_ADDENDUM_V2 + B3_ADDENDUM_V4_FIELD
B3_FIELD_NAME = "reader_must_hear_numbers"
B3_ADDENDA = {"v1": B3_ADDENDUM, "v2": B3_ADDENDUM_V2, "v3": B3_ADDENDUM_V3, "v4": B3_ADDENDUM_V4}
M1_RETRY_NOTE_TEMPLATE = (
    "\n\n【前回出力の修正指示(数値)】前回のselected_storylineには、次の数値が含まれていましたが、条件に合いません: {problems}。"
    "selected_storylineの1行に含めてよい数値は、台帳のnumeric_value欄にある表記のままの数値だけで、最大2個です。"
    "周辺的な数値や、numeric_value欄にない数値は含めないでください。数値を入れなくても構いません。"
    "Storylineの選び方・Factの採否はこのために変えないでください。"
)
M1_RETRY_NOTE_V3_TEMPLATE = (
    "\n\n【前回出力の修正指示(reader_must_hear_numbers)】前回のreader_must_hear_numbersには、次の項目が条件に合いませんでした: {problems}。"
    "この欄に入れてよいのは、採用Factに含まれる台帳numeric_value欄の数値(表記のまま、最大2個)だけです。"
    "条件に合う数値がなければ空の配列[]にしてください。Storylineの選び方・Factの採否はこのために変えないでください。"
)
RULE9_TEXT = (
    "\n9. 「テーマ：」の文に含まれる数字は、記事の中心的な問いに答える数字です。本文で必ず述べてください"
    "(表記はニュース欄のとおり。範囲は「AからB」と書き、波ダッシュは使わない)。推定や仮定が付いた数字は、"
    "「推定」「仮定」「としたら」など前提を示す言葉と同じ文で述べ、観測された事実のように書かないでください。"
    "それ以外の【中核数値】は使わなくて構いません。数字を増やすために文章を不自然にしないでください。"
)
RETENTION_NOTE_TEMPLATE = "次の数字が本文にありません: {items}。ニュース欄のとおりに含めて書き直してください。他の数字は増やさないでください。"

# 誤解表現WARN(観察のみ・ブロックしない。M2)
MISREAD_NEAR_TIME = ("今も", "いまも", "現在も", "毎年", "一定の速", "ずっと", "今なお", "いまだに", "縮み続け", "縮んでいる")
ORIGIN_CLAIMS = ("月の誕生以来", "誕生以来", "生まれてから", "誕生してから", "月ができてから", "月が生まれて")
TIME_PREMISE_UNIT_RE = re.compile(r"(?:万|億|兆)?年(?:前|間)?")

MAX_E = 2


def sha_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


nfkc = P.nfkc


def rdt(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def wj(p, obj):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def wt(p, text):
    w1.wt(p, text)


# ======================================================================================================
# M4: 較正済み照合(単位の言い換え表・単位無し一致の厳格化)
# ======================================================================================================
UNIT_GROUPS = {
    "m": ["m", "メートル"], "km": ["km", "キロメートル", "キロ"], "cm": ["cm", "センチメートル", "センチ"],
    "mm": ["mm", "ミリメートル", "ミリ"], "kg": ["kg", "キログラム"], "g": ["g", "グラム"],
    "%": ["%", "パーセント"], "USD": ["ドル", "米ドル", "$", "usd"], "GBP": ["£", "ポンド"], "EUR": ["€", "ユーロ"],
    "JPY": ["円"], "cent": ["セント", "¢"], "month": ["か月", "カ月", "ヶ月", "ケ月", "ヵ月", "カ月間", "か月間", "ヶ月間"],
}
CURRENCY_SYMBOL = {"$": "USD", "¥": "JPY", "€": "EUR", "£": "GBP"}
_UNIT_SUFFIX_RE = re.compile(r"(?:間|分|ほど|程度)$")
WAVES = "〜～~"


def unit_key(u: str) -> str:
    """単位文字列 -> 言い換え群ID(群に無ければ正規化文字列そのもの)。空なら ''。"""
    u = nfkc(u).strip().lower()
    if not u:
        return ""
    base = _UNIT_SUFFIX_RE.sub("", u)
    for g, toks in UNIT_GROUPS.items():
        tl = [t.lower() for t in toks]
        if u in tl or base in tl:
            return g
    return base or u


def currency_of(surface: str) -> str:
    for ch in nfkc(surface):
        if ch in CURRENCY_SYMBOL:
            return CURRENCY_SYMBOL[ch]
    return ""


def own_unit_of(surface: str) -> str:
    """表記自体に含まれる単位(範囲の波ダッシュ等は単位でない)。通貨記号は別扱い(currency_of)。"""
    return re.sub(r"[〜～~\-–]", "", P.unit_of(surface) or "")


def req_unit(surface: str, hint: str = "") -> str:
    """表記に含まれる単位(または通貨記号)、無ければニュース欄で直後に付く単位hint。"""
    return unit_key(own_unit_of(surface)) or currency_of(surface) or unit_key(hint)


def _tokens_for(req: str):
    return UNIT_GROUPS.get(req) or [req]


def trailing_has_unit(after: str, req: str) -> bool:
    a = nfkc(after).lstrip(" 　").lower()
    for tok in sorted(_tokens_for(req), key=len, reverse=True):
        tl = tok.lower()
        if a.startswith(tl):
            if re.fullmatch(r"[a-z]+", tl) and re.match(r"[a-z]", a[len(tl):len(tl) + 1] or ""):
                continue
            return True
    return False


_MARK_PREFIX_RE = re.compile(r"^(?:【[^】\n]*】)+")
_ALL_UNIT_TOKENS = sorted({t for toks in UNIT_GROUPS.values() for t in toks}, key=len, reverse=True)


def unit_hint_after(news_text: str, surface: str) -> str:
    """ニュース欄(注記済み)で、表記の直後に付く単位。表記自体に単位が無い場合(例: 『約42〜46【中核数値】 m』)にだけ使う。"""
    t = nfkc(news_text)
    s = nfkc(surface)
    for p in P.find_all(t, s):
        after = _MARK_PREFIX_RE.sub("", t[p + len(s):]).lstrip(" 　")
        for tok in _ALL_UNIT_TOKENS:
            tl = tok.lower()
            if after.lower().startswith(tl):
                if re.fullmatch(r"[a-z]+", tl) and re.match(r"[a-z]", after[len(tl):len(tl) + 1] or "", re.I):
                    continue
                return tok
        m = re.match(r"([ァ-ヶー]{1,8})", after)
        if m:
            return m.group(1)
    return ""


def match_core(surface: str, text: str, unit_hint: str = "", approx_forms=()) -> dict:
    """較正済み照合。戻り値 {present, mode: strong|weak|approx|none}。
    - 一致 = 同じ種類・同じ主数字(+範囲は a,b)。単位が分かる場合(表記/通貨記号/ニュース欄hint)は、本文側も同じ単位(言い換え表)であること。
    - 単位が全く分からない場合のみ数字一致を weak として認める(計測に区別して残す)。
    - 概数可の概数表記(approx_forms)は mode=approx。"""
    t = nfkc(text or "")
    s = nfkc(surface or "")
    if not s or not t:
        return {"present": False, "mode": "none"}
    k = P.surface_kind(s)
    key = P.main_numbers(s, k)
    own_unit = bool(unit_key(own_unit_of(s)) or currency_of(s))
    req = req_unit(s, unit_hint)
    weak = False
    # (1) 表記そのものの出現
    for p in P.find_all(t, s):
        end = p + len(s)
        if own_unit or not req:
            return {"present": True, "mode": "strong" if req else "weak"}
        if trailing_has_unit(t[end:], req):
            return {"present": True, "mode": "strong"}
    # (2) 同じ(種類,主数字)の表記
    for m in P.SURF_RE.finditer(t):
        if m.group("perday"):
            continue
        ts = m.group(0).strip()
        if not re.search(r"\d", ts):
            continue
        tk = P.surface_kind(ts)
        if tk != k or P.main_numbers(ts, tk) != key:
            continue
        tg = unit_key(own_unit_of(ts)) or currency_of(ts)
        if req:
            if tg:
                if tg == req:
                    return {"present": True, "mode": "strong"}
                continue
            if trailing_has_unit(t[m.end():], req):
                return {"present": True, "mode": "strong"}
            continue
        weak = True
    # (3) 範囲: 『AからB』『A〜B』(間に単位が入ってよい)
    if k == "range" and key[0] == "R" and len(key[1]) == 2:
        a, b = key[1]
        rx = re.compile(rf"(?<![\d.]){re.escape(a)}[^\d]{{0,12}}?(?:[{re.escape(WAVES)}\-–ー]|から)[^\d]{{0,6}}?{re.escape(b)}(?![\d])")
        for m in rx.finditer(t.replace(",", "")):
            if not req or trailing_has_unit(t.replace(",", "")[m.end():], req) or own_unit:
                return {"present": True, "mode": "strong" if req else "weak"}
    if weak:
        return {"present": True, "mode": "weak"}
    for ap in approx_forms or ():
        if ap and P.contains(t, ap):
            return {"present": True, "mode": "approx"}
    return {"present": False, "mode": "none"}


# ---- 英訳側(observe-only): er114.en_present に m/km/cm 等の単位hintを追加 ----
EN_UNIT_RE = {
    "m": r"\b(?:m|meters?|metres?)\b", "km": r"\b(?:km|kilomet(?:er|re)s?)\b", "cm": r"\b(?:cm|centimet(?:er|re)s?)\b",
    "mm": r"\b(?:mm|millimet(?:er|re)s?)\b", "%": r"percent|%", "USD": r"dollars?|[$]", "GBP": r"pounds?|£", "EUR": r"euros?|€",
    "month": r"months?", "年": r"years?", "億年": r"years?", "万年": r"years?", "年前": r"years?", "cent": r"cents?",
    # 委任_06 C-3(Opus条件C推奨): 倍率語。『三倍→three times』『3倍→3x/threefold/triple』(観察用WARNのみ・Gate化しない)
    "倍": r"times|fold\b|x\b|×|triple|double|quadruple",
}
_WORD_NUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
_WORD_NUM.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100})
_SCALE = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9, "trillion": 10 ** 12}


def en_values(text):
    t = nfkc(text).replace(",", "")
    ctx = []
    # 委任_06: 数字の直後に大文字1字が続く語(3D/5G/4K)は数値でない(単位なしの『3』が『3D』に誤一致するのを除外)。小数の途中で切れる誤分割も除外。
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?!\d|\.\d)(?!(?-i:[A-Z])\b)\s*(thousand|million|billion|trillion)?", t, re.I):
        v = P.dec(repr(float(m.group(1)) * (_SCALE[m.group(2).lower()] if m.group(2) else 1)))
        ctx.append((v, t[m.end(): m.end() + 30].lower()))
    for m in re.finditer(r"\b(" + "|".join(sorted(_WORD_NUM, key=len, reverse=True)) + r")\b(?:\s+(thousand|million|billion|trillion))?", t, re.I):
        v = P.dec(repr(float(_WORD_NUM[m.group(1).lower()]) * (_SCALE[m.group(2).lower()] if m.group(2) else 1)))
        ctx.append((v, t[m.end(): m.end() + 30].lower()))
    return t, ctx


def en_present(surface: str, text: str, unit_hint: str = ""):
    """True/False、評価対象外はNone。"""
    k = P.surface_kind(surface)
    if k in ("date_time", "year", "ordinal", "name_embedded"):
        return None
    key = P.main_numbers(surface, k)
    req = req_unit(surface, unit_hint)
    pat = EN_UNIT_RE.get(req) if req else None
    t, ctx = en_values(text)
    if k == "range" and key[0] == "R" and len(key[1]) == 2:
        a, b = key[1]
        for m in re.finditer(rf"(?<![\d.]){re.escape(a)}[^\d]{{0,20}}{re.escape(b)}(?![\d])", t):
            if not pat or re.search(pat, t[m.end(): m.end() + 25].lower()):
                return True
        return False
    if key[0] == "M" and key[1] is not None:
        for v, after in ctx:
            if v == key[1] and (not pat or re.search(pat, after)):
                return True
        return False
    return None


# ======================================================================================================
# R4: 範囲値の正規化(入力側のみ・数字〜数字だけ)
# ======================================================================================================
def normalize_ranges(text: str) -> str:
    """ニュース欄/『テーマ：』行の「数字〜数字」(波ダッシュ)を「数字から数字」へ。日付範囲・ハイフン範囲・R0_PROMPT本体には触れない。"""
    out, last = [], 0
    for m in P.SURF_RE.finditer(text or ""):
        s = m.group(0)
        if P.surface_kind(s) != "range":
            continue
        new = re.sub(rf"\s*[{WAVES}]\s*", "から", s)
        if new == s:
            continue
        out.append(text[last:m.start()])
        out.append(new)
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def build_r0_prompt_dev(storyline_line: str, news_text: str, overlay=None, *, range_norm: bool = False, rule9: bool = False) -> str:
    """R0 Prompt(DEV合成)。range_norm=False かつ rule9=False のとき w1.build_r0_prompt とバイト一致(Isolation test)。"""
    if range_norm:
        storyline_line, news_text = normalize_ranges(storyline_line), normalize_ranges(news_text)
    prompt = w1.build_r0_prompt(storyline_line, news_text, overlay)
    if rule9:
        prompt += RULE9_TEXT
    return prompt


# ======================================================================================================
# M1 / E: Storylineの数値検査と必須集合
# ======================================================================================================
def is_time_premise(surface: str) -> bool:
    k = P.surface_kind(surface)
    return k == "magnitude" and bool(TIME_PREMISE_UNIT_RE.fullmatch(P.unit_of(surface) or ""))


def derive_E(out_dir: str, *, surfaces=None, extra_violations=None, item_count=None) -> dict:
    """producer出力(annotation.json / selected_brief_annotated.md)から M1検査とEを決定論で得る。LLM/APIなし。
    違反(violations)があれば E は空にせず candidates に残すが、gate_E は空(呼出側がB3再実行/記録/STOPを判断)。
    surfaces: 指定時は Storylineからでなく、その表記リスト(R5=reader_must_hear_numbers欄)を同じ規則で検査・写像する。"""
    sdir = os.path.join(out_dir, "storyline_b3")
    ann = rj(os.path.join(sdir, "annotation.json"))
    ev = rj(os.path.join(sdir, "fact_selection_evidence.json"))
    annotated_md = rdt(os.path.join(sdir, "selected_brief_annotated.md"))
    _, facts_marked = w1.parse_brief_md(annotated_md)
    facts_plain = P.strip_marks(w1.strip_tags(facts_marked))
    story = (ev.get("selected_storyline") or "").strip()
    nums = ann["numbers"]
    violations, ignored, ambiguous, candidates = [], [], [], []
    seen_concepts = {}
    for s in dict.fromkeys(P.extract_surfaces(story) if surfaces is None else surfaces):
        kind = P.surface_kind(s)
        if kind in ("year", "ordinal", "name_embedded"):
            ignored.append({"surface": s, "kind": kind, "reason": "never_core_kind"})
            continue
        if T_is_ambiguous(s):
            ambiguous.append(s)
            continue
        entry = next((n for n in nums if nfkc(n["surface"]) == nfkc(s)), None)
        if entry is None:
            k = P.main_numbers(s, kind)
            entry = next((n for n in nums if P.surface_kind(n["surface"]) == kind and P.main_numbers(n["surface"], kind) == k), None)
        if entry is None:
            violations.append({"surface": s, "reason": "unmapped_to_news_field"})
            continue
        if entry["class"] != "core":
            violations.append({"surface": s, "reason": "peripheral_number_in_storyline"})
            continue
        if list(entry.get("ledger_ids") or []) == ["_STORY"]:
            violations.append({"surface": s, "reason": "story_only_number"})
            continue
        cid = entry["concept"]
        same = [n for n in nums if n["concept"] == cid and n["class"] == "core" and "_STORY" not in (n.get("ledger_ids") or [])
                and P.contains(facts_plain, n["surface"])]
        if not same:
            violations.append({"surface": s, "reason": "no_news_field_surface_for_concept"})
            continue
        news_surface = max((n["surface"] for n in same), key=len)
        if cid in seen_concepts:
            continue
        hint = unit_hint_after(facts_marked, news_surface)
        kindn = P.surface_kind(news_surface)
        premise = is_time_premise(news_surface)
        rec = {"concept": cid, "story_surface": s, "news_surface": news_surface, "kind": kindn, "unit_hint": hint,
               "time_premise": premise, "gate_required": (kindn in ("magnitude", "range")) and not premise}
        seen_concepts[cid] = rec
        candidates.append(rec)
    if len(candidates) > MAX_E:
        violations.append({"surface": [c["story_surface"] for c in candidates], "reason": f"too_many_numbers(>{MAX_E})"})
    if item_count is not None and item_count > MAX_E:
        violations.append({"surface": f"{item_count} items", "reason": f"too_many_field_items(>{MAX_E})"})
    violations.extend(extra_violations or [])
    ok = not violations
    return {"storyline": story, "ok": ok, "violations": violations, "candidates": candidates,
            "gate_E": [c for c in candidates if c["gate_required"]] if ok else [],
            "observe_E": [c for c in candidates if not c["gate_required"]] if ok else candidates,
            "ignored": ignored, "ambiguous_small_ints": ambiguous, "storyline_has_no_numbers": not candidates and not violations}


def read_field_items(out_dir: str) -> list:
    p = os.path.join(out_dir, "storyline_b3", B3_FIELD_NAME + ".json")
    return [str(x) for x in (rj(p).get("items") or [])] if os.path.exists(p) else []


def derive_E_r5(out_dir: str) -> dict:
    """R5(委任_04): E = reader_must_hear_numbers欄(B3自身の判断)。Storyline由来のE(従来)は整合の記録だけ(欄を優先、Storyline数値が欄に無くても記録のみ)。
    欄の各項目は従来のM1検査と同じ写像規則(ニュース欄の中核数値・_STORYのみは不可・同一概念は1個・最大2個)を通す。LLM/APIなし。"""
    items = read_field_items(out_dir)
    pre, surfs = [], []
    for it in items:
        ss = P.extract_surfaces(it)
        if not ss:
            pre.append({"surface": it, "reason": "field_item_no_numeric_surface"})
        surfs.extend(ss)
    E = derive_E(out_dir, surfaces=list(dict.fromkeys(surfs)), extra_violations=pre, item_count=len(items))
    story = derive_E(out_dir)   # Storyline由来(記録用)
    f_news = {nfkc(c["news_surface"]) for c in E["candidates"]}
    s_news = {nfkc(c["news_surface"]) for c in story["candidates"]}
    E["source"] = B3_FIELD_NAME
    E["field_items"] = items
    E["storyline_consistency"] = {
        "storyline_numbers": sorted(s_news), "field_numbers": sorted(f_news),
        "storyline_not_in_field(record_only)": sorted(s_news - f_news), "field_not_in_storyline": sorted(f_news - s_news),
        "storyline_m1_violations_record_only": story["violations"], "match": s_news == f_news}
    E["storyline_has_no_numbers"] = story["storyline_has_no_numbers"]
    return E


def T_is_ambiguous(s: str) -> bool:
    """er114.is_ambiguous と同一規則(単位なしの小さな整数<=31は照合の分母/Gate対象から除く)。"""
    k = P.surface_kind(s)
    key = P.main_numbers(s, k)
    if k == "magnitude" and key[0] == "M" and key[1] is not None and not P.unit_of(s):
        try:
            v = float(key[1])
            return v <= 31 and v == int(v)
        except ValueError:
            return False
    return False


def approx_forms_of(out_dir: str) -> dict:
    p = os.path.join(out_dir, "storyline_b3", "rounding_overlay.json")
    out = {}
    if os.path.exists(p):
        for e in rj(p).get("entries", []):
            if e.get("final_decision") == "APPROXIMATE_OK":
                for s in e.get("surfaces", []):
                    if s.get("approx"):
                        out[nfkc(s.get("surface"))] = s["approx"]
    return out


# ======================================================================================================
# 保持Gate(本文は書き換えない)
# ======================================================================================================
def check_retention(text: str, E: list, approx: dict | None = None) -> dict:
    """E(gate_required)のうち本文にないものを返す。観察対象(time_premise/日付)はmissingに含めない。"""
    approx = approx or {}
    missing, detail = [], []
    for e in E:
        r = match_core(e["news_surface"], text, e.get("unit_hint", ""), [approx.get(nfkc(e["news_surface"]))])
        detail.append({"surface": e["news_surface"], **r})
        if not r["present"]:
            missing.append(e)
    return {"missing": missing, "detail": detail}


def display_form(e: dict) -> str:
    s = normalize_ranges(e["news_surface"])
    return s + (f" {e['unit_hint']}" if e.get("unit_hint") else "")


def retention_note(missing: list) -> str:
    return RETENTION_NOTE_TEMPLATE.format(items="、".join(display_form(e) for e in missing))


NEGATION_AFTER = ("ではない", "ではなく", "でない", "わけではない", "とは限らない", "ではありません", "という意味ではない", "ではなかった", "ではないこと", "の総決算ではない", "禁物", "は早い", "早すぎ", "急ぐのは", "と言い切れ", "とは言えない")


def scan_misreading(text: str, observe_E: list | None = None) -> dict:
    """時間・前提の数値の近くにある誤解表現/起源の主張(観察のみ・ブロックしない)。
    起源の主張(『月の誕生以来』等)は直後に否定(『…ではない』等)が続けば negated=True(正しい打ち消し)。人手確認が最終。"""
    t = text or ""
    near = []
    for m in re.finditer(r"[0-9０-９][0-9０-９,，.]*\s*(?:万|億|兆)?年", t):
        win = t[max(0, m.start() - 40): m.end() + 40]
        for w in MISREAD_NEAR_TIME:
            if w in win:
                near.append({"time_expr": m.group(0), "phrase": w, "window": win})
    origin = []
    for w in ORIGIN_CLAIMS:
        for m in re.finditer(re.escape(w), t):
            after = t[m.end(): m.end() + 40]
            origin.append({"phrase": w, "negated": any(n in after for n in NEGATION_AFTER), "context": t[max(0, m.start() - 20): m.end() + 40]})
    return {"near_time_misread": near, "origin_claims": origin, "origin_claims_unnegated": [o for o in origin if not o["negated"]]}


# ======================================================================================================
# 委任_03 O-2'(Opus OPUS_REVIEW_02 M1): 同じ単位系の非E中核数値だけを、Writer向けの印で【周辺数値】へ付け替える(DEV wrapper内のみ)
#   Production derive_ranks・規則5の文言・注記済みB3ファイル(契約sha)は不変。付け替えは契約検証後のメモリ上のnews欄文字列に対してだけ行う。
#   付け替え対象 = クラスcore・Eの概念でない・magnitude/range・年系/日付でない・単位が取れて、その単位系がEのgate_requiredの単位系と同じ。
#   残す = 年系(期間・前提)、別の単位系、単位が取れない数値、単位なし小整数(現状のまま)。
# ======================================================================================================
DIM_OF_GROUP = {"m": "length", "km": "length", "cm": "length", "mm": "length", "kg": "mass", "g": "mass",
                "%": "percent", "USD": "currency:USD", "GBP": "currency:GBP", "EUR": "currency:EUR", "JPY": "currency:JPY", "cent": "currency:USD"}
_RATE_SPLIT_RE = re.compile(r"[/／]|毎|あたり|当たり")
CORE_MARK, PERIPH_MARK = "【中核数値】", "【周辺数値】"


def dimension_of(surface: str, hint: str = "") -> str:
    """表記(+ニュース欄の直後単位hint)から単位系を返す。取れない/対象外は ''。『cm/100万年』『m/s』等の速度は先頭の単位(長さ)で判定。"""
    cur = currency_of(surface)
    if cur:
        return DIM_OF_GROUP.get(cur, "")
    u = own_unit_of(surface) or hint or ""
    head = _RATE_SPLIT_RE.split(nfkc(u).strip())[0].strip()
    if not head:
        return ""
    return DIM_OF_GROUP.get(unit_key(head), "")


def plan_o2prime(ann: dict, facts_marked: str, E_info: dict) -> dict:
    """E(gate_required)と同じ単位系の、E以外の中核数値を列挙する(LLM/API 0)。副作用なし。"""
    facts_plain = P.strip_marks(w1.strip_tags(facts_marked))
    gate = list(E_info.get("gate_E") or [])
    e_concepts = {c["concept"] for c in (E_info.get("candidates") or [])}
    e_dims = sorted({d for d in (dimension_of(e["news_surface"], e.get("unit_hint", "")) for e in gate) if d})
    demote, kept = [], []
    for n in ann.get("numbers", []):
        if n.get("class") != "core" or list(n.get("ledger_ids") or []) == ["_STORY"]:
            continue
        s = n["surface"]
        if not P.contains(facts_plain, s):
            continue
        hint = unit_hint_after(facts_marked, s)
        kind = P.surface_kind(s)
        dim = dimension_of(s, hint)
        rec = {"surface": s, "concept": n.get("concept"), "kind": kind, "unit_hint": hint, "dimension": dim}
        if n.get("concept") in e_concepts:
            kept.append({**rec, "why_kept": "in_E"})
        elif kind not in ("magnitude", "range"):
            kept.append({**rec, "why_kept": "not_magnitude_or_range"})
        elif (not dim) and (is_time_premise(s) or re.search(r"(?:万|億|兆)?年|か月|ヶ月|カ月|週間|日間", nfkc(s))):
            kept.append({**rec, "why_kept": "year_system_or_period"})
        elif T_is_ambiguous(s):
            kept.append({**rec, "why_kept": "unitless_small_int"})
        elif not dim:
            kept.append({**rec, "why_kept": "unit_unresolved_or_other_system"})
        elif dim not in e_dims:
            kept.append({**rec, "why_kept": "different_unit_system_from_E"})
        else:
            demote.append(rec)
    return {"e_dimensions": e_dims, "demote": demote, "kept_core": kept, "applied": bool(e_dims)}


def swap_marks(text: str, surfaces) -> tuple:
    """text中の『<surface>【中核数値】』の印だけを『【周辺数値】』へ付け替える(NFKC一致・数字境界つき)。戻り値=(新text, 付け替え件数)。本文の他の文字は不変。"""
    norm, idx = P._norm_with_map(text)
    spans = []
    for s in surfaces:
        sn = nfkc(s)
        for p in P.find_all(norm, sn):
            q = p + len(sn)
            if norm.startswith(CORE_MARK, q):
                spans.append((idx[q], idx[q + len(CORE_MARK) - 1] + 1))
    spans = sorted(set(spans))
    out, last = [], 0
    for a, b in spans:
        out.append(text[last:a])
        out.append(PERIPH_MARK)
        last = b
    out.append(text[last:])
    return "".join(out), len(spans)


def filter_overlay(overlay, surfaces):
    """付け替えた表記の【概数表記】行をWriter向けoverlay(メモリ上のコピー)から外す(印と矛盾する制約を残さない)。"""
    if not overlay:
        return overlay
    dem = {nfkc(s) for s in surfaces}
    ov = copy.deepcopy(overlay)
    ents = []
    for e in ov.get("entries", []):
        e["surfaces"] = [x for x in e.get("surfaces", []) if nfkc(x.get("surface")) not in dem]
        if e["surfaces"] or e.get("final_decision") != "APPROXIMATE_OK":
            ents.append(e)
    ov["entries"] = ents
    return ov


# ======================================================================================================
# 委任_03 M2(Opus OPUS_REVIEW_02): R1/R2出力の新規数値検出(R0本文にもニュース欄にもない数値。例: 範囲値の中点『約45』)。決定論・LLM 0。
# ======================================================================================================
_NUMTOK_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _num_tokens(text: str) -> set:
    return {P.dec(m.group(0).replace(",", "")) for m in _NUMTOK_RE.finditer(nfkc(text or ""))}


def new_numbers(stage_text: str, r0_text: str, news_text: str) -> list:
    """stage_textの数値表記(magnitude/range・単位なし小整数を除く)のうち、数字がR0本文+ニュース欄のどの数字とも一致しないもの。"""
    allowed = _num_tokens(r0_text) | _num_tokens(news_text)
    t = re.sub(r"(\d)\s*から\s*(\d)", r"\g<1>〜\g<2>", nfkc(stage_text or ""))
    out, seen = [], set()
    for s in P.extract_surfaces(t):
        k = P.surface_kind(s)
        if k not in ("magnitude", "range") or T_is_ambiguous(s):
            continue
        toks = _num_tokens(s)
        if toks and not toks <= allowed and s not in seen:
            seen.add(s)
            out.append(s)
    return out


# ======================================================================================================
# W-1 DEV(Production W-1の合成。Prompt定数は変更しない)
# ======================================================================================================
class JANumericRetentionStopError(RuntimeError):
    """保持Gateが再実行1回の後も不足(STOP)。本文は手で直さず audit に残す。"""

    def __init__(self, stage: str, message: str, texts: dict, missing: list):
        super().__init__(message)
        self.stage, self.texts, self.missing = stage, texts, missing


def _meta(resp):
    return w1._resp_meta(resp)


def normalize_ranges_counted(text: str):
    """normalize_ranges + 置換件数(R1/R2出力の後処理用)。"""
    new = normalize_ranges(text)
    pat = rf"\d\s*[{WAVES}]\s*\d"
    n = len(re.findall(pat, text or "")) - len(re.findall(pat, new))
    return new, max(n, 0)


def make_astra(client):
    """R1/R2(Astra段)の呼出。出力の『数字〜数字』は決定論で『数字から数字』へ戻す(R1/R2がR0の『から』を波ダッシュへ戻す実測=
    PHASE1 s1/s3で観測のため。数字以外の波ダッシュには触れない=既存の記号QAが従来どおり検出する)。"""
    def astra(src_path, stage_tag):
        user = w1.USER_TMPL.format(body=w1.rdt(src_path).strip())
        t0 = time.time()
        resp = w1.call_astra(client, user, stage_tag)
        raw0 = (resp.output_text or "").strip()
        raw, nrep = normalize_ranges_counted(raw0)
        meta = {"model": resp.model, "response_id": resp.id, "sec": round(time.time() - t0, 1), "stage": stage_tag,
                "range_wave_normalized": nrep, "raw_sha256_before_norm": sha_text(raw0),
                "usage": {"input_tokens": getattr(resp.usage, "input_tokens", None), "output_tokens": getattr(resp.usage, "output_tokens", None)}}
        return raw, w1.postprocess_ja(raw), meta
    return astra


def _sym_of(text):
    f = safety.detect_prohibited_symbols(text, language="ja")
    return f, safety.symbol_gate_requires_stop(f)


def _new_numbers_m2(text, m2):
    """M2: m2=None(無効)なら []。有効なら R0本文+ニュース欄に無い数値表記を返す。"""
    if not m2:
        return []
    return new_numbers(text, m2["r0_text"], m2["news_plain"])


def _run_r2(d, fdir, astra, gate_E, approx, ev, budget_check, m2ctx=None):
    """R2 + 記号QA + 保持Gate(再実行枠は共有=1回)。成功なら (final, p2, raw2, m2, r2_all)、不足/残存ならSTOP。"""
    budget_check()
    raw2, p2, m2 = astra(os.path.join(fdir, "r1.raw.md"), "w1_astra_r2")
    final = w1.clean_ja_for_next(p2)
    f2, sym2 = _sym_of(final)
    miss2 = check_retention(final, gate_E, approx)
    new2 = _new_numbers_m2(final, m2ctx)
    if new2:
        miss2 = {"missing": list(miss2["missing"]) + [{"news_surface": "NEW:" + x} for x in new2], "detail": miss2.get("detail")}
    ev.setdefault("new_numbers", {})["r2"] = {"first": new2, "rerun": False}
    ev["symbol_qa"]["r2"] = {"findings_first": f2, "rerun": False}
    ev["retention"]["r2"] = {"missing_first": [e["news_surface"] for e in miss2["missing"]], "rerun": False,
                            "table_case": ("sym+ret" if sym2 and miss2["missing"] else "sym_only" if sym2 else "ret_only" if miss2["missing"] else "ok")}
    r2_all = [m2]
    if sym2 or miss2["missing"]:
        wt(os.path.join(fdir, "r2.first.final_rejected.md"), final)
        budget_check()
        raw2b, p2b, m2b = astra(os.path.join(fdir, "r1.raw.md"), "w1_astra_r2_rerun")
        r2_all.append(m2b)
        final_b = w1.clean_ja_for_next(p2b)
        f2b, sym2b = _sym_of(final_b)
        miss2b = check_retention(final_b, gate_E, approx)
        new2b = _new_numbers_m2(final_b, m2ctx)
        if new2b:
            miss2b = {"missing": list(miss2b["missing"]) + [{"news_surface": "NEW:" + x} for x in new2b], "detail": miss2b.get("detail")}
        ev["new_numbers"]["r2"].update({"rerun": True, "after": new2b})
        ev["symbol_qa"]["r2"].update({"rerun": True, "findings_after": f2b})
        ev["retention"]["r2"].update({"rerun": True, "missing_after": [e["news_surface"] for e in miss2b["missing"]]})
        if sym2b or miss2b["missing"]:
            wt(os.path.join(d, "audit", "rejected_w1_r2.md"), final_b)
            wj(os.path.join(d, "runtime_evidence_stopped.json"), ev)
            raise JANumericRetentionStopError("r2", f"[STOP] JA_NUMERIC_RETENTION_STOP(R2): 再実行後も symbol={sym2b} missing={[e['news_surface'] for e in miss2b['missing']]}",
                                              {"first": final, "rerun": final_b}, miss2b["missing"])
        final, p2, raw2, m2 = final_b, p2b, raw2b, m2b
    wt(os.path.join(fdir, "r2.raw.md"), raw2)
    wj(os.path.join(fdir, "r2.response.json"), r2_all)
    return final, p2, raw2, m2, r2_all


def _finish(d, ev, r0_calls, r1_all, r2_all, clean0, p1, final):
    ev.update({"r0_calls": r0_calls, "r1_calls": r1_all, "r2_calls": r2_all, "title": w1.extract_title(final), "ja_text_sha256": sha_text(final),
               "calls_count": {"r0": len(r0_calls), "r1": len(r1_all), "r2": len(r2_all)},
               "finished": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
    wt(os.path.join(d, "original.md"), clean0)
    wt(os.path.join(d, "revision1.md"), p1)
    wj(os.path.join(d, "runtime_evidence.json"), ev)
    wt(os.path.join(d, "revision2.md"), final)
    return {"ja_text": final, "title": ev["title"], "runtime_evidence": ev}


def resume_w1_dev_from_r2(out_dir: str, client, E_info: dict, *, arm: str = "A", budget_check=None) -> dict:
    """STOP済み標本の再開: 保存済みのR0(clean)・R1生出力を再利用し、R1生出力へ決定論の範囲正規化を適用してR2から再実行する。
    (R0/R1の入力・Promptは不変=R1を再サンプルするのと同条件。R1の再生成費用を避ける。元のR1生出力は r1.raw.orig.md に保存。)"""
    budget_check = budget_check or (lambda: None)
    d = os.path.join(out_dir, "ja_writer")
    fdir = os.path.join(d, "factlock")
    prior = rj(os.path.join(d, "runtime_evidence_stopped.json"))
    gate_E = list(E_info.get("gate_E") or [])
    approx = approx_forms_of(out_dir)
    ev = dict(prior)
    ev["resumed_from_r2"] = {"reason": "R2 symbol STOP due to R1/R2 wave-dash reintroduction", "prior_symbol_qa_r2": prior.get("symbol_qa", {}).get("r2"),
                             "prior_retention_r2": prior.get("retention", {}).get("r2"),
                             "resumed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    ev["post_range_norm"] = True
    clean0 = w1.rdt(os.path.join(fdir, "r0.md"))
    r0_calls = rj(os.path.join(fdir, "r0_meta.json"))["writer_calls"]
    orig_raw1 = w1.rdt(os.path.join(fdir, "r1.raw.md"))
    if not os.path.exists(os.path.join(fdir, "r1.raw.orig.md")):
        wt(os.path.join(fdir, "r1.raw.orig.md"), orig_raw1)
    raw1, nrep = normalize_ranges_counted(orig_raw1)
    p1 = w1.postprocess_ja(raw1)
    r1_all = rj(os.path.join(fdir, "r1.response.json"))
    ev["resumed_from_r2"]["r1_raw_range_wave_normalized"] = nrep
    miss1 = check_retention(p1, gate_E, approx)
    ev["retention"]["r1"] = {**(ev["retention"].get("r1") or {}), "missing_after_post_norm": [e["news_surface"] for e in miss1["missing"]]}
    wt(os.path.join(fdir, "r1.raw.md"), raw1)
    wt(os.path.join(fdir, "r1.p1.md"), p1)
    if miss1["missing"]:
        raise JANumericRetentionStopError("r1", "[STOP] 再開時のR1に保持不足", {"p1": p1}, miss1["missing"])
    for stale in ("r2.first.final_rejected.md",):
        sp = os.path.join(fdir, stale)
        if os.path.exists(sp):
            os.replace(sp, sp.replace(".md", ".prior_stop.md"))
    for stale in ("rejected_w1_r2.md",):
        sp = os.path.join(d, "audit", stale)
        if os.path.exists(sp):
            os.replace(sp, sp.replace(".md", ".prior_stop.md"))
    astra = make_astra(client)
    final, p2, raw2, m2, r2_all = _run_r2(d, fdir, astra, gate_E, approx, ev, budget_check)
    return _finish(d, ev, r0_calls, r1_all, r2_all, clean0, p1, final)


def run_w1_dev(out_dir: str, client, E_info: dict, *, arm: str = "A", budget_check=None, o2prime: bool = False, m2: bool = False) -> dict:
    """arm A = 範囲正規化(R4) + 保持Gate / arm B = A + R0規則9。ja_writer/ 以下へ Production と同名で出力。
    再実行枠: R0<=2 / R1<=2 / R2<=2 呼出。R0は記号QAと保持を1枠に合流、R2も記号QAと保持で1回を共有(M3)。"""
    assert arm in ("A", "B")
    budget_check = budget_check or (lambda: None)
    annotated = contract.validate_annotated_b3(out_dir)
    storyline, facts_text = w1.parse_brief_md(annotated.annotated_md_text)
    from er053_b3_deterministic_producer_01 import CONS_HEADING, compose_news_field
    overlay, rounding_ev = rounding.load_overlay_for_writer(out_dir, annotated.annotated_md_sha256)
    approx = approx_forms_of(out_dir)
    gate_E = list(E_info.get("gate_E") or [])
    o2_plan, base_news, facts_for_news = None, annotated.news_field_text, facts_text
    if o2prime:
        # O-2'(DEV wrapper内のみ): 契約検証済みの注記済みB3(ファイル・sha)は不変。メモリ上のnews欄/Facts文字列の印だけを付け替える。
        ann_sc = annotated.sidecar
        o2_plan = plan_o2prime(ann_sc, facts_text, E_info)
        dem = [x["surface"] for x in o2_plan["demote"]]
        if dem:
            facts_for_news, n_f = swap_marks(facts_text, dem)
            base_news, n_n = swap_marks(annotated.news_field_text, dem)
            o2_plan["marks_swapped"] = {"facts_text": n_f, "news_field_text": n_n, "demoted_surfaces": len(dem)}
            if n_f < len(dem) or n_n < len(dem):
                wj(os.path.join(out_dir, "o2prime_plan.json"), o2_plan)
                raise RuntimeError(f"[STOP] O-2' 印の付け替えが想定件数に満たない facts={n_f} news={n_n} demote={len(dem)}(API呼出前)")
            overlay = filter_overlay(overlay, dem)
        o2_plan["news_field_sha256_before"] = sha_text(annotated.news_field_text)
        o2_plan["news_field_sha256_after"] = sha_text(base_news)
        wj(os.path.join(out_dir, "o2prime_plan.json"), o2_plan)
    news_text = rounding.news_field_for_writer(base_news, facts_for_news, annotated.constraints_text, overlay, CONS_HEADING, compose_news_field)
    routing_ok = w1.routing.require_model("FAMILY_X_FACTLOCK_R0", w1.R0_MODEL), w1.routing.require_model("FAMILY_X_FACTLOCK_REVISE", w1.ASTRA_MODEL)
    d = os.path.join(out_dir, "ja_writer")
    fdir = os.path.join(d, "factlock")
    ev = {"arm": arm, "chain_method": "W-1_DEV_er115", "post_range_norm": True, "annotated_md_sha256": annotated.annotated_md_sha256,
          "verbatim_shas": w1.verbatim_shas(), "rounding": rounding_ev, "gate_E": gate_E, "observe_E": E_info.get("observe_E"),
          "rule9_text_sha256": sha_text(RULE9_TEXT), "retention_note_template_sha256": sha_text(RETENTION_NOTE_TEMPLATE),
          "range_norm": True, "o2prime": bool(o2prime), "m2_new_number_gate": bool(m2), "o2prime_plan": o2_plan,
          "retention": {}, "symbol_qa": {}, "model_contract": [str(x) for x in routing_ok],
          "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    prompt0 = build_r0_prompt_dev(storyline, news_text, overlay, range_norm=True, rule9=(arm == "B"))
    ev["r0_prompt_sha256"] = sha_text(prompt0)
    ev["r0_prompt_has_wave_in_news"] = bool(re.search(r"\d\s*[〜～~]\s*\d", prompt0.split("[ニュース]", 1)[-1]))
    wt(os.path.join(fdir, "r0_prompt_dev.txt"), prompt0)

    sym_of = _sym_of

    # ---- R0 (初回 + 最大1回の再生成。記号QAと保持を1枠に合流) ----
    budget_check()
    resp0 = w1.call_luna_r0(client, prompt0, "w1_r0")
    text0 = resp0.output_text.strip()
    r0_calls = [{"stage": "w1_r0", **_meta(resp0), "prompt_sha256": sha_text(prompt0)}]
    f0, sym0 = sym_of(text0)
    miss0 = check_retention(w1.strip_tags(text0), gate_E, approx)
    ev["symbol_qa"]["r0"] = {"findings_first": f0, "regenerated": False}
    ev["retention"]["r0"] = {"missing_first": [e["news_surface"] for e in miss0["missing"]], "detail_first": miss0["detail"], "regenerated": False,
                            "table_case": ("sym+ret" if sym0 and miss0["missing"] else "sym_only" if sym0 else "ret_only" if miss0["missing"] else "ok")}
    wt(os.path.join(fdir, "r0_first_with_tags.md"), text0)
    if sym0 or miss0["missing"]:
        budget_check()
        notes = prompt0
        if sym0:
            notes += "\n\n" + safety.build_symbol_violation_prompt_note(f0)
        if miss0["missing"]:
            notes += "\n\n" + retention_note(miss0["missing"])
        resp0b = w1.call_luna_r0(client, notes, "w1_r0_retention_regen" if miss0["missing"] else "w1_r0_symbol_regen")
        text0b = resp0b.output_text.strip()
        r0_calls.append({"stage": "w1_r0_regen", **_meta(resp0b), "prompt_sha256": sha_text(notes)})
        f0b, sym0b = sym_of(text0b)
        miss0b = check_retention(w1.strip_tags(text0b), gate_E, approx)
        ev["symbol_qa"]["r0"].update({"regenerated": True, "findings_after": f0b})
        ev["retention"]["r0"].update({"regenerated": True, "missing_after": [e["news_surface"] for e in miss0b["missing"]], "detail_after": miss0b["detail"]})
        wt(os.path.join(fdir, "r0_regen_with_tags.md"), text0b)
        if sym0b or miss0b["missing"]:
            wt(os.path.join(d, "audit", "rejected_w1_r0_first.md"), text0)
            wt(os.path.join(d, "audit", "rejected_w1_r0_regen.md"), text0b)
            wj(os.path.join(d, "runtime_evidence_stopped.json"), ev)
            raise JANumericRetentionStopError("r0", f"[STOP] JA_NUMERIC_RETENTION_STOP(R0): 再生成後も不足/残存 symbol={sym0b} missing={[e['news_surface'] for e in miss0b['missing']]}",
                                              {"first": text0, "regen": text0b}, miss0b["missing"])
        text0 = text0b
    clean0 = w1.clean_ja_for_next(text0).strip() + "\n"
    wt(os.path.join(fdir, "r0_with_tags.md"), text0)
    wt(os.path.join(fdir, "r0.md"), clean0)
    wj(os.path.join(fdir, "r0_meta.json"), {"writer_calls": r0_calls, "tags_used": sorted({t for m in w1.TAG_RE.finditer(text0) for t in w1.tag_ids(m.group(0))}),
                                            "r0_sha256": sha_text(clean0), "r0_prompt_sha256": sha_text(prompt0)})

    astra = make_astra(client)
    m2ctx = {"r0_text": clean0, "news_plain": P.strip_marks(w1.strip_tags(news_text))} if m2 else None

    # ---- R1 (保持不足なら1回だけ再実行=新規。記号QAはR1では従来どおり検査なし) ----
    budget_check()
    raw1, p1, m1 = astra(os.path.join(fdir, "r0.md"), "w1_astra_r1")
    miss1 = check_retention(p1, gate_E, approx)
    new1 = _new_numbers_m2(p1, m2ctx)
    if new1:
        miss1 = {"missing": list(miss1["missing"]) + [{"news_surface": "NEW:" + x} for x in new1], "detail": miss1.get("detail")}
    ev.setdefault("new_numbers", {})["r1"] = {"first": new1, "rerun": False}
    ev["retention"]["r1"] = {"missing_first": [e["news_surface"] for e in miss1["missing"]], "rerun": False}
    r1_all = [m1]
    if miss1["missing"]:
        wt(os.path.join(fdir, "r1.first.raw.md"), raw1)
        budget_check()
        raw1b, p1b, m1b = astra(os.path.join(fdir, "r0.md"), "w1_astra_r1_retention_rerun")
        r1_all.append(m1b)
        miss1b = check_retention(p1b, gate_E, approx)
        new1b = _new_numbers_m2(p1b, m2ctx)
        if new1b:
            miss1b = {"missing": list(miss1b["missing"]) + [{"news_surface": "NEW:" + x} for x in new1b], "detail": miss1b.get("detail")}
        ev["new_numbers"]["r1"].update({"rerun": True, "after": new1b})
        ev["retention"]["r1"].update({"rerun": True, "missing_after": [e["news_surface"] for e in miss1b["missing"]]})
        if miss1b["missing"]:
            wt(os.path.join(d, "audit", "rejected_w1_r1.md"), p1b)
            wj(os.path.join(d, "runtime_evidence_stopped.json"), ev)
            raise JANumericRetentionStopError("r1", f"[STOP] JA_NUMERIC_RETENTION_STOP(R1): 再実行後も不足 {[e['news_surface'] for e in miss1b['missing']]}",
                                              {"first": p1, "rerun": p1b}, miss1b["missing"])
        raw1, p1, m1 = raw1b, p1b, m1b
    wt(os.path.join(fdir, "r1.raw.md"), raw1)
    wj(os.path.join(fdir, "r1.response.json"), r1_all)
    wt(os.path.join(fdir, "r1.p1.md"), p1)

    # ---- R2 (記号QAと保持で再実行枠を共有=1回だけ。helper) ----
    final, p2, raw2, m2r, r2_all = _run_r2(d, fdir, astra, gate_E, approx, ev, budget_check, m2ctx)
    return _finish(d, ev, r0_calls, r1_all, r2_all, clean0, p1, final)


# ======================================================================================================
# 計測
# ======================================================================================================
def measure_run(out_dir: str, E_info: dict | None = None) -> dict:
    """段別(R0/R1/R2/EN Std/EN Adv)の E保持・非E中核掲載・周辺数値混入・誤解表現WARN。照合は較正済み match_core / en_present。"""
    sdir = os.path.join(out_dir, "storyline_b3")
    ann = rj(os.path.join(sdir, "annotation.json"))
    annotated_md = rdt(os.path.join(sdir, "selected_brief_annotated.md"))
    _, facts_marked = w1.parse_brief_md(annotated_md)
    approx = approx_forms_of(out_dir)
    E_info = E_info or derive_E(out_dir)
    e_surfaces = {nfkc(e["news_surface"]) for e in E_info["candidates"]}
    texts = {}
    for st, rel in (("R0", "ja_writer/factlock/r0.md"), ("R1", "ja_writer/revision1.md"), ("R2", "ja_writer/revision2.md"),
                    ("EN_Std", "a2/article.md"), ("EN_Adv", "b1b/article.md")):
        p = os.path.join(out_dir, rel)
        texts[st] = rdt(p) if os.path.exists(p) else None
    core = [n for n in ann["numbers"] if n["class"] == "core" and "_STORY" not in (n.get("ledger_ids") or [])]
    # 同一概念の表記は1個(ニュース欄に現れるもの)
    by_c = {}
    for n in core:
        if P.contains(P.strip_marks(facts_marked), n["surface"]):
            by_c.setdefault(n["concept"], n)
    core_rows = []
    for cid, n in by_c.items():
        hint = unit_hint_after(facts_marked, n["surface"])
        row = {"concept": cid, "surface": n["surface"], "ambiguous": T_is_ambiguous(n["surface"]), "in_E": nfkc(n["surface"]) in e_surfaces,
               "time_premise": is_time_premise(n["surface"]), "unit_hint": hint, "present": {}}
        for st in ("R0", "R1", "R2"):
            row["present"][st] = match_core(n["surface"], texts[st] or "", hint, [approx.get(nfkc(n["surface"]))])["present"] if texts[st] else None
        for st in ("EN_Std", "EN_Adv"):
            row["present"][st] = en_present(n["surface"], texts[st], hint) if texts[st] else None
        core_rows.append(row)
    periph = [n for n in ann["numbers"] if n["class"] != "core"]
    body = {}
    for st in ("R0", "R1", "R2"):
        if not texts[st]:
            continue
        pers, unc, amb = [], [], []
        seen = set()
        for s in P.extract_surfaces(re.sub(r"(\d)\s*から\s*(\d)", r"\g<1>〜\g<2>", texts[st])):
            k = P.surface_kind(s)
            kk = (k, P.main_numbers(s, k))
            if kk in seen:
                continue
            seen.add(kk)
            if any((P.surface_kind(c["surface"]), P.main_numbers(c["surface"], P.surface_kind(c["surface"]))) == kk for c in core):
                continue
            if T_is_ambiguous(s):
                amb.append(s)
            elif any((P.surface_kind(c["surface"]), P.main_numbers(c["surface"], P.surface_kind(c["surface"]))) == kk for c in periph):
                pers.append(s)
            else:
                unc.append(s)
        body[st] = {"peripheral_included": pers, "uncatalogued": unc, "ambiguous_small": amb}
    stages = [s for s in ("R0", "R1", "R2", "EN_Std", "EN_Adv") if texts[s]]
    ev_rows = [r for r in core_rows if not r["ambiguous"]]
    gate_E = [r for r in ev_rows if r["in_E"] and not r["time_premise"] and P.surface_kind(r["surface"]) in ("magnitude", "range")]
    plan_p = os.path.join(out_dir, "o2prime_plan.json")
    plan = rj(plan_p) if os.path.exists(plan_p) else None
    dem_rows = []
    news_plain = P.strip_marks(w1.strip_tags(facts_marked))
    if plan:
        for dsc in plan.get("demote", []):
            row = {"surface": dsc["surface"], "dimension": dsc["dimension"], "present": {}}
            for st in ("R0", "R1", "R2"):
                row["present"][st] = match_core(dsc["surface"], texts[st] or "", dsc.get("unit_hint", ""), [approx.get(nfkc(dsc["surface"]))])["present"] if texts[st] else None
            for st in ("EN_Std", "EN_Adv"):
                row["present"][st] = en_present(dsc["surface"], texts[st], dsc.get("unit_hint", "")) if texts[st] else None
            dem_rows.append(row)
    new_nums = {st: new_numbers(texts[st], texts["R0"] or "", news_plain) for st in ("R1", "R2") if texts.get(st) and texts.get("R0")}
    dem_surf = {nfkc(r["surface"]) for r in dem_rows}
    summ = {
        "o2prime_demoted": [r["surface"] for r in dem_rows], "o2prime_demoted_present": {r["surface"]: r["present"] for r in dem_rows},
        "new_numbers_vs_r0_news": new_nums,
        "n_core_selected_news_field": len(core_rows), "n_core_evaluable": len(ev_rows), "n_E_candidates": len(E_info["candidates"]),
        "n_E_gate": len(gate_E),
        "E_retained": {st: [r["surface"] for r in gate_E if r["present"].get(st)] for st in stages},
        "E_all_retained": {st: all(r["present"].get(st) for r in gate_E) if gate_E else None for st in stages},
        "non_E_core_included": {st: [r["surface"] for r in ev_rows if (not r["in_E"]) and r["present"].get(st)] for st in stages},
        "non_E_core_included_excluding_demoted": {st: [r["surface"] for r in ev_rows if (not r["in_E"]) and nfkc(r["surface"]) not in dem_surf and r["present"].get(st)] for st in stages},
        "observe_E_present": {st: {r["surface"]: r["present"].get(st) for r in ev_rows if r["in_E"] and r not in gate_E} for st in stages},
        "peripheral_included": {st: body[st]["peripheral_included"] for st in body},
        "misreading_warn": ({"R2": scan_misreading(texts["R2"])} if texts.get("R2") else {}),
    }
    return {"out_dir": os.path.relpath(out_dir, ROOT).replace("\\", "/"), "storyline": E_info["storyline"], "E_ok": E_info["ok"],
            "violations": E_info["violations"], "core_rows": core_rows, "body": body, "summary": summ,
            "texts_present": {k: bool(v) for k, v in texts.items()}}


# ======================================================================================================
# B3 DEV / 検証・再実行 / 費用 / sink guard
# ======================================================================================================
ARTICLES = {
    "moon_shrinking": "er019_output/moon_shrinking/run_ms_02",
    "uk_train_speaker_playback": "er019_output/uk_train_speaker_playback/run_nws_02",
    "manga_ai_chat_byus": "er019_output/manga_ai_chat_byus/run_byus_01",
    "ig_nobel_2026": "er019_output/ig_nobel_2026/run_nws_02",
    "coffee_prices": "er019_output/coffee_prices/run_fxpw_01",
    "semiconductor_earnings": "er019_output/semiconductor_earnings/run_devconfirm_01",
}


def with_field_schema(text_kw: dict) -> dict:
    """text={"format":{"type":"json_schema",...}} のコピーへ reader_must_hear_numbers(文字列配列)を足す。元のdict/Production定数は変更しない。"""
    t = copy.deepcopy(text_kw)
    sch = t["format"]["schema"]
    assert B3_FIELD_NAME not in sch["properties"]
    sch["properties"][B3_FIELD_NAME] = {"type": "array", "items": {"type": "string"}}
    sch["required"] = list(sch["required"]) + [B3_FIELD_NAME]
    return t


def save_field_from_calls(out_dir: str, wrapper) -> dict:
    """最終採用されたB3 call(runtime_evidence.jsonのresponse_id)の出力JSONからreader_must_hear_numbersを保存する。全call分も証跡に残す。"""
    rid = rj(os.path.join(out_dir, "storyline_b3", "runtime_evidence.json")).get("response_id")
    hit = next((c for c in reversed(wrapper.field_log) if c["response_id"] == rid), None) or (wrapper.field_log[-1] if wrapper.field_log else None)
    if hit is None:
        raise RuntimeError("[STOP] R5: B3のcall記録がありません")
    obj = json.loads(hit["output_text"])
    rec = {"items": list(obj.get(B3_FIELD_NAME) or []), "response_id": hit["response_id"], "matched_final_response": hit["response_id"] == rid,
           "all_calls": [{"response_id": c["response_id"], "items": (json.loads(c["output_text"]).get(B3_FIELD_NAME) if c["output_text"] else None)} for c in wrapper.field_log]}
    wj(os.path.join(out_dir, "storyline_b3", B3_FIELD_NAME + ".json"), rec)
    return rec


class _AddendumClient:
    """B3のuser messageの末尾へ追記ブロックを足すだけのclientラッパ(Production B3関数をそのまま呼ぶため)。"""

    def __init__(self, client, addendum: str, field_schema: bool = False):
        # field_schema=True(R5): 送信直前に、STORYLINE_B3_JSON_SCHEMAのdeepcopyへreader_must_hear_numbers欄を足す(Production定数は不変)。
        self._c, self.addendum, self.sent_user_shas = client, addendum, []
        self.field_schema, self.field_log = field_schema, []
        outer = self

        class _Resp:
            def create(self_inner, **kw):
                inp = copy.deepcopy(kw.get("input"))
                if inp and inp[-1].get("role") == "user":
                    inp[-1]["content"] = inp[-1]["content"] + outer.addendum
                    outer.sent_user_shas.append(sha_text(inp[-1]["content"]))
                kw["input"] = inp
                if outer.field_schema:
                    kw["text"] = with_field_schema(kw.get("text"))
                resp = outer._c.responses.create(**kw)
                if outer.field_schema:
                    outer.field_log.append({"response_id": getattr(resp, "id", None), "output_text": getattr(resp, "output_text", None)})
                return resp

            def __getattr__(self_inner, name):
                return getattr(outer._c.responses, name)
        self.responses = _Resp()

    def __getattr__(self, name):
        return getattr(self._c, name)


def sample_dir(article: str, arm: str, sample: str) -> str:
    return os.path.join(OUT_ROOT, article, arm, sample)


def prepare_dir(article: str, out_dir: str) -> dict:
    src = os.path.join(ROOT, ARTICLES[article])
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "research_ledger")
    if not os.path.isdir(dst):
        shutil.copytree(os.path.join(src, "research_ledger"), dst)
    theme = rj(os.path.join(src, "entry_point.json"))["args"]["theme"]
    wj(os.path.join(out_dir, "dev_source.json"), {"article": article, "source_run": ARTICLES[article], "topic_sha256": sha_text(theme),
                                                  "ledger_sha256": sha_text(rdt(os.path.join(dst, "verified_fact_ledger.txt")))})
    return {"theme": theme, "ledger_text": rdt(os.path.join(dst, "verified_fact_ledger.txt"))}


def phase_spent_jpy() -> float:
    total = 0.0
    for p in sorted(glob_logs()):
        try:
            total += ca.compute_stage_cost_breakdown_multi(p)["total_jpy"]
        except Exception:   # 空/不正logは0扱い(fail-open for 集計のみ。実行ガードはefam.assert_budget_ok側)
            pass
    return total


def glob_logs():
    out = []
    for dp, _dn, fn in os.walk(OUT_ROOT):
        if "raw_usage_log.jsonl" in fn:
            out.append(os.path.join(dp, "raw_usage_log.jsonl"))
    return out


def guard_budget(out_dir: str, per_run_cap: float, phase_cap: float, note: str):
    efam.assert_budget_ok(out_dir, per_run_cap, note)
    spent = phase_spent_jpy()
    if spent > phase_cap:
        raise RuntimeError(f"[BUDGET_GUARD] phase spent {spent:.2f} > cap {phase_cap} ({note})")


def sink_snapshot() -> dict:
    """Production sinkの前後比較用: git管理下で変更中の全pathのsha(er115_output/ と docs/ は除外)。"""
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    snap = {}
    for ln in out.splitlines():
        path = ln[3:].strip().strip('"')
        if path.startswith(("er115_output/", "docs/")):
            continue
        p = os.path.join(ROOT, path)
        snap[path] = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "DIR_OR_MISSING"
    return snap


def run_b3_dev(article: str, arm: str, sample: str, *, per_run_cap: float, phase_cap: float, client=None, addendum_version: str = "v1", max_attempts: int = 2) -> dict:
    """B3 DEV(追記ブロック付き) -> 注記producer(決定論) -> M1検査 -> 違反なら B3を1回だけ再実行 -> E確定。丸め・Writerは呼ばない。"""
    out_dir = sample_dir(article, arm, sample)
    info = prepare_dir(article, out_dir)
    cl.install(os.path.join(out_dir, "raw_usage_log.jsonl"))
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = client or vfl01.get_client()
    guard_budget(out_dir, per_run_cap, phase_cap, "before b3 dev")
    attempts = []
    base_addendum = B3_ADDENDA[addendum_version]
    addendum = base_addendum
    E_info = None
    r5 = addendum_version in ("v3", "v4")
    for attempt in range(1, max_attempts + 1):   # 既定2=従来(M1違反時にB3を1回だけ再実行)。委任_06 C-2は費用予約のため1(再実行なし)で呼ぶ
        wrapper = _AddendumClient(client, addendum, field_schema=r5)
        if attempt == 2:
            # 1回目のartifactを退避(上書きしない)
            shutil.copytree(os.path.join(out_dir, "storyline_b3"), os.path.join(out_dir, "storyline_b3_attempt1"))
            shutil.rmtree(os.path.join(out_dir, "storyline_b3"))
        runner.run_storyline_b3(wrapper, info["theme"], info["ledger_text"], out_dir)
        guard_budget(out_dir, per_run_cap, phase_cap, f"after b3 dev attempt{attempt}")
        runner.assert_b3_min_verified(out_dir)
        runner.run_annotation_producer(out_dir)
        if r5:
            save_field_from_calls(out_dir, wrapper)
            E_info = derive_E_r5(out_dir)
        else:
            E_info = derive_E(out_dir)
        attempts.append({"attempt": attempt, "storyline": E_info["storyline"], "ok": E_info["ok"], "violations": E_info["violations"],
                         "candidates": E_info["candidates"], "user_prompt_sha256": wrapper.sent_user_shas,
                         **({"field_items": E_info["field_items"], "storyline_consistency": E_info["storyline_consistency"]} if r5 else {})})
        if E_info["ok"]:
            break
        if attempt == 1:
            probs = "、".join(f"{v['surface']}({v['reason']})" for v in E_info["violations"])
            addendum = base_addendum + (M1_RETRY_NOTE_V3_TEMPLATE if r5 else M1_RETRY_NOTE_TEMPLATE).format(problems=probs)
    final_status = "E_OK" if E_info["ok"] and E_info["gate_E"] else ("E_EMPTY" if E_info["ok"] else "M1_VIOLATION")
    res = {"article": article, "arm": arm, "sample": sample, "status": final_status, "first_pass_ok": attempts[0]["ok"],
           "b3_rerun": len(attempts) == 2, "attempts": attempts, "E": E_info, "b3_addendum_version": addendum_version, "b3_addendum_sha256": sha_text(base_addendum),
           "b3_cost_jpy": ca.compute_stage_cost_breakdown_multi(os.path.join(out_dir, "raw_usage_log.jsonl"))["total_jpy"]}
    wj(os.path.join(out_dir, "m1_result.json"), res)
    print(f"[ER115][b3] {article}/{arm}/{sample} status={final_status} first_pass_ok={res['first_pass_ok']} rerun={res['b3_rerun']} "
          f"E={[e['news_surface'] for e in E_info['candidates']]} cost={res['b3_cost_jpy']}")
    return res


def run_chain_dev(article: str, arm: str, sample: str, *, per_run_cap: float, phase_cap: float, client=None, resume_r2: bool = False,
                  o2prime: bool = False, m2: bool = False, allow_empty_E: bool = False) -> dict:
    out_dir = sample_dir(article, arm, sample)
    m1 = rj(os.path.join(out_dir, "m1_result.json"))
    # allow_empty_E: B3 v2がStorylineに数値を入れなかった(E=∅)標本でも、保持Gate無し・O-2'無作用のまま必要数値の掲載を測るために実行(Phase 2の測定用)
    if m1["status"] != "E_OK" and not (allow_empty_E and m1["status"] == "E_EMPTY"):
        raise RuntimeError(f"[STOP] chain前提不成立: m1 status={m1['status']}")
    if os.path.exists(os.path.join(out_dir, "ja_writer", "revision2.md")):
        raise RuntimeError("[STOP] ja_writer/revision2.md が既にあります(DEV chainは再実行しない)。")
    if resume_r2 and not os.path.exists(os.path.join(out_dir, "ja_writer", "runtime_evidence_stopped.json")):
        raise RuntimeError("[STOP] --resume-r2 はSTOP済み標本(runtime_evidence_stopped.json)にのみ使えます。")
    src_info = prepare_dir(article, out_dir)
    cl.install(os.path.join(out_dir, "raw_usage_log.jsonl"))
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = client or vfl01.get_client()
    before = sink_snapshot()
    args = types.SimpleNamespace(regenerate_stage=None, budget_jpy=per_run_cap)
    E_info = m1["E"]
    guard_budget(out_dir, per_run_cap, phase_cap, "before chain")
    rounding_r = runner.run_core_number_rounding(client, out_dir, src_info["ledger_text"], args, "all")
    t0 = time.time()
    stop = None
    try:
        _bc = lambda: guard_budget(out_dir, per_run_cap, phase_cap, "w1 dev")   # noqa: E731
        if resume_r2:
            wres = resume_w1_dev_from_r2(out_dir, client, E_info, arm=arm, budget_check=_bc)
        else:
            wres = run_w1_dev(out_dir, client, E_info, arm=arm, budget_check=_bc, o2prime=o2prime, m2=m2)
    except JANumericRetentionStopError as exc:
        stop = {"stage": exc.stage, "message": str(exc), "missing": [e["news_surface"] for e in exc.missing]}
        wj(os.path.join(out_dir, "stop_record.json"), stop)
        print(f"[ER115][chain] STOP {stop}")
        return {"status": "STOP_RETENTION", "stop": stop}
    wsec = round(time.time() - t0, 1)
    theme = {"theme_id": article, "topic": src_info["theme"], "out_dir": out_dir, "ledger_path": os.path.join(out_dir, "research_ledger", "verified_fact_ledger.txt")}
    for lvl in ("advanced", "standard"):
        with cl.logging_context(TRIAL_TAG, lvl):
            efam.run_writer_stage(client, theme, wres["ja_text"], src_info["ledger_text"], per_run_cap, only=lvl)
        guard_budget(out_dir, per_run_cap, phase_cap, f"after {lvl}")
    metrics = measure_run(out_dir, E_info if m1.get("b3_addendum_version") in ("v3", "v4") else derive_E(out_dir))
    wj(os.path.join(out_dir, "trial_metrics.json"), metrics)
    after = sink_snapshot()
    sink_diff = {k: (before.get(k), after.get(k)) for k in set(before) | set(after) if before.get(k) != after.get(k)}
    cost = ca.compute_stage_cost_breakdown_multi(os.path.join(out_dir, "raw_usage_log.jsonl"))
    cost["b3_core_number_rounding"] = rounding.summarize_for_run(out_dir)
    wj(os.path.join(out_dir, "cost.json"), cost)
    wj(os.path.join(out_dir, "sink_guard.json"), {"changed_paths_during_chain": sink_diff, "note": "並行agentの変更を含みうる。er115由来の書込みはer115_output/のみのはず"})
    print(f"[ER115][chain] {article}/{arm}/{sample} cost={cost['total_jpy']} w1_sec={wsec} sink_changed={len(sink_diff)}")
    return {"status": "DONE", "metrics": metrics, "cost": cost, "sink_diff": sink_diff}


# ======================================================================================================
# 委任_06 C-1(Opus条件C): 欄(reader_must_hear_numbers)の数値をderive_ranksで『Storylineの数値』と同等以上に扱う(DEV専用・既定OFF)
#   事実(OPUS_REVIEW_03 C-1): M1違反3件は全て peripheral_number_in_storyline = 欄の数値がderive_ranksのcap(最低3)からあふれただけで、意味判断ではない。
#   方式: derive_ranks本体は変えず、storyline引数に渡す文字列へ欄の数値(Fact本文に写像できるものだけ)を足す。Production moduleは編集しない。
#   この関数群は呼び出されない限り何も起きない(Productionからimportされない=test_isolationで確認、flag/環境変数なし)。
# ======================================================================================================
def field_priority_surfaces(items, facts_all_text: str, story: str) -> dict:
    """欄の各項目から数値表記を抽出し、Fact本文(または元Storyline)に写像できるものだけを優先対象にする。写像できないものは unmapped(M1の構造検査が違反として扱う)。"""
    kept, unmapped = [], []
    for it in items or []:
        for s in P.extract_surfaces(str(it)):
            if P.surface_kind(s) in ("year", "ordinal", "name_embedded") or T_is_ambiguous(s):
                continue
            if P.contains(facts_all_text, s) or P.contains(story or "", s):
                kept.append(s)
            else:
                unmapped.append(s)
    return {"kept": list(dict.fromkeys(kept)), "unmapped": list(dict.fromkeys(unmapped))}


def field_priority_story(story: str, items, facts_all_text: str) -> str:
    """derive_ranksへ渡す『Storyline相当文字列』= 元Storyline + 欄の数値(写像可能なもの)。元Storylineの文字列自体(出力・Writerに渡る文)は変えない。"""
    sf = field_priority_surfaces(items, facts_all_text, story)
    return (story or "") + ("\n" + " ".join(sf["kept"]) if sf["kept"] else "")


def make_field_priority_ddet(items):
    """P.ddet と同じ戻り値のdet関数(欄の数値をStoryline同等として導出)。"""
    def ddet(ledger, ids, story, assembled_text=True):
        ids2 = [i for i in ids if i in P.B1.parse_ledger(ledger)[0]]
        tb = P.line_texts(P.B1.assemble_D(ledger, ids2, story, P.BASE_VARIANT)) if assembled_text else None
        facts_all = "\n".join((tb or {}).values())
        aug = field_priority_story(story, items, facts_all)
        return P.RK.derive_ranks(ledger, ids2, aug, with_story=True, text_by_fact=tb)
    return ddet


class field_priority_ddet:
    """contextmanager: with内だけ P.ddet を差し替える(終了時に必ず復元)。produce_annotated_b3 が module-global の ddet を呼ぶことを利用(Production moduleのファイルは不変)。"""

    def __init__(self, items):
        self.items, self._orig = list(items or []), None

    def __enter__(self):
        self._orig = P.ddet
        P.ddet = make_field_priority_ddet(self.items)
        return self

    def __exit__(self, *exc):
        P.ddet = self._orig
        return False


def _core_summary(out_dir: str) -> dict:
    sdir = os.path.join(out_dir, "storyline_b3")
    ann = rj(os.path.join(sdir, "annotation.json"))
    man = rj(os.path.join(sdir, "annotation_manifest.json"))
    notes = ann.get("annotation_notes") or []
    return {"cap": man.get("cap"), "n_concepts": man.get("n_concepts"),
            "core": sorted({n["surface"] for n in ann["numbers"] if n.get("class") == "core"}),
            "peripheral_capped_off": notes}


def reapply_field_priority(sample_path: str, dst_dir: str, *, attempt1: bool = False) -> dict:
    """保存済みB3出力に、(base) 現行方式の導出と (new) 欄優先の導出を決定論で当てる。API 0。元標本は変更せず dst_dir/{base,new} に複製して行う。"""
    src_b3 = os.path.join(sample_path, "storyline_b3_attempt1" if attempt1 else "storyline_b3")
    res = {"sample": os.path.relpath(sample_path, OUT_ROOT).replace("\\", "/") + ("#attempt1" if attempt1 else "")}
    for variant in ("base", "new"):
        d = os.path.join(dst_dir, variant)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        shutil.copytree(os.path.join(sample_path, "research_ledger"), os.path.join(d, "research_ledger"))
        shutil.copytree(src_b3, os.path.join(d, "storyline_b3"))
    items = read_field_items(os.path.join(dst_dir, "base"))
    res["field_items"] = items
    res["storyline"] = (rj(os.path.join(dst_dir, "base", "storyline_b3", "fact_selection_evidence.json")).get("selected_storyline") or "").strip()
    out = {}
    for variant in ("base", "new"):
        d = os.path.join(dst_dir, variant)
        err = None
        try:
            if variant == "new":
                with field_priority_ddet(items):
                    P.produce_annotated_b3(d)
            else:
                P.produce_annotated_b3(d)     # baseline再導出(現行Production導出。保存済み注記と一致することを確認する)
            E = derive_E_r5(d)
            ann = rj(os.path.join(d, "storyline_b3", "annotation.json"))
            _, fm = w1.parse_brief_md(rdt(os.path.join(d, "storyline_b3", "selected_brief_annotated.md")))
            plan = plan_o2prime(ann, fm, E)
            out[variant] = {"status": "E_OK" if E["ok"] and E["gate_E"] else ("E_EMPTY" if E["ok"] else "M1_VIOLATION"),
                            "violations": E["violations"], "E": [c["news_surface"] for c in E["candidates"]],
                            "E_gate": [c["news_surface"] for c in E["gate_E"]], "ranks": _core_summary(d),
                            "o2prime_demote": [x["surface"] for x in plan["demote"]], "o2prime_dims": plan["e_dimensions"]}
        except Exception as ex:   # noqa: BLE001  producer失敗も結果として残す(fail-closed)
            err = f"{type(ex).__name__}: {ex}"
            out[variant] = {"status": "PRODUCER_ERROR", "error": err}
    res.update(out)
    b, n = out["base"], out["new"]
    if b.get("ranks") and n.get("ranks"):
        res["core_added"] = sorted(set(n["ranks"]["core"]) - set(b["ranks"]["core"]))
        res["core_removed"] = sorted(set(b["ranks"]["core"]) - set(n["ranks"]["core"]))
        res["demote_changed"] = {"base": b["o2prime_demote"], "new": n["o2prime_demote"]}
    return res


def plan_for_existing(out_dir: str) -> dict:
    """既存B3標本のannotation/E(m1_result.json)にO-2'の計画だけを当てる(無料)。"""
    sdir = os.path.join(out_dir, "storyline_b3")
    ann = rj(os.path.join(sdir, "annotation.json"))
    _, facts_marked = w1.parse_brief_md(rdt(os.path.join(sdir, "selected_brief_annotated.md")))
    E_info = derive_E(out_dir)
    plan = plan_o2prime(ann, facts_marked, E_info)
    return {"out_dir": os.path.relpath(out_dir, ROOT).replace("\\", "/"), "storyline": E_info["storyline"], "E": [e["news_surface"] for e in E_info["candidates"]],
            "E_gate": [e["news_surface"] for e in E_info["gate_E"]], "plan": plan}


def main():
    ap = argparse.ArgumentParser(description="FX-CORE-NUMERIC-RETENTION-TRIAL-01 DEV runner(Production非接続)")
    ap.add_argument("cmd", choices=("b3", "chain", "measure", "plan"))
    ap.add_argument("--article", required=True, choices=sorted(ARTICLES))
    ap.add_argument("--arm", default="A", choices=("A", "B"))
    ap.add_argument("--sample", required=True)
    ap.add_argument("--per-run-cap-jpy", type=float, default=30.0)
    ap.add_argument("--phase-cap-jpy", type=float, default=120.0)
    ap.add_argument("--resume-r2", action="store_true", help="STOP済み標本のR0/R1を再利用しR2から再開(範囲正規化つき)")
    ap.add_argument("--b3-addendum", default="v1", choices=sorted(B3_ADDENDA), help="B3追記ブロック版(v1=Phase 1 / v2=O-1')")
    ap.add_argument("--o2prime", action="store_true", help="O-2'(同単位系の非E中核数値を周辺扱い、DEV wrapper内のみ)")
    ap.add_argument("--allow-empty-E", action="store_true", help="B3がStorylineに数値を入れなかった標本(E=∅)でもchainを実行(測定用・Gate無し)")
    ap.add_argument("--max-attempts", type=int, default=2, choices=(1, 2), help="b3のみ: 1=M1違反でもB3を再実行しない(委任_06 C-2。既定2=従来)")
    ap.add_argument("--m2", action="store_true", help="M2(R1/R2の新規数値検出を保持Gateの再実行枠で行う)")
    a = ap.parse_args()
    if a.cmd == "b3":
        run_b3_dev(a.article, a.arm, a.sample, per_run_cap=a.per_run_cap_jpy, phase_cap=a.phase_cap_jpy, addendum_version=a.b3_addendum, max_attempts=a.max_attempts)
    elif a.cmd == "chain":
        run_chain_dev(a.article, a.arm, a.sample, per_run_cap=a.per_run_cap_jpy, phase_cap=a.phase_cap_jpy, resume_r2=a.resume_r2,
                      o2prime=a.o2prime, m2=a.m2, allow_empty_E=a.allow_empty_E)
    elif a.cmd == "plan":
        # 手順(i): 既存B3標本に O-2' を決定論で当て直す(API 0・B3再実行なし・標本のファイルは変更せず別名で保存)
        d = sample_dir(a.article, a.arm, a.sample)
        res = plan_for_existing(d)
        wj(os.path.join(d, "o2prime_plan_offline.json"), res)
        print("[ER115][plan]", a.article, a.arm, a.sample, "E=", res["E"], "dims=", res["plan"]["e_dimensions"], "demote=", [x["surface"] for x in res["plan"]["demote"]],
              "kept=", [(x["surface"], x["why_kept"]) for x in res["plan"]["kept_core"]])
    else:
        d = sample_dir(a.article, a.arm, a.sample)
        wj(os.path.join(d, "trial_metrics.json"), measure_run(d))
        print("measured", d)


if __name__ == "__main__":
    main()
