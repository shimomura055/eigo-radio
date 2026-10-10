# -*- coding: utf-8 -*-
"""er053_b3_deterministic_producer_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C4(2026-10-10、ユーザー確定 APPROVED_FOR_PRODUCTION)。
正式 annotated B3 producer = D-det v2 + 決定論assembler(LLM call 0、¥0/記事)。

B3のPrompt/schemaは不変。B3が選んだFact ID(storyline_b3/fact_selection_evidence.json の selected_fact_ids)から、台帳
(research_ledger/verified_fact_ledger.txt。numeric_value / date_or_period / notes_for_writer / ambiguity_note 欄を含む)を使い、
Writer入力briefを**決定論で**組み立てる:
  - Fact欄 = D-full規則(claim + scope/conditions由来の限定を括弧で付す。1Fact1行。selected_fact_ids順)
  - 注意書き(notes_for_writer / ambiguity_note と、指示調のscope/conditions)は別欄「制約ブロック」(storyline_b3/writer_constraints.txt)へ逐語複写
  - AMBIGUOUS Factは固定限定文「この点は確定していない。」を付与
  - 【事実N】は決定論付与、【中核数値】【周辺数値】は D-det v2(単位換算表込み、対象=組立済みFact行+Storyline行)
出力(契約: er053_b3_annotation_contract_01 と DESIGN_03 3節):
  storyline_b3/selected_brief_annotated.md / annotation.json(annotator=DETERMINISTIC) / annotation_manifest.json(producer="deterministic_v2")
  storyline_b3/writer_constraints.txt(制約ブロック。空なら空ファイル。manifest.writer_constraints_sha256 で束縛)
  storyline_b3/fact_selection_evidence.json の selected_fact_brief_text 欄(維持。中身は決定論出力。元のB3 LLM文は b3_llm_selected_fact_brief_text へ退避)

移植契約: 下の「移植元」ブロックは Trial 3ファイルの該当constant/関数を**ソース逐語**で移植した(関数本体のbyte-identicalをtestで機械証明):
  b3sep_build_01.py(ROOTFIX-01 assembler: assemble_D ほか。assemble_Aprime[A'腕]は不要につき移植せず)
  b3r2_rank_02.py(ROOTFIX-02 D-det v2: 抽出regex・単位換算・適格判定・上限・優先規則・insert_marks。validate_number_ranks[LLM出力検証]は不要につき移植せず)
  b3r2_eval_01.py(line_texts / ddet / orig_surface / build_annotated)
Trial moduleはimportしない(同一性はtest内でのみTrial moduleを読んで機械証明)。Trial内の `B1.` `RK.` 参照は本module内の同名namespaceで解決する。
禁止: 注記なしB3の入力・fallback・runtime switch・CLI引数・環境変数。Lane B(LLM注記)・Trial checker(b3_annotation_check_01)はimportしない。
既存注記検査(b3_annotation_check_01)の同等規則は本module内の run_internal_checks で代替する(a_alignment/b_numbers/c_core_peripheral/d_tags/e_sidecar)。
"""
from __future__ import annotations

import datetime
import hashlib
import inspect
import json
import os
import re
import types
import unicodedata

import er053_family_x_factlock_ja_writer_01 as w1
from er053_b3_annotation_contract_01 import (ANNOTATED_NAME, BRIEF_NAME, CONSTRAINTS_NAME, LEDGER_REL, MANIFEST_NAME,
                                             MANIFEST_SCHEMA_VERSION, SIDECAR_NAME)

PRODUCER = "deterministic_v2"
RULE_VERSION = "deterministic_v2.0"
ANNOTATOR = "DETERMINISTIC"
EVIDENCE_NAME = "fact_selection_evidence.json"

# ======================================================================================================
# 移植元: er052_output/b3_fact_instruction_separation_trial_01/b3sep_build_01.py (ROOTFIX-01 assembler)
# ======================================================================================================
LINK = re.compile(r"\s*\(\[[^\]]*\]\(https?://[^)]*\)\)|\s*\(https?://[^)]*\)")


HEAD = re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$")


FLD = re.compile(r"^  (\w+): (.*)$")


IMP = re.compile(r"(ないこと|こと[。]?$|書かない|断定しない|付け加えない|補わない|混同しない|扱わない|分けて扱う|区別する|区別して|"
                 r"として扱う|言い換えない|一般化しない|帰属させない|結び付けない|同一視しない|しない[。]?$|とは書|と断定|"
                 r"位置付ける|してはならない|使わない|転用しない|比較はしない)")


AMB_QUALIFIER = "この点は確定していない。"          # R1: AMBIGUOUS Factの決定論の固定限定文


AMB_TAG_ORIGINAL = "[AMBIGUOUS - 断定禁止、曖昧さを保持すること] "   # Dtag変種(台帳タグ原文保持。Facts側に指示調が入るため比較用)


CONS_HEADING = "Writerへの注意(事実ではありません)："


def clean(s):
    return LINK.sub("", s or "").strip()


def parse_ledger(text):
    facts, order, cur = {}, [], None
    for ln in text.replace("\r\n", "\n").split("\n"):
        m = HEAD.match(ln)
        if m:
            cur = m.group(2)
            facts[cur] = {"tag": m.group(1), "ambiguous": m.group(1).startswith("AMBIGUOUS"), "claim": m.group(3)}
            order.append(cur)
            continue
        m = FLD.match(ln)
        if m and cur:
            facts[cur][m.group(1)] = m.group(2)
    return facts, order


def _strip_period(s):
    return clean(s).rstrip("。 ")


def _ordered(order, selected_ids, how):
    """並び順。既定 how='selected'=B3の選定順(selected_fact_ids順)。'ledger'=台帳順。"""
    if how == "ledger":
        return [f for f in order if f in set(selected_ids)]
    return [f for f in selected_ids if f in set(order)]


def compose_news_field(facts_text, constraints_text):
    """R0ニュース欄(=Writerが読む文字列)の唯一の組立。Facts部(注記済みでも可)+制約ブロック。制約が空ならFacts部のみ。"""
    if not constraints_text:
        return facts_text
    return facts_text.rstrip("\n") + "\n\n" + constraints_text.rstrip("\n") + "\n"


