# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 Trial専用の決定論数値監査(API 0。Productionには入れない)。

目的: 現行Productionには「出力数値が中核数値表記と一致するか」を機械拒否する検査が無い(Writer規則(5)はPromptのみ、RFは非Blocking)。
そこでTrial専用に、Writer/英訳出力の全数値トークンを
  EXACT_CORE            中核数値の厳密値と一致
  DESIGNATED_APPROX     丸め判断overlayで指定された概数と一致(Trial限定例外)
  UNDESIGNATED_ROUNDING 厳密値を指定外の桁へ丸めた値
  PERIPHERAL_USED       周辺数値(書いてはいけない)
  UNAUTHORIZED          上記いずれでもない数値
へ分類する。UNDESIGNATED_ROUNDING/PERIPHERAL_USED/UNAUTHORIZED = 規則(5)・Ledger整合の逸脱候補(丸め由来かWriter揺れ由来かは
呼出側でControl比較により分類する)。
"""
from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

_JA_MULT = {"千": Decimal(1000), "万": Decimal(10000), "億": Decimal(10 ** 8), "兆": Decimal(10 ** 12)}
_EN_MULT = {"thousand": Decimal(1000), "million": Decimal(10 ** 6), "billion": Decimal(10 ** 9), "trillion": Decimal(10 ** 12)}
_TOK = re.compile(r"(?<![\d.,A-Za-z])(\d[\d,]*(?:\.\d+)?)(?![\d])")


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def sig_digits(d: Decimal) -> int:
    return len(d.normalize().as_tuple().digits)


def round_sig(value: Decimal, k: int):
    if value is None or value <= 0 or k < 1:
        return None
    q = Decimal(1).scaleb(value.adjusted() - k + 1)
    return (value / q).quantize(Decimal(1), rounding=ROUND_HALF_UP) * q


def _num(g: str) -> Decimal:
    return Decimal(g.replace(",", "").rstrip("."))


def tokens(text: str) -> list:
    """[{raw, value(Decimal), start, end, displayed_sig}]。JA複合(295億9,100万/13万5千)とEN倍率語(29.59 billion)を値へ展開。"""
    s = nfkc(text)
    out, pos = [], 0
    while True:
        m = _TOK.search(s, pos)
        if not m:
            break
        num = _num(m.group(1))
        end = m.end()
        j, acc, chained = m.start(), Decimal(0), False
        while True:
            mm = _TOK.match(s, j)
            if not mm:
                break
            n = _num(mm.group(1))
            if mm.end() < len(s) and s[mm.end()] in _JA_MULT:
                acc += n * _JA_MULT[s[mm.end()]]
                j = mm.end() + 1
                chained = True
            else:
                if chained:
                    acc += n
                    j = mm.end()
                break
        if chained:
            total, end, dsig = acc, j, sig_digits(acc)
        else:
            em = re.match(r"\s*(thousand|million|billion|trillion)\b", s[end:], re.I)
            if em:
                total, end = num * _EN_MULT[em.group(1).lower()], end + em.end()
                dsig = sig_digits(num)
            else:
                total, dsig = num, sig_digits(num)
        out.append({"raw": s[m.start():end], "value": total, "start": m.start(), "end": end, "displayed_sig": dsig})
        pos = max(end, m.end())
    return out


def surface_values(surface: str) -> set:
    """表記に含まれる数値(複合展開値 + 構成数字そのもの。日付表記の年・月・日を許容するため構成数字も含める)。"""
    vals = {t["value"] for t in tokens(surface)}
    for g in re.findall(r"\d[\d,]*(?:\.\d+)?", nfkc(surface)):
        vals.add(_num(g))
    return vals


def build_allowed(sidecar: dict, overlay) -> dict:
    exact, approx, periph = set(), set(), set()
    for n in sidecar["numbers"]:
        if n["class"] == "core":
            exact |= surface_values(n["surface"])
        else:
            periph |= surface_values(n["surface"])
    if overlay:
        for e in overlay["entries"]:
            if e["final_decision"] == "APPROXIMATE_OK":
                for s in e["surfaces"]:
                    if s.get("approx"):
                        approx |= surface_values(s["approx"])
    periph -= exact
    return {"exact": exact, "approx": approx, "peripheral": periph}


def classify(text: str, allowed: dict, lang: str, ja_value_set=None) -> dict:
    """text内の全数値トークンを分類。lang='ja'|'en'。enでは表示精度を考慮(29.59 billion等)。
    ja_value_setを渡すとEN側でJA R2に無い数値(翻訳段の逸脱)を not_in_ja_r2 に列挙する。"""
    res = {"EXACT_CORE": [], "DESIGNATED_APPROX": [], "UNDESIGNATED_ROUNDING": [], "PERIPHERAL_USED": [], "UNAUTHORIZED": [], "not_in_ja_r2": []}
    for t in tokens(text):
        v, k = t["value"], t["displayed_sig"]
        cat = None
        if v in allowed["exact"]:
            cat = "EXACT_CORE"
        elif v in allowed["approx"]:
            cat = "DESIGNATED_APPROX"
        elif lang == "en":
            full = [e for e in allowed["exact"] if e > 0 and round_sig(e, k) == v]
            if full:
                # 表示桁kが厳密値の有効桁以上に近い=単なる表示形差(29.59 billion)。大きく桁を落としていれば指定外丸め
                cat = "EXACT_CORE" if any(sig_digits(e) <= k + 1 for e in full) else "UNDESIGNATED_ROUNDING"
        if cat is None:
            for e in allowed["exact"]:
                if e > 0 and sig_digits(e) >= 2 and any(round_sig(e, kk) == v for kk in range(1, sig_digits(e))):
                    cat = "UNDESIGNATED_ROUNDING"
                    break
        if cat is None and v in allowed["peripheral"]:
            cat = "PERIPHERAL_USED"
        if cat is None:
            cat = "UNAUTHORIZED"
        res[cat].append(t["raw"])
        if lang == "en" and ja_value_set is not None and v not in ja_value_set:
            if not any(j > 0 and round_sig(j, k) == v for j in ja_value_set):
                res["not_in_ja_r2"].append(t["raw"])
    res["n_tokens"] = sum(len(res[c]) for c in ("EXACT_CORE", "DESIGNATED_APPROX", "UNDESIGNATED_ROUNDING", "PERIPHERAL_USED", "UNAUTHORIZED"))
    res["violations"] = len(res["UNDESIGNATED_ROUNDING"]) + len(res["PERIPHERAL_USED"]) + len(res["UNAUTHORIZED"])
    return res


def ja_value_set(text: str) -> set:
    return {t["value"] for t in tokens(text)}


def designated_surface_check(text: str, overlay) -> dict:
    """指定概数surfaceが使われたとき、限定語(最大/以上等)を伴う逐語形で書かれているか(JA R2用)。"""
    out = {"designated_used_verbatim": [], "designated_number_without_verbatim_surface": [], "exact_form_used": [], "unused": []}
    if not overlay:
        return out
    t = nfkc(text)
    toks = tokens(t)
    for e in overlay["entries"]:
        if e["final_decision"] != "APPROXIMATE_OK":
            continue
        for s in e["surfaces"]:
            ap, ex = nfkc(s["approx"]), nfkc(s["surface"])
            apv, exv = surface_values(ap), surface_values(ex)
            if ap in t:
                out["designated_used_verbatim"].append(s["approx"])
            elif any(tok["value"] in apv and tok["value"] not in exv for tok in toks):
                out["designated_number_without_verbatim_surface"].append(s["approx"])
            elif ex in t:
                out["exact_form_used"].append(s["surface"])
            else:
                out["unused"].append(s["surface"])
    return out
