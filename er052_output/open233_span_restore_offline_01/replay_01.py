# -*- coding: utf-8 -*-
# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_65: L6「完結文復元」の試作と決定論replay(¥0、API呼び出しなし)。
# runner本体は変更しない(既存関数をimportするだけ)。L6はこのスクリプト内の試作実装であり、Production未接続。
# 実行: .venv\Scripts\python.exe er052_output\open233_span_restore_offline_01\replay_01.py
from __future__ import annotations

import collections
import glob
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402

OUT_DIR = "er052_output/open233_span_restore_offline_01"
runner.VS_MATCH_EXT = True      # 実flow(rep24)と同じ照合設定
runner.VS_EXPLAIN_SPLIT = True

# ---------------- L6 しきい値(設計書§4-3。根拠は§5の実測) ----------------
MIN_FRAG_WORDS = 3          # 断片(境界不一致型・省略記号の各部分)の最小語数
MIN_FRAG_CHARS = 12         # 同、最小文字数
MIN_ANCHOR_WORDS = 4        # アンカー(先頭側/末尾側の逐語連続部分)の最小語数
MIN_ANCHOR_CHARS = 20       # 同、最小文字数
MAX_UNMATCHED_TOKENS = 6    # アンカー外(Checker由来の記事にない語)の連続語数の上限
MIN_COVER_RATIO = 0.5       # アンカーがclaim全体の文字数に占める割合の下限(逐語連続部分のみ、類似度ではない)
MAX_SENTENCES = 2           # 復元する連続文の最大数
MAX_RESTORED_CHARS = 700    # 復元文の最大文字数(根拠は§5の実測分布)

ELL_RE = re.compile(r"\s*(?:\.{3,}|…+|・{2,}|(?:\.\s){2,}\.)\s*")
EDGE = ".,;:!?\"'“”‘’「」『』()[]— \t\r\n"
CJK_RE = re.compile(r"[぀-ヿ一-鿿]")


# ---------------- 文の単位 ----------------
def sentence_group(text: str, a: int, b: int):
    """[a,b)と重なる文(runner.vs_sentence_segments、改行区切りも文区切り)の連続群を返す。"""
    segs = runner.vs_sentence_segments(text)
    hit = [s for s in segs if s[0] < b and s[1] > a]
    return hit


def quote_balanced(s: str) -> bool:
    return s.count("“") == s.count("”") and s.count('"') % 2 == 0


def restored_range_from(text: str, hit: list):
    """文群 hit から (start,end,reject_reason) を返す。引用符が閉じていなければ隣接文で閉じられるか試す。"""
    if not hit:
        return None, None, "no_sentence"
    if len(hit) > MAX_SENTENCES:
        return None, None, "spans_more_than_%d_sentences" % MAX_SENTENCES
    segs = runner.vs_sentence_segments(text)
    s, e = hit[0][0], hit[-1][1]
    if "\n\n" in text[s:e]:
        return None, None, "crosses_paragraph"
    if not quote_balanced(text[s:e]):
        idx = segs.index(hit[0])
        jdx = segs.index(hit[-1])
        ok = False
        for (i0, j0) in ((idx - 1, jdx), (idx, jdx + 1)):
            if i0 < 0 or j0 >= len(segs) or (j0 - i0 + 1) > MAX_SENTENCES:
                continue
            ss, ee = segs[i0][0], segs[j0][1]
            if "\n\n" not in text[ss:ee] and quote_balanced(text[ss:ee]):
                s, e, ok = ss, ee, True
                break
        if not ok:
            return None, None, "unbalanced_quote_not_closable_within_%d_sentences" % MAX_SENTENCES
    if e - s > MAX_RESTORED_CHARS:
        return None, None, "restored_too_long(%d)" % (e - s)
    if runner.vs_is_structural_label_range(text, (s, e)):
        return None, None, "label_only"
    return s, e, None


# ---------------- 正規化済み記事上の探索 ----------------
class Art:
    def __init__(self, text: str):
        self.text = text
        self.nt, self.nm = runner.vs_norm_with_map(text, True)

    def occ(self, nv: str, boundary: bool):
        out = []
        for a, b in runner.vs_find_all(self.nt, nv):
            if boundary and not num_word_boundary_ok(self.nt, (a, b)):
                continue
            out.append((self.nm[a][0], self.nm[b - 1][1]))
        return out


def num_word_boundary_ok(text: str, span: tuple) -> bool:
    """runnerのvs_word_boundary_okに「数値内の小数点・桁区切り(2.6の.、1,000の,)」を加えた境界判定(L6試作用)。"""
    if not runner.vs_word_boundary_ok(text, span):
        return False
    a, b = span
    if text[a:a + 1].isdigit() and a >= 2 and text[a - 1] in ".," and text[a - 2].isdigit():
        return False
    if text[b - 1:b].isdigit() and b + 1 < len(text) and text[b] in ".," and text[b + 1].isdigit():
        return False
    return True


def norm(s: str) -> str:
    return runner.vs_norm_with_map(s.strip(), True)[0]


def strip_edge(s: str) -> str:
    return s.strip(EDGE)