def build_constraints(items):
    """items = [(label, text), ...]。label は 'N' 付き表記済みの文頭(例 '事実2について')。ID・【】は使わない(R5)。"""
    if not items:
        return ""
    return CONS_HEADING + "\n" + "\n".join(f"- {lab}：{t}" for lab, t in items) + "\n"


def assemble_D(ledger_text, selected_ids, storyline, variant="Dmin", order_how="selected"):
    facts, order = parse_ledger(ledger_text)
    sel = _ordered(order, selected_ids, order_how)
    lines, cons, moved, amb_info = [], [], [], []
    for n, fid in enumerate(sel, 1):
        f = facts[fid]
        body = clean(f["claim"])
        if f["ambiguous"]:
            body = (AMB_TAG_ORIGINAL if variant == "Dtag" else "") + body + ("" if variant == "Dtag" else AMB_QUALIFIER)
            amb_info.append({"fact_id": fid, "n": n})
        if variant == "Dfull":
            parts = []
            for key, lab in (("scope", "範囲"), ("conditions", "条件")):
                v = _strip_period(f.get(key, ""))
                if not v:
                    continue
                if IMP.search(v):
                    cons.append((f"事実{n}の{lab}について", clean(f[key])))
                    moved.append({"fact_id": fid, "n": n, "field": key, "text": v})
                else:
                    parts.append(f"{lab}：{v}")
            if parts:
                body += "（" + "。".join(parts) + "）"
        lines.append(f"- {body}")
        if f.get("notes_for_writer"):
            cons.append((f"事実{n}について", clean(f["notes_for_writer"])))
        if f.get("ambiguity_note"):
            cons.append((f"事実{n}について", clean(f["ambiguity_note"])))
    facts_text = "\n".join(lines) + "\n"
    cons_text = build_constraints(cons)
    brief_md = "# Selected Fact Brief\n\n## Storyline\n" + storyline + "\n\n## Selected Facts\n" + facts_text
    return {"variant": variant, "ordered_ids": sel, "facts_text": facts_text, "constraints_text": cons_text,
            "news_field": compose_news_field(facts_text, cons_text), "brief_md": brief_md,
            "constraint_items": cons, "moved_to_constraints": moved, "ambiguous_facts": amb_info,
            "evidence": {"selected_storyline": storyline, "selected_fact_ids": sel, "selected_fact_brief_text": facts_text,
                         "writer_constraints_text": cons_text, "writer_news_field_text": compose_news_field(facts_text, cons_text)}}

B1 = types.SimpleNamespace(clean=clean, parse_ledger=parse_ledger, assemble_D=assemble_D, IMP=IMP,
                           compose_news_field=compose_news_field, build_constraints=build_constraints)   # 移植元コード内の `B1.` 参照の解決先

# ======================================================================================================
# 移植元: er052_output/b3_rootfix_trial_02/b3r2_rank_02.py (ROOTFIX-02 D-det v2。単位換算表 canon_unit / _bp_to_pp 含む)
# ======================================================================================================
HEDGE_PRE = r"(?:約|およそ|ほぼ|最大で|最大|少なくとも|数)?"


HEDGE_POST = r"(?:超|以上|以下|未満|前後|近く)?"


UNIT = r"(?:ベーシスポイント|ポイント|パーセント|％|%|ドル|円|ユーロ|バレル|リットル|万|億|兆|千|件|人|社|倍|機|隻|台|施設|カ国|か国|ヶ国|基|周年|年|カ月|か月|ヶ月|日間|時間|分|週間|週|回|度|位|点|割|歳|本|個|枚|名|店|校|軒|世帯|戸|便|票|カ所|か所|ヶ所|品目|種類|種|冊|部)*"


NUM = r"\d[\d,]*(?:\.\d+)?"


NUM_C = NUM + r"(?:[万億兆]" + NUM + r")*"          # A2: 合成数 1万5000


CUR_PRE = r"[$¥€£]?"


QUARTER = r"(?:\d{4}年)?第\d+四半期"                  # A2


DATE_FULL = r"\d{4}年\d{1,2}月\d{1,2}日(?:(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?)?"


DATE_YM = r"\d{4}年\d{1,2}月"


DATE_MD = r"\d{1,2}月\d{1,2}日(?:(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?)?"


MONTH_ONLY = r"\d{1,2}月(?!\d)"                      # A2: 9月


DAY_ONLY = r"\d{1,2}日(?!間|あたり|当たり|につき)"      # A2: 翌14日の「14日」(日間・1日あたりは除く)


TIME = r"(?:午前|午後)?\d{1,2}時(?!間)(?:\d{1,2}分)?|\d{1,2}:\d{2}"   # A2


RANGE = NUM + r"\s*[～〜~\-–]\s*" + NUM


IDENT = r"\d{1,2}:\d{2}-[A-Za-z]{2}-\d+"                    # 事件番号(1:26-cv-08892)は識別子=name_embedded


ISO = r"\d{4}-\d{1,2}-\d{1,2}"                              # 2026-10-08


DATE_RANGE = r"\d{1,2}月\d{1,2}日?\s*[～〜~\-–]\s*(?:\d{1,2}月)?\d{1,2}日"      # 10月27~28日


RATIO = r"\d+対\d+"                                                 # 12対0(票数など)


NAME_EMB = r"[A-Z][A-Za-z]+ " + r"\d{1,4}(?!\d|\.\d|,\d|ドル|円|%|％|万|億|兆|件|人|社|倍|年|月|日|台|機|名|分|時)"   # Fall 2026 / Hyperion 12 (名称の一部の番号)


PERDAY = r"(?P<perday>\d{1,2})(?=日(?:あたり|当たり|につき))"   # 「1日あたり」の1は抽出しない(毎日の意味)


SURF_RE = re.compile("|".join([
    PERDAY, IDENT, NAME_EMB, QUARTER, ISO, DATE_FULL, DATE_RANGE, RATIO, DATE_YM, DATE_MD, MONTH_ONLY, DAY_ONLY, TIME,
    HEDGE_PRE + CUR_PRE + r"(?:" + RANGE + r")" + UNIT + HEDGE_POST,
    r"第" + NUM + r"[回条号章]",
    HEDGE_PRE + CUR_PRE + NUM_C + UNIT + HEDGE_POST,
]))


