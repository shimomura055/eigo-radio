# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 作業3(¥0、実装しない): (d)型5件の決定論的解決可能性の試作replay。
# 試作ルール(runnerは変更しない。このファイル内の複製):
#   Q(引用符の字形を同一視): P-strict-closedの断片照合が不一致(none)のとき、断片と記事の引用符字形(" ' ‘ ’ “ ” 等)を
#       同一クラスへ写像(文字数不変)して再照合。一意(1箇所)のときだけ採用。範囲は記事側の原文のまま。
#   R(長い説明文の残りの棄却ガード[remainder_too_long]の置換): 断片は逐語・一意(従来どおり)、残りは範囲に入れず捨てる。
#       残りが(記事に逐語/隣接/対比参照語/閉じていない位置語/数字を含む)ならこれまでどおり棄却。長さだけでは棄却しない
#       (上限は語数25)。位置語(headline/one-line/opening)は閉じた語彙として名指しされた構造要素を範囲へ加える(U-2(1)、拡張のみ)。
#       範囲の源は「逐語・一意の断片」と「名指しされた閉じた構造要素」だけで、残りの文字列は範囲に一切入らない
#       (=最悪でも範囲が狭すぎる[under-scope]だけで、無関係な文を書き換える[wrong-range]ことは構造上起きない)。
import importlib.util, json, os, re, sys
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
HERE = "er052_output/open233_span_restore_offline_01"
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
spec = importlib.util.spec_from_file_location("replay_01_q", f"{HERE}/replay_01.py")
rep = importlib.util.module_from_spec(spec)
sys.modules["replay_01_q"] = rep
spec.loader.exec_module(rep)
runner = rep.runner
runner.VS_MATCH_EXT = True
runner.VS_EXPLAIN_SPLIT = True   # 現行Trial構成(rep23〜25)
Q_GLYPHS = {}
for _c in "’‘‚‛`´'":
    Q_GLYPHS[_c] = "'"
for _c in '“”„"':
    Q_GLYPHS[_c] = "'"


def qnorm(s):
    return "".join(Q_GLYPHS.get(c, c) for c in s)


MAX_LONG_WORDS = 25


def p_proto(claim_text, en, use_q=True, use_r=True):
    claim = (claim_text or "").strip()
    out = {"status": "unverified", "reason": None, "ranges": [], "added_elements": [], "dropped": [], "q_used": [], "r_used": []}

    def rej(r, **kw):
        out["reason"] = "explain_split_rejected:" + r
        out.update(kw)
        return out
    frags, balanced, segs = runner._vs_explain_extract_fragments(claim)
    if not frags:
        return rej("no_quote")
    if not balanced:
        return rej("unbalanced_quote")
    spans = []
    for (_s, _e, inner) in frags:
        st, _lv, _stp, sp = runner.vs_match_levels(inner, en, "EN")
        if st == "ok":
            spans.append(sp[0])
            continue
        if st == "none":
            e = runner.vs_edge_punct_match(inner, en, "EN")
            if e is not None and e["status"] == "ok":
                spans.append(e["spans"][0])
                continue
            if e is not None and e["status"] == "multi":
                return rej("fragment_multi_match", detail=inner)
            if use_q:   # Q
                st2, _l2, _s2, sp2 = runner.vs_match_levels(qnorm(inner), qnorm(en), "EN")
                if st2 == "ok":
                    spans.append(sp2[0])
                    out["q_used"].append(inner)
                    continue
        return rej("fragment_multi_match" if st == "multi" else "fragment_not_in_article", detail=inner)
    merged = runner.vs_merge_spans(spans, en)
    if any(runner.vs_is_structural_label_range(en, m) for m in merged):
        return rej("label_only")
    nt, _ = runner.vs_norm_with_map(en, True)
    el = runner._vs_explain_structure_elements(en)
    added = []
    for sg in segs:
        s = sg.strip(runner._VS_EXPLAIN_SEG_EDGE).strip()
        if not s:
            continue
        m = runner.VS_EXPLAIN_POSITION_REJECT_RE.search(s)
        if m:
            return rej("position_word:" + m.group(0))
        want = []
        if runner._VS_EXPLAIN_HEAD_RE.search(s):
            want.append("headline")
        if runner._VS_EXPLAIN_ONELINE_RE.search(s):
            want.append("one_line")
        if runner._VS_EXPLAIN_OPENING_RE.search(s):
            want.append("opening")
        dang = [w for w in want if w in el and not any(sa < el[w][1] and el[w][0] < sb for sa, sb in spans)]
        if dang:
            if any(w not in ("headline", "one_line") for w in dang):
                return rej("dangling_position:" + ",".join(dang))
            added.extend(dang)   # U-2(1)
        m = runner.VS_EXPLAIN_CONTRAST_REF_EN_RE.search(s) or runner.VS_EXPLAIN_CONTRAST_REF_JA_RE.search(s)
        if m:
            return rej("contrast_or_reference_word:" + m.group(0))
        if s.lower() in runner._VS_EXPLAIN_CONNECTIVE:
            continue
        cjk = bool(runner._VS_EXPLAIN_CJK_RE.search(s))
        nwords = len(s.split())
        too_long = (len(s) >= runner.VS_EXPLAIN_MAX_JA_CHARS) if cjk else (nwords >= runner.VS_EXPLAIN_MAX_EN_WORDS)
        # 逐語・隣接の棄却は長さより先に評価(R用)
        ns = runner.vs_norm_str(s, True)
        if ns and ns in nt and s.lower().lstrip("#").strip() not in runner.VS_STRUCTURAL_LABELS:
            if (len(s) >= 8) if cjk else (nwords >= runner.VS_EXPLAIN_MIN_VERBATIM_WORDS):
                return rej("remainder_verbatim_in_article")
        nss = ns.strip(runner._VS_EXPLAIN_SEG_EDGE)
        for (a, b) in spans:
            pre = runner.vs_norm_with_map(en[max(0, a - 400):a], True)[0].rstrip(runner._VS_EXPLAIN_SEG_EDGE)
            post = runner.vs_norm_with_map(en[b:b + 400], True)[0].lstrip(runner._VS_EXPLAIN_SEG_EDGE)
            if nss and (pre.endswith(nss) or post.startswith(nss)):
                return rej("remainder_adjacent_in_article")
        if too_long:
            if not use_r or cjk or nwords > MAX_LONG_WORDS or re.search(r"\d", s):
                return rej("remainder_too_long")
            out["r_used"].append(s)   # R: 長いが、逐語/隣接/対比/数字/閉じていない位置語のいずれでもない説明文→捨てる
        out["dropped"].append(s)
    all_spans = list(spans) + [el[w] for w in sorted(set(added))]
    merged2 = runner.vs_merge_spans(all_spans, en)
    out.update(status="resolved", reason=None, added_elements=sorted(set(added)), ranges=[en[a:b] for a, b in merged2],
               fragment_ranges=[en[a:b] for a, b in merged])
    out["spans"] = merged2
    out["fragment_spans"] = merged
    return out


