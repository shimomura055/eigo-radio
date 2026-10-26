# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01: Key Phrase候補Gate除外の棚卸し(read-only・API 0)。

- 既存ログ(er019/er026/er121/er011_output)を読むだけ。何も書かない(--out/--mdで指定したファイルを除く)。
- LLM/TTS clientは使わない。決定論validator(er003_key_words_canonicalization / er105 / er108)の関数だけを呼ぶ。
  それらのimport連鎖でopenaiパッケージ(module)が読み込まれるが、clientは生成せず、念のためsocket.connectを塞ぎ、
  通信が起きれば例外で止まる(=API 0を機械的に保証)。
- what-if(--inventory内のrescue_probe)は、in-memoryで閉じた表/guardを一時的に差し替えて『もし受理面を広げたら通るか』を
  机上計算するだけ。Productionファイルは変更しない(処理後に必ず元へ戻す)。
Usage:
  py kp_exclusion_inventory_01.py --out inventory_01.json --md EXCLUSION_PATTERNS_01.md
  py kp_exclusion_inventory_01.py --recheck rescue_candidates_01.json --out recheck_01.json
"""
from __future__ import annotations

import argparse
import collections
import glob
import itertools
import json
import os
import re
import socket
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
# pronouncing/cmudict(純Python・CMU辞書データ)だけを.venvから参照する(.venvのpythonは起動しない。`py`のsite-packagesに無いため末尾に追加)
_VENV_SP = os.path.join(ROOT, ".venv", "Lib", "site-packages")
if os.path.isdir(_VENV_SP):
    sys.path.append(_VENV_SP)


def _blocked(*a, **k):
    raise RuntimeError("network blocked: KP-GATE-EXCLUSION-RESCUE-DESIGN-01 is an API-0 offline analysis")


socket.socket.connect = _blocked          # type: ignore[assignment]
socket.create_connection = _blocked       # type: ignore[assignment]

import er003_key_words_canonicalization as kc   # noqa: E402  決定論validatorのみ使用
import er105_kp_fulltext_selector_01 as ft      # noqa: E402
import er108_kp_cmu_lexicon_gate_01 as cmu      # noqa: E402

FAMILY_OF = {"er019_output": "X", "er026_output": "Z", "er121_output": "Y", "er011_output": "LEGACY(A/B/C)"}
STOP_EDGE = frozenset("a an the to of and or but in on at for with by from as is are was were be been it its that this these those".split())


# ------------------------------------------------------------------ 分類
def rule7_parts(reason: str):
    m = re.search(r"key_phrase\((.+?)\)が(?:display_phrase)", reason)
    s = re.search(r"source_span\((.+?)\)内の連続部分文字列", reason)
    strip = lambda x: x.strip("'\"") if x else None   # noqa: E731
    return (strip(m.group(1)) if m else None, strip(s.group(1)) if s else None)


def classify(reason: str, stage: str = ""):
    """理由文字列(現行Gateの原文)をそのまま分類する。returns (class, subclass)。"""
    r = reason or ""
    if "語数が1〜5語でない" in r or "1〜5語でない" in r:
        return "WORDCOUNT_OVER5", ""
    if "有限助動詞" in r:
        return "FINITE_AUX_TOKEN", ""
    if "本文に連続一致しない" in r:
        return "NOT_CONTIGUOUS_IN_TEXT", ""
    if "文の境界" in r:
        return "CROSS_SENTENCE", ""
    if "CMU発音辞書" in r:
        return "CMU_UNREGISTERED", ""
    if "Humanが不適切" in r:
        return "HUMAN_NG_EXCLUDED", ""
    if "前記の選定済み表現と同一または包含" in r:
        return "DUPLICATE_OF_TOP3", ""
    if "を超過(下位のため除外)" in r:
        return "OVERFLOW_OVER5_CALL2", ""
    if r.startswith("重複") or r == "重複":
        return "DUPLICATE_IN_SELECTION", ""
    if "Rule7" in r:
        k, s = rule7_parts(r)
        sub = "UNPARSED"
        if k and s:
            kt, st = k.lower().split(), s.lower().split()
            person = {"one's", "someone's", "somebody's", "oneself", "someone", "somebody", "one"}
            if len(kt) > len(st):
                sub = "LLM_EXPANDED_BEYOND_SPAN"
            elif len(kt) == len(st):
                sub = "PERSON_GENERALIZATION_REJECTED" if any(t in person for t in kt) else "LEMMA_1TO1_REJECTED"
            else:
                sub = "SHORTENED_OR_REORDERED"
        return "RULE7_NORMALIZATION", sub
    if "QAでFAIL" in r:
        return "QA_REVIEW_REQUIRED(非除外・旗)", ""
    if "旧形式" in r or "placeholder" in r:
        return "LEGACY_FORM_PRECHECK", ""
    return "OTHER", ""


# ------------------------------------------------------------------ rescue probe (机上再検査)
def _norm_tokens(s):
    return ft._norm_tokens(s)


def _validate(key, display, span, reason="lemma_normalization"):
    return kc.validate_canonicalization_item(key, display, span, normalization_reason=reason, original_span=span,
                                              allow_inflection_normalization=True)


def _cmu_ok(key):
    return not cmu.reasons_for_phrase(key)


def rederive_keys(span: str):
    """決定論の基本形再導出: spanの各tokenを『既存validatorの許す1対1置換候補』へ置換した全組合せのうち、
    validator PASS かつ CMU辞書登録語のみのものを返す(変化token数の多い順)。LLMなし・既存表のみ。"""
    toks = _norm_tokens(span)
    n = len(toks)
    opts = []
    for i, t in enumerate(toks):
        o = {t}
        dl = t.lower()
        o |= set(kc._PERSON_DEPENDENT_TO_GENERIC.get(dl, ()))
        if i == 0 or toks[i - 1].lower() == "to":
            if dl in ft._FUNCTION_VERB_FORMS:
                o.add(ft._FUNCTION_VERB_FORMS[dl])
            if dl in ft._PAST_ONLY_IRREGULAR:
                o.add(ft._PAST_ONLY_IRREGULAR[dl])
            if dl in ft._AMBIGUOUS_IRREGULAR:
                o.add(ft._AMBIGUOUS_IRREGULAR[dl])
            o |= ft._verb_base_candidates(dl)
        if i == n - 1:
            if dl in ft._IRREGULAR_PLURAL:
                o.add(ft._IRREGULAR_PLURAL[dl])
            o |= ft._plural_base_candidates(dl)
        opts.append(sorted(o))
    total = 1
    for o in opts:
        total *= len(o)
    if total > 400:
        return []
    out = []
    for combo in itertools.product(*opts):
        key = " ".join(combo)
        if key.lower() == " ".join(toks).lower():
            continue
        if _validate(key, span, span)["ok"] and _cmu_ok(key):
            out.append((sum(1 for a, b in zip(combo, toks) if a.lower() != b.lower()), key))
    out.sort(reverse=True)
    return [k for _, k in out]


class _Whatif:
    """in-memory一時差替え(Productionファイルは不変)。with文で必ず復元。"""
    def __init__(self, det_add=(), adverb_ly=False, past_only=None):
        self.det_add, self.adverb_ly, self.past_only = set(det_add), adverb_ly, past_only or {}

    def __enter__(self):
        self.o_det, self.o_guard = ft._GUARD_DET, ft._guard_ok
        self.o_past = dict(ft._PAST_ONLY_IRREGULAR)
        ft._GUARD_DET = frozenset(set(ft._GUARD_DET) | self.det_add)
        if self.adverb_ly:
            base = self.o_guard

            def g(key_tokens, idx):
                nxt = key_tokens[idx + 1].lower() if idx + 1 < len(key_tokens) else ""
                return base(key_tokens, idx) or nxt.endswith("ly")
            ft._guard_ok = g
        ft._PAST_ONLY_IRREGULAR.update(self.past_only)
        return self

    def __exit__(self, *a):
        ft._GUARD_DET, ft._guard_ok = self.o_det, self.o_guard
        ft._PAST_ONLY_IRREGULAR.clear()
        ft._PAST_ONLY_IRREGULAR.update(self.o_past)


QUANT_DET = {"no", "each", "every", "all", "both", "another", "either", "neither", "many", "much", "several", "few"}


def still_rejected_now(llm_key, span):
    """当時のLLM出力key_phraseを、現行(本スクリプト実行時点)の決定論validatorへ通した結果。Trueなら現行Gateでも同じ除外。"""
    if not llm_key or not span:
        return None
    ok = any(_validate(llm_key, span, span, r)["ok"] for r in ("lemma_normalization", "generalize_person_dependent_reference"))
    return not ok


def rescue_probe(span: str):
    """1つの除外spanについて、(A)表層形のまま(B)現行表だけの決定論再導出(C)what-if(受理面拡大)を机上判定。"""
    res = {"span": span}
    res["surface_pass"] = {"validator": _validate(span, span, span)["ok"], "cmu": _cmu_ok(span),
                           "words": ft.count_words(span)}
    res["rederive_current_tables"] = rederive_keys(span)
    with _Whatif(det_add=QUANT_DET):
        res["whatif_W1_quantifier_determiners"] = rederive_keys(span)
    with _Whatif(det_add=QUANT_DET, adverb_ly=True):
        res["whatif_W2_plus_ly_adverb"] = rederive_keys(span)
    with _Whatif(past_only={"rang": "ring", "sang": "sing", "swam": "swim", "drank": "drink", "began": "begin",
                            "froze": "freeze", "ate": "eat", "wrote": "write", "spoke": "speak", "woke": "wake",
                            "flew": "fly", "threw": "throw", "hid": "hide", "rode": "ride", "stole": "steal"}):
        res["whatif_W3_past_only_table_completed"] = rederive_keys(span)
    return res


# ------------------------------------------------------------------ 棚卸し
def _level(path):
    m = re.search(r"[\\/](a2|b1b)[\\/]", path)
    return m.group(1) if m else "?"


def _runid(path):
    p = path.replace("\\", "/")
    p = p.split("/key_phrases")[0]
    return "/".join(p.split("/")[-3:])


def article_text_for(kpdir: str):
    for cand in (f"{kpdir}/kp_candidates/round_1/work/keywords_selector_prompt.txt", f"{kpdir}/keywords_selector_prompt.txt"):
        if os.path.exists(cand):
            t = open(cand, encoding="utf-8").read()
            i = t.find("\n---\n")
            return t[i + 5:] if i >= 0 else t
    return None


def sentence_of(text, span):
    if not text or not span:
        return None
    flat = re.sub(r"\s+", " ", text.replace("’", "'").replace("“", '"').replace("”", '"'))
    i = flat.lower().find(span.lower())
    if i < 0:
        return None
    a = max(flat.rfind(". ", 0, i), flat.rfind("? ", 0, i), flat.rfind("! ", 0, i))
    b = min([x for x in (flat.find(". ", i), flat.find("? ", i), flat.find("! ", i)) if x >= 0] or [len(flat)])
    return flat[a + 2 if a >= 0 else 0:b + 1].strip()


def inventory():
    events = _inventory_raw()
    for e in events:
        e["bucket"], e["bucket_note"] = bucket_of(e)
    return events


def _inventory_raw():
    events = []
    # ---- A: HR導入後 kp_candidates.json の dropped[](最終docに残った除外。smoke_a_mockとdocs複製は除く)
    fs = []
    for pat in ("er019_output", "er026_output", "er121_output"):
        fs += glob.glob(f"{pat}/**/kp_candidates.json", recursive=True)
    fs = [f for f in fs if "/round_" not in f.replace("\\", "/") and "smoke" not in f]
    for f in sorted(fs):
        d = json.load(open(f, encoding="utf-8"))
        fam = FAMILY_OF[f.replace("\\", "/").split("/")[0]]
        kpdir = os.path.dirname(f)
        text = article_text_for(kpdir)
        for x in d.get("dropped", []):
            reason = " / ".join(x.get("reasons") or [])
            cls, sub = classify(reason, x.get("stage"))
            ev = {"era": "HR(kp_candidates.json dropped)", "family": fam, "run": _runid(f), "level": d.get("level") or _level(f),
                  "origin": x.get("origin"), "stage": x.get("stage"), "phrase": x.get("phrase"), "reason": reason,
                  "class": cls, "sub": sub, "source": f.replace("\\", "/")}
            if cls == "RULE7_NORMALIZATION":
                k, s = rule7_parts(reason)
                ev["llm_key_phrase"], ev["source_span"] = k, s
                ev["probe"] = rescue_probe(s or x.get("phrase"))
                ev["still_rejected_now"] = still_rejected_now(k, s)
            ev["context"] = sentence_of(text, ev.get("source_span") or x.get("phrase"))
            events.append(ev)
    # ---- B: HR導入前の共通Gate除外(fulltext_p2 runのみ=現行Gate世代)。selector gate + canonicalization INVALID
    seen = set()
    for pat in ("er019_output", "er026_output", "er121_output"):
        for f in glob.glob(f"{pat}/**/keywords_runtime_metadata.json", recursive=True):
            fp = f.replace("\\", "/")
            if "/kp_candidates/round_" in fp:
                continue
            d = json.load(open(f, encoding="utf-8"))
            if (d.get("kp_backend_used") or d.get("kp_backend")) != "fulltext_p2":
                continue
            fam = FAMILY_OF[pat]
            kpdir = os.path.dirname(f)
            text = article_text_for(kpdir)
            for a in d.get("attempts_detail", []):
                for ir in a.get("item_reasons") or []:
                    reason = " / ".join(ir.get("reasons") or [])
                    cls, sub = classify(reason)
                    key = (fam, _runid(fp), _level(fp), "selector_gate", ir.get("phrase"), cls)
                    if key in seen:
                        continue
                    seen.add(key)
                    events.append({"era": "preHR(outer-retry全置換)", "family": fam, "run": _runid(fp), "level": _level(fp),
                                   "stage": "selector_gate(validate/CMU)", "phrase": ir.get("phrase"), "reason": reason,
                                   "class": cls, "sub": sub, "context": sentence_of(text, ir.get("phrase")), "source": fp})
        for f in glob.glob(f"{pat}/**/canonicalization_runtime_metadata.json", recursive=True):
            fp = f.replace("\\", "/")
            if "/kp_candidates/round_" in fp:
                continue
            kmeta = os.path.join(os.path.dirname(f), "keywords_runtime_metadata.json")
            if not os.path.exists(kmeta):
                continue
            km = json.load(open(kmeta, encoding="utf-8"))
            if (km.get("kp_backend_used") or km.get("kp_backend")) != "fulltext_p2":
                continue
            d = json.load(open(f, encoding="utf-8"))
            fam = FAMILY_OF[pat]
            text = article_text_for(os.path.dirname(f))
            for a in d.get("attempts_detail", []):
                parsed_items = (a.get("parsed") or {}).get("items") or []
                for ir in a.get("item_reasons") or []:
                    reason = " / ".join(ir.get("reasons") or [])
                    cls, sub = classify(reason)
                    k, s = rule7_parts(reason)
                    phrase = s
                    if not phrase and ir.get("rank") and ir["rank"] <= len(parsed_items):
                        phrase = parsed_items[ir["rank"] - 1].get("key_phrase")
                    key = (fam, _runid(fp), _level(fp), "canon", phrase, cls)
                    if key in seen:
                        continue
                    seen.add(key)
                    ev = {"era": "preHR(outer-retry全置換)", "family": fam, "run": _runid(fp), "level": _level(fp),
                          "stage": "canonicalization", "phrase": phrase, "reason": reason, "class": cls, "sub": sub,
                          "context": sentence_of(text, phrase), "source": fp}
                    if cls == "RULE7_NORMALIZATION":
                        ev["llm_key_phrase"], ev["source_span"] = k, s
                        ev["probe"] = rescue_probe(s) if s else None
                        ev["still_rejected_now"] = still_rejected_now(k, s)
                    events.append(ev)
    return events


LEXICAL_HAVE = re.compile(r"\b(have|has|had)\s+(a|an|the|our|my|his|her|their|your|its|one's)\b", re.I)

BUCKETS = {
    "NOT_GATE": "Gate除外ではない(Human NG=復活禁止 / QA旗)",
    "NOW_PASS": "過去世代validatorの除外で、現行validatorでは既に通る",
    "S1_IN_SCOPE_MECHANICAL": "段階1: 承認済み規則内・機械的(API 0)で救済可(再導出 or 表層形revert。既存validator通過を机上確認)",
    "S2_NEEDS_NEW_RULE": "段階2: 新規則(ユーザー承認要)があれば救済可の見込み",
    "HARD": "救済困難(意味喪失・本文対応喪失・CMU必須Gate等)",
}


def bucket_of(e):
    c = e["class"]
    if c in ("HUMAN_NG_EXCLUDED", "QA_REVIEW_REQUIRED(非除外・旗)"):
        return "NOT_GATE", ""
    if c in ("OVERFLOW_OVER5_CALL2", "DUPLICATE_OF_TOP3", "DUPLICATE_IN_SELECTION"):
        return "NOT_GATE", "重複/超過は救済対象外(設計上の正当な除外)"
    if c == "RULE7_NORMALIZATION":
        if e.get("still_rejected_now") is False:
            return "NOW_PASS", ""
        pr = e.get("probe") or {}
        sp = pr.get("surface_pass") or {}
        base = pr.get("rederive_current_tables") or []
        if base:
            return "S1_IN_SCOPE_MECHANICAL", "再導出:" + base[0]
        if sp.get("validator") and sp.get("cmu"):
            wi = pr.get("whatif_W1_quantifier_determiners") or pr.get("whatif_W3_past_only_table_completed") or pr.get("whatif_W2_plus_ly_adverb")
            note = "表層形revert"
            if wi:
                note += "(基本形化は閉表/guard拡張[新規則]で可: " + wi[0] + ")"
            return "S1_IN_SCOPE_MECHANICAL", note
        return "HARD", "表層形もGate不通過"
    if c == "WORDCOUNT_OVER5":
        return "S2_NEEDS_NEW_RULE", "部分列短縮(選定段。意味反転リスクあり=AI/HR判断)"
    if c == "FINITE_AUX_TOKEN":
        if LEXICAL_HAVE.search(e["phrase"] or ""):
            return "S2_NEEDS_NEW_RULE", "lexical have(語形リストが助動詞と区別しない)=Gate精緻化"
        return "HARD", "法助動詞/進行形aux等。句の核であり縮約すると意味喪失"
    if c in ("CMU_UNREGISTERED", "NOT_CONTIGUOUS_IN_TEXT", "CROSS_SENTENCE"):
        return "HARD", {"CMU_UNREGISTERED": "CMU必須Gate(代替合格禁止)", "NOT_CONTIGUOUS_IN_TEXT": "本文に無い(本文対応喪失)", "CROSS_SENTENCE": "文境界またぎ"}[c]
    return "HARD", "分類外"


def summarize(events):
    out = {}
    for era in sorted({e["era"] for e in events}):
        ev = [e for e in events if e["era"] == era]
        by = collections.Counter((e["class"], e["sub"]) for e in ev)
        byfam = collections.Counter((e["family"], e["class"]) for e in ev)
        uniq = collections.defaultdict(set)
        for e in ev:
            uniq[(e["class"], e["sub"])].add((e["family"], (e["phrase"] or "").lower()))
        bk = collections.Counter(e["bucket"] for e in ev)
        bku = collections.defaultdict(set)
        for e in ev:
            bku[e["bucket"]].add((e["family"], (e["phrase"] or "").lower()))
        out[era] = {"total": len(ev),
                    "buckets": {k: {"events": bk[k], "unique_family_phrase": len(bku[k])} for k in BUCKETS if bk[k]},
                    "buckets_by_family": {f"{f}|{b}": n for (f, b), n in sorted(collections.Counter((e["family"], e["bucket"]) for e in ev).items())},
                    "by_class": {f"{c}/{s}" if s else c: {"events": n, "unique_family_phrase": len(uniq[(c, s)])} for (c, s), n in sorted(by.items())},
                    "by_family_class": {f"{fam}|{c}": n for (fam, c), n in sorted(byfam.items())}}
    return out


def write_md(events, summ, path):
    L = ["# EXCLUSION_PATTERNS_01 (script出力部。API 0・read-only)", "",
         "生成: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/tools/kp_exclusion_inventory_01.py`。分類は現行Gateの理由原文の機械分類。", ""]
    for era, s in summ.items():
        L += [f"## {era}: 除外イベント {s['total']}件", "", "| 区分(class/sub) | イベント数 | 一意(Family,句)数 |", "|---|---|---|"]
        for k, v in s["by_class"].items():
            L.append(f"| {k} | {v['events']} | {v['unique_family_phrase']} |")
        L += ["", "### 救済区分(bucket)", "", "| 区分 | イベント数 | 一意(Family,句)数 | 意味 |", "|---|---|---|---|"]
        for k, v in s["buckets"].items():
            L.append(f"| {k} | {v['events']} | {v['unique_family_phrase']} | {BUCKETS[k]} |")
        L += ["", "Family別bucket: " + ", ".join(f"{k}={v}" for k, v in s["buckets_by_family"].items())]
        L += ["", "Family別: " + ", ".join(f"{k}={v}" for k, v in s["by_family_class"].items()), ""]
    L += ["## 実例(全イベント)", "", "| era | Family | run | lv | stage | 句 | class/sub | bucket(note) | 理由(先頭110字) |", "|---|---|---|---|---|---|---|---|---|"]
    for e in events:
        L.append("| {} | {} | {} | {} | {} | `{}` | {} | {}{} | {} |".format(
            e["era"].split("(")[0], e["family"], e["run"], e["level"], e["stage"], e["phrase"],
            e["class"] + ("/" + e["sub"] if e["sub"] else ""), e["bucket"], (" (" + e["bucket_note"] + ")" if e["bucket_note"] else ""),
            (e["reason"] or "")[:110].replace("|", "/")))
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


# ------------------------------------------------------------------ recheck
def recheck(path):
    import er030_key_phrase_db_hybrid_core_01 as core   # 本文→文unit(決定論・通信なし)
    cases = json.load(open(path, encoding="utf-8"))["cases"]
    out = []
    for c in cases:
        r = {"id": c["id"], "note": c.get("note"), "method": c.get("method"), "scope": c.get("scope"),
             "display_phrase": c["display_phrase"], "proposed_key": c["proposed_key"]}
        key = c["proposed_key"]
        # 選定段のsub-span救済(selection_phrase有)は、新しい選定句がdisplay=source_spanになる。validator_displayで上書き可(Rule7再現用)
        disp = c.get("validator_display") or c.get("selection_phrase") or c["display_phrase"]
        span = c.get("source_span") or disp
        r["words"] = ft.count_words(key)
        r["canonicalization_validator"] = _validate(key, disp, span, c.get("normalization_reason", "lemma_normalization"))
        r["cmu_reasons"] = cmu.reasons_for_phrase(key)
        r["finite_aux_token"] = kc._contains_finite_auxiliary(key)
        if c.get("article_dir"):
            text = article_text_for(c["article_dir"])
            units = core.build_sentence_units(text)
            v = ft.validate_and_resolve([{"phrase": c.get("selection_phrase") or key, "declared_word_count": None}], units)
            r["selection_gate"] = {"ok": v["ok"], "item_reasons": v["item_reasons"],
                                   "span": (v["resolved"][0].get("source_span") if v["resolved"] else None),
                                   "sentence_id": (v["resolved"][0].get("source_sentence_id") if v["resolved"] else None)}
        r["overall_pass"] = bool(r["canonicalization_validator"]["ok"] and not r["cmu_reasons"] and not r["finite_aux_token"]
                                 and (r.get("selection_gate", {"ok": True})["ok"]))
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--recheck")
    a = ap.parse_args()
    if a.recheck:
        res = recheck(a.recheck)
        json.dump({"results": res}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        for r in res:
            print(r["id"], "PASS" if r["overall_pass"] else "FAIL", repr(r["proposed_key"]), r["words"], "語",
                  "validator_ok=%s" % r["canonicalization_validator"]["ok"], "cmu=%s" % (r["cmu_reasons"] or "ok"),
                  "sel=%s" % (r.get("selection_gate", {}).get("ok", "n/a")))
        return
    ev = inventory()
    summ = summarize(ev)
    json.dump({"summary": summ, "events": ev}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if a.md:
        write_md(ev, summ, a.md)
    for era, s in summ.items():
        print(era, s["total"])
        for k, v in s["by_class"].items():
            print("  ", k, v)
        for k, v in s["buckets"].items():
            print("  [bucket]", k, v)


if __name__ == "__main__":
    main()
