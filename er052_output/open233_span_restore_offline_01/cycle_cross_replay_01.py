# -*- coding: utf-8 -*-
# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_66 作業3-2: cycle横断replay(Opus#9代替案、¥0、API呼び出しなし)。
# 既存ログで「cycle N-1の本文で確定したclaimを、cycle Nの本文(=N-1のRewrite後)に当てる」。Checkerが前cycleの
# 本文を古く引用する型(B3 s2 cycle2の`so`)の再現。L6(runner実装、`VS_SENTENCE_RESTORE`ON)が
#  (1)誤った文を選ばない(正解=N-1のRewriteが書き換えた文を含む文群、との重なりで判定。誤選択0が必須)
#  (2)issueの引用語句が復元範囲に無いとき`issue_focus_absent`が適切に発火する
# を確認する。実行: .venv\Scripts\python.exe er052_output\open233_span_restore_offline_01\cycle_cross_replay_01.py
from __future__ import annotations

import collections
import difflib
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402

OUT_DIR = "er052_output/open233_span_restore_offline_01"
runner.VS_MATCH_EXT = True
runner.VS_EXPLAIN_SPLIT = True
runner.VS_SENTENCE_RESTORE = True


def article_at(d, idx, fixture_en):
    cycles = d.get("cycles", [])
    if idx == 0:
        return cycles[0].get("en_text_before_rewrite") or fixture_en
    prev = cycles[idx - 1]
    return prev.get("en_text_after_rewrite") or prev.get("en_text_before_rewrite")


def rewrite_pairs(cycle):
    out = []
    for rr in cycle.get("rewrite_records", []) or []:
        h = rr.get("handoff") or {}
        for att in h.get("level_attempts", []) or []:
            if att.get("result") == "success":
                for ba in att.get("before_after", []) or []:
                    out.append(ba)
    return out