def main():
    rows = rep.collect()
    uniq = {}
    for r in rows:
        uniq.setdefault((r["claim"], r["en"]), r)
    res = {"total_unique": len(uniq), "base_resolved": 0, "base_unresolved": 0, "d_type": [], "other_changed": []}
    changed_vs_old_p = []   # 現行Pが確定しているもの(base resolvedのうちP経由)の結果が試作で変わるか
    for (claim, en), u in uniq.items():
        base = runner._resolve_claim_string(claim, en, None)
        if base["status"] == "resolved":
            res["base_resolved"] += 1
            if str(base.get("level", "")).startswith("P:"):
                new = p_proto(claim, en)
                if new["status"] != "resolved" or new["ranges"] != base.get("ranges"):
                    changed_vs_old_p.append({"claim": claim[:200], "old": base.get("ranges"), "new": new["ranges"]})
            continue
        res["base_unresolved"] += 1
        l6 = rep.l6_restore(claim, en)
        t = rep.classify_unresolved(claim, {"reason": base.get("reason")}, l6, u.get("detected_by"))
        new = p_proto(claim, en)
        entry = {"claim": claim[:220], "type": t, "p_reason_now": (base.get("explain_split") or {}).get("reason"),
                 "proto_status": new["status"], "proto_reason": new["reason"], "q_used": new["q_used"], "r_used": new["r_used"],
                 "added_elements": new["added_elements"], "ranges": [x[:160] for x in new.get("ranges", [])]}
        if new["status"] == "resolved":
            # 誤範囲検査: (1)断片が最終範囲に全て含まれる (2)全範囲が記事に逐語で一意
            entry["fragments_inside_final"] = all(any(fa >= a and fb <= b for a, b in new["spans"]) for fa, fb in new["fragment_spans"])
            entry["unique_in_article"] = all(en.count(rg) == 1 for rg in new["ranges"])
        (res["d_type"] if t.startswith("d_") else res["other_changed"]).append(entry)
    res["regression_changed_vs_current_P_resolved"] = changed_vs_old_p
    json.dump(res, open(f"{OUT}/replay_d_type_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total_unique", res["total_unique"], "base_resolved", res["base_resolved"], "base_unresolved", res["base_unresolved"])
    print("regression changed vs current P-resolved:", len(changed_vs_old_p))
    for e in res["d_type"]:
        print("D:", e["proto_status"], e["proto_reason"], "q:", bool(e["q_used"]), "r:", bool(e["r_used"]), e["added_elements"], "|", e["claim"][:90])
        for rg in e["ranges"]:
            print("      range:", rg)
        if e["proto_status"] == "resolved":
            print("      checks: frags_inside=%s unique=%s" % (e["fragments_inside_final"], e["unique_in_article"]))
    print("OTHER unresolved changed by proto (non-d types):")
    for e in res["other_changed"]:
        if e["proto_status"] == "resolved":
            print("  !!", e["type"], e["claim"][:100], e["ranges"][:2])
    print("other unresolved still unresolved:", sum(1 for e in res["other_changed"] if e["proto_status"] != "resolved"))


main()
