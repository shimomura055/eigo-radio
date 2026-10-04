# -*- coding: utf-8 -*-
# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_66 作業3-4: U-2(1)「位置語→構造要素の対応」の設計案のオフラインreplay(¥0、実装しない)。
# 承認済みP-strict-closed(`vs_explain_split_resolve`)のうち「位置語が名指しする構造要素(見出し行・In one line直下の1行)が
# どの断片とも重ならない」ことで棄却する`dangling_position`だけを、「その構造要素を範囲に加える(拡張のみ)」に変えた場合に、
# 過去ログの(d)説明文混入型5件がどう変わるかを見る。他のP-strict-closedのガード(位置語[段落/末尾等]・対比参照語・長さ・
# 逐語・隣接)はそのまま。runnerは変更しない(このファイル内の試作)。実行:
#   .venv\Scripts\python.exe er052_output\open233_span_restore_offline_01\u2_position_word_replay_01.py
from __future__ import annotations

import importlib.util
import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
HERE = "er052_output/open233_span_restore_offline_01"
spec = importlib.util.spec_from_file_location("replay_01_for_u2", f"{HERE}/replay_01.py")
rep = importlib.util.module_from_spec(spec)
sys.modules["replay_01_for_u2"] = rep
spec.loader.exec_module(rep)
runner = rep.runner

CLOSED_VOCAB = ("headline", "one_line")  # U-2(1)の対象。`opening`(冒頭)は閉じた語彙に含めない(従来どおり棄却)


def p_with_u2(claim_text: str, en: str) -> dict:
    """`vs_explain_split_resolve`の複製。`dangling_position`のうち閉じた語彙(headline/one_line)は棄却せず、
    名指しされた構造要素を範囲へ加える。それ以外の分岐・順序・ガードは原本と同一。"""
    claim = (claim_text or "").strip()
    out = {"status": "unverified", "reason": None, "fragments": [], "added_elements": [], "spans": [], "ranges": []}

    def rej(r, **kw):
        out["reason"] = "explain_split_rejected:" + r
        out.update(kw)
        return out
    frags, balanced, segs = runner._vs_explain_extract_fragments(claim)
    if not frags:
        return rej("no_quote")
    if not balanced:
        return rej("unbalanced_quote")
    out["fragments"] = [f[2] for f in frags]
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
            if any(w not in CLOSED_VOCAB for w in dang):
                return rej("dangling_position:" + ",".join(dang))
            added.extend(dang)  # ★U-2(1): 閉じた語彙の構造要素は範囲へ加える(棄却しない)
        m = runner.VS_EXPLAIN_CONTRAST_REF_EN_RE.search(s) or runner.VS_EXPLAIN_CONTRAST_REF_JA_RE.search(s)
        if m:
            return rej("contrast_or_reference_word:" + m.group(0))
        if s.lower() in runner._VS_EXPLAIN_CONNECTIVE:
            continue
        cjk = bool(runner._VS_EXPLAIN_CJK_RE.search(s))
        if (len(s) >= runner.VS_EXPLAIN_MAX_JA_CHARS) if cjk else (len(s.split()) >= runner.VS_EXPLAIN_MAX_EN_WORDS):
            return rej("remainder_too_long")
        ns = runner.vs_norm_str(s, True)
        if ns and ns in nt and s.lower().lstrip("#").strip() not in runner.VS_STRUCTURAL_LABELS:
            if (len(s) >= 8) if cjk else (len(s.split()) >= runner.VS_EXPLAIN_MIN_VERBATIM_WORDS):
                return rej("remainder_verbatim_in_article")
        nss = ns.strip(runner._VS_EXPLAIN_SEG_EDGE)
        adj = False
        for (a, b) in spans:
            pre = runner.vs_norm_with_map(en[max(0, a - 400):a], True)[0].rstrip(runner._VS_EXPLAIN_SEG_EDGE)
            post = runner.vs_norm_with_map(en[b:b + 400], True)[0].lstrip(runner._VS_EXPLAIN_SEG_EDGE)
            if nss and (pre.endswith(nss) or post.startswith(nss)):
                adj = True
                break
        if adj:
            return rej("remainder_adjacent_in_article")
    added = sorted(set(added))
    all_spans = list(spans) + [el[w] for w in added]
    merged2 = runner.vs_merge_spans(all_spans, en)
    out.update(status="resolved", reason=None, added_elements=added, spans=merged2, ranges=[en[a:b] for a, b in merged2],
               fragment_spans=merged)
    return out