def main():
    fixtures = {i["instance_id"]: i["fixture"]["article_text"] for i in runner.build_target_instances()}
    files = sorted(glob.glob("er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json"))
    rows, cat = [], collections.Counter()
    for p in files:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        cycles = d.get("cycles") or []
        iid = d.get("instance_id") or os.path.basename(p)[:-5]
        for ci in range(len(cycles) - 1):
            c = cycles[ci]
            en_prev = article_at(d, ci, fixtures.get(iid))
            en_next = article_at(d, ci + 1, fixtures.get(iid))
            if not en_prev or not en_next or en_prev == en_next:
                continue
            pairs = rewrite_pairs(c)
            for sr in c.get("stage2_results", []):
                if sr.get("materiality") != "BLOCKING" or sr.get("detected_by") == "precheck":
                    continue
                claim = sr.get("claim_text") or ""
                if not claim.strip():
                    continue
                dev = sr.get("dev") or {}
                issue = dev.get("issue") or sr.get("issue") or ""
                prev = runner._resolve_claim_string(claim, en_prev, None)
                if prev["status"] != "resolved":
                    cat["prev_unresolved(対象外)"] += 1
                    continue
                nxt = runner._resolve_claim_string(claim, en_next, None)
                rec = {"file": p.replace("er052_output/open233_self_recovery_flow_runner_01", "").replace("\\", "/"),
                       "instance": iid, "cycle_prev": c.get("cycle"), "claim": claim, "issue": issue,
                       "prev_level": prev.get("level"), "next_status": nxt["status"], "next_level": nxt.get("level")}
                if nxt["status"] == "resolved" and nxt.get("level") != runner.VS_L6_LEVEL:
                    cat["next_resolved_by_L0-P(L6非関与)"] += 1
                    rec["category"] = "next_resolved_by_L0_P"
                    rows.append(rec)
                    continue
                if nxt["status"] != "resolved":
                    cat["next_unresolved(L6も復元せず=従来どおりunresolvable)"] += 1
                    rec["category"] = "next_unresolved"
                    rec["l6"] = {k: (nxt.get("sentence_restore") or {}).get(k) for k in ("status", "reason")}
                    rows.append(rec)
                    continue
                # L6が復元した: 正解(N-1のRewriteが書き換えた文を含む文群)と比較
                sr6 = nxt["sentence_restore"]
                s, e = nxt["spans"][0]
                pspan = prev["spans"][0] if prev["spans"] else None
                truth = None
                for ba in pairs:
                    b, a_ = ba.get("before"), ba.get("after")
                    if not b or a_ is None or not pspan:
                        continue
                    pos = en_prev.find(b)
                    if pos >= 0 and pos < pspan[1] and pos + len(b) > pspan[0] and a_ and en_next.count(a_) == 1:
                        ap = en_next.find(a_)
                        truth = (ap, ap + len(a_))
                        break
                segs = runner.vs_sentence_segments_l6(en_next)
                oracle = "rewrite_pair" if truth else None
                if not truth and pspan:
                    # 補助の正解判定(replayの検証用オラクルであり、照合には使わない): 文単位でN-1とNを対応づけ(difflib)、
                    # claimを含むN-1の文群が`replace`された先のNの文群を正解とする。
                    sp = runner.vs_sentence_segments_l6(en_prev)
                    ps = [en_prev[a:b] for a, b in sp]
                    ns = [en_next[a:b] for a, b in segs]
                    claim_idx = [i for i, (a, b) in enumerate(sp) if a < pspan[1] and b > pspan[0]]
                    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ps, ns, autojunk=False).get_opcodes():
                        if tag == "replace" and any(i1 <= i < i2 for i in claim_idx) and j2 > j1:
                            truth = (segs[j1][0], segs[j2 - 1][1])
                            oracle = "sentence_diff"
                            break
                        if tag == "delete" and any(i1 <= i < i2 for i in claim_idx):
                            oracle = "claim_sentence_deleted"
                if truth:
                    tg = [sg for sg in segs if sg[0] < truth[1] and sg[1] > truth[0]]
                    overlap = s < truth[1] and e > truth[0]
                    verdict = "restored_overlaps_rewritten_sentence(OK)" if overlap else "WRONG_restored_elsewhere"
                elif oracle == "claim_sentence_deleted":
                    verdict = "WRONG_restored_although_claim_sentence_was_deleted"
                else:
                    verdict = "no_truth_to_judge"
                fa = runner.vs_l6_focus_absent(runner.vs_l6_issue_quoted_phrases(issue), en_next[s:e],
                                               sr6.get("claim_core") or claim)
                rec.update({"category": "L6_restored", "verdict": verdict, "restored": en_next[s:e], "oracle": oracle,
                            "restore_reason": sr6.get("restore_reason"), "n_sentences": sr6.get("n_sentences"),
                            "truth_after_text": (en_next[truth[0]:truth[1]] if truth else None),
                            "issue_focus": fa, "residual_check": sr6.get("residual_check"), "anchors": sr6.get("anchors")})
                cat["L6_restored:" + verdict] += 1
                if fa["absent"]:
                    cat["L6_restored_and_issue_focus_absent_fires"] += 1
                rows.append(rec)
    uniq = {}
    for r in rows:
        k = (r["claim"], r.get("restored"), r["category"])
        u = uniq.setdefault(k, dict(r, occurrences=[]))
        u["occurrences"].append(f"{r['file']}:{r['instance']}:c{r['cycle_prev']}")
    uq = list(uniq.values())
    l6 = [r for r in uq if r["category"] == "L6_restored"]
    summary = {"files": len(files), "runs_by_category": dict(cat),
               "L6_restored_unique": len(l6),
               "L6_restored_by_verdict_unique": dict(collections.Counter(r["verdict"] for r in l6)),
               "wrong_restore_unique": sum(1 for r in l6 if r["verdict"].startswith("WRONG")),
               "issue_focus_absent_fires_unique": sum(1 for r in l6 if r["issue_focus"]["absent"]),
               "issue_focus_present_unique(通常Rewrite)": sum(1 for r in l6 if not r["issue_focus"]["absent"] and r["issue_focus"]["phrases"]),
               "issue_has_no_quoted_phrase_unique(通常Rewrite)": sum(1 for r in l6 if not r["issue_focus"]["phrases"])}
    json.dump({"summary": summary, "unique_rows": uq}, open(f"{OUT_DIR}/cycle_cross_replay_01.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=str)
    L = ["# cycle横断replay結果(委任_66、¥0)\n",
         "既存ログのcycle N-1の確定claimを、cycle N(N-1のRewrite後)の本文へ当てた(B3型の古い引用の再現)。\n",
         "## 集計\n", "```", json.dumps(summary, ensure_ascii=False, indent=1), "```\n",
         "## L6が復元した全件(unique)\n"]
    for i, r in enumerate(l6, 1):
        L.append(f"### X{i:02d} {r['verdict']} [oracle={r['oracle']}] (出現{len(r['occurrences'])}回: {', '.join(r['occurrences'][:3])})")
        L.append(f"- claim(N-1で確定したCheckerの引用): `{r['claim'][:300]}`")
        L.append(f"- issue: {r['issue'][:300]}")
        L.append(f"- 復元文({r['n_sentences']}文, {r['restore_reason']}): `{r['restored'][:400]}`")
        L.append(f"- 正解(N-1のRewrite後の文): `{(r['truth_after_text'] or '(判定材料なし)')[:300]}`")
        L.append(f"- issue引用語句: {json.dumps(r['issue_focus'], ensure_ascii=False)[:500]} -> issue_focus_absent={'発火(Rewrite見送り+Recheckのみ)' if r['issue_focus']['absent'] else '非発火(通常Rewrite)'}\n")
    open(f"{OUT_DIR}/cycle_cross_replay_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