DEFAULT_KINDS = ("magnitude", "date_time", "range", "year", "ordinal", "name_embedded")


DIGITS = "0123456789"


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def dec(s):
    """10進比較用の正規化(1,500 -> 1500, 4.00 -> 4, 04 -> 4)。"""
    s = s.replace(",", "")
    try:
        f = float(s)
    except ValueError:
        return s
    return str(int(f)) if f == int(f) else repr(f)


def find_all(norm, s):
    """norm(NFKC済)中の s(NFKC済)の出現位置リスト。数字で始まる表記は直前が数字・'.'・','でないこと、
    数字で終わる表記は直後が数字でなく、'.'/',' + 数字 でもないこと。(1.5%の中の5%、13日の中の3日、2,300件の中の300、5.5の中の5 を除く)"""
    out, start = [], 0
    if not s:
        return out
    while True:
        p = norm.find(s, start)
        if p < 0:
            break
        e = p + len(s)
        ok = True
        if s[0] in DIGITS and p > 0 and (norm[p - 1] in DIGITS or norm[p - 1] in ".,"):
            ok = False
        if ok and s[-1] in DIGITS and e < len(norm):
            c = norm[e]
            if c in DIGITS or (c in ".," and e + 1 < len(norm) and norm[e + 1] in DIGITS):
                ok = False
        if ok:
            out.append(p)
        start = p + 1
    return out


def contains(hay, s):
    return bool(find_all(nfkc(hay), nfkc(s)))


