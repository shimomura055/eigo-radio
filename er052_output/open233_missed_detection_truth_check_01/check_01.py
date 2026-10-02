# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_46: 見逃し型の事実確認(read-only集計)。

【性質】既存の er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json、
委任_44のcases_detail_01.csv、委任_41のclaims_detail_01.csv、既存fixtureの監査JSON(prompt)を「読むだけ」。
LLM/API/TTS/Web Search/Trialは一切使わない。標準ライブラリのみ。既存モジュールはimportしない。
出力: 同ディレクトリの results_01.json と cases_01.csv。

【定義】
 問A: meta_run03_standard全実行(iter5〜rep22の全sample)で、文「Some calls needed user information to continue.」
   が(1)最終EN記事に元のまま(完全一致、空白正規化のみ)残るか (2)その実行中のStage2結果にBLOCKING(最終materiality)で
   一度でも指摘されたか(文との包含関係=正規化文字列の一方が他方を含む、で判定) (3)最終状態。
 問B: cases_detail_01.csvのP2a/P2b行を(instance, fact, 正規化claim[外側引用符除去・空白/大小/曲線引用符正規化])で
   重複排除し「種類」とする。各種類の代表文字列(元記事に逐語で存在する形)が、同instanceの他実行の最終記事に完全一致
   (大小区別あり、空白正規化のみ)で残り、一度もBLOCKING指摘されず、最終状態が解消(RESOLVED_*/ACCEPTABLE_STAGE1)の
   実行を数える。類似度は使わない。
 問C: 全実行のStage2結果のうち最終materiality==BLOCKINGで、claimがEN記事の見出し行(# で始まる行)の全部または一部を
   含むもの(文字列照合で確定した範囲が見出し行と重なる)を数える。
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ER = os.path.join(ROOT, "er052_output")
TARGET_NAMES = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")  # 委任_44と同じ範囲
EXTRA_NAMES = re.compile(r"rep22$")  # 並行タスク(委任_42)が生成中。参考扱い(集計外)
FIXTURE = os.path.join(ER, "open233_self_recovery_flow_runner_01_rep19", "stage1_fixtures",
                       "meta_run03_standard_iter8_cycle1_frozen.json")
CASES44 = os.path.join(ER, "open233_cycle_new_issue_analysis_01", "cases_detail_01.csv")
AUDIT_META = os.path.join(ROOT, "er019_output", "family_x_refresh_e2e_01", "meta", "run_03", "a2", "audit",
                          "deviation_checks", "standard_attempt1.json")
TARGET_SENT = "Also, some calls needed user information to continue."
RESOLVED_STATES = ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE", "RESOLVED_STAGE2_DOWNGRADE", "ACCEPTABLE_STAGE1")

CURLY_MAP = {"’": "'", "‘": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"'}
QUOTE_PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
FRAG_RE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
JA_RE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")


def is_ja(s):
    t = re.sub(r"\s", "", s)
    return bool(t) and len(JA_RE.findall(t)) / len(t) >= 0.15


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def strip_one_pair(s):
    s = s.strip()
    if len(s) >= 2:
        for o, c in QUOTE_PAIRS:
            if s[0] == o and s[-1] == c:
                return s[1:-1].strip()
    return s


def norm_loose(s):
    s = ws(strip_one_pair(s or ""))
    return "".join(CURLY_MAP.get(ch, ch) for ch in s).lower()


def find_all(text, sub):
    out, i = [], 0
    if not sub:
        return out
    while True:
        j = text.find(sub, i)
        if j < 0:
            return out
        out.append((j, j + len(sub)))
        i = j + len(sub)


def norm_with_map(text, lower):
    chars, spans = [], []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            chars.append(" ")
            spans.append((i, j))
            i = j
            continue
        ch2 = CURLY_MAP.get(ch, ch)
        if lower:
            lo = ch2.lower()
            ch2 = lo if len(lo) == 1 else ch2
        chars.append(ch2)
        spans.append((i, i + 1))
        i += 1
    return "".join(chars), spans


def locate(cand, text):
    """cand(1文字列)をtext内で探す(L0〜L3)。返値 list[(s,e)] (全出現)。"""
    raw = cand.strip()
    for v in (raw, strip_one_pair(raw)):
        if v:
            occ = find_all(text, v)
            if occ:
                return occ
    for lower in (False, True):
        nt, nm = norm_with_map(text, lower)
        for v in (raw, strip_one_pair(raw)):
            if not v:
                continue
            nv = norm_with_map(v.strip(), lower)[0]
            occ = find_all(nt, nv)
            if occ:
                return [(nm[a][0], nm[b - 1][1]) for a, b in occ]
    return []


def claim_spans(claim, text):
    """claim全体、または引用断片ごとに本文内の範囲を求める。"""
    occ = locate(claim, text)
    if occ:
        return occ, "whole"
    frags = [next(g for g in m.groups() if g is not None) for m in FRAG_RE.finditer(claim or "")]
    out = []
    for f in frags:
        occ = locate(f, text)
        if not occ:
            # Checkerが付加した末尾の句読点(.,;:)だけを除いて再照合(本文側の文字列は変更しない)
            f2 = f.strip().rstrip(".,;:")
            occ = locate(f2, text) if f2 and f2 != f.strip() else []
        out.extend(occ)
    return out, ("fragments" if out else "none")


def ov(a, b):
    return min(a[1], b[1]) > max(a[0], b[0])


# ------------------------------------------------------------ 読み込み
def load_runs(pattern):
    runs = []
    for dd in sorted(glob.glob(os.path.join(ER, "open233_self_recovery_flow_runner_01_*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not pattern.match(name):
            continue
        for f in sorted(glob.glob(os.path.join(dd, "instances_*", "*.json"))):
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if "cycles" not in d:
                continue
            rel = os.path.relpath(f, ER).replace("\\", "/").replace("open233_self_recovery_flow_runner_01_", "")
            runs.append({"path": rel, "dir": name, "d": d})
    return runs


def originals(runs):
    en, ja = defaultdict(set), defaultdict(set)
    for r in runs:
        cy = r["d"]["cycles"]
        if cy and cy[0].get("en_text_before_rewrite") is not None:
            en[r["d"]["instance_id"]].add(cy[0]["en_text_before_rewrite"])
        if cy and cy[0].get("ja_text_before_rewrite") is not None:
            ja[r["d"]["instance_id"]].add(cy[0]["ja_text_before_rewrite"])
    return en, ja


def final_text(run, lang, orig):
    cy = run["d"]["cycles"]
    key = "en_text_after_rewrite" if lang == "EN" else "ja_text_after_rewrite"
    for c in reversed(cy):
        if c.get(key) is not None:
            return c[key], "recorded_after_rewrite"
    return orig, "original_no_rewrite_recorded"


def cycle_text(cycles, i, lang, orig):
    """cycle i(0始まり)のRecheck対象本文。own before > 直前cycleのafter > 元記事(cycle1のみ)。"""
    kb = "en_text_before_rewrite" if lang == "EN" else "ja_text_before_rewrite"
    ka = "en_text_after_rewrite" if lang == "EN" else "ja_text_after_rewrite"
    c = cycles[i]
    if c.get(kb) is not None:
        return c[kb]
    if i > 0:
        for j in range(i - 1, -1, -1):
            if cycles[j].get(ka) is not None:
                return cycles[j][ka]
    return orig


def flagged_blocking(run, target_norm_list):
    """run内のStage2結果で最終materiality==BLOCKINGかつclaimが対象文字列と包含関係(正規化)にあるもの。"""
    hits, nonblock = [], []
    for c in run["d"]["cycles"]:
        for s in c["stage2_results"]:
            cl = s["dev"].get("claim_in_article", "") or ""
            cands = [norm_loose(cl)] + [norm_loose(next(g for g in m.groups() if g is not None)) for m in FRAG_RE.finditer(cl)]
            rel = False
            for cn in cands:
                if len(cn) < 12:
                    continue
                for tn in target_norm_list:
                    if cn in tn or tn in cn:
                        rel = True
            if rel:
                (hits if s["materiality"] == "BLOCKING" else nonblock).append((c["cycle"], s))
    return hits, nonblock


def sentences_en(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p:
            continue
        if p.startswith("#"):
            out.append(p)
            continue
        out.extend(x for x in re.split(r"(?<=[.!?])\s+", p) if x)
    return out


def sentences_ja(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p:
            continue
        out.extend(x for x in re.split(r"(?<=[。！？])", p) if x.strip())
    return out


def true_flags(dv):
    keys = ["changed_fact", "changed_scope", "changed_causality", "changed_certainty", "changed_number", "changed_actor",
            "changed_negation", "changed_comparison", "changed_time", "unsupported_new_claim", "auto_downgraded"]
    return [k for k in keys if dv.get(k) is True]


def main():
    runs = load_runs(TARGET_NAMES)
    extra = load_runs(EXTRA_NAMES)
    en_o, ja_o = originals(runs + extra)
    uniq_en = {k: v for k, v in en_o.items() if len(v) == 1}
    uniq_ja = {k: v for k, v in ja_o.items() if len(v) == 1}
    out = {"scope": {"n_runs_target": len(runs), "n_runs_extra_rep22": len(extra),
                     "en_original_variants_per_instance": {k: len(v) for k, v in en_o.items()},
                     "ja_original_variants_per_instance": {k: len(v) for k, v in ja_o.items()}}}
    fx = json.load(open(FIXTURE, encoding="utf-8"))
    fx_claims = sorted(norm_loose(x["claim_in_article"]) for x in fx["deviations"])

    # ====================================================================== 問A
    audit = json.load(open(AUDIT_META, encoding="utf-8"))
    pr = audit["prompt"]
    blocks = re.split(r"\n\n(?=\[VERIFIED\])", pr)
    ledger_hc010 = next(b for b in blocks if b.startswith("[VERIFIED] MUSE-HC-010"))
    ledger_hc010 = ledger_hc010.split("\n\n【検証対象の記事】")[0]
    ledger_neighbors = {}
    for fid in ("MUSE-HC-009", "MUSE-HC-011", "MUSE-HC-012", "MUSE-HC-015", "MUSE-HC-003"):
        ledger_neighbors[fid] = next(b for b in blocks if b.startswith(f"[VERIFIED] {fid}")).split("\n\n【検証対象の記事】")[0]
    ja_src = pr.split("【原文記事(翻訳・適応元)】")[1].strip()
    out["A1_ledger"] = {"source": AUDIT_META.replace(ROOT + os.sep, ""), "MUSE-HC-010": ledger_hc010,
                        "neighbors": ledger_neighbors}
    meta_en = uniq_en["meta_run03_standard"].pop()
    uniq_en["meta_run03_standard"] = {meta_en}
    en_orig_meta = meta_en
    sents = sentences_en(en_orig_meta)
    idx = next(i for i, s in enumerate(sents) if s == TARGET_SENT)
    out["A2_en_context"] = sents[max(0, idx - 2): idx + 3]
    jsents = sentences_ja(ja_src)
    jidx = next(i for i, s in enumerate(jsents) if "電話を進めるために利用者の情報が必要" in s)
    out["A2_ja_context"] = jsents[max(0, jidx - 2): jidx + 3]
    out["A2_ja_original_equals_recorded_c1_ja"] = (ja_src == next(iter(uniq_ja["meta_run03_standard"])).strip()
                                                    if "meta_run03_standard" in uniq_ja else None)
    out["A2_en_original_equals_audit_article"] = (audit["prompt"].split("【検証対象の記事】")[1].split("\n\n【判定対象は")[0].strip()
                                                   == en_orig_meta.strip())

    tnorm = [norm_loose(TARGET_SENT)]
    meta_runs = [r for r in runs + extra if r["d"]["instance_id"] == "meta_run03_standard"]
    a5, a3_flag, a3_unflag = [], [], []
    for r in meta_runs:
        d = r["d"]
        cy = d["cycles"]
        extra_flag = bool(EXTRA_NAMES.match(r["dir"]))
        c1_k1 = sorted(norm_loose(s["dev"]["claim_in_article"]) for s in (cy[0]["stage2_results"] if cy else [])
                       if s.get("detected_by") != "precheck" and not s["dev"].get("enumeration_source_claim"))
        frozen = bool(cy) and c1_k1 == fx_claims
        ft, ftsrc = final_text(r, "EN", en_orig_meta)
        present = TARGET_SENT in ws(ft).replace("\n", " ") if ft else None
        same_form = None
        if not present:
            m = [x for x in sentences_en(ft) if "user information" in x]
            same_form = m
        hits, nonb = flagged_blocking(r, tnorm)
        # HC-010でBLOCKINGになったもの(fact id基準)も別に数える
        fact_blocking = [(c["cycle"], s["dev"]["claim_in_article"]) for c in cy for s in c["stage2_results"]
                         if s.get("related_fact_id") == "MUSE-HC-010" and s["materiality"] == "BLOCKING"]
        resolved = d["final_state"] in RESOLVED_STATES
        a5.append({"run": r["path"], "dir": r["dir"], "excluded_inprogress_rep22": extra_flag, "stage1_frozen_fixture": frozen,
                   "n_cycles": len(cy), "final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                   "final_text_source": ftsrc, "sentence_in_final_article_verbatim": present,
                   "final_article_sentences_with_'user information'": same_form,
                   "BLOCKING_flag_cycles_sentence_level": [c for c, _ in hits],
                   "BLOCKING_flag_cycles_factid_MUSE-HC-010": [c for c, _ in fact_blocking],
                   "nonblocking_flag_cycles_sentence_level": [c for c, _ in nonb],
                   "resolved_without_human": resolved,
                   "target_pattern(原文残存&未指摘&解消)": bool(present and not hits and resolved)})
        # A-3: cycle>=2のRecheck(frozen runのみ)
        if frozen and not extra_flag:
            for i in range(1, len(cy)):
                txt = cycle_text(cy, i, "EN", en_orig_meta)
                txt_present = TARGET_SENT in ws(txt) if txt else None
                hs = [s for s in cy[i]["stage2_results"] if any(
                    (len(cn) >= 12 and (cn in tnorm[0] or tnorm[0] in cn)) for cn in
                    [norm_loose(s["dev"].get("claim_in_article", ""))])]
                if hs:
                    for s in hs:
                        dv = s["dev"]
                        a3_flag.append({"run": r["path"], "cycle": cy[i]["cycle"], "sentence_present_in_rechecked_text": txt_present,
                                        "claim_in_article": dv.get("claim_in_article"), "issue": dv.get("issue"),
                                        "severity": dv.get("severity"), "true_flags": true_flags(dv),
                                        "related_fact_id": s.get("related_fact_id"), "origin": dv.get("origin"),
                                        "llm_materiality": s.get("llm_materiality"), "final_materiality": s["materiality"],
                                        "floor_reason": s.get("floor_reason"), "floor_cited_materiality": s.get("floor_cited_materiality"),
                                        "floor_cited_reason": s.get("floor_cited_reason"), "stage2_route": s.get("stage2_route"),
                                        "basis": s.get("basis"), "rewrite_kind": s.get("rewrite_kind"),
                                        "auto_downgraded": dv.get("auto_downgraded"), "severity_final": dv.get("severity_final"),
                                        "detected_by": s.get("detected_by"), "qualifier_present": dv.get("qualifier_present"),
                                        "explanation": dv.get("explanation"), "ledger_field_basis": dv.get("ledger_field_basis")})
                else:
                    a3_unflag.append({"run": r["path"], "cycle": cy[i]["cycle"], "sentence_present_in_rechecked_text": txt_present,
                                      "n_stage2_results": len(cy[i]["stage2_results"]),
                                      "results": [(s.get("related_fact_id"), s["materiality"], (s["dev"].get("claim_in_article") or "")[:110])
                                                  for s in cy[i]["stage2_results"]]})
    out["A3_flagged_rechecks"] = a3_flag
    out["A3_unflagged_rechecks"] = a3_unflag
    out["A5_table"] = a5
    cnt = [x for x in a5 if not x["excluded_inprogress_rep22"]]
    out["A5_counts"] = {
        "n_runs(excl rep22)": len(cnt),
        "n_runs_with_rep22": len(a5),
        "sentence_verbatim_in_final": sum(1 for x in cnt if x["sentence_in_final_article_verbatim"]),
        "target_pattern(原文残存&未指摘&解消)": sum(1 for x in cnt if x["target_pattern(原文残存&未指摘&解消)"]),
        "target_pattern_with_rep22": sum(1 for x in a5 if x["target_pattern(原文残存&未指摘&解消)"]),
        "by_final_state": dict(Counter(x["final_state"] for x in cnt)),
        "frozen_runs": sum(1 for x in cnt if x["stage1_frozen_fixture"]),
        "frozen_runs_target_pattern": sum(1 for x in cnt if x["stage1_frozen_fixture"] and x["target_pattern(原文残存&未指摘&解消)"]),
        "nonfrozen_runs_target_pattern": sum(1 for x in cnt if not x["stage1_frozen_fixture"] and x["target_pattern(原文残存&未指摘&解消)"]),
        "flagged_blocking_runs": sum(1 for x in cnt if x["BLOCKING_flag_cycles_sentence_level"]),
    }

    # ====================================================================== 問B
    rows44 = list(csv.DictReader(open(CASES44, encoding="utf-8-sig")))
    p2 = [r for r in rows44 if r["cls"] in ("P2a", "P2b")]
    kinds = {}
    for r in p2:
        key = (r["instance"], r["fact"], norm_loose(r["claim"]))
        k = kinds.setdefault(key, {"instance": r["instance"], "fact": r["fact"], "claims_variants": [], "rows": []})
        if r["claim"] not in k["claims_variants"]:
            k["claims_variants"].append(r["claim"])
        k["rows"].append({"run": r["run"], "cycle": r["cycle"], "cls": r["cls"], "kind": r["kind"],
                          "materiality": r["materiality"], "llm_materiality": r["llm_materiality"], "floor_reason": r["floor_reason"],
                          "final_state": r["final_state"]})
    out["B1"] = {"n_rows_P2a_P2b": len(p2), "n_rows_P2a": sum(1 for r in p2 if r["cls"] == "P2a"),
                 "n_rows_P2b": sum(1 for r in p2 if r["cls"] == "P2b"), "n_kinds": len(kinds)}
    runs_by_inst = defaultdict(list)
    for r in runs:
        runs_by_inst[r["d"]["instance_id"]].append(r)
    csv_rows = []
    kind_out = []
    for ki, (key, k) in enumerate(sorted(kinds.items(), key=lambda kv: (kv[1]["instance"], kv[1]["fact"], kv[0][2]))):
        inst = k["instance"]
        orig_en = next(iter(uniq_en.get(inst, set())), None)
        orig_ja = next(iter(uniq_ja.get(inst, set())), None)
        # 代表文字列: 元記事(EN/JA)に逐語(空白正規化のみ)で存在する外側引用符除去済みclaim変種
        rep, lang = None, None
        for v in k["claims_variants"]:
            for cand in [ws(strip_one_pair(v))] + [ws(next(g for g in m.groups() if g is not None)) for m in FRAG_RE.finditer(v)][:0]:
                for lg, ot in (("EN", orig_en), ("JA", orig_ja)):
                    if ot is not None and cand and cand in ws(ot):
                        rep, lang = cand, lg
                        break
                if rep:
                    break
            if rep:
                break
        if rep is None:
            # 全変種で元記事に逐語存在せず(複数断片・説明文混在・語頭大小違い等)。大小無視で元記事に存在するか確認し、あれば元記事側の形を採用
            for v in k["claims_variants"]:
                cand = ws(strip_one_pair(v))
                for lg, ot in (("EN", orig_en), ("JA", orig_ja)):
                    if ot is not None and cand:
                        m = re.search(re.escape(cand), ws(ot), re.I)
                        if m:
                            rep, lang = ws(ot)[m.start():m.end()], lg
                            break
                if rep:
                    break
        kinfo = {"kind_id": f"K{ki+1:02d}", "instance": inst, "fact": k["fact"], "n_rows": len(k["rows"]),
                 "rows": k["rows"], "claim_variants": k["claims_variants"], "representative": rep, "lang": lang,
                 "n_runs_same_instance": len(runs_by_inst[inst]), "qualifying": [], "unconfirmable": [], "present_unflagged_but_stage4": [],
                 "present_flagged": [], "absent_in_final": []}
        for r in runs_by_inst[inst]:
            d = r["d"]
            if rep is None:
                kinfo["unconfirmable"].append({"run": r["path"], "reason": "代表文字列が元記事に逐語で存在せず照合不能"})
                continue
            orig = orig_en if lang == "EN" else orig_ja
            if orig is None:
                kinfo["unconfirmable"].append({"run": r["path"], "reason": "元記事本文の記録なし"})
                continue
            ft, src = final_text(r, lang, orig)
            if lang == "JA" and src == "original_no_rewrite_recorded" and not any(
                    c.get("ja_text_before_rewrite") is not None for c in d["cycles"]):
                pass  # 記録は「変更時のみ」(runner 5378行付近)なので元記事=最終JAと推定(推測として明記)
            present = rep in ws(ft)
            hits, nonb = flagged_blocking(r, [norm_loose(rep)])
            resolved = d["final_state"] in RESOLVED_STATES
            rec = {"run": r["path"], "final_state": d["final_state"], "final_text_source": src,
                   "BLOCKING_flag_cycles": [c for c, _ in hits], "nonblocking_flag_cycles": [c for c, _ in nonb]}
            csv_rows.append({"section": "B", "kind_id": kinfo["kind_id"], "instance": inst, "fact": k["fact"], "lang": lang,
                             "representative": rep, "run": r["path"], "final_state": d["final_state"],
                             "present_in_final": present, "blocking_flagged": bool(hits), "nonblocking_flagged": bool(nonb),
                             "final_text_source": src,
                             "qualifies": bool(present and not hits and resolved)})
            if not present:
                kinfo["absent_in_final"].append(rec)
            elif hits:
                kinfo["present_flagged"].append(rec)
            elif resolved:
                kinfo["qualifying"].append(rec)
            else:
                kinfo["present_unflagged_but_stage4"].append(rec)
        kinfo["n_qualifying"] = len(kinfo["qualifying"])
        kinfo["n_unconfirmable"] = len(kinfo["unconfirmable"])
        kind_out.append(kinfo)
    out["B_kinds"] = kind_out
    inst_tot = {i: len(v) for i, v in runs_by_inst.items() if i in {k["instance"] for k in kind_out}}
    out["B_instance_run_totals"] = inst_tot
    out["B_total_runs_of_these_instances"] = sum(inst_tot.values())
    top = sorted(kind_out, key=lambda k: -k["n_qualifying"])
    out["B_rank_by_qualifying"] = [(k["kind_id"], k["instance"], k["n_qualifying"]) for k in top]
    out["B2_summary"] = {"n_kinds": len(kind_out),
                         "kinds_with_qualifying": sum(1 for k in kind_out if k["n_qualifying"]),
                         "sum_qualifying_kind_run_pairs": sum(k["n_qualifying"] for k in kind_out),
                         "distinct_runs_with_any_qualifying": len({q["run"] for k in kind_out for q in k["qualifying"]}),
                         "sum_unconfirmable_pairs": sum(k["n_unconfirmable"] for k in kind_out),
                         "kinds_unconfirmable": [k["kind_id"] for k in kind_out if k["representative"] is None]}

    # ====================================================================== 問C
    c_rows = []
    all_blocking = 0
    for r in runs:
        d = r["d"]
        cy = d["cycles"]
        inst = d["instance_id"]
        for ci, c in enumerate(cy):
            en_t = cycle_text(cy, ci, "EN", next(iter(uniq_en.get(inst, set())), None))
            if en_t is None:
                for s in c["stage2_results"]:
                    if s["materiality"] == "BLOCKING":
                        all_blocking += 1
                        c_rows.append({"run": r["path"], "instance": inst, "cycle": c["cycle"], "fact": s.get("related_fact_id"),
                                       "claim": s["dev"].get("claim_in_article"), "heading_hit": None, "reason": "EN本文記録なし"})
                continue
            head_line = en_t.lstrip().split("\n", 1)[0]
            h_start = en_t.find(head_line)
            h_span = (h_start, h_start + len(head_line))
            is_head = head_line.startswith("# ")
            for s in c["stage2_results"]:
                if s["materiality"] != "BLOCKING":
                    continue
                all_blocking += 1
                cl = s["dev"].get("claim_in_article", "") or ""
                spans, how = claim_spans(cl, en_t) if not is_ja(cl) else ([], "ja_claim")
                hit = is_head and any(ov(sp, h_span) for sp in spans)
                # 補助: same_fact_id_locations(同factの別箇所として列挙された文字列)に見出しが含まれるか
                locs = [x for x in (s["dev"].get("same_fact_id_locations") or []) if isinstance(x, str)]
                loc_hit = False
                for lx in locs:
                    sp2 = locate(lx, en_t) if lx.strip() else []
                    if is_head and any(ov(sp, h_span) for sp in sp2):
                        loc_hit = True
                # 補助: 見出しを引用せず位置語(headline/title)だけで指している
                pos_word = bool(re.search(r"(?<![A-Za-z])(headline|title|heading)(?![A-Za-z])", cl, re.I)) if not hit else False
                c_rows.append({"run": r["path"], "instance": inst, "cycle": c["cycle"], "fact": s.get("related_fact_id"),
                               "claim": cl, "heading_hit": hit, "heading_in_same_fact_locations": loc_hit, "position_word_only": pos_word, "resolve": how, "heading": head_line, "materiality": s["materiality"],
                               "llm_materiality": s.get("llm_materiality"), "floor_reason": s.get("floor_reason"),
                               "final_state": d["final_state"], "kind": ("K3" if s.get("detected_by") == "precheck" else
                                                                         "K2" if s["dev"].get("enumeration_source_claim") else "K1")})
    out["C2_all_blocking_rows"] = all_blocking
    hh = [x for x in c_rows if x.get("heading_hit")]
    out["C2_heading_hit_rows"] = len(hh)
    out["C2_heading_hit"] = hh
    out["C2_by_instance_fact"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(Counter((x["instance"], x["fact"]) for x in hh).items(), key=lambda kv: str(kv[0]))}
    out["C2_heading_in_same_fact_locations_only"] = [x for x in c_rows if x.get("heading_in_same_fact_locations") and not x.get("heading_hit")]
    out["C2_position_word_only"] = [x for x in c_rows if x.get("position_word_only")]
    # ---- 日本語claim(JA側)が日本語記事の1行目(タイトル)と重なるもの
    ja_head_hits = []
    for r in runs:
        d = r["d"]
        cy = d["cycles"]
        inst = d["instance_id"]
        oj = next(iter(uniq_ja.get(inst, set())), None)
        for ci, c in enumerate(cy):
            jt = cycle_text(cy, ci, "JA", oj)
            if jt is None:
                continue
            first = [l for l in jt.splitlines() if l.strip()][0]
            st = jt.find(first)
            hs = (st, st + len(first))
            for s_ in c["stage2_results"]:
                if s_["materiality"] != "BLOCKING":
                    continue
                cl = s_["dev"].get("claim_in_article", "") or ""
                if not is_ja(cl):
                    continue
                sp, how = claim_spans(cl, jt)
                if any(ov(x, hs) for x in sp):
                    ja_head_hits.append({"run": r["path"], "cycle": c["cycle"], "fact": s_.get("related_fact_id"), "claim": cl,
                                         "ja_first_line": first})
    out["C2_ja_title_hit_rows"] = ja_head_hits
    union = [x for x in c_rows if x.get("heading_hit") or x.get("heading_in_same_fact_locations") or x.get("position_word_only")]
    out["C2_union_any_heading_touch_rows"] = len(union)
    out["C2_union_by_instance_fact"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(Counter((x["instance"], x["fact"]) for x in union).items(), key=lambda kv: str(kv[0]))}
    out["C2_unresolved_none_rows"] = sum(1 for x in c_rows if x.get("resolve") == "none")
    out["C2_ja_claim_rows"] = sum(1 for x in c_rows if x.get("resolve") == "ja_claim")
    out["C2_no_en_text_rows"] = sum(1 for x in c_rows if x.get("heading_hit") is None)
    out["C2_unresolved_blocking_rows"] = sum(1 for x in c_rows if x.get("resolve") in ("none", "ja_claim") or x.get("heading_hit") is None)
    # ---- C-3: 見出しが絡む記事のEN見出し(元記事1行目)・JA記事1行目(原文記事=翻訳元)・出荷用JAタイトル(ja_writer/runtime_evidence.json)
    c3_sources = {
        "bgroup_B4": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json",
        "neg1_meta_b3prod_a2": "er019_output/family_x_b3_production_wiring_01/run_01/a2/audit/deviation_checks/standard_attempt1.json",
        "hormuz_run03_standard": "er019_output/family_x_refresh_e2e_01/hormuz/run_03/a2/audit/deviation_checks/standard_attempt1.json",
    }
    insts = sorted({x["instance"] for x in hh} | {x["instance"] for x in out["C2_heading_in_same_fact_locations_only"]} |
                   {x["instance"] for x in out["C2_position_word_only"]} | {"neg1_meta_b3prod_a2"})
    c3 = {}
    for inst in insts:
        info = {"en_heading_original": None, "ja_first_line_of_source_article": None, "audit_source": c3_sources.get(inst),
                "ja_title_runtime_evidence": None}
        oe = next(iter(uniq_en.get(inst, set())), None)
        if oe:
            info["en_heading_original"] = oe.lstrip().splitlines()[0]
        sp = c3_sources.get(inst)
        if sp and os.path.exists(os.path.join(ROOT, sp)):
            ad = json.load(open(os.path.join(ROOT, sp), encoding="utf-8"))
            prm = ad["prompt"]
            if "【原文記事(翻訳・適応元)】" in prm:
                ja_art = prm.split("【原文記事(翻訳・適応元)】")[1].strip()
                info["ja_first_line_of_source_article"] = ja_art.splitlines()[0]
            # 出荷用JAタイトル: audit_sourceのrun dir配下のja_writer/runtime_evidence.json
            run_dir = sp.split("/audit/")[0]
            run_dir = os.path.dirname(run_dir)  # .../run_NN/a2 -> .../run_NN
            ev = os.path.join(ROOT, run_dir, "ja_writer", "runtime_evidence.json")
            info["ja_writer_runtime_evidence_path"] = os.path.relpath(ev, ROOT) if os.path.exists(ev) else None
            if os.path.exists(ev):
                info["ja_title_runtime_evidence"] = json.load(open(ev, encoding="utf-8")).get("title")
            for nm in ("revision2.md", "revision1.md", "original.md"):
                pp = os.path.join(ROOT, run_dir, "ja_writer", nm)
                if os.path.exists(pp):
                    info[f"ja_writer_{nm}_first_line"] = open(pp, encoding="utf-8").read().splitlines()[0].strip()
        c3[inst] = info
    out["C3_headings"] = c3
    for x in hh:
        csv_rows.append({"section": "C2", "kind_id": "", "instance": x["instance"], "fact": x["fact"], "lang": "EN",
                         "representative": x["claim"], "run": x["run"], "final_state": x["final_state"], "present_in_final": "",
                         "blocking_flagged": True, "nonblocking_flagged": "", "final_text_source": f"cycle{x['cycle']}", "qualifies": ""})
    for x in a5:
        csv_rows.append({"section": "A5", "kind_id": "A", "instance": "meta_run03_standard", "fact": "MUSE-HC-010", "lang": "EN",
                         "representative": TARGET_SENT, "run": x["run"], "final_state": x["final_state"],
                         "present_in_final": x["sentence_in_final_article_verbatim"],
                         "blocking_flagged": bool(x["BLOCKING_flag_cycles_sentence_level"]),
                         "nonblocking_flagged": bool(x["nonblocking_flag_cycles_sentence_level"]),
                         "final_text_source": x["final_text_source"], "qualifies": x["target_pattern(原文残存&未指摘&解消)"]})
    cols = ["section", "kind_id", "instance", "fact", "lang", "representative", "run", "final_state", "present_in_final",
            "blocking_flagged", "nonblocking_flagged", "final_text_source", "qualifies"]
    with open(os.path.join(OUT_DIR, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for x in csv_rows:
            w.writerow({c: ("" if x.get(c) is None else str(x.get(c)).replace("\n", " ")) for c in cols})
    with open(os.path.join(OUT_DIR, "results_01.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("scope", "A5_counts", "B1", "B2_summary", "C2_all_blocking_rows", "C2_heading_hit_rows",
                                          "C2_by_instance_fact", "C2_unresolved_blocking_rows")}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