# ---------------- アンカー探索(逐語連続部分のみ。類似度ではない) ----------------
def anchor_scan(art: Art, part: str):
    """partが記事に全体一致しないとき、先頭側・末尾側の「逐語で記事にちょうど1箇所ある最長の連続語列」を探す。
    返値: {"head": (k, span)|None, "tail": (j, span)|None, "n": 語数, "unmatched": int, "cover": 比率}"""
    toks = norm(part).split()
    n = len(toks)
    res = {"n": n, "head": None, "tail": None}
    if n < MIN_ANCHOR_WORDS:
        return res

    def variants(seg_tokens, side):
        s = " ".join(seg_tokens)
        yield s
        s2 = s.rstrip(EDGE) if side == "head" else s.lstrip(EDGE)
        if s2 != s and s2:
            yield s2

    for k in range(n - 1, MIN_ANCHOR_WORDS - 1, -1):
        found = None
        for v in variants(toks[:k], "head"):
            o = art.occ(v, True)
            if o:
                found = (v, o)
                break
        if found:
            v, o = found
            if len(o) == 1 and len(strip_edge(v)) >= MIN_ANCHOR_CHARS:
                res["head"] = (k, o[0], v)
            elif len(o) >= 2:
                res["head"] = (k, None, v)  # 先頭側アンカーは複数箇所=曖昧
            break
    for j in range(1, n - MIN_ANCHOR_WORDS + 1):
        found = None
        for v in variants(toks[j:], "tail"):
            o = art.occ(v, True)
            if o:
                found = (v, o)
                break
        if found:
            v, o = found
            if len(o) == 1 and len(strip_edge(v)) >= MIN_ANCHOR_CHARS:
                res["tail"] = (j, o[0], v)
            elif len(o) >= 2:
                res["tail"] = (j, None, v)
            break
    return res


def locate_part(art: Art, part: str, role: str, relaxed: bool = False):
    """1つの断片(partは正規化前の文字列)を記事内の範囲(元本文座標)へ。
    返値 {"kind": "exact"/"anchor"/"none"/"too_short"/"multi", "spans": [(a,b)], "detail": ...}"""
    core = strip_edge(part)
    if not core:
        return {"kind": "none", "spans": [], "detail": "empty"}
    nv = norm(core)
    words = nv.split()
    if (len(words) < MIN_FRAG_WORDS or len(nv) < MIN_FRAG_CHARS) and not (relaxed and len(words) >= 1):
        return {"kind": "too_short", "spans": [], "detail": f"words={len(words)},chars={len(nv)}"}
    # 先頭・末尾の境界は role で緩める: head=この断片の先頭は語境界、末尾は切れていてよい(tail省略)など。
    occ_any = art.occ(nv, False)
    if len(occ_any) >= 2:
        return {"kind": "multi", "spans": occ_any, "detail": "fragment_occurs_%d_times" % len(occ_any)}
    if len(occ_any) == 1:
        a, b = occ_any[0]
        na = runner.vs_norm_with_map(art.text, True)  # 同じ写像
        # 境界判定(元本文の座標で)
        ok_head = not (runner._vs_wordch(art.text, a) and runner._vs_wordch(art.text, a - 1)) and not (
            art.text[a:a + 1].isdigit() and a >= 2 and art.text[a - 1] in ".," and art.text[a - 2].isdigit())
        ok_tail = not (runner._vs_wordch(art.text, b - 1) and runner._vs_wordch(art.text, b)) and not (
            art.text[b - 1:b].isdigit() and b + 1 < len(art.text) and art.text[b] in ".," and art.text[b + 1].isdigit())
        return {"kind": "exact", "spans": [(a, b)], "detail": {"ok_head": ok_head, "ok_tail": ok_tail}}
    an = anchor_scan(art, core)
    sp = []
    for side in ("head", "tail"):
        t = an[side]
        if t and t[1] is not None:
            sp.append(t[1])
    ambiguous = [s for s in ("head", "tail") if an[s] and an[s][1] is None]
    if not sp:
        return {"kind": "none", "spans": [], "detail": {"anchor": an, "ambiguous_anchor": ambiguous}}
    return {"kind": "anchor", "spans": sp, "detail": {"anchor": an, "ambiguous_anchor": ambiguous}}