def _compound_value(t):
    """1万5000 -> 15000(合成数の10進値)。合成数でなければ None。"""
    m = re.fullmatch(r"(\d[\d,]*(?:\.\d+)?)([万億兆])(\d[\d,]*(?:\.\d+)?)", t)
    if not m:
        return None
    mult = {"万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}[m.group(2)]
    v = float(m.group(1).replace(",", "")) * mult + float(m.group(3).replace(",", ""))
    return dec(repr(v))


def value_of(t):
    """数値表記の値(万・億・兆の倍率つき。2億5,000万 -> 250000000, 1万5000 -> 15000, 200万 -> 2000000)。数字が無ければ None。"""
    toks = re.findall(r"(\d[\d,]*(?:\.\d+)?)([万億兆]?)", nfkc(t))
    if not toks:
        return None
    mult = {"": 1, "万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}
    v = sum(float(n.replace(",", "")) * mult[m] for n, m in toks)
    return dec(repr(v))


def surface_kind(surf):
    t = nfkc(surf)
    if re.fullmatch(IDENT, t) or re.fullmatch(NAME_EMB, t):
        return "name_embedded"
    if re.fullmatch(ISO, t):
        return "date_time"
    if re.fullmatch(RATIO, t):
        return "magnitude"
    if re.fullmatch(DATE_RANGE, t):
        return "date_time"
    if re.search(r"第\d+四半期", t):
        return "date_time"
    if re.search(r"第\d+[回条号章]", t):
        return "ordinal"
    if re.search(r"\d+月", t) or re.fullmatch(r"(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?|\d{1,2}:\d{2}|\d{1,2}日", t):
        return "date_time"
    if re.fullmatch(r"\d{4}年", t):
        return "year"
    if re.search(RANGE, t):
        return "range"
    return "magnitude"


def unit_of(surf):
    """単位(ヘッジ語・通貨前置・数字を除いた残り)。概念キー用(仕様3-3: 台帳IDと単位を含める)。"""
    t = nfkc(surf)
    t = re.sub("^" + HEDGE_PRE, "", t)
    t = re.sub(HEDGE_POST + "$", "", t)
    return canon_unit(re.sub(r"[\s$¥€£]|" + NUM, "", t))     # V2-4


def canon_unit(u):
    """V2-1 単位換算表(決定論)。ポイント系(ベーシスポイント・パーセントポイント・%ポイント・ポイント)は同一単位<pp>、パーセントは%。"""
    for a in ("ベーシスポイント", "パーセントポイント", "%ポイント", "ポイント"):
        u = u.replace(a, "\x00")
    u = u.replace("パーセント", "%")
    return u.replace("\x00", "<pp>")


def _bp_to_pp(v):
    """V2-2 ベーシスポイント値 -> パーセントポイント値(10進。25 -> 0.25)。"""
    from decimal import Decimal
    return dec(str(Decimal(v) / 100))


def main_numbers(surf, kind):
    """概念キー用の主数字(主数字=表記末尾の数字列。合成数は値に展開。dateは年/月/日の存在要素、時刻・四半期は別キー)。"""
    t = nfkc(surf)
    if kind == "date_time":
        iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
        if iso:
            return ("D", iso.group(1), dec(iso.group(2)), dec(iso.group(3)))
        q = re.search(r"(?:(\d{4})年)?第(\d+)四半期", t)
        if q:
            return ("Q", q.group(1), q.group(2))
        y = re.search(r"(\d{4})年", t); m = re.search(r"(\d{1,2})月", t); d = re.search(r"月(\d{1,2})|(\d{1,2})日", t)
        if y or m or d:
            return ("D", y.group(1) if y else None, dec(m.group(1)) if m else None, dec(d.group(1) or d.group(2)) if d else None)
        tm = re.search(r"(\d{1,2})時(?:(\d{1,2})分)?|(\d{1,2}):(\d{2})", t)
        if tm:
            h = tm.group(1) or tm.group(3); mi = tm.group(2) or tm.group(4)
            return ("T", dec(h), dec(mi) if mi else None)
        return ("D", None, None, None)
    if kind in ("year", "ordinal", "name_embedded"):
        return (kind[0].upper(), tuple(dec(x) for x in re.findall(NUM, t)))
    nums = re.findall(NUM_C, t)
    if kind == "range":
        rr = re.findall(NUM, t)
        return ("R", tuple(dec(x) for x in rr[:2]))
    if not nums:
        return ("M", None)
    # 主数字=表記末尾の数字列(仕様3-5-1)。倍率(万・億・兆)がつく場合は倍率適用後の値(比較は台帳側も同じ展開を使う)
    mu = re.search(r"((?:\d[\d,]*(?:\.\d+)?[万億兆]?)+)(?!.*\d)", t)
    val = value_of(mu.group(1)) if mu else dec(re.findall(NUM, nums[-1])[-1])
    if "ベーシスポイント" in t and val is not None:       # V2-2
        val = _bp_to_pp(val)
    return ("M", val)


def extract_surfaces(text):
    out = []
    for m in SURF_RE.finditer(nfkc(text)):
        if m.group("perday"):
            continue
        s = m.group(0).strip()
        if re.search(r"\d", s):
            out.append(s)
    return out


def _date_expr_first(text):
    """先頭の日付表現 -> (年|None, 月, 日|None) 。ISO形・和文(年月日/年月/月日)。"""
    t = nfkc(text or "")
    cands = []
    for pat, f in ((r"(\d{4})-(\d{1,2})-(\d{1,2})", lambda m: (m.group(1), dec(m.group(2)), dec(m.group(3)))),
                   (r"(\d{4})年(\d{1,2})月(\d{1,2})日", lambda m: (m.group(1), dec(m.group(2)), dec(m.group(3)))),
                   (r"(\d{4})年(\d{1,2})月", lambda m: (m.group(1), dec(m.group(2)), None)),
                   (r"(?<![\d年])(\d{1,2})月(\d{1,2})日", lambda m: (None, dec(m.group(1)), dec(m.group(2))))):
        m = re.search(pat, t)
        if m:
            cands.append((m.start(), f(m)))
    return min(cands, key=lambda x: x[0])[1] if cands else None


def _numbers_of(text):
    """表記集合(10進)。numeric_scope括弧内は除く。合成数は値も追加。"""
    t = nfkc(text or "")
    t = re.sub(r"\(numeric_scope:[^)]*\)", "", t)
    out = {dec(x) for x in re.findall(NUM, t)}
    for c in re.findall(r"(?:\d[\d,]*(?:\.\d+)?[万億兆]?)+", t):
        v = value_of(c)
        if v:
            out.add(v)
    for c in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*ベーシスポイント", t):      # V2-3
        out.add(_bp_to_pp(dec(c)))
    return out


def ledger_flags(facts):
    """仕様3-5-2の代替規則の発動条件(台帳全体で欄が1件も無いか)。"""
    return {"has_numeric_value": any(f.get("numeric_value") for f in facts.values()),
            "has_date_or_period": any(f.get("date_or_period") for f in facts.values())}


def eligible(kind, key, fact, lflags=None):
    """適格判定(仕様3-5-2)。lflags の欄が台帳に1件も無い場合のみ、Fact本文(ID行)で代替する。"""
    lflags = lflags or {"has_numeric_value": True, "has_date_or_period": True}
    if kind in ("year", "ordinal", "name_embedded"):
        return False
    if kind == "date_time":
        if key[0] != "D":
            return False
        if lflags["has_date_or_period"]:
            d = _date_expr_first(fact.get("date_or_period"))
        else:
            d = _date_expr_first(B1.clean(fact.get("claim", "")))
        if not d or key[2] is None:
            return False
        y, m, dd = key[1], key[2], key[3]
        if y is not None and (d[0] is None or y != d[0]):
            return False
        if m != d[1]:
            return False
        if dd is not None and (d[2] is None or dd != d[2]):
            return False
        return True
    src = fact.get("numeric_value") if lflags["has_numeric_value"] else B1.clean(fact.get("claim", ""))
    if not src:
        return False
    nums = _numbers_of(src)
    ms = [x for x in (key[1] if key[0] == "R" else (key[1],)) if x is not None]
    return bool(ms) and all(x in nums for x in ms)


def cap_of(n):
    return max(3, min(6, n // 2))


def concept_key(fact_id, kind, key, surf):
    """概念キー(仕様3-3): Fact ID + 種類 + 主数字 + 単位。日付は同一Fact内で包含関係(9月 ⊂ 2026年9月13日)なら同じ概念に束ねる(別関数で後処理)。"""
    if kind == "magnitude" or kind == "range":
        return (fact_id, kind, key, unit_of(surf))
    return (fact_id, kind, key)


def _merge_date_concepts(items):
    """同一Fact内の日付表記で、含まれる側(要素が全て一致して少ない側)を長い表記の概念へ束ねる。"""
    by_fact = {}
    for it in items:
        if it["kind"] == "date_time" and it["key"][0] == "D":
            by_fact.setdefault(it["fact_id"], []).append(it)
    for fid, its in by_fact.items():
        for a in its:
            ka = a["key"]
            for b in its:
                kb = b["key"]
                if a is b or sum(x is not None for x in kb[1:]) <= sum(x is not None for x in ka[1:]):
                    continue
                if all(ka[i] is None or ka[i] == kb[i] for i in (1, 2, 3)):
                    a["ckey"] = b["ckey"]
                    break


def derive_ranks(ledger_text, ordered_ids, storyline, surfaces_by_fact=None, with_story=False, text_by_fact=None):
    """決定論の導出。surfaces_by_fact={fact_id:[surface,...]} を与えればその表記を使う(LLM出力の規則検証用)。
    与えなければ各Fact claimからregexで抽出(D-det腕)。
    戻り値: {"items":[{fact_id,surface,kind,key,role,concept,eligible,ckey}],n_concepts,cap,capped_off}"""
    facts, _ = B1.parse_ledger(ledger_text)
    lf = ledger_flags(facts)
    items = []
    for fid in ordered_ids:
        f = facts[fid]
        srfs = surfaces_by_fact.get(fid, []) if surfaces_by_fact is not None else list(dict.fromkeys(extract_surfaces((text_by_fact or {}).get(fid) or B1.clean(f["claim"]))))
        for s in srfs:
            k = surface_kind(s)
            key = main_numbers(s, k)
            items.append({"fact_id": fid, "surface": s, "kind": k, "key": key, "ckey": concept_key(fid, k, key, s)})
    if with_story:
        # Storylineにだけ現れる表記(要約で表記が変わる等)も印の対象。同じ(種類,主数字)の表記を持つ最初のFactへ紐付け、無ければ未紐付け(_STORY)=中核にしない
        have = {nfkc(it["surface"]) for it in items}
        for s_ in dict.fromkeys(extract_surfaces(storyline or "")):
            if nfkc(s_) in have:
                continue
            k_ = surface_kind(s_)
            key_ = main_numbers(s_, k_)
            m_ = next((it for it in items if it["kind"] == k_ and it["key"] == key_), None)
            fid_ = m_["fact_id"] if m_ else "_STORY"
            items.append({"fact_id": fid_, "surface": s_, "kind": k_, "key": key_, "ckey": concept_key(fid_, k_, key_, s_), "story_only": True})
    _merge_date_concepts(items)
    # 概念(仕様3-3/3-1): 同じ表記(NFKC)は全Factで1概念 / 同じFactで概念キー一致 / 同じFactで一方が他方に(境界つきで)含まれる表記 は1概念に束ねる
    parent = list(range(len(items)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_, b_ = items[i], items[j]
            si, sj = nfkc(a_["surface"]), nfkc(b_["surface"])
            same_fact = a_["fact_id"] == b_["fact_id"]
            if si == sj or (same_fact and (a_["ckey"] == b_["ckey"] or contains(si, sj) or contains(sj, si))):
                parent[find(i)] = find(j)
    story = nfkc(storyline or "")
    concepts = {}
    for i, it in enumerate(items):
        r = find(i)
        c = concepts.setdefault(r, {"kind": it["kind"], "elig": False, "in_story": False, "first": i, "name": "|".join(map(str, it["ckey"])), "len": 0})
        if len(nfkc(it["surface"])) > c["len"]:
            c["kind"], c["len"] = it["kind"], len(nfkc(it["surface"]))   # 概念の種類=最も長い表記の種類
        it["_root"] = r
        if eligible(it["kind"], it["key"], facts.get(it["fact_id"], {}), lf):
            c["elig"] = True
        if contains(story, it["surface"]):
            c["in_story"] = True
    counted = [k for k, c in concepts.items() if c["kind"] in ("magnitude", "date_time", "range")]
    cap = cap_of(len(counted))

    def prio(k):
        c = concepts[k]
        if c["kind"] == "date_time":
            return (2, c["first"])
        return (0 if c["in_story"] else 1, c["first"])
    order = sorted([k for k, c in concepts.items() if c["elig"] and c["kind"] in ("magnitude", "range", "date_time")], key=prio)
    core = set(order[:cap])
    capped_off = [concepts[k]["name"] for k in order[cap:]]
    for it in items:
        it["role"] = "core" if it["_root"] in core else "peripheral"
        it["eligible"] = concepts[it["_root"]]["elig"]
        it["concept"] = concepts[it["_root"]]["name"]
        it["ikey"] = "|".join(map(str, it["ckey"]))
    return {"items": items, "n_concepts": len(counted), "cap": cap, "capped_off": capped_off,
            "ledger_flags": lf}


MARK = {"core": "【中核数値】", "peripheral": "【周辺数値】"}


def _norm_with_map(text):
    """NFKC正規化文字列と、正規化後index -> 原文index の対応(1文字ずつ正規化するため単調)。"""
    norm, idx = [], []
    for i, ch in enumerate(text):
        n = unicodedata.normalize("NFKC", ch)
        for c in n:
            norm.append(c); idx.append(i)
    return "".join(norm), idx


def insert_marks(text, items):
    """決定論のタグ挿入。items=[{surface,role}]。原文(text)は一切改変せず、表記の末尾へ印だけを足す。
    A1: 数字境界つき一致(1.5%の中の5%には付けない)。長い表記を優先し、すでに印が付いた範囲と重なる出現はスキップ。
    同じ表記が複数itemにあれば、coreが1つでもあればcore(同じ表記は同じ印)。"""
    norm, idx = _norm_with_map(text)
    role_of = {}
    for it in items:
        s = nfkc(it["surface"])
        if s and (role_of.get(s) != "core"):
            role_of[s] = it["role"]
    spans = []
    for s in sorted(role_of, key=lambda x: -len(x)):
        for p in find_all(norm, s):
            a, b = p, p + len(s)
            if not any(a < e and b > st for st, e, _ in spans):
                spans.append((a, b, role_of[s]))
    out, last = [], 0
    for a, b, role in sorted(spans):
        end_orig = idx[b - 1] + 1
        out.append(text[last:end_orig]); out.append(MARK[role]); last = end_orig
    out.append(text[last:])
    return "".join(out)


def strip_marks(text):
    return text.replace(MARK["core"], "").replace(MARK["peripheral"], "")

RK = types.SimpleNamespace(nfkc=nfkc, find_all=find_all, contains=contains, derive_ranks=derive_ranks, insert_marks=insert_marks,
                           strip_marks=strip_marks, _norm_with_map=_norm_with_map, extract_surfaces=extract_surfaces, cap_of=cap_of,
                           eligible=eligible, surface_kind=surface_kind, MARK=MARK)   # 移植元コード内の `RK.` 参照の解決先
NF = RK.nfkc

# ======================================================================================================
# 移植元: er052_output/b3_rootfix_trial_02/b3r2_eval_01.py (line_texts / ddet / orig_surface / build_annotated。M11/E9で使われた注記済みbrief組立)
# ======================================================================================================
BASE_VARIANT = "Dfull"      # D-base=D-full(ROOTFIX-01の事前登録規則で選択済み)


def line_texts(a):
    """組立済みFact行(Writerが読む文字列)の本文。D-fullはscope/conditions(指示調でないもの)をFact行へ移すため、数字の表記もそこから抽出する。"""
    return {fid: ln[2:] if ln.startswith("- ") else ln for fid, ln in zip(a["ordered_ids"], [x for x in a["facts_text"].split("\n") if x.strip()])}


def ddet(ledger, ids, story, assembled_text=True):
    """D-det(call 0): 決定論の表記抽出+規則導出。既定=D-base組立済みFact行+Storylineから抽出。assembled_text=Falseでclaimのみ(LLM number_ranksと同じ範囲)。"""
    ids2 = [i for i in ids if i in B1.parse_ledger(ledger)[0]]
    tb = line_texts(B1.assemble_D(ledger, ids2, story, BASE_VARIANT)) if assembled_text else None
    return RK.derive_ranks(ledger, ids2, story, with_story=True, text_by_fact=tb)


def orig_surface(text, surface):
    norm, idx = RK._norm_with_map(text)
    s = NF(surface)
    ps = RK.find_all(norm, s)
    if not ps:
        return None
    a = ps[0]
    return text[idx[a]: idx[a + len(s) - 1] + 1]


def build_annotated(ledger, ids, story, der, variant="Dmin"):
    a = B1.assemble_D(ledger, ids, story, BASE_VARIANT)
    role_s = {}
    for it in der["items"]:
        s = NF(it["surface"])
        if role_s.get(s) != "core":
            role_s[s] = it["role"]
    lines = a["facts_text"].split("\n")
    out_lines = []
    n = 0
    for ln in lines:
        if not ln.strip():
            out_lines.append(ln)
            continue
        n += 1
        fid = a["ordered_ids"][n - 1]
        body = ln[2:] if ln.startswith("- ") else ln
        its = [{"surface": it["surface"], "role": role_s[NF(it["surface"])]} for it in der["items"] if it["fact_id"] == fid]
        out_lines.append("- 【事実%d】" % n + RK.insert_marks(body, its))
    story_m = RK.insert_marks(story, [{"surface": s, "role": r} for s, r in role_s.items()])
    annotated = "# Selected Fact Brief\n\n## Storyline\n" + story_m + "\n\n## Selected Facts\n" + "\n".join(out_lines)
    # sidecar: 同じ表記(NFKC)は1項目。ledger_idsは表記を持つ全Fact。概念=derive_ranksの束ね(同表記/同Factのキー一致・包含)
    full_plain = a["brief_md"]
    nums, seen, cid = [], {}, {}
    for it in der["items"]:
        s_ = NF(it["surface"])
        cid.setdefault(it["concept"], "C%d" % (len(cid) + 1))
        if s_ in seen:
            seen[s_]["ledger_ids"] = sorted(set(seen[s_]["ledger_ids"]) | {it["fact_id"]})
            continue
        osf = orig_surface(full_plain, it["surface"]) or it["surface"]
        seen[s_] = {"surface": osf, "kind": it["kind"], "class": role_s[s_], "concept": cid[it["concept"]], "ledger_ids": [it["fact_id"]], "role": ""}
        nums.append(seen[s_])
    sidecar = {"slug": "b3r2", "annotator": "DETERMINISTIC", "spec_sha256": None, "brief_sha256": hashlib.sha256(a["brief_md"].encode("utf-8")).hexdigest(),
               "facts": [{"n": i + 1, "ledger_ids": [fid]} for i, fid in enumerate(a["ordered_ids"])], "numbers": nums, "unmapped_claims": [], "annotation_notes": []}
    return a["brief_md"], annotated, sidecar

# ======================================================================================================
# ここから本C4で新規に書いたProduction code(上の「移植元」ブロックは逐語。以下は移植ではない)
# ======================================================================================================
class AnnotationProducerError(RuntimeError):
    """producer失敗(入力欠落・ID不整合・内部検査FAIL等)。契約違反と同じく課金前STOP(技術QA)。"""

    def __init__(self, problems: list):
        self.problems = problems
        super().__init__("[STOP] ANNOTATION_PRODUCER_FAILED: " + "; ".join(problems[:6]))


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_text(s: str) -> str:
    return _sha(s.encode("utf-8"))


_PORTED_NAMES = (
    # b3sep_build_01(assembler)
    "LINK", "HEAD", "FLD", "IMP", "AMB_QUALIFIER", "AMB_TAG_ORIGINAL", "CONS_HEADING", "clean", "parse_ledger", "_strip_period",
    "_ordered", "compose_news_field", "build_constraints", "assemble_D",
    # b3r2_rank_02(D-det v2)
    "HEDGE_PRE", "HEDGE_POST", "UNIT", "NUM", "NUM_C", "CUR_PRE", "QUARTER", "DATE_FULL", "DATE_YM", "DATE_MD", "MONTH_ONLY", "DAY_ONLY",
    "TIME", "RANGE", "IDENT", "ISO", "DATE_RANGE", "RATIO", "NAME_EMB", "PERDAY", "SURF_RE", "DEFAULT_KINDS", "DIGITS", "nfkc", "dec",
    "find_all", "contains", "_compound_value", "value_of", "surface_kind", "unit_of", "canon_unit", "_bp_to_pp", "main_numbers",
    "extract_surfaces", "_date_expr_first", "_numbers_of", "ledger_flags", "eligible", "cap_of", "concept_key", "_merge_date_concepts",
    "derive_ranks", "MARK", "_norm_with_map", "insert_marks", "strip_marks",
    # b3r2_eval_01
    "BASE_VARIANT", "line_texts", "ddet", "orig_surface", "build_annotated")


def rules_sha_table() -> dict:
    """移植した規則(constant・regex・換算表・関数ソース)のsha256表(runtime evidence・委任ログ用)。"""
    g = globals()
    out = {}
    for name in _PORTED_NAMES:
        obj = g[name]
        if inspect.isfunction(obj):
            out[name] = _sha_text(inspect.getsource(obj))
        else:
            out[name] = _sha_text(getattr(obj, "pattern", None) or json.dumps(obj, ensure_ascii=False, sort_keys=True, default=repr))
    return out


def rules_sha256() -> str:
    return _sha_text(json.dumps({"rule_version": RULE_VERSION, "table": rules_sha_table()}, sort_keys=True))


def assemble_plain(ledger_text: str, ids: list, story: str) -> dict:
    """契約のV10(DETERMINISTIC)が再導出に使う: 台帳+選択ID+Storylineから D-full 組立結果(Fact行・制約ブロック)を返す。"""
    return assemble_D(ledger_text, ids, story, BASE_VARIANT)


def _check_inputs(ledger_text: str, ids, story, brief_story: str) -> list:
    probs = []
    facts, _order = parse_ledger(ledger_text)
    if not facts:
        probs.append("ledger has no parsable facts")
    if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
        probs.append("selected_fact_ids must be a non-empty list of strings")
        return probs
    if len(set(ids)) != len(ids):
        probs.append(f"selected_fact_ids has duplicates: {ids}")
    unknown = [i for i in ids if i not in facts]
    if unknown:
        probs.append(f"selected_fact_ids not in ledger (REJECTED or unknown): {unknown}")
    if not isinstance(story, str) or not story.strip():
        probs.append("selected_storyline missing")
    elif story != brief_story:
        probs.append("evidence.selected_storyline != Storyline of selected_brief.md")
    return probs


def run_internal_checks(plain: dict, annotated_md: str, sidecar: dict, der: dict, story: str, ledger_text: str) -> dict:
    """既存注記検査(b3_annotation_check_01)の5区分に対応する決定論検査(Trial scriptはimportしない)。
    戻り値 {a_alignment,b_numbers,c_core_peripheral,d_tags,e_sidecar: {"status": PASS|FAIL, "problems": [...]}}。"""
    res = {k: [] for k in ("a_alignment", "b_numbers", "c_core_peripheral", "d_tags", "e_sidecar")}
    try:
        story_m, facts_m = w1.parse_brief_md(annotated_md)
    except ValueError as e:
        res["a_alignment"].append(f"parse_brief_md failed: {e}")
        return {k: {"status": "FAIL" if v else "PASS", "problems": v} for k, v in res.items()}
    plain_lines = [x for x in plain["facts_text"].split("\n") if x.strip()]
    ann_lines = [x for x in facts_m.split("\n") if x.strip()]
    # a_alignment: 注記(タグ・印)を除くと組立済みの原文と厳密一致
    if w1.strip_tags(story_m) != story:
        res["a_alignment"].append("Storyline differs after removing marks")
    if len(plain_lines) != len(ann_lines):
        res["a_alignment"].append(f"fact line count {len(ann_lines)} != assembled {len(plain_lines)}")
    else:
        for i, (p, a) in enumerate(zip(plain_lines, ann_lines), 1):
            m = w1.FACT_LINE_RE.match(a)
            body = w1.strip_tags(m.group(2)) if m else None
            if body is None or "- " + body != p:
                res["a_alignment"].append(f"fact {i} differs from assembled text after removing tag/marks")
    # d_tags: 【事実N】は1..Kの連番で各行頭に1つだけ。変形タグなし。数値印は標準形のみ
    nums = [int(m.group(1)) for m in (w1.FACT_LINE_RE.match(a) for a in ann_lines) if m]
    if len(nums) != len(ann_lines) or nums != list(range(1, len(ann_lines) + 1)):
        res["d_tags"].append(f"fact tags not 1..K contiguous on every line: {nums}")
    if len(w1.BROAD_TAG_RE.findall(facts_m)) != len(w1.TAG_RE.findall(facts_m)) or len(w1.TAG_RE.findall(facts_m)) != len(ann_lines):
        res["d_tags"].append("unexpected tag forms in Selected Facts")
    other = [x for x in re.findall(r"【[^】\n]*数値[^】\n]*】", story_m + "\n" + facts_m) if not w1.MARK_RE.fullmatch(x)]
    if other:
        res["d_tags"].append(f"non-standard number marks: {other[:3]}")
    # b_numbers: 抽出された数字表記は全て(正規化後の)注記本文で印付き
    whole_n = nfkc(story_m + "\n" + facts_m)
    for it in der["items"]:
        s = nfkc(it["surface"])
        if not any(s + MARK[r] in whole_n for r in ("core", "peripheral")):
            res["b_numbers"].append(f"extracted number {it['surface']!r} ({it['fact_id']}) has no mark in the annotated text")
    # b_numbers(続き): 全出現位置の印を再計算と照合(印の付け漏れ・余分な印・印の取り違えを検出。表記ごとの1出現確認では見逃すため)
    role_s = {}
    for it in der["items"]:
        if role_s.get(nfkc(it["surface"])) != "core":
            role_s[nfkc(it["surface"])] = it["role"]
    exp_story = insert_marks(story, [{"surface": x, "role": r} for x, r in role_s.items()])
    if story_m != exp_story:
        res["b_numbers"].append("Storyline marks differ from the deterministic marking")
    if len(plain["ordered_ids"]) == len(plain_lines) == len(ann_lines):
        for i, (fid, pl, al) in enumerate(zip(plain["ordered_ids"], plain_lines, ann_lines), 1):
            body = pl[2:] if pl.startswith("- ") else pl
            its = [{"surface": it["surface"], "role": role_s[nfkc(it["surface"])]} for it in der["items"] if it["fact_id"] == fid]
            m = w1.FACT_LINE_RE.match(al)
            if not m or m.group(2) != insert_marks(body, its):
                res["b_numbers"].append(f"fact {i} marks differ from the deterministic marking")
    # c_core_peripheral: 上限・適格性・種類の規則を導出結果と別に再点検
    role_by_surface, eligible_concepts, core_concepts = {}, set(), set()
    for it in der["items"]:
        s = nfkc(it["surface"])
        if it["role"] == "core":
            role_by_surface[s] = "core"
            core_concepts.add(it["concept"])
            if not it["eligible"]:
                res["c_core_peripheral"].append(f"core {it['surface']!r} is not eligible")
            if it["kind"] in ("year", "ordinal", "name_embedded"):
                res["c_core_peripheral"].append(f"core {it['surface']!r} has never-core kind {it['kind']}")
        else:
            role_by_surface.setdefault(s, "peripheral")
        if it["eligible"] and it["kind"] in ("magnitude", "range", "date_time"):
            eligible_concepts.add(it["concept"])
    if len(core_concepts) > der["cap"]:
        res["c_core_peripheral"].append(f"core concepts {len(core_concepts)} exceed cap {der['cap']}")
    if len(core_concepts) != min(der["cap"], len(eligible_concepts)):
        res["c_core_peripheral"].append(f"core concepts {len(core_concepts)} != min(cap {der['cap']}, eligible {len(eligible_concepts)})")
    for n in sidecar["numbers"]:
        if role_by_surface.get(nfkc(n["surface"])) not in (None, n["class"]):
            res["c_core_peripheral"].append(f"sidecar class of {n['surface']!r} disagrees with derived role")
    # e_sidecar: 番号集合・台帳ID・数値表記・sha欄
    if sorted(f["n"] for f in sidecar["facts"]) != list(range(1, len(ann_lines) + 1)):
        res["e_sidecar"].append("sidecar.facts n set != 1..K")
    lf, _ = parse_ledger(ledger_text)
    for f in sidecar["facts"]:
        for lid in f["ledger_ids"]:
            if lid not in lf:
                res["e_sidecar"].append(f"ledger id {lid} not in ledger")
    for n in sidecar["numbers"]:
        if (n["surface"] + MARK[n["class"]]) not in (story_m + "\n" + facts_m):
            res["e_sidecar"].append(f"sidecar number {n['surface']!r} has no marked occurrence")
    for k in ("spec_sha256", "brief_sha256"):
        if not sidecar.get(k):
            res["e_sidecar"].append(f"sidecar.{k} empty")
    return {k: {"status": "FAIL" if v else "PASS", "problems": v} for k, v in res.items()}


def _write_bytes(p: str, b: bytes) -> None:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b)


def produce_annotated_b3(out_dir: str) -> dict:
    """out_dir の research_ledger / storyline_b3(B3出力)から注記済みB3 artifact を決定論で生成する(冪等)。
    入力: research_ledger/verified_fact_ledger.txt, storyline_b3/selected_brief.md, storyline_b3/fact_selection_evidence.json
    失敗は AnnotationProducerError(課金前STOP)。LLM/API呼出なし。"""
    sdir = os.path.join(out_dir, "storyline_b3")
    for name in (ANNOTATED_NAME, SIDECAR_NAME, MANIFEST_NAME, CONSTRAINTS_NAME):    # fail-closed: 失敗時に古い注記artifactを残さない
        try:
            os.remove(os.path.join(sdir, name))
        except FileNotFoundError:
            pass
    paths = {"ledger": os.path.join(out_dir, LEDGER_REL), "brief": os.path.join(sdir, BRIEF_NAME), "evidence": os.path.join(sdir, EVIDENCE_NAME)}
    missing = [os.path.relpath(p, out_dir) for p in paths.values() if not os.path.isfile(p)]
    if missing:
        raise AnnotationProducerError([f"missing input: {m}" for m in missing])
    raw = {}
    for k, p in paths.items():
        with open(p, "rb") as f:
            raw[k] = f.read()
    try:
        ledger_text = raw["ledger"].decode("utf-8")
        ev = json.loads(raw["evidence"].decode("utf-8"))
        brief_story, _ = w1.parse_brief_md(raw["brief"].decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise AnnotationProducerError([f"input unreadable/invalid: {type(e).__name__}: {e}"])
    ids, story = ev.get("selected_fact_ids"), ev.get("selected_storyline")
    probs = _check_inputs(ledger_text, ids, story, brief_story)
    if probs:
        raise AnnotationProducerError(probs)

    plain = assemble_plain(ledger_text, ids, story)
    der = ddet(ledger_text, ids, story)
    plain_brief, annotated_md, sidecar = build_annotated(ledger_text, ids, story, der)
    if plain_brief != plain["brief_md"]:
        raise AnnotationProducerError(["internal: build_annotated plain brief != assemble_D brief"])
    rsha = rules_sha256()
    sidecar["spec_sha256"] = rsha
    sidecar["brief_sha256"] = _sha(raw["brief"])       # 契約V9: manifest.source_selected_brief_sha256 (=selected_brief.mdのsha) と同値
    sidecar["rule_version"] = RULE_VERSION
    elig = {nfkc(it["surface"]) for it in der["items"] if it["eligible"]}
    sidecar["unmapped_claims"] = []                     # 決定論assemblerは台帳外の記述を作らない(規則により常に空)
    sidecar["annotation_notes"] = [f"cap({der['cap']})超過で周辺化: {n['surface']}"
                                   for n in sidecar["numbers"] if n["class"] == "peripheral" and nfkc(n["surface"]) in elig]
    checks = run_internal_checks(plain, annotated_md, sidecar, der, story, ledger_text)
    failed = {k: v["problems"] for k, v in checks.items() if v["status"] != "PASS"}
    if failed:
        raise AnnotationProducerError([f"internal check {k}: {p[:3]}" for k, p in failed.items()])

    ann_b = annotated_md.encode("utf-8")
    side_b = json.dumps(sidecar, ensure_ascii=False, indent=2).encode("utf-8")
    cons_b = plain["constraints_text"].encode("utf-8")
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION, "producer": PRODUCER,
        "source_selected_brief_sha256": _sha(raw["brief"]), "ledger_sha256": _sha(raw["ledger"]),
        "annotated_md_sha256": _sha(ann_b), "sidecar_sha256": _sha(side_b), "spec_sha256": rsha,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "checks": {k: v["status"] for k, v in checks.items()}, "model_ids": [],
        "writer_constraints_sha256": _sha(cons_b),
        "rule_version": RULE_VERSION, "rules_sha256": rsha, "llm_calls": 0,
        "input_shas": {"selected_brief_md": _sha(raw["brief"]), "ledger": _sha(raw["ledger"]), "fact_selection_evidence_json": _sha(raw["evidence"])},
        "internal_checks": checks, "n_facts": len(plain["ordered_ids"]), "n_number_surfaces": len(sidecar["numbers"]),
        "cap": der["cap"], "n_concepts": der["n_concepts"],
    }
    _write_bytes(os.path.join(sdir, ANNOTATED_NAME), ann_b)
    _write_bytes(os.path.join(sdir, SIDECAR_NAME), side_b)
    _write_bytes(os.path.join(sdir, CONSTRAINTS_NAME), cons_b)
    _write_bytes(os.path.join(sdir, MANIFEST_NAME), json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    # evidence: selected_fact_brief_text 欄は維持し中身を決定論出力へ(下流契約不変)。元のB3 LLM文は初回のみ退避。
    ev.setdefault("b3_llm_selected_fact_brief_text", ev.get("selected_fact_brief_text"))
    ev["selected_fact_brief_text"] = plain["facts_text"]
    ev["selected_fact_brief_text_source"] = PRODUCER
    ev["writer_constraints_text"] = plain["constraints_text"]
    ev["writer_news_field_text"] = plain["news_field"]
    _write_bytes(paths["evidence"], json.dumps(ev, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"out_dir": out_dir, "producer": PRODUCER, "rule_version": RULE_VERSION, "rules_sha256": rsha,
            "annotated_md_sha256": manifest["annotated_md_sha256"], "writer_constraints_sha256": manifest["writer_constraints_sha256"],
            "input_shas": manifest["input_shas"], "n_facts": manifest["n_facts"], "manifest": manifest}
