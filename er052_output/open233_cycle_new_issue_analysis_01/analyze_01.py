# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_44: 2周目以降の新規指摘の原因切り分け(分析専用)。

【性質】既存の er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json を「読むだけ」の
分析物であり、どこからも呼ばれない。runner等の既存モジュールはimportしない(標準ライブラリのみ)。
LLM/API/TTS/Web Search/Trialは一切使わない。出力は同ディレクトリの results_01.json と cases_detail_01.csv。
読む既存成果物: 上記instance JSON、stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json、
委任_41の claims_detail_01.csv(P3の「取りこぼし型」付記にrelation列だけ使用)。

【分類の定義】(単位: cycle k>=2 の Stage 2 結果のうち最終 materiality==BLOCKING の指摘。K1/K2/K3の別は列kindに保持)
 前処理: 指摘文字列(claim_in_article)を委任_41と同じ文字照合L0〜L4でcycle kの本文(EN/JA)へ確定。
   確定できない(0箇所/複数箇所/説明文混在/本文記録なし) -> U。
 P : 確定した文字列(全断片)が cycle1入力記事にも同じ文字列で存在する(元記事に最初から存在)。
   earlier = それ以前の周回の全Stage2結果(重大度問わず)。「同じ範囲」= cycle1記事座標での範囲の重なり、または
   claim文字列の正規化包含(12文字以上)。
   P3 : 同じ範囲の指摘が以前の周回でBLOCKINGだった(書き換えで直らず再指摘)
   P1 : (P3でなく)同じ範囲の指摘が以前の周回にあり、全てQUALITY/ACCEPTABLE
   P2a: 同じ範囲の指摘は以前に無いが、同じfact_idの別箇所は以前に指摘済み
   P2b: 同じfact_id自体が以前の周回に初出
   ※委任文のP1定義「同じ範囲または同じfact_id」とP2定義「同じ範囲・同じfact_id一切なし」「P2a=同じfact_idの別箇所」は
     同一fact_id別範囲の扱いが重複するため、P1は「同じ範囲」に限定しP2aを「同じfact_id別範囲」とした(解釈を明記)。
 R : 文字列がcycle1記事に無く、cycle1記事->cycle k本文の差分(語単位difflib)の変更範囲に重なる(Rewrite起因)。
   R1: 直前周回のRewriteで「対象指摘(直前周回のBLOCKING指摘の範囲)と重なる編集」に重なる
   R2: 直前周回のRewriteで「対象指摘と重ならない編集」に重なる(対象外の箇所を変えた)
   R_older: 直前周回の編集には重ならず、より前の周回のRewrite起因
 U : 判定不能。