# ---------------- L6 本体 ----------------
def l6_restore(claim: str, en: str, art: Art | None = None) -> dict:
    """base照合(L0〜L5+P-strict-closed)で確定しなかったclaimに対する完結文復元の試作。
    status: restored / cand0 / cand_multi / guard_rejected / not_fired / not_applicable。"""
    art = art or Art(en)
    out = {"status": "not_fired", "reason": None, "restore_reason": None, "fired_by": [], "restored": None,
           "span": None, "n_sentences": None, "fragments": [], "detail": None}
    raw = (claim or "").strip()
    if CJK_RE.search(raw):
        out.update(status="not_applicable", reason="claim_is_japanese")
        return out
    core = runner.vs_strip_one_pair(raw)
    core = raw if core is None else core
    # 記事に全体として(正規化後)出現する場合は説明文混入ではない(記事自身が引用符を含む文)。出現しなければ、
    # 引用符断片+説明文の形(raw側で判定)はL6の対象外(P-strict-closedの領域)。
    if not art.occ(norm(strip_edge(core)), False):
        frags_, _bal, segs_ = runner._vs_explain_extract_fragments(raw)
        if frags_:
            # 引用符の外側の語句が「3語以上かつ記事に逐語で存在しない」場合は、Checkerの説明文が混ざっているとみなす
            # (P-strict-closedの領域、L6は触らない)。2語以下のつなぎ・または記事に逐語で存在する語句は本文の一部とみなす。
            expl = [sg for sg in segs_ if len(strip_edge(sg).split()) >= 3 and norm(strip_edge(sg)) not in art.nt]
            if expl:
                out.update(status="not_fired", reason="explanatory_mixed_left_to_P", detail=[strip_edge(x) for x in expl])
                return out
    head_ell = bool(re.match(r"^\s*(?:\.{3,}|…+|・{2,})", core))
    tail_ell = bool(re.search(r"(?:\.{3,}|…+|・{2,})\s*$", core))
    parts = [p for p in ELL_RE.split(core) if strip_edge(p)]
    mid_ell = len(parts) >= 2
    if not parts:
        out.update(status="not_fired", reason="empty")
        return out
    if mid_ell:
        out["fired_by"].append("ellipsis_mid")
    if tail_ell:
        out["fired_by"].append("ellipsis_tail")
    if head_ell:
        out["fired_by"].append("ellipsis_head")

    longest = max(parts, key=lambda p: len(norm(strip_edge(p))))
    locs = [locate_part(art, p, "mid", relaxed=(mid_ell and p is not longest)) for p in parts]
    out["fragments"] = [{"part": p, "kind": l["kind"], "detail": l["detail"] if l["kind"] != "multi" else l["detail"]}
                        for p, l in zip(parts, locs)]
    kinds = [l["kind"] for l in locs]
    if any(k == "too_short" for k in kinds):
        out.update(status="guard_rejected", reason="fragment_too_short")
        return out
    if any(k == "multi" for k in kinds):
        # 部分が複数箇所に出る。省略記号型で、他の部分と組み合わせて1組に絞れるかは下で見る
        pass
    if any(k == "none" for k in kinds):
        amb = [l["detail"].get("ambiguous_anchor") for l in locs if l["kind"] == "none"]
        out.update(status="cand0", reason="no_verbatim_anchor_in_article", detail={"ambiguous": amb})
        return out

    # 各部分の候補範囲リスト(multiは全出現、exact/anchorは確定した範囲)
    cand_lists = []
    for p, l in zip(parts, locs):
        if l["kind"] == "anchor":
            an = l["detail"]["anchor"]
            toks = an["n"]
            unmatched = toks - (an["head"][0] if an["head"] and an["head"][1] else 0) - (
                (toks - an["tail"][0]) if an["tail"] and an["tail"][1] else 0)
            if an["head"] and an["tail"] and an["head"][1] and an["tail"][1]:
                unmatched = an["tail"][0] - an["head"][0]
            if unmatched > MAX_UNMATCHED_TOKENS:
                out.update(status="cand0", reason=f"unmatched_run_too_long({unmatched}>{MAX_UNMATCHED_TOKENS})")
                return out
            cover = 0
            if an["head"] and an["head"][1]:
                cover += len(an["head"][2])
            if an["tail"] and an["tail"][1]:
                cover += len(an["tail"][2])
            if cover / max(1, len(norm(strip_edge(p)))) < MIN_COVER_RATIO:
                out.update(status="cand0", reason="anchor_cover_below_%.2f" % MIN_COVER_RATIO)
                return out
            out["fired_by"].append("anchor_with_substituted_words(unmatched=%d)" % unmatched)
            if len(l["spans"]) == 2 and l["spans"][1][0] < l["spans"][0][1]:
                out.update(status="cand0", reason="head_tail_anchors_out_of_order")
                return out
            lo = min(a for a, _ in l["spans"])
            hi = max(b for _, b in l["spans"])
            cand_lists.append([(lo, hi)])
        else:
            cand_lists.append(list(l["spans"]))
    # 境界不一致(切断)の判定: exact一致が語境界を満たさない
    for l in locs:
        if l["kind"] == "exact":
            d = l["detail"]
            if not d["ok_head"]:
                out["fired_by"].append("truncated_head")
            if not d["ok_tail"] and not tail_ell:
                out["fired_by"].append("truncated_tail")
    if not out["fired_by"]:
        # 全部分が逐語で1箇所・境界も良好・省略記号なし: 通常はbaseで確定するはず(labelなど別理由)
        out.update(status="not_fired", reason="exact_and_boundary_ok_but_base_unresolved")
        return out

    # 組み合わせ(省略記号型では、後ろの部分が前の部分より後にあり、同じ/隣接する文群に収まる組)
    groups = []
    import itertools
    for combo in itertools.product(*cand_lists):
        ok = True
        for x, y in zip(combo, combo[1:]):
            if y[0] < x[1]:
                ok = False
        if not ok:
            continue
        a, b = min(c[0] for c in combo), max(c[1] for c in combo)
        hit = sentence_group(art.text, a, b)
        s, e, why = restored_range_from(art.text, hit)
        groups.append({"span": (s, e), "why": why, "frag_span": (a, b), "n_sent": len(hit)})
    valid = [g for g in groups if g["why"] is None]
    if len(valid) == 0:
        why = collections.Counter(g["why"] for g in groups).most_common(1)
        out.update(status="cand0", reason=(why[0][0] if why else "no_ordered_combination"))
        return out
    uniq = sorted({g["span"] for g in valid})
    if len(uniq) >= 2:
        out.update(status="cand_multi", reason="%d_candidate_sentence_groups" % len(uniq),
                   detail=[art.text[a:b] for a, b in uniq])
        return out
    s, e = uniq[0]
    restored = art.text[s:e]
    if art.text.count(restored) != 1:
        out.update(status="cand_multi", reason="restored_text_occurs_%d_times" % art.text.count(restored))
        return out
    reasons = []
    for f in out["fired_by"]:
        reasons.append(f.split("(")[0])
    out.update(status="restored", reason=None, restored=restored, span=(s, e),
               n_sentences=valid[0]["n_sent"],
               restore_reason=sorted(set(reasons)))
    return out


# ---------------- 既存claimの収集 ----------------
def en_for_cycle(d, idx, fixture_en):
    cycles = d.get("cycles", [])
    if idx == 0:
        return cycles[0].get("en_text_before_rewrite") or fixture_en
    prev = cycles[idx - 1]
    return prev.get("en_text_after_rewrite") or prev.get("en_text_before_rewrite")


