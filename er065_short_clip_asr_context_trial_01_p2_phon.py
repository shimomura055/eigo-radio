# -*- coding: utf-8 -*-
"""FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 委任_03 (Trial / DEV only, Production未配線)。

音韻水準の「連結発音で説明できるか」判定(Trial専用)。承認済み基本原則:
  「自然な英語で、子音が連続することにより一方の音が融合・弱化・脱落し得る場合、その音韻構造を診断し、
   正常な連結発音で説明できるなら許容する。ただし文脈によるASRの推測だけを根拠に自動PASSしない。」

本モジュールは (1) canonical文と ASR転写の差を音素列(CMU辞書+限定的なOOV派生)で比較し、
語境界の子音連続(同一子音の重なり/歯擦音連続/yod融合/歯擦音+口蓋歯擦音/同調音位置破裂音)による
語末子音の融合・脱落で説明できるかを返す。(2) three_way()で 許容/NG/HR の3分類へ落とす際、
「独立証拠」(音響のgeminate長・別engine等)が無ければ HR に止める(ASR推測だけで許容にしない)。

Productionの `er011_b1_connected_speech_validator_01` / `er011_connected_speech_equivalence_layer_production_01`
は import するが変更しない(読取のみ)。新しい許容条件はここ(Trial)に閉じる。
"""
from __future__ import annotations

import difflib
import re
from typing import Optional

try:
    import pronouncing
except ImportError:  # pragma: no cover
    pronouncing = None

VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
SIBILANT_ALV = {"S", "Z"}
SIBILANT_PAL = {"SH", "ZH", "CH", "JH"}
STOPS = {"P", "B", "T", "D", "K", "G"}
PLACE = {"P": "bil", "B": "bil", "M": "bil", "T": "alv", "D": "alv", "N": "alv", "S": "alv", "Z": "alv", "L": "alv",
         "K": "vel", "G": "vel", "NG": "vel", "SH": "pal", "ZH": "pal", "CH": "pal", "JH": "pal", "Y": "pal",
         "F": "lab", "V": "lab", "TH": "den", "DH": "den"}
VOICING_PAIRS = {"T": "D", "D": "T", "S": "Z", "Z": "S", "P": "B", "B": "P", "K": "G", "G": "K", "F": "V", "V": "F",
                 "SH": "ZH", "ZH": "SH", "CH": "JH", "JH": "CH", "TH": "DH", "DH": "TH"}

_TOK = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    return _TOK.findall((text or "").lower().replace("’", "'"))


def _strip(ph: str) -> str:
    return "".join(c for c in ph if not c.isdigit())


def cmu(word: str) -> Optional[list[str]]:
    if pronouncing is None:
        return None
    v = pronouncing.phones_for_word(word.lower().strip("'"))
    if not v:
        return None
    return [_strip(p) for p in v[0].split()]


def phones(word: str) -> tuple[Optional[list[str]], str]:
    """(音素列, 出典)。出典: cmu / derived_stem_s(OOVの-s語を stem+S/Z で派生) / none。
    G2P(g2p_en等)は未導入のため、それ以外のOOVは None(=音韻水準の証拠なし、HRへ)。"""
    w = word.lower().strip("'")
    p = cmu(w)
    if p:
        return p, "cmu"
    if w.endswith("'s") and len(w) > 3:
        sp = cmu(w[:-2])
        if sp:
            last = sp[-1]
            z = "IH Z" if last in {"S", "Z", "SH", "ZH", "CH", "JH"} else ("S" if last in {"P", "T", "K", "F", "TH"} else "Z")
            return sp + z.split(), "derived_possessive"
    if w.endswith("s") and len(w) > 3:
        sp = cmu(w[:-1])
        if sp:
            last = sp[-1]
            if last in {"S", "Z", "SH", "ZH", "CH", "JH"}:
                return sp + ["IH", "Z"], "derived_stem_s"
            return sp + ["S" if last in {"P", "T", "K", "F", "TH"} else "Z"], "derived_stem_s"
    return None, "none"


def phones_of_asr_token(tok: str) -> tuple[Optional[list[str]], str]:
    """ASR出力トークン(OOV連結語 'meloset' 等)は、2つの既知語への分割で音素化を試みる(語境界の再分節の表現)。"""
    p, src = phones(tok)
    if p:
        return p, src
    n = len(tok)
    best = None
    for k in range(2, n - 1):
        a, b = tok[:k], tok[k:]
        pa, sa = phones(a)
        pb, sb = phones(b)
        if pa and pb and sa == "cmu" and sb == "cmu":
            cand = (pa + pb, f"split:{a}+{b}")
            if best is None:
                best = cand
    return best if best else (None, "none")


def seq_phones(words: list[str], asr_side: bool = False) -> tuple[Optional[list[str]], list[str]]:
    out, srcs = [], []
    for w in words:
        p, s = (phones_of_asr_token(w) if asr_side else phones(w))
        if not p:
            return None, srcs + [f"{w}:none"]
        out.extend(p)
        srcs.append(f"{w}:{s}")
    return out, srcs