def main():
    rows = rep.collect()
    uniq = {}
    for r in rows:
        k = (r["claim"], r["en"])
        u = uniq.setdefault(k, dict(r, occurrences=[]))
        u["occurrences"].append(f"{r['file']}:{r['instance']}:c{r['cycle']}")
    out = []
    for (claim, en), u in uniq.items():
        base = runner._resolve_claim_string(claim, en, None)  # 現行(MATCH_EXT+EXPLAIN_SPLIT)
        if base["status"] == "resolved":
            continue
        l6 = rep.l6_restore(claim, en)
        t = rep.classify_unresolved(claim, {"reason": base.get("reason")}, l6, u.get("detected_by"))
        if not t.startswith("d_"):
            continue
        es = base.get("explain_split") or {}
        new = p_with_u2(claim, en)
        row = {"claim": claim, "issue": u.get("issue"), "occurrences": u["occurrences"], "p_reason_now": es.get("reason"),
               "u2_status": new["status"], "u2_reason": new["reason"], "added_elements": new["added_elements"]}
        if new["status"] == "resolved":
            row["u2_ranges"] = new["ranges"]
            row["fragment_ranges"] = [en[a:b] for a, b in new["fragment_spans"]]
            # 誤範囲0の確認: (1)断片の範囲がすべて最終範囲に含まれる(縮小0) (2)追加した範囲は名指しされた構造要素そのもの
            row["fragments_all_inside_final_ranges"] = all(any(fa >= a and fb <= b for a, b in new["spans"])
                                                           for fa, fb in new["fragment_spans"])
            el = runner._vs_explain_structure_elements(en)
            row["added_ranges_are_exactly_named_elements"] = all(
                any(sp == el[w] or (sp[0] <= el[w][0] and sp[1] >= el[w][1]) for sp in new["spans"]) for w in new["added_elements"])
            row["every_range_is_verbatim_unique_in_article"] = all(en.count(rg) == 1 for rg in new["ranges"])
        out.append(row)
    resolved = [r for r in out if r["u2_status"] == "resolved"]
    summary = {"d_type_unique": len(out), "restorable_by_u2_1": len(resolved),
               "still_rejected_by_reason": {}, "wrong_range_count": sum(
                   1 for r in resolved if not (r["fragments_all_inside_final_ranges"] and r["added_ranges_are_exactly_named_elements"]
                                               and r["every_range_is_verbatim_unique_in_article"]))}
    for r in out:
        if r["u2_status"] != "resolved":
            summary["still_rejected_by_reason"][r["u2_reason"]] = summary["still_rejected_by_reason"].get(r["u2_reason"], 0) + 1
    json.dump({"summary": summary, "rows": out}, open(f"{HERE}/u2_position_word_replay_01.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    L = ["# U-2(1) 位置語→構造要素 replay(委任_66、¥0、実装なし)\n", "```", json.dumps(summary, ensure_ascii=False, indent=1), "```\n"]
    for i, r in enumerate(out, 1):
        L.append(f"## D{i} {r['u2_status']} (現行P棄却理由: {r['p_reason_now']}) 出現{len(r['occurrences'])}回")
        L.append(f"- claim: `{r['claim'][:300]}`")
        L.append(f"- issue: {str(r['issue'])[:300]}")
        L.append(f"- U-2(1)後: status={r['u2_status']} reason={r['u2_reason']} 追加要素={r['added_elements']}")
        if r["u2_status"] == "resolved":
            L.append(f"- 断片の範囲: {json.dumps(r['fragment_ranges'], ensure_ascii=False)[:400]}")
            L.append(f"- 最終範囲: {json.dumps(r['u2_ranges'], ensure_ascii=False)[:600]}")
            L.append(f"- 検査: 断片が全て含まれる={r['fragments_all_inside_final_ranges']} / 追加は名指しされた要素そのもの="
                     f"{r['added_ranges_are_exactly_named_elements']} / 全範囲が記事に一意に逐語={r['every_range_is_verbatim_unique_in_article']}")
        L.append("")
    open(f"{HERE}/u2_position_word_replay_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    for r in out:
        print(r["u2_status"], r["u2_reason"], r["added_elements"], "|", r["claim"][:100])


if __name__ == "__main__":
    main()
