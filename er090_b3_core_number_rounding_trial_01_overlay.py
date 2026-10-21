# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01(2026-10-21、Trial専用・Production未配線)。

機能: 決定論producerが選定済みの【中核数値】について、「厳密値維持(EXACT_REQUIRED)」か「概数化可(APPROXIMATE_OK)」かを
LLMが判断し(1記事1call)、概数可の場合のみWriterへ「Writerへの注意」ブロック追記行として伝える。
隔離: 本moduleはProductionのどのmoduleもimport元として改変しない(読取り専用import)。注記md/sidecar/manifestは無改変。
       概数可0件ならWriter入力は従来とバイト一致(no-op)。Productionのrunner/CLI/起動scriptからは参照されない。
純関数のみ(API呼出なし)。API呼出は er090_b3_core_number_rounding_trial_01_run.py。
"""
from __future__ import annotations

import json
import re
from decimal import Decimal, ROUND_HALF_UP

# ---- 承認済みルール原文(新しい品質基準は足さない)----
from er003_v1_n3_01_evidence_compression_editor import (
    LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK,
    NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK,
)

# CURRENT_SPEC.md:1730 の本文(逐語。testでCURRENT_SPECの該当行に含まれることを確認する)
SPOKEN_FIRST_NUMBER_TREATMENT_TEXT = (
    "Verified Fact Ledgerは常にexact factを保持する。spoken narrative側は、精度自体に意味がない数字を、"
    "丸め(round)・概数化(approximate)・方向化(directionalize)してListening easeを優先してよい。"
    "分類は2軸: Importance(`ANCHOR`/`SUPPORTING`/`DISPENSABLE`)、Exactness(`EXACT_REQUIRED`/`APPROXIMATE_OK`/`DIRECTION_ONLY`)。"
    "スコア・日付・記録・健康研究の結果・安全閾値など、精度そのものが意味を持つ数字はEXACT_REQUIREDのまま維持する"
)

DECISION_EXACT = "EXACT_REQUIRED"
DECISION_APPROX = "APPROXIMATE_OK"

# Writer R0 Promptへ差し込む1項(Trial wrapperのみ。概数可0件なら追加しない)
RULE8_TEXT = (
    "\n8. 「Writerへの注意」に【概数表記】として指定された数字は、規則5の例外として、指定された表記で書けます"
    "(書くかどうかは文脈次第です)。指定のない数字は規則5のとおり、丸めたり「約」「およそ」を足したりしません。"
)

HEDGE_WORDS = ("約", "およそ", "ほぼ", "前後", "ほど", "近く", "程度")
QUALIFIER_WORDS = ("最大", "最低", "少なくとも", "以上", "以下", "超", "未満", "以内", "余り")

JUDGE_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのNumeric Precision判定者です。機械的に選定済みの【中核数値】それぞれについて、"
    "承認済みルールに従い、厳密値を維持するか、聞き取りやすい概数にしてよいかだけを判断します。"
    "Fact選定・記事の構成・中核数値の選定は変更しません。Verified Fact Ledgerの数値も変更しません。"
)

JUDGE_JSON_SCHEMA = {
    "name": "core_number_rounding_decision",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "concept": {"type": "string"},
                        "decision": {"type": "string", "enum": [DECISION_EXACT, DECISION_APPROX]},
                        "surfaces": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "surface": {"type": "string"},
                                    "approx_surface": {"type": ["string", "null"]},
                                },
                                "required": ["surface", "approx_surface"],
                                "additionalProperties": False,
                            },
                        },
                        "reason": {"type": "string"},
                        "basis_fact_ids": {"type": "array", "items": {"type": "string"}},
                        "approved_condition": {"type": "string"},
                    },
                    "required": ["concept", "decision", "surfaces", "reason", "basis_fact_ids", "approved_condition"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["decisions"],
        "additionalProperties": False,
    },
}


# ============================================================
# 入力の読取り(sidecar / 注記md / Ledger)
# ============================================================
def parse_ledger_records(ledger_text: str) -> dict:
    """{Fxx: 記録ブロック全文}。"""
    recs = {}
    for m in re.finditer(r"\[VERIFIED\]\s+([A-Za-z0-9\-]+):.*?(?=\n\s*\n|\Z)", ledger_text, re.S):
        recs[m.group(1)] = m.group(0).strip()
    return recs


def core_concepts(sidecar: dict) -> list:
    """sidecar numbersからclass=coreのconcept毎の {concept, surfaces[順序保持,重複除去], kind, ledger_ids} を出現順で返す。"""
    out, idx = [], {}
    for n in sidecar["numbers"]:
        if n["class"] != "core":
            continue
        c = n["concept"]
        if c not in idx:
            idx[c] = len(out)
            out.append({"concept": c, "surfaces": [], "kind": n["kind"], "ledger_ids": list(n["ledger_ids"])})
        if n["surface"] not in out[idx[c]]["surfaces"]:
            out[idx[c]]["surfaces"].append(n["surface"])
    return out


def peripheral_numbers(sidecar: dict) -> list:
    return [{"surface": n["surface"], "concept": n["concept"], "ledger_ids": n["ledger_ids"]}
            for n in sidecar["numbers"] if n["class"] == "peripheral"]


def fact_n_for_ledger_ids(sidecar: dict, ledger_ids: list) -> list:
    ns = []
    for f in sidecar["facts"]:
        if any(i in f["ledger_ids"] for i in ledger_ids):
            ns.append(f["n"])
    return sorted(set(ns))


# ============================================================
# 判定Prompt
# ============================================================
def build_judge_user_prompt(*, storyline: str, facts_text: str, constraints_text: str, sidecar: dict, ledger_records: dict) -> str:
    cores = core_concepts(sidecar)
    ref_ids = []
    for c in cores:
        for i in c["ledger_ids"]:
            if i not in ref_ids:
                ref_ids.append(i)
    for p in peripheral_numbers(sidecar):
        for i in p["ledger_ids"]:
            if i not in ref_ids:
                ref_ids.append(i)
    lines = []
    lines.append("【承認済みルール(原文。新しい基準は追加しない)】")
    lines.append("■ Spoken-first Number Treatment(承認済み仕様)\n" + SPOKEN_FIRST_NUMBER_TREATMENT_TEXT)
    lines.append("■ " + LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK)
    lines.append("■ " + NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK)
    lines.append(
        "【今回の判定の進め方(出力形式と安全側の指示のみ)】\n"
        "- 判定するのは、下の「判定対象の中核数値」の各conceptだけです。conceptの追加・削除・並べ替えはしません。\n"
        "- 周辺数値は判定対象ではありません。丸めると値同士が同一視されないか等の確認にだけ使ってください。\n"
        "- 各conceptについて decision を EXACT_REQUIRED(厳密値を維持)か APPROXIMATE_OK(聞き取りやすい概数にしてよい)のどちらかで答えます。\n"
        "- 判断が不確かな場合は無理に丸めず EXACT_REQUIRED にしてください。\n"
        "- APPROXIMATE_OK の場合のみ、surfaces の各surface(判定対象に示された表記そのまま)に対し approx_surface を日本語で書きます。"
        "approx_surface は、surface文字列の**数字部分だけ**を、元の数値を通常の四捨五入(有効数字を減らす)で丸めた値に置き換え、"
        "「約」「およそ」等のヘッジ語を付けただけの表記にします。surfaceにある限定語(「最大」「以上」「超」「未満」等)と単位・接尾辞は"
        "そのまま残し、surfaceにない語句(説明・括弧書き・「前年同月比」等の補足)は一切足しません。surfaceに単位が無ければ単位も足しません。"
        "Factの意味(例: 解析ごとに人数が異なる等)はFact本文に残っており、Writerは別途Factを読みます。"
        "数字は算用数字と「万」「億」「千」で書いてください。形式の例(別の数字): surface「最大52,300人」→「最大約5万2千人」、surface「7.26」→「約7.3」。"
        "EXACT_REQUIRED の場合 approx_surface は null にします。\n"
        "- reason は1〜2文、basis_fact_ids は根拠にしたFact ID(Ledgerの記録ID)、approved_condition は上の承認済みルールのどの条件に当たるかを短く書きます。"
    )
    lines.append("【Storyline(確定済み)】\n" + storyline.strip())
    lines.append("【採用Fact(確定済み。【中核数値】【周辺数値】は決定論の機械印)】\n" + facts_text.strip())
    if constraints_text and constraints_text.strip():
        lines.append("【Writerへの注意(確定済み)】\n" + constraints_text.strip())
    lines.append("【参照Ledger記録(正確な値。変更しない)】\n" + "\n\n".join(ledger_records[i] for i in ref_ids if i in ledger_records))
    dl = ["【判定対象の中核数値(この順序・この表記のまま判定)】"]
    for c in cores:
        dl.append(f"- concept={c['concept']} kind={c['kind']} ledger_ids={c['ledger_ids']} surfaces={json.dumps(c['surfaces'], ensure_ascii=False)}")
    per = peripheral_numbers(sidecar)
    if per:
        dl.append("【周辺数値(参考。判定対象外)】")
        for p in per:
            dl.append(f"- {p['surface']} (concept={p['concept']}, ledger_ids={p['ledger_ids']})")
    lines.append("\n".join(dl))
    return "\n\n".join(lines)


# ============================================================
# 数値の機械検証(承認済み「通常の四捨五入で得られる近似値」の機械化)
# ============================================================
_UNIT_MULT = {"千": Decimal(1000), "万": Decimal(10000), "億": Decimal(100000000)}
_NUM_TOKEN = re.compile(r"(\d[\d,]*(?:\.\d+)?)([千万億]?)")


def _split_number(surface: str):
    """surfaceから (prefix, value(Decimal)|None, tail) を返す。数値は『13万5千』のような連続トークンを合算。"""
    s = surface.replace("，", ",")
    m = _NUM_TOKEN.search(s)
    if not m:
        return s, None, ""
    start = m.start()
    pos = start
    total = Decimal(0)
    last_end = start
    while True:
        mm = _NUM_TOKEN.match(s, pos)
        if not mm:
            break
        num = Decimal(mm.group(1).replace(",", ""))
        total += num * _UNIT_MULT.get(mm.group(2), Decimal(1))
        pos = mm.end()
        last_end = pos
        if not mm.group(2):          # 単位なしの数字(例: 5000)は連続の終端
            break
    return s[:start], total, s[last_end:]


def parse_surface(surface: str):
    prefix, val, tail = _split_number(surface)
    return {"prefix": prefix, "value": val, "tail": tail}


def _sig_digits(d: Decimal) -> int:
    t = d.normalize().as_tuple()
    return len(t.digits)


def is_ordinary_rounding(exact: Decimal, approx: Decimal) -> bool:
    """approxがexactの『通常の四捨五入(round-half-up)で有効数字k桁、1<=k<元の有効桁数』で得られる値か。"""
    if exact is None or approx is None or exact <= 0:
        return False
    n = _sig_digits(exact)
    if n < 2:
        return False
    exp10 = exact.adjusted()
    for k in range(1, n):
        q = Decimal(1).scaleb(exp10 - k + 1)
        r = (exact / q).quantize(Decimal(1), rounding=ROUND_HALF_UP) * q
        if r == approx:
            return True
    return False


def validate_surface_approx(exact_surface: str, approx_surface) -> list:
    """V3(通常の四捨五入)・V4(単位/限定語)・V5(ヘッジ語)。問題のlistを返す(空=OK)。"""
    issues = []
    if not approx_surface or not isinstance(approx_surface, str):
        return ["V5_approx_missing"]
    if approx_surface.strip() == exact_surface.strip():
        issues.append("V3_approx_equals_exact")
    ex, ap = parse_surface(exact_surface), parse_surface(approx_surface)
    if ex["value"] is None or ap["value"] is None:
        issues.append("V3_unparseable_number")
    elif not is_ordinary_rounding(ex["value"], ap["value"]):
        issues.append(f"V3_not_ordinary_rounding(exact={ex['value']},approx={ap['value']})")
    if ex["tail"].strip() != ap["tail"].strip():
        issues.append(f"V4_unit_tail_changed({ex['tail']!r}->{ap['tail']!r})")
    for q in QUALIFIER_WORDS:
        if q in exact_surface and q not in approx_surface:
            issues.append(f"V4_qualifier_dropped({q})")
    if not any(h in approx_surface for h in HEDGE_WORDS):
        issues.append("V5_no_hedge_word")
    return issues


def _round_sig(value: Decimal, k: int) -> Decimal:
    if value is None or value <= 0:
        return None
    q = Decimal(1).scaleb(value.adjusted() - k + 1)
    return (value / q).quantize(Decimal(1), rounding=ROUND_HALF_UP) * q


def collisions_with_other_numbers(sidecar: dict, concept: dict, approx_value: Decimal) -> list:
    """V7: 承認済み条件『丸めで異なる値が同一視されない/異なるFact・指標を統合しない』の機械化。
    同じLedger Factに属する他concept(core/peripheral)の数値を、approxと同じ有効数字桁で丸めた結果がapproxと一致するなら衝突。"""
    k = _sig_digits(approx_value)
    out = []
    for n in sidecar["numbers"]:
        if n["concept"] == concept["concept"] or not (set(n["ledger_ids"]) & set(concept["ledger_ids"])):
            continue
        other = parse_surface(n["surface"])["value"]
        if other is None or other <= 0:
            continue
        if _round_sig(other, k) == approx_value or other == approx_value:
            out.append(n["surface"])
    return out


# ============================================================
# 判定結果の検証 → overlay
# ============================================================
def build_overlay(sidecar: dict, judge_json: dict) -> dict:
    """LLM判定を決定論で検証し、overlayを返す。違反はEXACT_REQUIREDへ降格(fail-closed)。
    concept集合がsidecarのcore集合と一致しない場合は全conceptをEXACT_REQUIREDにして violations に記録。"""
    cores = core_concepts(sidecar)
    core_ids = [c["concept"] for c in cores]
    violations = []
    got = judge_json.get("decisions") if isinstance(judge_json, dict) else None
    entries = []
    structural_ok = True
    if not isinstance(got, list):
        violations.append("V1_decisions_missing")
        structural_ok = False
        got = []
    got_ids = [d.get("concept") for d in got]
    if got_ids != core_ids:
        violations.append(f"V1_concept_set_or_order_mismatch(expected={core_ids},got={got_ids})")
        structural_ok = False
    by_id = {d.get("concept"): d for d in got}
    for c in cores:
        d = by_id.get(c["concept"]) if structural_ok else None
        llm_decision = d.get("decision") if d else None
        final, downgrade, surf_out = DECISION_EXACT, [], []
        if d and llm_decision == DECISION_APPROX:
            smap = {s.get("surface"): s.get("approx_surface") for s in d.get("surfaces", [])}
            if list(smap.keys()) != c["surfaces"] and sorted(smap.keys()) != sorted(c["surfaces"]):
                downgrade.append(f"V2_surface_set_mismatch(expected={c['surfaces']},got={list(smap.keys())})")
            else:
                for s in c["surfaces"]:
                    iss = validate_surface_approx(s, smap.get(s))
                    av = parse_surface(smap.get(s) or "")["value"]
                    if av is not None:
                        col = collisions_with_other_numbers(sidecar, c, av)
                        if col:
                            iss.append(f"V7_collides_with_other_number_in_same_fact({col})")
                    if iss:
                        downgrade.extend(f"{s}:{x}" for x in iss)
                    surf_out.append({"surface": s, "approx": smap.get(s)})
            if not set(d.get("basis_fact_ids", [])) & set(c["ledger_ids"]) and d.get("basis_fact_ids") is not None:
                downgrade.append(f"V6_basis_fact_ids_not_in_concept_ledger_ids({d.get('basis_fact_ids')}vs{c['ledger_ids']})")
            if not downgrade:
                final = DECISION_APPROX
        entries.append({
            "concept": c["concept"], "kind": c["kind"], "ledger_ids": c["ledger_ids"],
            "fact_ns": fact_n_for_ledger_ids(sidecar, c["ledger_ids"]),
            "llm_decision": llm_decision, "final_decision": final, "downgrade_reasons": downgrade,
            "surfaces": surf_out if final == DECISION_APPROX else [{"surface": s, "approx": None} for s in c["surfaces"]],
            "reason": (d or {}).get("reason"), "basis_fact_ids": (d or {}).get("basis_fact_ids"),
            "approved_condition": (d or {}).get("approved_condition"),
        })
    return {"entries": entries, "violations": violations, "core_concept_order": core_ids,
            "n_approximate_ok": sum(1 for e in entries if e["final_decision"] == DECISION_APPROX)}


# ============================================================
# Writerへの伝達(追記のみ)
# ============================================================
def constraint_lines(overlay: dict) -> list:
    """APPROXIMATE_OK(最終)のsurface毎に1行。ファクトnが複数なら先頭n。EXACT_REQUIREDは何も出さない。"""
    lines = []
    for e in overlay["entries"]:
        if e["final_decision"] != DECISION_APPROX:
            continue
        n = e["fact_ns"][0]
        for s in e["surfaces"]:
            lines.append(f"- 事実{n}について：【概数表記】「{s['surface']}」は「{s['approx']}」と書いてよい。"
                         f"書く場合はこの表記に限り、他の丸め方や別の数字にはしない。")
    return lines


def apply_to_constraints(constraints_text: str, overlay: dict, heading: str) -> str:
    extra = constraint_lines(overlay)
    if not extra:
        return constraints_text
    base = (constraints_text or "").rstrip("\n")
    if not base:
        base = heading
    return base + "\n" + "\n".join(extra) + "\n"


def apply_to_news_field(facts_text: str, constraints_text: str, overlay: dict, heading: str, compose) -> str:
    return compose(facts_text, apply_to_constraints(constraints_text, overlay, heading))


def apply_rule8(prompt: str, overlay: dict) -> str:
    return prompt + RULE8_TEXT if constraint_lines(overlay) else prompt