def boundary_type(f: str, i: str) -> Optional[str]:
    """語末音素fと次語頭音素iの境界が、融合・弱化・脱落を起こし得る子音連続か。該当しなければNone。
    母音始まりの連結(resyllabification)は対象外(語末子音は脱落でなく連結する)。"""
    if f in VOWELS or i in VOWELS or f is None or i is None:
        return None
    if f == i:
        return "GEMINATE_SAME"            # s+s, t+t, d+d, n+n, k+k, l+l ...
    if f in SIBILANT_ALV and i in SIBILANT_ALV:
        return "SIBILANT_SEQ"             # s+z, z+s
    if (f in SIBILANT_ALV and i in SIBILANT_PAL) or (f in SIBILANT_PAL and i in SIBILANT_ALV | SIBILANT_PAL):
        return "SIBILANT_PALATAL"         # s+sh, z+sh, sh+ch
    if f in {"T", "D", "S", "Z"} and i == "Y":
        return "YOD_COALESCENCE"          # did you, meet you, miss you, as you
    if f in STOPS and i in STOPS and PLACE.get(f) == PLACE.get(i):
        return "HOMORGANIC_STOPS"         # good time, bad day, big car(同位置の破裂音連続)
    if f in STOPS and i in STOPS:
        return "STOP_STOP_UNRELEASED"     # last-position stop + stop (best-effort)
    return None


def phones_all(word: str) -> list[tuple[list[str], str]]:
    """CMUの全発音変種(最大4)。無ければ phones() の派生1件。"""
    w = word.lower().strip("'")
    if pronouncing is not None:
        v = pronouncing.phones_for_word(w)
        if v:
            return [([_strip(x) for x in e.split()], "cmu") for e in v[:4]]
    p, src = phones(word)
    return [(p, src)] if p else []


def _region_variants(c_words: list[str], prev_w: Optional[str], next_w: Optional[str]) -> list[dict]:
    """canonical差分領域(c_words)の音素列(各語のCMU全変種の直積、上限8)から、語境界の連結発音により
    生じ得る音素列の変種を作る。
    - 領域内部の境界(語k末子音 + 語k+1語頭): 語k末の子音を脱落(融合)
    - 右境界(領域末語の語末子音F + 次語頭I)が連続子音: F脱落(融合)
    - 左境界(前語の語末子音F' + 領域頭語の語頭I')が連続子音: 領域頭のI'脱落(融合を前語側が担う)
    各境界は単独で適用(複数同時の連鎖脱落は過受理防止のため対象外)。"""
    import itertools
    per_word = [phones_all(w) for w in c_words]
    if any(not x for x in per_word):
        return []
    combos = list(itertools.islice(itertools.product(*per_word), 8))
    vs = []
    for combo in combos:
        lists = [c[0] for c in combo]
        base = [ph for l in lists for ph in l]
        vs.append({"kind": "ORIG", "phones": base, "boundary": None, "dropped": None})
        # 内部境界
        off = 0
        for k in range(len(lists) - 1):
            off += len(lists[k])
            f, i = lists[k][-1], lists[k + 1][0]
            bt = boundary_type(f, i)
            if bt:
                vs.append({"kind": "INTERNAL_FINAL_DROP", "phones": base[:off - 1] + base[off:], "boundary": bt,
                           "dropped": f, "env": f"{c_words[k]}[{f}] + {c_words[k+1]}[{i}]"})
        if next_w:
            nb = phones_all(next_w)
            for npl, _ in nb[:2]:
                bt = boundary_type(base[-1], npl[0])
                if bt:
                    vs.append({"kind": "RIGHT_FINAL_DROP", "phones": base[:-1], "boundary": bt, "dropped": base[-1],
                               "env": f"{c_words[-1]}[{base[-1]}] + {next_w}[{npl[0]}]"})
                    break
        if prev_w:
            pb = phones_all(prev_w)
            for ppl, _ in pb[:2]:
                bt = boundary_type(ppl[-1], base[0])
                if bt:
                    vs.append({"kind": "LEFT_INITIAL_DROP", "phones": base[1:], "boundary": bt, "dropped": base[0],
                               "env": f"{prev_w}[{ppl[-1]}] + {c_words[0]}[{base[0]}]"})
                    break
    # 重複除去
    seen, out = set(), []
    for v in vs:
        k = (v["kind"], tuple(v["phones"]))
        if k not in seen:
            seen.add(k)
            out.append(v)
    return out


def _voicing_equiv(a: list[str], b: list[str]) -> bool:
    """最終音素のvoicingだけが異なる(例: ...EH D と ...EH T)。それ以外は完全一致が必要。"""
    if len(a) != len(b) or not a:
        return False
    if a[:-1] != b[:-1]:
        return False
    return a[-1] != b[-1] and VOICING_PAIRS.get(a[-1]) == b[-1]


