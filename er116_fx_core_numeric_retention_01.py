# -*- coding: utf-8 -*-
"""er116_fx_core_numeric_retention_01.py  (Production module / Family X専用)

FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07。Family X(日本語記事)の「中核数値保持方式 v4」+「J2(範囲値の波ダッシュ正規化)」の
Production実装。ユーザー承認(2026-10-25 USER_04/USER_05): 中核数値保持方式v4=APPROVED_FOR_PRODUCTION、J2=APPROVED_FOR_PRODUCTION。
対象はFamily X(Std/Adv)のみ。Family Y/Zからはimportされない(test_isolation)。

構成(検証済みTrial `er115_fx_numeric_retention_trial_01.py` からの移植。関数本体は `er116_..._test_01.py` がer115とソース同一性を検査する):
  B3   : v4指示文(V2=Storyline数値規則O-1' + 欄指示)と欄schema(`reader_must_hear_numbers`、最大2・空可)を、Production B3の呼出時だけ
         deepcopyへ足す(`variant()`/`with_field_schema`)。`STORYLINE_B3_JSON_SCHEMA`定数は直接変更しない(Y Trialのimport契約を守る)。
  M1   : 欄の各項目を注記済みニュース欄の【中核数値】へ写像する構造検査(写像不可/_STORYのみ/2個超/数値表記なし/年・序数/周辺数値)。
  E    : E = 欄の数値(決定論)。M1違反→B3を1回だけ再実行(runner)。再実行後も違反ならE=∅で続行+WARN+runtime evidence(現行Production同等)。
  Gate : R0/R1/R2直後のE保持検査(較正済み照合)。不足時は既存の再生成枠で1回、なお不足ならSTOP(JASymbolCheckStopErrorのサブクラス=既存STOP枠)。
  O-2' : Eと同単位系の非E中核数値を、Writer入力のメモリ上だけで【周辺数値】へ付け替え(年系は残す)。規則5の文言・R0 Prompt・注記済みB3ファイルは不変。
  M2   : R1/R2出力の新規数値検出(R0本文にもニュース欄にもない数値)→保持Gateと同じ再実行枠。
  J2/R4: 範囲値「A〜B」→「AからB」(数字・桁不変)。Writer入力(R4)と出力R0/R1/R2(J2)。E=∅の記事にも適用(OPEN-509の修正)。
         TTS用Normalizer(`er003.normalize_tilde_placeholder_ja`)は役割が違う(使い捨てコピー)ため残置し二重化しない。
  既定動作: 欄が無い(旧記事)/欄が空/M1最終違反 => E=∅ => Gate・O-2'・M2なし(現行Productionと同じ)。J2/R4のみ適用。
v1〜v3指示文・Storyline由来E・RULE9・resume_w1_dev_from_r2 はer115(Trialの記録)に残置し、本moduleは移植しない。
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import re

import er053_b3_deterministic_producer_01 as P   # noqa: E402
import er053_family_x_factlock_ja_writer_01 as w1   # noqa: E402

MANAGEMENT_ID = "FX-CORE-NUMERIC-RETENTION-TRIAL-01_DELEGATION_07"
RULE_VERSION = "fx_core_numeric_retention_v4_j2_01"

B3_ADDENDUM_V2 = (
    "\n\n【追加の指示: 数値の扱い(Storylineを決めた後の手順)】\n"
    "上の1〜5で中心Storylineと採用Factを決めた後、selected_storylineの1行を書くときだけ、次に従ってください。Storylineの選び方とFactの採否は、数値の有無で変えないでください(Test4のとおり、「数字がある」だけの理由でFactを残さないこと)。\n"
    "- そのStorylineの1行が答える中心的な問いに、台帳のnumeric_value欄にある数値で直接答えられる場合は、問いへの答えそのものの値だけを、numeric_value欄の表記のまま、selected_storylineの1行に含めてください(最大2個)。\n"
    "- 予測値・別の推定・過去の値・基準値など、答えと見比べるための数値(比較相手)は、比較そのものが問いへの答えである場合を除き、selected_storylineの1行に数値で入れず、言葉で述べてください(比較そのものが答えの場合は、比べる2つの値を入れてよい。合わせて最大2個)。\n"
    "- その数値の解釈に不可欠な前提(推定・仮定・期間・範囲)がある場合は、前提を示す言葉(「推定」「仮定」など)を含めてください。前提の数値を含めてよいのは、それが中心的な問いへの答えの一部である場合だけで、上記の最大2個に含みます。\n"
    "- 中心的な問いが数値で答えるものでない場合、または入れると文が不自然になる場合は、数値を入れなくてかまいません。数値を増やすために無関係な数値を入れないでください。\n"
    "- numeric_value欄にない数値や、他のFactの補足的な数値は、selected_storylineの1行に含めないでください。"
)
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
M1_RETRY_NOTE_V3_TEMPLATE = (
    "\n\n【前回出力の修正指示(reader_must_hear_numbers)】前回のreader_must_hear_numbersには、次の項目が条件に合いませんでした: {problems}。"
    "この欄に入れてよいのは、採用Factに含まれる台帳numeric_value欄の数値(表記のまま、最大2個)だけです。"
    "条件に合う数値がなければ空の配列[]にしてください。Storylineの選び方・Factの採否はこのために変えないでください。"
)
RETENTION_NOTE_TEMPLATE = "次の数字が本文にありません: {items}。ニュース欄のとおりに含めて書き直してください。他の数字は増やさないでください。"
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



def is_time_premise(surface: str) -> bool:
    k = P.surface_kind(surface)
    return k == "magnitude" and bool(TIME_PREMISE_UNIT_RE.fullmatch(P.unit_of(surface) or ""))



def read_field_items(out_dir: str) -> list:
    p = os.path.join(out_dir, "storyline_b3", B3_FIELD_NAME + ".json")
    return [str(x) for x in (rj(p).get("items") or [])] if os.path.exists(p) else []



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



def normalize_ranges_counted(text: str):
    """normalize_ranges + 置換件数(R1/R2出力の後処理用)。"""
    new = normalize_ranges(text)
    pat = rf"\d\s*[{WAVES}]\s*\d"
    n = len(re.findall(pat, text or "")) - len(re.findall(pat, new))
    return new, max(n, 0)



def with_field_schema(text_kw: dict) -> dict:
    """text={"format":{"type":"json_schema",...}} のコピーへ reader_must_hear_numbers(文字列配列)を足す。元のdict/Production定数は変更しない。"""
    t = copy.deepcopy(text_kw)
    sch = t["format"]["schema"]
    assert B3_FIELD_NAME not in sch["properties"]
    sch["properties"][B3_FIELD_NAME] = {"type": "array", "items": {"type": "string"}}
    sch["required"] = list(sch["required"]) + [B3_FIELD_NAME]
    return t


# ======================================================================================================
# 以下はProduction新規部分(Trialの DEV wrapper[_AddendumClient/run_w1_dev/run_b3_dev]は移植しない)
# ======================================================================================================
def variant(retry_problems: str | None = None) -> dict:
    """Production B3呼出へ渡すv4 variant(`b3.run_storyline_b3_selection(variant=...)`)。
    addendum = V2+欄指示(+M1再実行時は修正指示)をuser messageの末尾へ追記、text_transform = schema deepcopyへ欄を追加。
    Trial(er115 _AddendumClient)と同じバイト列を送る。"""
    add = B3_ADDENDUM_V4 + (M1_RETRY_NOTE_V3_TEMPLATE.format(problems=retry_problems) if retry_problems else "")
    return {"name": "v4", "addendum": add, "text_transform": with_field_schema,
            "base_addendum_sha256": sha_text(B3_ADDENDUM_V4), "addendum_sha256": sha_text(add), "m1_retry": bool(retry_problems)}


def save_field(stage_dir: str, parsed: dict, response_id: str | None) -> dict:
    """採用されたB3出力(同一call)の欄を `<stage_dir>/reader_must_hear_numbers.json` へ保存。resume/再生成時はこのファイルからEを決定論で再構成する。"""
    present = B3_FIELD_NAME in (parsed or {})
    rec = {"items": [str(x) for x in ((parsed or {}).get(B3_FIELD_NAME) or [])], "response_id": response_id,
           "field_present_in_output": present, "source": "production_b3_same_call", "rule_version": RULE_VERSION}
    wj(os.path.join(stage_dir, B3_FIELD_NAME + ".json"), rec)
    return rec


def derive_E(out_dir: str, *, surfaces, extra_violations=None, item_count=None) -> dict:
    """producer出力(annotation.json / selected_brief_annotated.md)から、表記リストsurfaces(=欄)のM1構造検査とEを決定論で得る。LLM/APIなし。
    違反(violations)があれば gate_E は空(呼出側がB3再実行/E=∅続行を判断)。移植元=er115.derive_E(surfaces指定経路のみ。Storyline由来Eは移植しない)。"""
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
    for s in dict.fromkeys(surfaces):
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


def derive_E_from_field(out_dir: str) -> dict:
    """E = reader_must_hear_numbers欄(B3自身の判断)。欄の各項目をM1構造検査(ニュース欄の中核数値へ写像・_STORYのみ不可・同一概念1個・最大2個)に通す。
    移植元=er115.derive_E_r5(Storyline由来Eとの整合記録は移植しない=Storyline数値は記録だけ)。LLM/APIなし。"""
    items = read_field_items(out_dir)
    pre, surfs = [], []
    for it in items:
        ss = P.extract_surfaces(it)
        if not ss:
            pre.append({"surface": it, "reason": "field_item_no_numeric_surface"})
        surfs.extend(ss)
    E = derive_E(out_dir, surfaces=list(dict.fromkeys(surfs)), extra_violations=pre, item_count=len(items))
    E["source"] = B3_FIELD_NAME
    E["field_items"] = items
    E["storyline_numbers_record_only"] = sorted({nfkc(s) for s in P.extract_surfaces(E["storyline"])})
    return E


def m1_problem_text(E_info: dict) -> str:
    """B3再実行の修正指示に埋める違反の説明(Trialと同じ書式)。"""
    return "、".join(f"{v['surface']}({v['reason']})" for v in E_info["violations"])


class NumericRetention:
    """1回のW-1(JA Writer)実行で使う中核数値保持の文脈。`w1.run_w1_writer(out_dir, ..., numeric=ctx)` に渡す。
    ctx=None(Family X以外・Trial)なら従来どおり。ctx.active(=gate_Eあり)のときだけ Gate/O-2'/M2。J2/R4は常に有効(ctxを渡した場合)。"""

    def __init__(self, out_dir: str, E_info: dict | None, mode: str):
        self.out_dir = out_dir
        self.E_info = E_info
        self.mode = mode   # legacy_no_field | field_empty | field_ok | m1_final_violation_E_empty | field_observe_only
        self.gate_E = list(E_info["gate_E"]) if (E_info and E_info.get("ok")) else []
        self.approx = approx_forms_of(out_dir) if self.gate_E else {}
        self.o2_plan = None
        self.m2ctx = None
        ok = bool(E_info and E_info.get("ok"))
        self.ev = {"rule_version": RULE_VERSION, "mode": mode,
                   "E": [c["news_surface"] for c in (E_info or {}).get("candidates", [])] if ok else [],
                   "gate_E": [c["news_surface"] for c in self.gate_E],
                   "observe_E": [c["news_surface"] for c in ((E_info or {}).get("observe_E") or [])] if ok else [],
                   "field_items": (E_info or {}).get("field_items"),
                   "m1_violations": (E_info or {}).get("violations") if E_info else None,
                   "j2": {"r4_input_changed": False, "output_normalized": {}}, "retention": {}, "new_numbers": {}, "o2prime": None,
                   "warn": [], "b3_addendum_sha256": sha_text(B3_ADDENDUM_V4)}
        if mode == "m1_final_violation_E_empty":
            self.ev["warn"].append("M1_FINAL_VIOLATION_E_EMPTY: 欄がM1構造検査に合格しなかったため E=∅ で続行(現行Production同等。Gate/O-2'/M2なし)")
            print("[WARN][numeric_retention] M1最終違反のため E=∅ で続行します(Gate/O-2'/M2なし=現行Production同等)。runtime evidenceに記録。")

    @classmethod
    def from_out_dir(cls, out_dir: str) -> "NumericRetention":
        """保存済みの欄(storyline_b3/reader_must_hear_numbers.json)からEを決定論で再構成する。B3は呼ばない。
        欄ファイルなし(旧記事)=E=∅。欄が空=E=∅。M1違反が残る=E=∅+WARN。それ以外=E=欄の数値。"""
        p = os.path.join(out_dir, "storyline_b3", B3_FIELD_NAME + ".json")
        if not os.path.exists(p):
            return cls(out_dir, None, "legacy_no_field")
        E = derive_E_from_field(out_dir)
        if not E["ok"]:
            return cls(out_dir, E, "m1_final_violation_E_empty")
        if not E["candidates"]:
            return cls(out_dir, E, "field_empty")
        return cls(out_dir, E, "field_ok" if E["gate_E"] else "field_observe_only")

    @property
    def active(self) -> bool:
        return bool(self.gate_E)

    # ---- O-2'(Writer入力のメモリ上の付け替え。注記済みB3ファイル・契約shaは不変) ----
    def apply_o2prime(self, annotated, facts_text: str, news_field_text: str, overlay):
        """戻り値 (news_field_text', facts_text', overlay')。active=Falseなら入力をそのまま返す。"""
        if not self.active:
            return news_field_text, facts_text, overlay
        plan = plan_o2prime(annotated.sidecar, facts_text, self.E_info)
        dem = [x["surface"] for x in plan["demote"]]
        facts_for_news, base_news = facts_text, news_field_text
        if dem:
            facts_for_news, n_f = swap_marks(facts_text, dem)
            base_news, n_n = swap_marks(news_field_text, dem)
            plan["marks_swapped"] = {"facts_text": n_f, "news_field_text": n_n, "demoted_surfaces": len(dem)}
            if n_f < len(dem) or n_n < len(dem):
                self.ev["o2prime"] = plan
                raise RuntimeError(f"[STOP] O-2' 印の付け替えが想定件数に満たない facts={n_f} news={n_n} demote={len(dem)}(API呼出前)")
            overlay = filter_overlay(overlay, dem)
        plan["news_field_sha256_before"] = sha_text(news_field_text)
        plan["news_field_sha256_after"] = sha_text(base_news)
        self.o2_plan = plan
        self.ev["o2prime"] = plan
        return base_news, facts_for_news, overlay

    # ---- R4(入力側の範囲正規化)/ J2(出力側) ----
    def normalize_inputs(self, storyline: str, news_text: str):
        s2, n2 = normalize_ranges(storyline), normalize_ranges(news_text)
        self.ev["j2"]["r4_input_changed"] = (s2 != storyline) or (n2 != news_text)
        return s2, n2

    def normalize_output(self, text: str, stage: str):
        new, n = normalize_ranges_counted(text)
        d = self.ev["j2"]["output_normalized"]
        d[stage] = d.get(stage, 0) + n
        return new, n

    # ---- 保持Gate / M2 ----
    def set_m2_context(self, r0_clean: str, news_text: str) -> None:
        if self.active:
            self.m2ctx = {"r0_text": r0_clean, "news_plain": P.strip_marks(w1.strip_tags(news_text))}

    def missing(self, text: str, stage: str, *, m2: bool = False) -> list:
        """Eの保持不足(+m2=Trueなら新規数値)のリスト。active=Falseなら常に[]。stage単位で1回目→再実行後の順に記録する。"""
        if not self.active:
            return []
        r = check_retention(text, self.gate_E, self.approx)
        miss = list(r["missing"])
        rec = self.ev["retention"].setdefault(stage, {})
        second = "missing_first" in rec
        if m2 and self.m2ctx:
            new = new_numbers(text, self.m2ctx["r0_text"], self.m2ctx["news_plain"])
            self.ev["new_numbers"].setdefault(stage, {})["after" if second else "first"] = new
            miss += [{"news_surface": "NEW:" + x} for x in new]
        rec["missing_after" if second else "missing_first"] = [e["news_surface"] for e in miss]
        if not second:
            rec["detail_first"] = r["detail"]
        return miss

    def retention_note(self, missing: list) -> str:
        return retention_note(missing)

    def mark(self, stage: str, **kv) -> None:
        self.ev["retention"].setdefault(stage, {}).update(kv)

    def write_evidence(self, out_dir: str | None = None, extra: dict | None = None) -> dict:
        ev = dict(self.ev)
        ev.update(extra or {})
        ev["written"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        wj(os.path.join(out_dir or self.out_dir, "ja_writer", "numeric_retention.json"), ev)
        return ev


# ======================================================================================================
# 英訳(Std/Adv)の数値照合: 観察のみのWARN(Gate化しない。承認事項外)
# ======================================================================================================
def observe_en(out_dir: str, ctx: "NumericRetention | None" = None) -> dict:
    """完成したEN Std(a2)/Adv(b1b)のarticle.mdで、E(gate+observe)の各数値が英語に現れるかを観察する(WARNのみ・例外を外へ出さない)。"""
    res = {"levels": {}, "warn": []}
    try:
        ctx = ctx or NumericRetention.from_out_dir(out_dir)
        res["mode"] = ctx.mode
        cands = list((ctx.E_info or {}).get("candidates") or []) if ctx.mode in ("field_ok", "field_observe_only") else []
        for lvl, rel in (("EN_Std", "a2/article.md"), ("EN_Adv", "b1b/article.md")):
            p = os.path.join(out_dir, rel)
            if not os.path.exists(p):
                continue
            text = rdt(p)
            row = {}
            for c in cands:
                r = en_present(c["news_surface"], text, c.get("unit_hint", ""))
                row[c["news_surface"]] = r
                if r is False:
                    res["warn"].append(f"[WARN][numeric_retention][{lvl}] E数値『{c['news_surface']}』が英語本文で確認できません(観察のみ・Gate化なし)")
            res["levels"][lvl] = row
            res.setdefault("wave_dash_in_en", {})[lvl] = bool(re.search(r"\d\s*[〜～~]\s*\d", text))
    except Exception as exc:  # noqa: BLE001 観察は本線を止めない
        res["observation_error"] = f"{type(exc).__name__}: {exc}"
    try:
        wj(os.path.join(out_dir, "ja_writer", "numeric_retention_en_observation.json"), res)
    except OSError as exc:
        res["write_error"] = str(exc)
    for w in res["warn"]:
        print(w)
    return res