def collect():
    fixtures = {i["instance_id"]: i["fixture"]["article_text"] for i in runner.build_target_instances()}
    rows = []
    files = sorted(glob.glob("er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json"))
    for p in files:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        iid = d.get("instance_id") or os.path.basename(p)[:-5]
        if not d.get("cycles"):
            continue
        run = p.replace("er052_output/open233_self_recovery_flow_runner_01", "").replace("\\", "/")
        for ci, c in enumerate(d["cycles"]):
            en = en_for_cycle(d, ci, fixtures.get(iid))
            if not en:
                continue
            for sr in c.get("stage2_results", []):
                if sr.get("materiality") != "BLOCKING":
                    continue
                dev = sr.get("dev") or {}
                rows.append({"file": run, "instance": iid, "cycle": c.get("cycle"), "claim": sr.get("claim_text") or "",
                             "issue": dev.get("claim_in_article") is not None and dev.get("issue") or sr.get("issue"),
                             "en": en, "recorded": sr.get("span_resolution_cycle_start"), "detected_by": sr.get("detected_by")})
    return rows


def runner_fixtures():
    return {i["instance_id"]: i["fixture"]["article_text"] for i in runner.build_target_instances()}


def mid_number_edge(text: str, span: tuple) -> bool:
    return not num_word_boundary_ok(text, span) and runner.vs_word_boundary_ok(text, span)


def classify_unresolved(claim: str, base: dict, l6: dict, detected_by=None) -> str:
    raw = (claim or "").strip()
    if detected_by == "precheck":
        return "h_precheck_descriptor(非Checker出力、数値差分の説明文)"
    if CJK_RE.search(raw):
        return "g_japanese_claim(旧Checker言語)"
    reason = base.get("reason") or ""
    if reason == "multi_match":
        return "f_multi_occurrence"
    if reason == "label_only":
        return "g_label_only"
    core = runner.vs_strip_one_pair(raw)
    core = raw if core is None else core
    mid = len([p for p in ELL_RE.split(core) if strip_edge(p)]) >= 2
    tail = bool(re.search(r"(?:\.{3,}|…+|・{2,})\s*$", core))
    head = bool(re.match(r"^\s*(?:\.{3,}|…+|・{2,})", core))
    if mid:
        return "c_ellipsis_mid"
    if tail or head:
        return "b_ellipsis_edge"
    if reason == "explanatory_mixed" or (len(runner._VS_FRAG_RE.findall(core)) >= 1 and runner.vs_split_fragments(core)[2] != ""):
        return "d_explanatory_mixed"
    if "truncated_head" in l6.get("fired_by", []) or "truncated_tail" in l6.get("fired_by", []):
        return "a_truncated_edge"
    if any(str(f).startswith("anchor_with_substituted") for f in l6.get("fired_by", [])):
        return "e_substituted_word"
    if l6.get("reason") == "unmatched_run_too_long" or str(l6.get("reason", "")).startswith("unmatched_run"):
        return "e_substituted_word(unmatched長すぎ)"
    return "g_other(記事に逐語アンカーなし等)"