def explain_diff(canonical: str, asr: str) -> dict:
    """canonicalとASRのトークン差分を、連結発音(語境界の子音連続)で説明できるか判定する。
    戻り値 verdict:
      EXACT                      差分なし(綴り一致)
      PHON_EXPLAINED_FUSION      全ての差分領域が、連結発音の変種と音素列で完全一致
      PHON_EXPLAINED_VOICING     同上だが最終音素のvoicingのみ不一致(弱い説明、要HR扱い)
      PHON_HOMOPHONE_ONLY        綴りは違うが音素列がcanonicalと同一(連結を要さない同音綴り違い、例 Mellow=Melo...では無い)
      NOT_EXPLAINED              連結発音では説明できない(語幹の置換・母音違い・別語など)
      NO_PHONOLOGICAL_EVIDENCE   OOV等で音素列が作れない(G2P欠如)
    """
    cw, aw = tokens(canonical), tokens(asr)
    sm = difflib.SequenceMatcher(a=cw, b=aw, autojunk=False)
    regions, worst = [], "EXACT"
    rank = {"EXACT": 0, "PHON_HOMOPHONE_ONLY": 1, "PHON_EXPLAINED_FUSION": 2, "PHON_EXPLAINED_VOICING": 3,
            "NO_PHONOLOGICAL_EVIDENCE": 4, "NOT_EXPLAINED": 5}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        c_reg, a_reg = cw[i1:i2], aw[j1:j2]
        prev_w = cw[i1 - 1] if i1 > 0 else None
        next_w = cw[i2] if i2 < len(cw) else None
        r = {"tag": tag, "canon": c_reg, "asr": a_reg}
        if not c_reg or not a_reg:
            r["verdict"] = "NOT_EXPLAINED"
            r["why"] = "pure_insertion_or_deletion_of_words"
            regions.append(r)
            worst = max(worst, r["verdict"], key=lambda k: rank[k])
            continue
        ap, asrcs = seq_phones(a_reg, asr_side=True)
        r["asr_srcs"] = asrcs
        vs = _region_variants(c_reg, prev_w, next_w)
        if ap is None or not vs:
            r["verdict"] = "NO_PHONOLOGICAL_EVIDENCE"
            r["why"] = "oov_no_phones"
            regions.append(r)
            worst = max(worst, r["verdict"], key=lambda k: rank[k])
            continue
        verdict, hit = "NOT_EXPLAINED", None
        for v in vs:
            if v["phones"] == ap:
                if v["kind"] == "ORIG":
                    verdict, hit = "PHON_HOMOPHONE_ONLY", v
                else:
                    verdict, hit = "PHON_EXPLAINED_FUSION", v
                    break
        if verdict == "NOT_EXPLAINED":
            for v in vs:
                if v["kind"] != "ORIG" and _voicing_equiv(v["phones"], ap):
                    verdict, hit = "PHON_EXPLAINED_VOICING", v
                    break
        r["verdict"], r["variants_tried"] = verdict, [(v["kind"], " ".join(v["phones"])) for v in vs]
        r["asr_phones"] = " ".join(ap)
        if hit:
            r["rule"], r["boundary"], r["dropped"], r["env"] = hit["kind"], hit.get("boundary"), hit.get("dropped"), hit.get("env")
        regions.append(r)
        worst = max(worst, verdict, key=lambda k: rank[k])
    return {"verdict": worst, "regions": regions, "n_diff_regions": len(regions)}


# ---------------------------------------------------------------- 3分類
def three_way(expl: dict, independent_evidence: Optional[dict] = None) -> dict:
    """許容 / NG / HR の3分類(Trial方針、Production未配線)。

    独立証拠 independent_evidence(辞書、無ければ{}):
      acoustic_geminate_ok: bool|None  境界の摩擦/閉鎖区間長が融合長(較正済み閾値以上)
      second_engine_exact:  bool|None  別engine(Azure+Phrase List等)が綴りまでcanonical一致
    ルール:
      EXACT                          -> 許容(通常PASS、本機構の対象外)
      PHON_EXPLAINED_FUSION          -> 独立証拠が1つ以上True: 許容 / 全てFalse(音響が融合長でない): HR / 証拠なし: HR
      PHON_EXPLAINED_VOICING / PHON_HOMOPHONE_ONLY / NO_PHONOLOGICAL_EVIDENCE -> HR
      NOT_EXPLAINED                  -> NG(連結発音では説明できない=別語/語幹置換/母音違い等。Productionの既存判定に委ねる)
    ASRの推測(=expl)だけでは決して『許容』にしない。
    """
    ev = independent_evidence or {}
    v = expl["verdict"]
    if v == "EXACT":
        return {"class": "許容", "reason": "exact"}
    if v == "NOT_EXPLAINED":
        return {"class": "NG", "reason": "not_explained_by_connected_speech"}
    if v == "PHON_EXPLAINED_FUSION":
        pos = [k for k in ("acoustic_geminate_ok", "second_engine_exact") if ev.get(k) is True]
        neg = [k for k in ("acoustic_geminate_ok",) if ev.get(k) is False]
        if pos and not neg:
            return {"class": "許容", "reason": "explained+independent:" + ",".join(pos)}
        if neg:
            return {"class": "HR", "reason": "explained_but_acoustic_negative"}
        return {"class": "HR", "reason": "explained_but_no_independent_evidence"}
    return {"class": "HR", "reason": v.lower()}
