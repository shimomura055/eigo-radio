# -*- coding: utf-8 -*-
"""er114_fx_numeric_trace_01.py  (DEV専用・読み取り専用・API 0円・Production不変)

FX-CORE-NUMERIC-RETENTION-TRIAL-01 Phase 0。既存Family X run artifactから、B3が印を付けた【中核数値】が
段(R0 / R1 / R2 / 英訳Standard / 英訳Advanced)ごとに本文へ残るかを決定論で計測する「計測器の原型」。
ユーザー原文§5-2の指標(選定数・必要数・最終掲載数・不要掲載数)の計測部分。

照合規則(新しい数値選定システムは作らない。B3自身の抽出・照合関数を読み取りで再利用する):
  - 日本語本文: er053_b3_deterministic_producer_01 の nfkc / contains(境界つき一致) / extract_surfaces / surface_kind /
    main_numbers / unit_of を import して使う(B3が表記を数えるのと同じ規則 = 表記ゆれ[カンマ・全半角・約/超の有無・万億の展開]を同じ基準で吸収)。
      一致 = (A) NFKC後の境界つき文字列一致、または (B) 同じ種類・同じ主数字(+同じ単位)の表記が本文にある、
             または (C) 範囲表記は「a と b が12字以内で並び、間に 〜～から- 等」がある。
  - 英訳本文: カンマ除去・million/billion/thousand展開後の値集合に主数字が含まれる(範囲は a,b の両方が20字以内)。日付種別は英訳では未評価(n/a)。
  - 曖昧(AMBIG): 単位なしの小さい整数(<=31)は誤照合を避けるため保持率の分母から除く(本数として別記)。
  - 丸め: 概数可(rounding_overlay.json)の数値は「約」「超」の有無や丸め表記を許容(値一致ではなく、同じ桁以上の一致を許容しない=厳密一致のみ。
    丸めで表記が変わった場合は MISS として記録され、手作業照合の対象になる)。
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er053_b3_deterministic_producer_01 as P   # read-only import (関数のみ使用)

OUT_DIR = os.path.join(ROOT, "er114_output", "fx_numeric_trace_01")
WAVE = "〜～~"


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def nf(s):
    return unicodedata.normalize("NFKC", s or "")


def skey(s):
    k = P.surface_kind(s)
    return (k, P.main_numbers(s, k), P.unit_of(s))


def is_ambiguous(s):
    k, key, unit = skey(s)
    if k == "magnitude" and key[0] == "M" and key[1] is not None and not unit:
        try:
            v = float(key[1])
            return v <= 31 and v == int(v)
        except ValueError:
            return False
    return False


# ---------------- 日本語本文の照合 ----------------
def ja_present(surf, text, text_keys):
    if not surf or not text:
        return False
    if P.contains(text, surf):
        return True
    k, key, unit = skey(surf)
    for (tk, tkey, tunit) in text_keys:
        if tk == k and tkey == key and (unit == tunit or not unit or not tunit):
            return True
    if k == "range" and key[0] == "R" and len(key[1]) == 2:
        a, b = key[1]
        t = nf(text).replace(",", "")
        if re.search(rf"(?<![\d.]){re.escape(a)}[^\d]{{0,12}}(?:[{re.escape(WAVE)}\-–ー]|から)[^\d]{{0,6}}{re.escape(b)}(?![\d])", t):
            return True
    return False


# ---------------- 英訳本文の照合 ----------------
_SCALE = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9, "trillion": 10 ** 12}
_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
_WORDS.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100})
_UNIT_HINT = {"か月": r"month", "ヶ月": r"month", "年": r"year", "年前": r"year", "%": r"percent|%", "倍": r"times|fold|tripl|doubl|quadrupl",
              "ドル": r"dollar|[$]"}


def en_values(text):
    """(値の集合, 正規化済み本文, [(値, 直後30字)])。綴り数字(seven等)も値として扱う。"""
    t = nf(text).replace(",", "")
    vals, ctx = set(), []
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(thousand|million|billion|trillion)?", t, re.I):
        v = P.dec(repr(float(m.group(1)) * (_SCALE[m.group(2).lower()] if m.group(2) else 1)))
        vals.add(v)
        ctx.append((v, t[m.end(): m.end() + 30].lower()))
    for m in re.finditer(r"\b(" + "|".join(sorted(_WORDS, key=len, reverse=True)) + r")\b(?:\s+(thousand|million|billion|trillion))?", t, re.I):
        v = P.dec(repr(float(_WORDS[m.group(1).lower()]) * (_SCALE[m.group(2).lower()] if m.group(2) else 1)))
        vals.add(v)
        ctx.append((v, t[m.end(): m.end() + 30].lower()))
    return vals, t, ctx


def en_present(surf, text):
    k, key, unit = skey(surf)
    if k in ("date_time", "year", "ordinal", "name_embedded"):
        return None   # n/a(英訳の日付は未評価)
    vals, t, ctx = en_values(text)
    if k == "range" and key[0] == "R" and len(key[1]) == 2:
        a, b = key[1]
        return bool(re.search(rf"(?<![\d.]){re.escape(a)}[^\d]{{0,20}}{re.escape(b)}(?![\d])", t)) or             bool(re.search(rf"{re.escape(a)}.{{0,25}}{re.escape(b)}", t))
    if key[0] == "M" and key[1] is not None:
        hint = _UNIT_HINT.get(unit)
        for v, after in ctx:
            if v == key[1] and (not hint or re.search(hint, after)):
                return True
        # 値は単位なしで現れることもある(例: 25% を "a quarter" 等)。単位ヒントなしの一致は上で判定済み
        return False
    return None


# ---------------- run単位の計測 ----------------
def stage_texts(run):
    d = os.path.join(run, "ja_writer")
    out = {}
    pr0 = os.path.join(d, "factlock", "r0.md")
    out["R0"] = rd(pr0) if os.path.exists(pr0) else None
    for name, rel in (("R1", "revision1.md"), ("R2", "revision2.md")):
        p = os.path.join(d, rel)
        out[name] = rd(p) if os.path.exists(p) else None
    for name, rel in (("EN_Std", "a2/article.md"), ("EN_Adv", "b1b/article.md")):
        p = os.path.join(run, rel)
        out[name] = rd(p) if os.path.exists(p) else None
    return out


def analyze(run, labels=None):
    ann = rj(os.path.join(run, "storyline_b3", "annotation.json"))
    texts = stage_texts(run)
    if not texts["R0"] or not texts["R2"]:
        return None
    evp = os.path.join(run, "storyline_b3", "fact_selection_evidence.json")
    storyline = ""
    if os.path.exists(evp):
        storyline = rj(evp).get("selected_storyline", "")
    r0meta_p = os.path.join(run, "ja_writer", "factlock", "r0_meta.json")
    tags_used = set(rj(r0meta_p).get("tags_used", [])) if os.path.exists(r0meta_p) else set()
    facts = {f["n"]: set(f["ledger_ids"]) for f in ann.get("facts", [])}
    overlay_p = os.path.join(run, "storyline_b3", "rounding_overlay.json")
    approx_ok, approx_forms = set(), {}
    if os.path.exists(overlay_p):
        for e in rj(overlay_p).get("entries", []):
            if e.get("final_decision") == "APPROXIMATE_OK":
                for s in e.get("surfaces", []):
                    approx_ok.add(s.get("surface"))
                    if s.get("approx"):
                        approx_forms[s.get("surface")] = s.get("approx")
    story_surf = {nf(s) for s in P.extract_surfaces(storyline)}
    ja_keys = {st: [skey(s) for s in P.extract_surfaces(texts[st] or "")] for st in ("R0", "R1", "R2")}

    nums = ann["numbers"]
    core = [n for n in nums if n["class"] == "core"]
    periph = [n for n in nums if n["class"] != "core"]
    rows = []
    for n in core:
        s = n["surface"]
        fact_ns = sorted(fn for fn, ids in facts.items() if ids & set(n.get("ledger_ids", [])))
        fact_used = any(f"F{fn}" in tags_used for fn in fact_ns) if tags_used else None
        row = {"surface": s, "kind": P.surface_kind(s), "has_wave_dash": any(c in s for c in WAVE),
               "ambiguous": is_ambiguous(s), "approx_ok": s in approx_ok, "in_storyline": nf(s) in story_surf or P.contains(storyline, s),
               "brief_fact_ns": fact_ns, "fact_used_by_R0": fact_used, "present": {}}
        for st in ("R0", "R1", "R2"):
            row["present"][st] = ja_present(s, texts[st], ja_keys[st]) or bool(approx_forms.get(s) and P.contains(texts[st] or "", approx_forms[s]))
        for st in ("EN_Std", "EN_Adv"):
            row["present"][st] = en_present(s, texts[st]) if texts[st] else None
        rows.append(row)
    # 非中核数値(本文に出た数値で、core表記と一致しないもの)
    def classify(stage):
        cnt = {"core": 0, "peripheral": 0, "uncatalogued": 0}
        lists = {"peripheral": [], "uncatalogued": []}
        seen = set()
        for s in P.extract_surfaces(texts[stage] or ""):
            k = skey(s)
            if k in seen:
                continue
            seen.add(k)
            if any(skey(c["surface"])[:2] == k[:2] for c in core):
                cnt["core"] += 1
            elif any(skey(c["surface"])[:2] == k[:2] for c in periph):
                cnt["peripheral"] += 1
                lists["peripheral"].append(s)
            else:
                cnt["uncatalogued"] += 1
                lists["uncatalogued"].append(s)
        return cnt, lists
    body = {}
    for st in ("R0", "R1", "R2"):
        c, l = classify(st)
        body[st] = {"counts": c, "peripheral": l["peripheral"], "uncatalogued": l["uncatalogued"]}
    # 段間遷移
    ev = [r for r in rows if not r["ambiguous"]]
    trans = {
        "lost_R0_to_R1": [r["surface"] for r in ev if r["present"]["R0"] and not r["present"]["R1"]],
        "lost_R1_to_R2": [r["surface"] for r in ev if r["present"]["R1"] and not r["present"]["R2"]],
        "gained_core_R1": [r["surface"] for r in ev if not r["present"]["R0"] and r["present"]["R1"]],
        "gained_core_R2": [r["surface"] for r in ev if not r["present"]["R1"] and r["present"]["R2"]],
        "periph_added_R1": sorted(set(body["R1"]["peripheral"]) - set(body["R0"]["peripheral"])),
        "periph_added_R2": sorted(set(body["R2"]["peripheral"]) - set(body["R1"]["peripheral"])),
        "uncat_added_R1": sorted(set(body["R1"]["uncatalogued"]) - set(body["R0"]["uncatalogued"])),
        "uncat_added_R2": sorted(set(body["R2"]["uncatalogued"]) - set(body["R1"]["uncatalogued"])),
    }
    stages = ["R0", "R1", "R2", "EN_Std", "EN_Adv"]
    summ = {"n_core": len(core), "n_core_evaluable": len(ev), "n_ambiguous": len(core) - len(ev),
            "n_core_in_storyline": sum(1 for r in rows if r["in_storyline"]), "n_storyline_numbers": len(story_surf),
            "n_wave_dash_core": sum(1 for r in rows if r["has_wave_dash"]),
            "kept": {st: sum(1 for r in ev if r["present"][st]) for st in stages if texts[st]},
            "n_en_evaluable": sum(1 for r in ev if r["present"]["EN_Std"] is not None) if texts["EN_Std"] else None}
    r2_text = texts["R2"] or ""
    density = {"r2_chars": len(r2_text), "r2_numeric_surfaces_total": len(P.extract_surfaces(r2_text)),
               "r2_numeric_surfaces_unique": len({skey(x)[:2] for x in P.extract_surfaces(r2_text)})}
    wave_counts = {st: sum((texts[st] or "").count(c) for c in WAVE) for st in ("R0", "R1", "R2")}
    return {"run": os.path.relpath(run, ROOT).replace("\\", "/"), "wave_dash_in_body": wave_counts, "density": density, "storyline": storyline, "storyline_numbers": sorted(story_surf),
            "n_peripheral_catalogued": len(periph), "core": rows, "body_noncore": body, "transitions": trans, "summary": summ,
            "texts_present": {k: bool(v) for k, v in texts.items()}}


def discover():
    runs = []
    for p in sorted(glob.glob(os.path.join(ROOT, "er019_output", "*", "run_*", "storyline_b3", "annotation.json"))):
        run = os.path.dirname(os.path.dirname(p))
        if os.path.exists(os.path.join(run, "ja_writer", "factlock", "r0.md")) and os.path.exists(os.path.join(run, "ja_writer", "revision2.md")):
            runs.append(run)
    return runs


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = []
    for run in discover():
        try:
            r = analyze(run)
        except Exception as e:  # 計測器の堅牢性: 1 runの失敗で全体を止めない(記録する)
            r = {"run": os.path.relpath(run, ROOT).replace("\\", "/"), "error": repr(e)}
        if r:
            results.append(r)
    with open(os.path.join(OUT_DIR, "trace_all_runs.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"runs analyzed: {len(results)}")
    for r in results:
        if "error" in r:
            print("ERR", r["run"], r["error"])
            continue
        s = r["summary"]
        print(r["run"], "core", s["n_core"], "eval", s["n_core_evaluable"], "kept", s["kept"], "story#", s["n_storyline_numbers"], "core_in_story", s["n_core_in_storyline"])


if __name__ == "__main__":
    main()


def aggregate(results):
    """段別・原因別の集計(R0=Writer初稿で落ちた中核数値の内訳)。AMBIGUOUSは分母から除く。"""
    ok = [r for r in results if "error" not in r and r["summary"]["n_core_evaluable"] > 0]
    agg = {"runs": len(ok), "core_eval": 0, "kept": {"R0": 0, "R1": 0, "R2": 0, "EN_Std": 0, "EN_Adv": 0},
           "dropped_R0": 0, "dropped_fact_unused": 0, "dropped_fact_used_number_omitted": 0,
           "wave": {"n": 0, "kept_R0": 0}, "nonwave": {"n": 0, "kept_R0": 0},
           "story": {"n": 0, "kept_R0": 0}, "nonstory": {"n": 0, "kept_R0": 0},
           "R1_R2_losses": 0, "R1_R2_core_gains": 0, "periph_added_R1R2": 0, "uncat_added_R1R2": 0,
           "periph_in_R2_body": 0, "uncat_in_R2_body": 0, "core_in_R2_body": 0}
    for r in ok:
        for c in r["core"]:
            if c["ambiguous"]:
                continue
            agg["core_eval"] += 1
            for st in agg["kept"]:
                if c["present"].get(st):
                    agg["kept"][st] += 1
            g = agg["wave"] if c["has_wave_dash"] else agg["nonwave"]
            g["n"] += 1
            g["kept_R0"] += 1 if c["present"]["R0"] else 0
            g = agg["story"] if c["in_storyline"] else agg["nonstory"]
            g["n"] += 1
            g["kept_R0"] += 1 if c["present"]["R0"] else 0
            if not c["present"]["R0"]:
                agg["dropped_R0"] += 1
                if c["fact_used_by_R0"] is False:
                    agg["dropped_fact_unused"] += 1
                else:
                    agg["dropped_fact_used_number_omitted"] += 1
        t = r["transitions"]
        agg["R1_R2_losses"] += len(t["lost_R0_to_R1"]) + len(t["lost_R1_to_R2"])
        agg["R1_R2_core_gains"] += len(t["gained_core_R1"]) + len(t["gained_core_R2"])
        agg["periph_added_R1R2"] += len(t["periph_added_R1"]) + len(t["periph_added_R2"])
        agg["uncat_added_R1R2"] += len(t["uncat_added_R1"]) + len(t["uncat_added_R2"])
        b = r["body_noncore"]["R2"]["counts"]
        agg["periph_in_R2_body"] += b["peripheral"]
        agg["uncat_in_R2_body"] += b["uncatalogued"]
        agg["core_in_R2_body"] += b["core"]
    return agg


if __name__ == "__main__" and os.environ.get("ER114_AGG"):
    res = rj(os.path.join(OUT_DIR, "trace_all_runs.json"))
    a = aggregate(res)
    with open(os.path.join(OUT_DIR, "trace_aggregate.json"), "w", encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=1)
    print(json.dumps(a, ensure_ascii=False, indent=1))


# ---------------- ユーザー原文§5-2 指標(選定数・必要数・最終掲載数・不要掲載数)と表 ----------------
# 必要数の定義(Phase 0 は基準案のみ。判定は Phase 1 以降に事前登録[結果を見る前にlabelを固定]する):
#   N1 記事の中心的な問い(タイトル/Storyline)への答えそのもの  N2 欠くと中心主張が曖昧・誤解を招く(例: 「ごくわずか」だけで規模がない)
#   N3 保持する数値の解釈に不可欠な前提・期間(推定条件)  いずれにも当たらない数値は「任意(掲載してよいが必須でない)」または「不要」。
# 月の記事のみユーザー表(§3)で確定。他記事は暫定proxy = 「B3 Storyline文に現れる中核数値」(core ∩ storyline)。
MOON_LABELS = {"required": ["約42〜46"], "needed_conditional": ["約4億年"], "note": "ユーザー§3表。約11cm/100万年・750m〜1.1kmは不要(B3上は周辺数値)"}


def metrics_row(r):
    s = r["summary"]
    core = r["core"]
    is_moon = "moon_shrinking" in r["run"]
    if is_moon:
        need = [c for c in core if c["surface"] in MOON_LABELS["required"] + MOON_LABELS["needed_conditional"]]
        basis = "user_table"
    else:
        need = [c for c in core if c["in_storyline"] and not c["ambiguous"]]
        basis = "proxy(core∩storyline)"
    b2 = r["body_noncore"]["R2"]
    return {"run": r["run"], "selected_core": s["n_core"], "selected_core_evaluable": s["n_core_evaluable"],
            "needed": len(need), "needed_basis": basis, "needed_kept_R2": sum(1 for c in need if c["present"]["R2"]),
            "published_core_R2": b2["counts"]["core"], "unneeded_published_R2": b2["counts"]["peripheral"] + b2["counts"]["uncatalogued"],
            "unneeded_list": b2["peripheral"] + b2["uncatalogued"], "density": r["density"], "wave_dash_core": s["n_wave_dash_core"]}


def write_table(results):
    mark = lambda v: "-" if v is None else ("Y" if v else "n")
    lines = ["# TRACE_TABLE_01 (er114_fx_numeric_trace_01.py 出力、API 0円、2026-10-25)", "",
             "凡例: Y=本文に有り / n=無し / -=評価対象外(英訳の日付等)。AMBIG=単位なし小整数で誤照合回避のため分母から除外。wave=表記に波ダッシュ(〜/～)を含む範囲値。story=B3 Storyline文に現れる数値。",
             "fact_unused=その中核数値を含むFactをR0が1度も引用していない(タグ未使用)。",
             "", "## 1. run × 中核数値 × 段", "", "| run | 中核数値 | 種別 | R0 | R1 | R2 | EN Std | EN Adv | 備考 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r:
            continue
        for c in r["core"]:
            p = c["present"]
            note = ",".join(x for x in (["AMBIG"] if c["ambiguous"] else []) + (["wave"] if c["has_wave_dash"] else []) +
                            (["story"] if c["in_storyline"] else []) + (["fact_unused"] if c["fact_used_by_R0"] is False else []) +
                            (["概数可"] if c["approx_ok"] else []))
            lines.append(f"| {r['run'].replace('er019_output/', '')} | {c['surface']} | {c['kind']} | {mark(p['R0'])} | {mark(p['R1'])} | {mark(p['R2'])} | {mark(p.get('EN_Std'))} | {mark(p.get('EN_Adv'))} | {note} |")
    lines += ["", "## 2. 4指標(選定数・必要数・最終掲載数・不要掲載数) ※月はユーザー§3表、他はproxy(core∩storyline、Phase 1以降で判定基準N1〜N3により確定)", "",
              "| run | 選定数(core) | 評価可能 | 必要数 | 必要の基準 | 必要のうちR2掲載 | R2に載ったcore数 | 不要掲載(周辺+未分類)R2 | 不要の中身 | R2字数 | R2数値表記(ユニーク) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r or r["summary"]["n_core"] == 0:
            continue
        m = metrics_row(r)
        lines.append(f"| {m['run'].replace('er019_output/', '')} | {m['selected_core']} | {m['selected_core_evaluable']} | {m['needed']} | {m['needed_basis']} | {m['needed_kept_R2']} | {m['published_core_R2']} | {m['unneeded_published_R2']} | {','.join(m['unneeded_list'])} | {m['density']['r2_chars']} | {m['density']['r2_numeric_surfaces_unique']} |")
    lines += ["", "## 3. 段間遷移(R0→R1→R2で中核数値/周辺数値が増減したrun)", ""]
    any_t = False
    for r in results:
        if "error" in r:
            continue
        t = {k: v for k, v in r["transitions"].items() if v}
        if t:
            any_t = True
            lines.append(f"- {r['run']}: {t}")
    if not any_t:
        lines.append("- 該当なし(全runで、R1/R2による中核数値の脱落・追加、周辺数値の追加は0)。")
    with open(os.path.join(OUT_DIR, "TRACE_TABLE_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__" and os.environ.get("ER114_AGG"):
    write_table(res)