def main():
    rows = collect()
    print("collected BLOCKING claim-runs:", len(rows))
    arts = {}
    results = []
    for r in rows:
        key = (r["claim"], r["en"])
        base = runner._resolve_claim_string(r["claim"], r["en"], None)
        r["base_status"] = base["status"]
        r["base_reason"] = base.get("reason")
        r["base_level"] = base.get("level")
        r["base_spans"] = base.get("spans")
    # 重複を除いた(claim, article)の一意集合
    uniq = {}
    for r in rows:
        k = (r["claim"], r["en"])
        u = uniq.setdefault(k, {"claim": r["claim"], "en": r["en"], "issue": r["issue"], "occurrences": [], "detected_by": r["detected_by"], "base_status": r["base_status"],
                                "base_reason": r["base_reason"], "base_level": r["base_level"], "base_spans": r["base_spans"]})
        u["occurrences"].append(f"{r['file']}:{r['instance']}:c{r['cycle']}")
        if not u["issue"] and r["issue"]:
            u["issue"] = r["issue"]
    out_rows = []
    mid_num_resolved = []
    for k, u in uniq.items():
        en = u["en"]
        art = arts.setdefault(en, Art(en))
        row = {"claim": u["claim"], "issue": u["issue"], "occurrences": u["occurrences"], "n_occ": len(u["occurrences"]),
               "base_status": u["base_status"], "base_reason": u["base_reason"], "base_level": u["base_level"]}
        if u["base_status"] == "resolved":
            row["l6"] = {"status": "not_invoked(base_resolved)"}
            # 確定済みで範囲の端が数値の途中(2.6の6から始まる等)かの診断
            bad = []
            for (a, b) in (u["base_spans"] or []):
                if mid_number_edge(en, (a, b)):
                    bad.append(en[a:b])
            if bad:
                row["mid_number_edge_in_resolved_range"] = bad
                mid_num_resolved.append(row)
                # 提案: 数値境界で再判定すると未確定になりL6の対象になる
                alt = l6_restore(u["claim"], en, art)
                row["l6_if_boundary_fixed"] = {k2: alt[k2] for k2 in ("status", "reason", "restore_reason", "restored", "n_sentences", "fired_by")}
        else:
            l6 = l6_restore(u["claim"], en, art)
            row["l6"] = {k2: l6[k2] for k2 in ("status", "reason", "restore_reason", "fired_by", "restored", "n_sentences", "fragments", "detail")}
            row["type"] = classify_unresolved(u["claim"], {"reason": u["base_reason"]}, l6, u.get("detected_by"))
            row["detected_by"] = u.get("detected_by")
        out_rows.append(row)
    unresolved = [r for r in out_rows if r["base_status"] != "resolved"]
    resolved = [r for r in out_rows if r["base_status"] == "resolved"]
    # ---- 集計
    def cnt(rs, f):
        return collections.Counter(f(r) for r in rs)
    summary = {
        "claim_runs": len(rows), "unique_claim_article": len(out_rows),
        "resolved_unique": len(resolved), "unresolved_unique": len(unresolved),
        "unresolved_runs": sum(r["n_occ"] for r in unresolved),
        "type_counts_unique": dict(cnt(unresolved, lambda r: r["type"])),
        "type_counts_runs": {t: sum(r["n_occ"] for r in unresolved if r["type"] == t) for t in {r["type"] for r in unresolved}},
        "l6_status_unique": dict(cnt(unresolved, lambda r: r["l6"]["status"])),
        "l6_status_by_type": {t: dict(cnt([r for r in unresolved if r["type"] == t], lambda r: r["l6"]["status"])) for t in sorted({r["type"] for r in unresolved})},
        "resolved_with_mid_number_edge": len(mid_num_resolved),
    }
    # 日本語claimを除いた(現行運用=英語のみ)集計
    non_ja = [r for r in unresolved if r["type"] != "g_japanese_claim(旧Checker言語)"]
    summary["unresolved_unique_non_japanese"] = len(non_ja)
    summary["l6_status_non_japanese"] = dict(cnt(non_ja, lambda r: r["l6"]["status"]))
    summary["restored_unique_non_japanese"] = sum(1 for r in non_ja if r["l6"]["status"] == "restored")
    restored = [r for r in unresolved if r["l6"]["status"] == "restored"]
    summary["restored_unique"] = len(restored)
    summary["restored_lengths_chars"] = sorted(len(r["l6"]["restored"]) for r in restored)
    # 確定済みclaimへL6を適用しても「baseが確定した」事実が変わらないこと: L6はunresolvedにのみ適用される構造なので0件
    summary["resolved_results_changed_by_L6"] = 0
    era = lambda f: ("rep" if "_rep" in f.split("/")[0] else "iter/初期")
    summary["unresolved_runs_by_era_and_detected_by"] = {}
    for r in rows:
        if r["base_status"] != "resolved":
            e = ("rep" if "_rep" in r["file"].split("/")[0] else "iter/初期") + "/" + str(r["detected_by"])
            summary["unresolved_runs_by_era_and_detected_by"][e] = summary["unresolved_runs_by_era_and_detected_by"].get(e, 0) + 1
    summary["precheck_claims_total_runs"] = sum(1 for r in rows if r["detected_by"] == "precheck")
    summary["precheck_claims_resolved_runs"] = sum(1 for r in rows if r["detected_by"] == "precheck" and r["base_status"] == "resolved")
    summary["type_d_P_rejection_reasons"] = []
    for r in unresolved:
        if r["type"].startswith("d_"):
            full = runner._resolve_claim_string(r["claim"], [x for x in rows if x["claim"] == r["claim"]][0]["en"], None)
            es = full.get("explain_split") or {}
            summary["type_d_P_rejection_reasons"].append({"claim": r["claim"][:160], "P_reason": es.get("reason"), "fragments": es.get("fragments"),
                                                            "dropped_remainders": es.get("dropped_remainders")})

    # ---- n-gram一意性(最小長しきい値の根拠): rep24で使われる全記事
    arts_u = {a: 1 for a in runner_fixtures().values()}
    ngram = {}
    for n in (2, 3, 4, 5, 6):
        tot = uniq_n = 0
        for en in arts_u:
            toks = runner.vs_norm_str(en, True).split()
            c = collections.Counter(" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1))
            tot += sum(c.values())
            uniq_n += sum(1 for v in c.values() if v == 1)
        ngram[n] = {"total_ngrams": tot, "unique_ngrams": uniq_n, "unique_rate": round(uniq_n / max(1, tot), 4)}
    summary["ngram_uniqueness_over_all_articles"] = ngram
    lens, pair = [], []
    for en in arts_u:
        segs = [x for x in runner.vs_sentence_segments(en) if not en[x[0]:x[1]].lstrip().startswith("#")]
        lens += [e - st for st, e in segs]
        pair += [segs[i + 1][1] - segs[i][0] for i in range(len(segs) - 1) if "\n\n" not in en[segs[i][0]:segs[i + 1][1]]]
    q = lambda v, p_: sorted(v)[min(len(v) - 1, int(len(v) * p_))]
    summary["sentence_length_stats_fixtures"] = {"n_sentences": len(lens), "median": statistics.median(lens), "p95": q(lens, 0.95),
                                                  "p99": q(lens, 0.99), "max": max(lens), "pair_n": len(pair),
                                                  "pair_median": statistics.median(pair), "pair_p95": q(pair, 0.95), "pair_max": max(pair)}
    summary["n_distinct_articles"] = len(arts_u)

    # ---- 記録済みhandoffとの一致確認(rep24のみ): 現行runnerのbaseが記録と同じ結果か
    mism = 0
    chk = 0
    for r in rows:
        if "_rep24/" in r["file"] + "/" and r["recorded"]:
            chk += 1
            if (r["recorded"].get("status") == "resolved") != (r["base_status"] == "resolved"):
                mism += 1
    summary["rep24_recorded_vs_replay_base_status_mismatch"] = {"checked": chk, "mismatch": mism}

    # ---- rep24の失敗・必須確認
    def find(sub_claim, inst, cyc, sample_tag):
        res = [r for r in rows if sub_claim in r["claim"] and r["instance"] == inst and r["cycle"] == cyc and "_rep24/" in r["file"] + "/"
               and sample_tag in r["file"]]
        return res
    must = {}
    for label, sub, inst, cyc, tag in (
        ("A2A3_s2_c2", "the trade and investment deals that the Gulf states", "safety_A2A3", 2, "instances_s2"),
        ("B3_s2_c2", "so the flashy 20% plan left the stage...", "bgroup_B3", 2, "instances_s2"),
        ("A2A3_s1_c1_6percent", "6 percent, because attacks", "safety_A2A3", 1, "instances_s1"),
        ("A2A3_s2_c1_6percent", "6 percent, because attacks", "safety_A2A3", 1, "instances_s2")):
        f = find(sub, inst, cyc, tag)
        if f:
            r0 = f[0]
            art = arts.setdefault(r0["en"], Art(r0["en"]))
            l6 = l6_restore(r0["claim"], r0["en"], art)
            must[label] = {"claim": r0["claim"], "issue": r0["issue"], "base_status": r0["base_status"], "base_reason": r0["base_reason"],
                           "base_level": r0["base_level"], "base_spans_text": [r0["en"][a:b] for a, b in (r0["base_spans"] or [])],
                           "l6": {k2: l6[k2] for k2 in ("status", "reason", "restore_reason", "fired_by", "restored", "n_sentences")}}
        else:
            must[label] = None
    summary["must_check"] = must

    # ---- 合成テスト(rep24のB3/A2A3の記事本文を使用)
    synth = run_synthetic(rows)
    summary["synthetic"] = synth
    summary["stress"] = stress_test(rows)

    # ---- コスト見積もり用: rep24のRewrite単価
    summary["cost_basis"] = cost_basis()

    json.dump({"summary": summary, "unresolved": unresolved, "resolved_mid_number_edge": mid_num_resolved,
               "must_check": must, "synthetic": synth, "stress": summary["stress"]}, open(f"{OUT_DIR}/results_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    write_md(summary, unresolved, mid_num_resolved, must, synth)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("synthetic", "must_check", "ngram_uniqueness_over_all_articles", "stress")}, ensure_ascii=False, indent=1))
    print("ngram:", json.dumps(summary["ngram_uniqueness_over_all_articles"]))



def stress_test(rows):
    """確定済みclaim(正解範囲が分かっている)を決定論的に壊して(切断・省略・語の置換・余分な語)L6に通し、
    復元結果が正解の文群と一致するかを判定する(誤復元率の実測)。乱数なし。"""
    seen = set()
    cases = []
    for r in rows:
        if r["base_status"] != "resolved" or r.get("detected_by") == "precheck" or CJK_RE.search(r["claim"]):
            continue
        sp = r["base_spans"] or []
        if len(sp) != 1:
            continue
        a, b = sp[0]
        key = (r["en"], a, b)
        if key in seen:
            continue
        seen.add(key)
        text = r["en"]
        seg = text[a:b]
        if runner.vs_is_structural_label_range(text, (a, b)) or "\n" in seg.strip():
            continue
        words = seg.split()
        if len(words) < 8 or len(seg) < 40:
            continue
        truth = sentence_group(text, a, b)
        if not truth or len(truth) > MAX_SENTENCES:
            continue
        cases.append((text, (a, b), seg, words, (truth[0][0], truth[-1][1])))

    def v_head(seg, words):
        w = words[0]
        return seg[1:] if len(w) >= 3 and w[0].isalpha() else None

    def v_tail(seg, words):
        t = seg.rstrip(".,;:!?\"”’'")
        w = t.split()[-1]
        return t[:-1] if len(w) >= 3 and t[-1:].isalpha() else None

    def v_tail_ell(seg, words):
        k = max(MIN_ANCHOR_WORDS, int(len(words) * 0.6))
        return " ".join(words[:k]) + "..." if k < len(words) else None

    def v_mid_ell(seg, words):
        k = max(3, int(len(words) * 0.35))
        return " ".join(words[:k]) + " ... " + " ".join(words[-k:]) if 2 * k < len(words) else None

    def v_subst(seg, words):
        i = len(words) // 2
        if words[i].lower().strip(".,;:") in ("so", "also"):
            return None
        return " ".join(words[:i] + ["so"] + words[i + 1:])

    def v_prepend(seg, words):
        return ("also " if words[0].lower() == "the" else "the ") + seg

    def v_append(seg, words):
        return seg.rstrip(".") + " also"
    variants = collections.OrderedDict([
        ("V1_head_midword_cut", v_head), ("V2_tail_midword_cut", v_tail), ("V3_tail_ellipsis", v_tail_ell),
        ("V4_mid_ellipsis", v_mid_ell), ("V5_one_word_substituted", v_subst), ("V6_extra_word_prepended", v_prepend),
        ("V7_extra_word_appended", v_append)])
    res = collections.OrderedDict()
    detail_bad = []
    detail_nonexact = []
    cache = {}
    for nm, fn in variants.items():
        c = collections.Counter()
        for (text, (a, b), seg, words, (ts, te)) in cases:
            claim = fn(seg, words)
            if not claim:
                c["skipped(variant_not_applicable)"] += 1
                continue
            base = runner._resolve_claim_string(claim, text, None)
            if base["status"] == "resolved":
                c["base_resolved(L6_not_invoked)"] += 1
                continue
            art = cache.setdefault(text, Art(text))
            r = l6_restore(claim, text, art)
            st = r["status"]
            if st == "restored":
                rs, re_ = r["span"]
                if (rs, re_) == (ts, te):
                    c["restored_exact_truth"] += 1
                elif rs >= ts and re_ <= te:
                    c["restored_subset_of_truth"] += 1
                    detail_nonexact.append({"variant": nm, "kind": "subset", "claim": claim[:200], "truth": text[ts:te][:300], "restored": r["restored"][:300]})
                elif rs <= ts and re_ >= te:
                    c["restored_superset_of_truth"] += 1
                    detail_nonexact.append({"variant": nm, "kind": "superset", "claim": claim[:200], "truth": text[ts:te][:300], "restored": r["restored"][:300]})
                elif rs < b and re_ > a:
                    c["restored_overlap_partial"] += 1
                    detail_nonexact.append({"variant": nm, "kind": "partial", "claim": claim[:200], "truth": text[ts:te][:300], "restored": r["restored"][:300]})
                else:
                    c["MISRESTORED_disjoint"] += 1
                    detail_bad.append({"variant": nm, "claim": claim, "truth": text[ts:te], "restored": r["restored"]})
            else:
                c["safe_fail:" + st + ":" + str(r["reason"])[:40]] += 1
        res[nm] = dict(c)
    tot = collections.Counter()
    for v in res.values():
        tot.update(v)
    return {"n_cases": len(cases), "by_variant": res, "total": dict(tot), "misrestored_detail": detail_bad,
            "nonexact_detail": detail_nonexact}

def article_of(rows, inst, cyc, tag):
    for r in rows:
        if r["instance"] == inst and r["cycle"] == cyc and "_rep24/" in r["file"] + "/" and tag in r["file"]:
            return r["en"]
    return None


def run_synthetic(rows):
    B3 = article_of(rows, "bgroup_B3", 2, "instances_s2")
    A2 = article_of(rows, "safety_A2A3", 2, "instances_s2")
    art_b, art_a = Art(B3), Art(A2)
    # 2回以上出る語句を自動で探す(同じ断片が2文に出現するケース)
    toks = runner.vs_norm_str(B3, True).split()
    cnt = collections.Counter(" ".join(toks[i:i + 4]) for i in range(len(toks) - 3))
    dup = next((g for g, v in cnt.items() if v >= 2 and len(g) >= 15), None)
    tests = [
        ("S1 先頭切断(語の途中から)", art_b, "oncerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14", "restored"),
        ("S2 末尾切断(語の途中まで)", art_b, "Concerns about US-Iran attacks, the sea blockade, and tanker safety continu", "restored"),
        ("S3 末尾...省略", art_b, "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan...", "restored"),
        ("S3b 末尾…省略(Unicode)", art_b, "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage…", "restored"),
        ("S4 中間...省略", art_b, "Concerns about US-Iran attacks ... the chart only pulled back briefly before recovering", "restored"),
        ("S5 短すぎる断片(語の途中で切断+2語)", art_b, "he flashy 2", "guard_rejected"),
        ("S6 同じ断片が2か所に出現(候補複数)", art_b, (dup or "the high level") + " ...", "cand_multi"),
        ("S7 引用符内の発話を含む文", art_b, "the oil chart’s “not over yet” movement happened on the same d", "restored"),
        ("S8 2文またがり(Brent...)", art_b, "Brent was up about 3%, above $85 a barrel. Its final settlement price was about $85, up about 2% from the da", "restored"),
        ("S9 3文以上またがり", art_b, "Soon, they returned close to the high level before the announcement. At the time of reporting, Brent was up about 3%, above $85 a barrel. Its final settlement price was about $85, up about 2% from the d", "cand0"),
        ("S10 記事に逐語アンカーなし(言い換え)", art_b, "Worries over attacks and shipping safety persisted, which is why the plan was dropped and prices dipped briefly", "cand0"),
        ("S11 語の置換1語(実例B3型)", art_b, "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage...", "restored"),
        ("S12 先頭に余分な語1つ(実例A2A3型)", art_a, "the trade and investment deals that the Gulf states were working on with the United States", "restored"),
        ("S13 置換が多すぎる(7語置換)", art_b, "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so very many extra changed words were inserted here before the flashy 20% plan left the stage", "cand0"),
    ]
    out = []
    for name, art, claim, expect in tests:
        r = l6_restore(claim, art.text, art)
        out.append({"name": name, "claim": claim, "expected": expect, "status": r["status"], "reason": r["reason"],
                    "fired_by": r["fired_by"], "restored": r["restored"], "n_sentences": r["n_sentences"],
                    "match": r["status"] == expect})
    return out


def cost_basis():
    d = "er052_output/open233_self_recovery_flow_runner_01_rep24"
    by = collections.defaultdict(list)
    tot_run = []
    for p in glob.glob(f"{d}/instances_s*/*.json"):
        j = json.load(open(p, encoding="utf-8"))
        tot_run.append(j.get("total_cost_jpy") or 0)
        for c in j.get("call_log", []):
            if c.get("recovery_stage") == "stage3_rewrite":
                lab = c.get("label", "")
                k = "paragraph" if "paragraph" in lab else ("sentence" if "sentence" in lab else ("e1" if "e1_" in lab else "other"))
                by[k].append(c.get("cost_jpy") or 0)
    return {"n_instance_runs": len(tot_run), "mean_instance_run_cost_jpy": round(statistics.mean(tot_run), 4),
            "rewrite_call_cost_jpy": {k: {"n": len(v), "mean": round(statistics.mean(v), 4), "max": round(max(v), 4)} for k, v in by.items()}}


def write_md(summary, unresolved, mid_num_resolved, must, synth):
    L = []
    L.append("# L6 完結文復元 決定論replay結果(委任_65、¥0)\n")
    L.append("## 集計\n")
    for k in ("claim_runs", "unique_claim_article", "resolved_unique", "unresolved_unique", "unresolved_runs",
              "unresolved_unique_non_japanese", "restored_unique", "restored_unique_non_japanese",
              "resolved_results_changed_by_L6", "resolved_with_mid_number_edge", "rep24_recorded_vs_replay_base_status_mismatch"):
        L.append(f"- {k}: {summary[k]}")
    L.append(f"- type別(unique): {json.dumps(summary['type_counts_unique'], ensure_ascii=False)}")
    L.append(f"- type別(runs): {json.dumps(summary['type_counts_runs'], ensure_ascii=False)}")
    L.append(f"- L6判定別(unresolved unique): {json.dumps(summary['l6_status_unique'], ensure_ascii=False)}")
    L.append(f"- L6判定別(日本語claim除く): {json.dumps(summary['l6_status_non_japanese'], ensure_ascii=False)}")
    L.append(f"- type別×L6判定: {json.dumps(summary['l6_status_by_type'], ensure_ascii=False)}")
    L.append(f"- 復元文長(chars): {summary['restored_lengths_chars']}")
    L.append(f"- n-gram一意率(全記事{summary['n_distinct_articles']}本): {json.dumps(summary['ngram_uniqueness_over_all_articles'])}")
    L.append(f"- 未確定runsの内訳(時代/検出元): {json.dumps(summary['unresolved_runs_by_era_and_detected_by'], ensure_ascii=False)}")
    L.append(f"- precheck由来claim: 全{summary['precheck_claims_total_runs']} runs中、base確定{summary['precheck_claims_resolved_runs']} runs")
    L.append(f"- 説明文混入型(d)のP-strict-closed拒否理由: {json.dumps(summary['type_d_P_rejection_reasons'], ensure_ascii=False)}")
    L.append(f"- 文長(fixture 28本、見出し除く): {json.dumps(summary['sentence_length_stats_fixtures'], ensure_ascii=False)}")
    L.append(f"- コスト基礎: {json.dumps(summary['cost_basis'], ensure_ascii=False)}\n")
    L.append("## 必須確認(rep24の実例)\n")
    for k, v in must.items():
        L.append(f"### {k}")
        if not v:
            L.append("(該当なし)\n")
            continue
        L.append(f"- claim: `{v['claim']}`")
        L.append(f"- Checker issue: {v['issue']}")
        L.append(f"- base: {v['base_status']} / {v['base_reason']} / {v['base_level']}; base範囲: {v['base_spans_text']}")
        L.append(f"- L6: {json.dumps(v['l6'], ensure_ascii=False)}\n")
    L.append("## 合成テスト\n")
    L.append("| 名前 | 期待 | 結果 | 一致 | reason/fired_by | 復元文 |")
    L.append("|---|---|---|---|---|---|")
    for s in synth:
        L.append(f"| {s['name']} | {s['expected']} | {s['status']} | {'OK' if s['match'] else 'NG'} | {s['reason']} {s['fired_by']} | {(s['restored'] or '')[:160]} |")
    st = summary["stress"]
    L.append("\n## 誤復元ストレステスト(確定済みclaimを壊してL6に通し、正解の文群と比較)\n")
    L.append(f"- 対象件数(確定済みclaimの一意(記事,範囲)): {st['n_cases']}")
    for vn, v in st["by_variant"].items():
        L.append(f"- {vn}: {json.dumps(v, ensure_ascii=False)}")
    L.append(f"- 合計: {json.dumps(st['total'], ensure_ascii=False)}")
    L.append(f"- 誤復元(正解と無関係の文)詳細: {json.dumps(st['misrestored_detail'], ensure_ascii=False)[:3000]}")
    L.append(f"- 正解と完全一致しなかった復元(部分集合・上位集合・部分重なり)詳細(先頭20件): {json.dumps(st['nonexact_detail'][:20], ensure_ascii=False)[:6000]}")
    L.append("\n## 過去unresolved全claim(unique)\n")
    for i, r in enumerate(unresolved, 1):
        L.append(f"### U{i:02d} [{r['type']}] L6={r['l6']['status']} (出現{r['n_occ']}回)")
        L.append(f"- base: {r['base_status']}/{r['base_reason']}")
        L.append(f"- claim: `{r['claim'][:400]}`")
        L.append(f"- issue: {str(r['issue'])[:300]}")
        L.append(f"- L6: reason={r['l6'].get('reason')} fired_by={r['l6'].get('fired_by')} restore_reason={r['l6'].get('restore_reason')}")
        if r["l6"].get("restored"):
            L.append(f"- 復元文({r['l6']['n_sentences']}文): `{r['l6']['restored'][:500]}`")
        L.append(f"- 出現: {', '.join(r['occurrences'][:4])}{' ...' if len(r['occurrences'])>4 else ''}\n")
    L.append("\n## 確定済みだが範囲の端が数値の途中(小数点・桁区切り)のclaim\n")
    for r in mid_num_resolved:
        L.append(f"- claim: `{r['claim'][:200]}` / 範囲先頭: {r['mid_number_edge_in_resolved_range'][0][:80]} / 出現{r['n_occ']}回 {r['occurrences'][:2]}")
        L.append(f"  - 境界修正後のL6: {json.dumps(r['l6_if_boundary_fixed'], ensure_ascii=False)[:500]}")
    open(f"{OUT_DIR}/results_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