"""
import csv
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_NAMES = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")
FIXTURE = os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_rep19", "stage1_fixtures",
                       "meta_run03_standard_iter8_cycle1_frozen.json")
CSV41 = os.path.join(ROOT, "er052_output", "open233_handoff_log_aggregation_01", "claims_detail_01.csv")

# ------------------------------------------------------------ 文字照合(委任_41と同じL0〜L4)
QUOTE_PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
CURLY_MAP = {"’": "'", "‘": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"'}


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


def norm_str(s, lower=True):
    return norm_with_map(s.strip(), lower)[0]


def strip_one_pair(s):
    s = s.strip()
    if len(s) >= 2:
        for o, c in QUOTE_PAIRS:
            if s[0] == o and s[-1] == c:
                return s[1:-1].strip()
    return None


def match_levels(cand, text):
    raw = cand.strip()
    stripped = strip_one_pair(raw)
    for label, v in (("L0", raw), ("L1", stripped)):
        if v:
            occ = find_all(text, v)
            if len(occ) == 1:
                return "ok", label, occ
            if len(occ) >= 2:
                return "multi", label, occ
    for label, lower in (("L2", False), ("L3", True)):
        nt, nm = norm_with_map(text, lower)
        for v in (raw, stripped):
            if not v:
                continue
            nv = norm_str(v, lower)
            if not nv:
                continue
            occ = find_all(nt, nv)
            if len(occ) == 1:
                s, e = occ[0]
                return "ok", label, [(nm[s][0], nm[e - 1][1])]
            if len(occ) >= 2:
                return "multi", label, [(nm[a][0], nm[b - 1][1]) for a, b in occ]
    return "none", None, []


FRAG_RE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
CONNECT_RE = re.compile(r"\b(and|or)\b|[&,;、，；と/／.。:：]|および|\s", re.I)
JA_RE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")


def is_ja(s):
    t = re.sub(r"\s", "", s)
    return bool(t) and len(JA_RE.findall(t)) / len(t) >= 0.15


def resolve_in_text(claim, text):
    st, _lv, spans = match_levels(claim, text)
    if st in ("ok", "multi"):
        return {"status": st, "spans": spans}
    frags = [next(g for g in m.groups() if g is not None) for m in FRAG_RE.finditer(claim)]
    rest_clean = CONNECT_RE.sub("", FRAG_RE.sub("", claim))
    if len(frags) >= 2 and rest_clean == "":
        sp = []
        for f in frags:
            s2, _l2, spans2 = match_levels(f, text)
            if s2 != "ok":
                return {"status": "frag_unresolved", "spans": []}
            sp.append(spans2[0])
        return {"status": "ok", "spans": sp}
    if len(frags) >= 1 and rest_clean != "":
        return {"status": "explanatory", "spans": []}
    return {"status": "none", "spans": []}


def resolve_claim(claim, en, ja):
    """EN優先。返値 dict(status, lang, spans, strings, reason)"""
    c = (claim or "").strip()
    if not c:
        return {"status": "U", "reason": "empty_claim", "lang": None, "spans": [], "strings": []}
    cands = []
    if en is not None:
        cands.append(("EN", en))
    if ja is not None:
        cands.append(("JA", ja))
    if not cands:
        return {"status": "U", "reason": "no_text", "lang": None, "spans": [], "strings": []}
    res = {lang: resolve_in_text(c, t) for lang, t in cands}
    for lang, t in cands:
        if res[lang]["status"] == "ok":
            sp = sorted(res[lang]["spans"])
            return {"status": "ok", "lang": lang, "spans": sp, "strings": [t[a:b] for a, b in sp], "reason": None}
    sts = [v["status"] for v in res.values()]
    if is_ja(c) and ja is None:
        return {"status": "U", "reason": "ja_text_missing", "lang": None, "spans": [], "strings": []}
    for key, reason in (("multi", "multi_match"), ("explanatory", "explanatory_text_mixed"),
                        ("frag_unresolved", "fragment_unresolved")):
        if key in sts:
            return {"status": "U", "reason": reason, "lang": None, "spans": [], "strings": []}
    return {"status": "U", "reason": "no_match", "lang": None, "spans": [], "strings": []}


# ------------------------------------------------------------ 範囲・差分
def overlap(a, b):
    return min(a[1], b[1]) > max(a[0], b[0])


def spans_overlap(s1, s2):
    return any(overlap(x, y) for x in s1 for y in s2)


def word_tokens(text):
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def diff_ranges(before, after):
    """語単位diff。返値 [(before_range, after_range, tag)] (equal以外)"""
    tb, ta = word_tokens(before), word_tokens(after)
    sm = difflib.SequenceMatcher(None, [t[0] for t in tb], [t[0] for t in ta], autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if i2 > i1:
            br = (tb[i1][1], tb[i2 - 1][2])
        else:
            p = tb[i1][1] if i1 < len(tb) else len(before)
            br = (p, p)
        if j2 > j1:
            ar = (ta[j1][1], ta[j2 - 1][2])
        else:
            p = ta[j1][1] if j1 < len(ta) else len(after)
            ar = (p, p)
        out.append((br, ar, tag))
    return out


def touches(rng, spans):
    a, b = rng
    for s, e in spans:
        if a == b:
            if s <= a <= e:
                return True
        elif overlap((a, b), (s, e)):
            return True
    return False


def hits(spans, ar):
    return any(overlap(sp, ar) or (ar[0] == ar[1] and sp[0] <= ar[0] <= sp[1]) for sp in spans)


# ------------------------------------------------------------ 読み込み
def load_runs():
    runs, dirs = [], []
    for dd in sorted(glob.glob(os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not TARGET_NAMES.match(name):
            continue
        fs = sorted(glob.glob(os.path.join(dd, "instances_*", "*.json")))
        dirs.append((name, len(fs)))
        for f in fs:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if "cycles" not in d:
                continue
            rel = os.path.relpath(f, os.path.join(ROOT, "er052_output")).replace("\\", "/")
            rel = rel.replace("open233_self_recovery_flow_runner_01_", "")
            runs.append({"path": rel, "dir": name, "d": d})
    return runs, dirs


def build_borrow(runs):
    en_t, ja_t = defaultdict(set), defaultdict(set)
    for run in runs:
        if not run["d"]["cycles"]:
            continue
        c0 = run["d"]["cycles"][0]
        if c0.get("en_text_before_rewrite") is not None:
            en_t[run["d"]["instance_id"]].add(c0["en_text_before_rewrite"])
        if c0.get("ja_text_before_rewrite") is not None:
            ja_t[run["d"]["instance_id"]].add(c0["ja_text_before_rewrite"])
    return ({k: next(iter(v)) for k, v in en_t.items() if len(v) == 1},
            {k: next(iter(v)) for k, v in ja_t.items() if len(v) == 1})


def cycle_texts(cycles, i, iid, borrow):
    c = cycles[i]
    en, ja = c.get("en_text_before_rewrite"), c.get("ja_text_before_rewrite")
    src = "own" if en is not None else None
    if i > 0:
        p = cycles[i - 1]
        if en is None and p.get("en_text_after_rewrite") is not None:
            en, src = p["en_text_after_rewrite"], "prev_after"
        if ja is None and p.get("ja_text_after_rewrite") is not None:
            ja = p["ja_text_after_rewrite"]
    else:
        if en is None and iid in borrow[0]:
            en, src = borrow[0][iid], "borrowed_same_fixture"
        if ja is None and iid in borrow[1]:
            ja = borrow[1][iid]
    return en, ja, src


def mat_letter(m):
    return {"BLOCKING": "B", "QUALITY": "Q", "ACCEPTABLE": "A"}.get(m, "?")


def kind_of(s):
    if s.get("detected_by") == "precheck":
        return "K3"
    if s["dev"].get("enumeration_source_claim"):
        return "K2"
    return "K1"


def load_csv41():
    rel = {}
    if os.path.exists(CSV41):
        with open(CSV41, encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                rel[(r["run"], int(r["cycle"]), int(r["k"]))] = r.get("relation") or ""
    return rel


def claim_norm(claim):
    return norm_str(strip_one_pair(claim or "") or (claim or ""))


def main():
    runs, dirs = load_runs()
    borrow = build_borrow(runs)
    csv41 = load_csv41()
    fixture = json.load(open(FIXTURE, encoding="utf-8"))
    fx_claims = [claim_norm(x["claim_in_article"]) for x in fixture["deviations"]]
    fx_locs = [norm_str(loc) for x in fixture["deviations"] for loc in (x.get("same_fact_id_locations") or [])]

    rows = []
    run_info = {}
    n_multi_cycle = 0
    for run in runs:
        d = run["d"]
        cycles = d["cycles"]
        iid = d["instance_id"]
        if len(cycles) >= 2:
            n_multi_cycle += 1
        if not cycles:
            continue
        texts = [cycle_texts(cycles, i, iid, borrow) for i in range(len(cycles))]
        en1, ja1, _ = texts[0]
        c1_k1 = [claim_norm(s["dev"]["claim_in_article"]) for s in cycles[0]["stage2_results"] if kind_of(s) == "K1"]
        fixed = (iid == "meta_run03_standard" and sorted(c1_k1) == sorted(fx_claims))
        run_info[run["path"]] = {"instance": iid, "final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                                 "n_cycles": len(cycles), "fixed_stage1": fixed}
        resolved = []
        for ci, c in enumerate(cycles):
            en, ja, _src = texts[ci]
            rl = []
            for s in c["stage2_results"]:
                r = resolve_claim(s["dev"].get("claim_in_article", ""), en, ja)
                span1 = None
                if r["status"] == "ok":
                    base = en1 if r["lang"] == "EN" else ja1
                    if base is not None:
                        sp, okall = [], True
                        for st in r["strings"]:
                            occ = find_all(base, st)
                            if not occ:
                                okall = False
                                break
                            sp.extend(occ)
                        span1 = sp if okall else None
                r["span1"] = span1
                rl.append(r)
            resolved.append(rl)
        for ci in range(1, len(cycles)):
            c = cycles[ci]
            en_k, ja_k, _ = texts[ci]
            for k, s in enumerate(c["stage2_results"]):
                if s["materiality"] != "BLOCKING":
                    continue
                dv = s["dev"]
                claim = dv.get("claim_in_article", "")
                F = resolved[ci][k]
                row = {
                    "run": run["path"], "dir": run["dir"], "instance": iid, "cycle": c["cycle"], "k": k,
                    "kind": kind_of(s), "fact": s.get("related_fact_id"), "claim": claim,
                    "checker_severity": dv.get("severity"), "materiality": s["materiality"],
                    "llm_materiality": s.get("llm_materiality"), "floor_reason": s.get("floor_reason"),
                    "final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                    "is_last_cycle": ci == len(cycles) - 1, "fixed_stage1": fixed,
                    "cls": None, "reason": None,
                }
                lm, fm = s.get("llm_materiality"), s["materiality"]
                row["floor_dir"] = ("raised" if (lm != fm and lm in ("ACCEPTABLE", "QUALITY") and fm == "BLOCKING") else
                                    "lowered" if (lm != fm and lm == "BLOCKING") else "none")
                if F["status"] != "ok":
                    row["cls"], row["reason"] = "U", F["reason"]
                    if F["reason"] == "explanatory_text_mixed":
                        fr = [next(g for g in m.groups() if g is not None) for m in FRAG_RE.finditer(claim)]
                        row["u_single_fragment_resolvable"] = (len(fr) == 1 and any(
                            match_levels(fr[0], t)[0] == "ok" for t in (en_k, ja_k) if t is not None))
                    rows.append(row)
                    continue
                lang = F["lang"]
                base = en1 if lang == "EN" else ja1
                text_k = en_k if lang == "EN" else ja_k
                row["lang"] = lang
                if base is None:
                    row["cls"], row["reason"] = "U", "no_cycle1_text"
                    rows.append(row)
                    continue
                in_a1 = F["span1"] is not None
                fcl = claim_norm(claim)
                earlier = []
                for cj in range(ci):
                    for kj, sj in enumerate(cycles[cj]["stage2_results"]):
                        Ej = resolved[cj][kj]
                        ov = bool(in_a1 and Ej.get("span1") and spans_overlap(F["span1"], Ej["span1"]))
                        ecl = claim_norm(sj["dev"].get("claim_in_article", ""))
                        if len(fcl) >= 12 and len(ecl) >= 12 and (fcl in ecl or ecl in fcl):
                            ov = True
                        earlier.append({"cj": cj, "kj": kj, "s": sj, "ov": ov, "res": Ej})
                if in_a1:
                    over = [e for e in earlier if e["ov"]]
                    row["fixture_rel"] = ("fixture_dev" if any(fcl in fc or fc in fcl for fc in fx_claims if len(fcl) >= 12)
                                          else "fixture_location_only" if any(fcl in fl or fl in fcl for fl in fx_locs if len(fcl) >= 12)
                                          else "not_in_fixture")
                    loc_hit = False
                    for e in earlier:
                        for loc in (e["s"]["dev"].get("same_fact_id_locations") or []):
                            if isinstance(loc, str) and len(loc.strip()) >= 8:
                                st, _lv, sp = match_levels(loc, base)
                                if st in ("ok", "multi") and spans_overlap(F["span1"], sp):
                                    loc_hit = True
                    row["in_prior_same_fact_locations"] = loc_hit
                    if not fixed:
                        row["fixture_rel"] = "n/a(non_fixed_run)"
                    # 以前の周回で、同じ文字列が検査対象本文に存在し、かつその周回に重なる指摘が無かった周回(見逃し周回)
                    miss, pres = [], []
                    for cj in range(ci):
                        tj = texts[cj][0] if lang == "EN" else texts[cj][1]
                        if tj is not None and all(st in tj for st in F["strings"]):
                            pres.append(cj + 1)
                            if not any(e["ov"] for e in earlier if e["cj"] == cj):
                                miss.append(cj + 1)
                    row["string_present_in_cycles_before"] = ",".join(map(str, pres))
                    row["unflagged_cycles_though_present"] = ",".join(map(str, miss))
                    same_fact = [e for e in earlier if e["s"].get("related_fact_id") and
                                 e["s"].get("related_fact_id") == s.get("related_fact_id")]
                    row["prior_same_fact_n"] = len(same_fact)
                    if over:
                        row["prior_overlap"] = ";".join(f"c{e['cj']+1}k{e['kj']}:{mat_letter(e['s']['materiality'])}" for e in over)
                        blk = [e for e in over if e["s"]["materiality"] == "BLOCKING"]
                        if blk:
                            row["cls"] = "P3"
                            eb = max(blk, key=lambda e: (e["cj"], -e["kj"]))
                            row["p3_prior_relation_csv41"] = csv41.get((run["path"], eb["cj"] + 1, eb["kj"]), "")
                            row["p3_prior_claim"] = eb["s"]["dev"].get("claim_in_article", "")
                        else:
                            row["cls"] = "P1"
                            e = max(over, key=lambda e: (e["cj"], -e["kj"]))
                            es, ed = e["s"], e["s"]["dev"]
                            ch = []
                            if ed.get("severity") != dv.get("severity"):
                                ch.append("sev_changed")
                            if es.get("llm_materiality") != s.get("llm_materiality"):
                                ch.append("llm_changed")
                            if (es.get("floor_reason") or None) != (s.get("floor_reason") or None):
                                ch.append("floor_changed")
                            row["p1_prior"] = (f"c{e['cj']+1}k{e['kj']}:{mat_letter(es['materiality'])}"
                                               f"(llm={mat_letter(es.get('llm_materiality'))},floor={es.get('floor_reason')})")
                            row["p1_changes"] = ",".join(ch) or "none"
                    elif same_fact:
                        row["cls"] = "P2a"
                    else:
                        row["cls"] = "P2b"
                else:
                    if text_k is None:
                        row["cls"], row["reason"] = "U", "no_text_k"
                        rows.append(row)
                        continue
                    ch_total = diff_ranges(base, text_k)
                    if not any(hits(F["spans"], ar) for (_br, ar, _t) in ch_total):
                        row["cls"], row["reason"] = "U", "not_in_article1_no_diff_overlap"
                        rows.append(row)
                        continue
                    prev_text = texts[ci - 1][0] if lang == "EN" else texts[ci - 1][1]
                    cls = "R_older"
                    if prev_text is not None and prev_text != text_k:
                        tgt = []
                        for kj, sj in enumerate(cycles[ci - 1]["stage2_results"]):
                            Ej = resolved[ci - 1][kj]
                            if sj["materiality"] == "BLOCKING" and Ej["status"] == "ok" and Ej["lang"] == lang:
                                tgt.extend(Ej["spans"])
                        r1 = r2 = False
                        for (br, ar, _t) in diff_ranges(prev_text, text_k):
                            if not hits(F["spans"], ar):
                                continue
                            if touches(br, tgt):
                                r1 = True
                            else:
                                r2 = True
                        cls = "R1" if r1 else ("R2" if r2 else "R_older")
                        row["rewrite_diff_before_after"] = "; ".join(
                            f"{prev_text[br[0]:br[1]]!r}->{text_k[ar[0]:ar[1]]!r}" for (br, ar, _t) in diff_ranges(prev_text, text_k))[:400]
                    row["cls"] = cls
                    row["prev_rewrite_ladders"] = ",".join(str(x.get("ladder_level_used")) for x in (cycles[ci - 1].get("rewrite_records") or []))
                rows.append(row)

    # ---------------------------------------------------------------- 集計
    def uniq(rs):
        seen, incons = {}, 0
        for r in rs:
            key = (r["instance"], claim_norm(r["claim"]))
            if key not in seen:
                seen[key] = r
            elif seen[key]["cls"] != r["cls"]:
                incons += 1
        return list(seen.values()), incons

    def cnt(rs):
        return dict(sorted(Counter(r["cls"] for r in rs).items()))

    def strkeys(counter):
        return {str(k): v for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}

    out = {}
    out["scope"] = {"dirs": dirs, "n_dirs": len(dirs), "n_files": sum(n for _, n in dirs),
                    "n_files_with_cycles_key": len(runs), "n_files_with_2plus_cycles": n_multi_cycle,
                    "rows_blocking_cycle2plus": len(rows), "rows_by_kind": dict(Counter(r["kind"] for r in rows)),
                    "n_stage4_runs_with_2plus_cycles": sum(1 for r in run_info.values() if r["final_state"] == "STAGE4_ESCALATION" and r["n_cycles"] >= 2)}
    ub, inc = uniq(rows)
    out["B_all"] = {"rows": cnt(rows), "unique(instance,claim)": cnt(ub), "n_unique": len(ub), "unique_inconsistent_class": inc}
    out["B_K1_only"] = {"rows": cnt([r for r in rows if r["kind"] == "K1"])}
    out["B_by_instance_rows"] = {i: cnt([r for r in rows if r["instance"] == i]) for i in sorted({r["instance"] for r in rows})}
    s4 = [r for r in rows if r["final_state"] == "STAGE4_ESCALATION"]
    out["B_stage4_all_rows"] = cnt(s4)
    out["B_stage4_last_cycle_rows"] = cnt([r for r in s4 if r["is_last_cycle"]])
    out["B_stage4_by_reason_rows"] = {rs: cnt([r for r in s4 if r["stage4_reason"] == rs])
                                      for rs in sorted({r["stage4_reason"] for r in s4 if r["stage4_reason"]})}
    out["B_non_stage4_rows"] = cnt([r for r in rows if r["final_state"] != "STAGE4_ESCALATION"])
    out["U_reasons"] = dict(Counter(r["reason"] for r in rows if r["cls"] == "U"))
    p1 = [r for r in rows if r["cls"] == "P1"]
    out["P1_changes"] = dict(Counter(r["p1_changes"] for r in p1))
    out["checker_severity_values_all_rows"] = dict(Counter(r["checker_severity"] for r in rows))
    out["P1_llm_and_floor"] = strkeys(Counter((r["llm_materiality"], (r["floor_reason"] or "none").split("(")[0]) for r in p1))
    out["floor_direction_all_rows"] = dict(Counter(r["floor_dir"] for r in rows))
    out["floor_reason_x_direction_all_rows"] = strkeys(Counter(((r["floor_reason"] or "none").split("(")[0], r["floor_dir"]) for r in rows))
    out["P3_relation_csv41"] = dict(Counter((r.get("p3_prior_relation_csv41") or "") for r in rows if r["cls"] == "P3"))
    out["P_fixture_rel"] = {c: dict(Counter(r.get("fixture_rel") for r in rows if r["cls"] == c)) for c in ("P1", "P2a", "P2b", "P3")}
    out["P2a_in_prior_same_fact_locations"] = dict(Counter(r.get("in_prior_same_fact_locations") for r in rows if r["cls"] == "P2a"))
    out["P2b_in_prior_same_fact_locations"] = dict(Counter(r.get("in_prior_same_fact_locations") for r in rows if r["cls"] == "P2b"))
    out["R_by_prev_ladder"] = {c: dict(Counter(r.get("prev_rewrite_ladders") for r in rows if r["cls"] == c)) for c in ("R1", "R2", "R_older")}
    out["U_single_fragment_resolvable"] = dict(Counter(r.get("u_single_fragment_resolvable") for r in rows if r["cls"] == "U"))
    out["P_unflagged_cycles_though_present_nonempty"] = {c: sum(1 for r in rows if r["cls"] == c and r.get("unflagged_cycles_though_present")) for c in ("P1", "P2a", "P2b", "P3")}
    out["fixed_stage1_rows"] = cnt([r for r in rows if r["fixed_stage1"]])
    out["nonfixed_rows"] = cnt([r for r in rows if not r["fixed_stage1"]])

    dist = defaultdict(list)
    for run in runs:
        d = run["d"]
        for c in d["cycles"]:
            for s in c["stage2_results"]:
                dist[(d["instance_id"], claim_norm(s["dev"].get("claim_in_article", "")))].append(
                    (s["materiality"], s.get("llm_materiality"), (s.get("floor_reason") or "none").split("(")[0]))
    both_final = [k for k, v in dist.items() if {"QUALITY", "BLOCKING"} <= {x[0] for x in v}]
    out["same_string_stage2_distribution"] = {
        "n_distinct_(instance,claim)": len(dist), "n_observations": sum(len(v) for v in dist.values()),
        "kinds_with_both_QUALITY_and_BLOCKING_final": len(both_final),
        "observations_of_those": sum(len(dist[k]) for k in both_final),
        "kinds_with_2plus_distinct_final_materiality": sum(1 for v in dist.values() if len({x[0] for x in v}) >= 2),
        "kinds_with_2plus_distinct_llm_materiality": sum(1 for v in dist.values() if len({x[1] for x in v}) >= 2),
        "kinds_with_floor_reason_varying": sum(1 for v in dist.values() if len({x[2] for x in v}) >= 2),
        "both_QUALITY_and_BLOCKING_by_instance": dict(Counter(k[0] for k in both_final)),
    }

    # 同一文字列でQUALITY/BLOCKING両方が出た種類の原因: Stage2 LLM判定が揺れたのか、決定論ルール(floor/downgrade)側が揺れたのか
    cause = Counter()
    for k in both_final:
        obs = dist[k]
        llm_set = {x[1] for x in obs}
        cause["llm_materiality_varies" if len(llm_set) > 1 else "llm_constant(floor_or_downgrade_varies)"] += 1
    out["same_string_QB_cause"] = dict(cause)
    DG_RE = re.compile(r"(did not|didn't|could not|couldn't|had no way to|were not aware|was not aware|no way of knowing|could not tell|couldn't tell|didn't realize|did not realize|did not know|didn't know)", re.I)
    DISQ = ["changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time", "changed_scope"]
    dg = Counter()
    for run in runs:
        for c in run["d"]["cycles"]:
            for s in c["stage2_results"]:
                dv = s["dev"]
                if s.get("llm_materiality") == "BLOCKING" and DG_RE.search(dv.get("claim_in_article", "") or "") and (dv.get("unsupported_new_claim") or dv.get("changed_certainty")):
                    flags = ",".join(f[8:] for f in DISQ if dv.get(f)) or "none"
                    dg[(s["materiality"], (s.get("floor_reason") or "none").split("(")[0], flags)] += 1
    out["disclosure_gap_candidates_final_by_disqualifying_flags"] = strkeys(dg)
    meta = {p: i for p, i in run_info.items() if i["instance"] == "meta_run03_standard"}
    out["meta_runs"] = meta
    matrix = defaultdict(dict)
    for run in runs:
        if run["d"]["instance_id"] != "meta_run03_standard":
            continue
        for c in run["d"]["cycles"]:
            for s in c["stage2_results"]:
                cl = s["dev"].get("claim_in_article", "")
                key = f"{s.get('related_fact_id')}|{claim_norm(cl)[:90]}"
                tag = f"c{c['cycle']}:{mat_letter(s['materiality'])}"
                if s["materiality"] != s.get("llm_materiality"):
                    tag += f"(llm={mat_letter(s.get('llm_materiality'))})"
                matrix[key].setdefault(run["path"], []).append(tag)
    out["meta_matrix"] = {k: v for k, v in sorted(matrix.items())}

    with open(os.path.join(OUT_DIR, "results_01.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True, default=str)
    cols = ["run", "instance", "cycle", "k", "kind", "fact", "checker_severity", "materiality", "llm_materiality",
            "floor_reason", "floor_dir", "cls", "reason", "prior_overlap", "p1_prior", "p1_changes",
            "p3_prior_relation_csv41", "fixture_rel", "in_prior_same_fact_locations", "prior_same_fact_n",
            "string_present_in_cycles_before", "unflagged_cycles_though_present", "u_single_fragment_resolvable", "prev_rewrite_ladders", "rewrite_diff_before_after", "final_state", "stage4_reason", "is_last_cycle",
            "fixed_stage1", "claim"]
    with open(os.path.join(OUT_DIR, "cases_detail_01.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([("" if r.get(c) is None else str(r.get(c))).replace("\n", " ") for c in cols])
    print(json.dumps({k: v for k, v in out.items() if k != "meta_matrix"}, ensure_ascii=False, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
