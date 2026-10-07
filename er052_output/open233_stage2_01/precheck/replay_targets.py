# -*- coding: utf-8 -*-
"""STAGE2-01 委任_01 作業6: 現行Stage1版(stage1_coverage_v1、PROMPT_SHA256一致)のログが残る記事の一覧(API無し)。"""
import os, re, json, collections, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
import er052_open233_stage1_coverage_checker_01 as cov
cur = cov.PROMPT_SHA256
keys = list(cur)
pat = {k: re.compile('"%s": "([0-9a-f]{64})"' % k) for k in keys}
inst, other = [], collections.Counter()
for root, ds, fs in os.walk("er052_output"):
    for f in fs:
        if not f.endswith(".json"):
            continue
        p = os.path.join(root, f).replace(os.sep, "/")
        if "/open233_stage2_01/" in p:
            continue
        try:
            t = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if '"R3_PROMPT_TEMPLATE"' not in t:
            continue
        h = {k: (pat[k].search(t).group(1) if pat[k].search(t) else None) for k in keys}
        diff = [k for k in keys if h[k] != cur[k]]
        top = p.split("/")[1]
        is_dup = ("/after_instances/" in p) or bool(re.search(r"/worker\d_instances/", p)) or "dryrun" in top
        is_inst = "/checker/runs/" in p or re.search(r"/(runs|runs/s1|checker_after_01/runs|replay/fixed/runs|runtime_evidence/run/runs)/[^/]+\.json$", p)
        if diff:
            other[(top, "diff:" + ",".join(diff))] += 1
            continue
        if is_dup or not is_inst:
            other[(top, "same_but_excluded(dup/dryrun/stage1_experiment_artifact)")] += 1
            continue
        try:
            d = json.loads(t)
        except Exception:
            continue
        if not isinstance(d, dict) or "cycles" not in d:  # runner全体のインスタンスログ(cyclesあり)のみ。Stage1単体実験の出力は除外
            other[(top, "same_but_stage1_only_experiment_output(no cycles)")] += 1
            continue
        inst.append({"path": p, "set": top, "final_state": d.get("final_state"), "n_cycles": len(d.get("cycles") or []),
                     "rewrite_occurred": any((c.get("rewrite_records") for c in d.get("cycles") or [])),
                     "group": d.get("group"), "instance_id": d.get("instance_id")})
by_set = collections.Counter(i["set"] for i in inst)
out = {"current_stage1_version": {"module_version": cov.MODULE_VERSION, "PROMPT_SHA256": cur},
       "match_rule": "ログ内prompt_sha256辞書の10要素全てが現行cov.PROMPT_SHA256と一致(テンプレート・schema・FLAG_DESCRIPTIONS)",
       "n_instance_logs_same_version": len(inst), "by_set": dict(by_set),
       "other_logs": {f"{a}|{b}": n for (a, b), n in sorted(other.items())},
       "b3_trial": "open233_b3_trial_01は--no-checkerのためStage1ログ自体が無い(版違い以前に対象外)",
       "note": "r3_support_fact_idsは全ログで未保存(Grep確認)。復元には同版でのreplay(API要)が必要。同一記事の重複(ccp 18=meta nb 10+他8、e2e_02等)は記事単位ではinstance単位=記事。",
       "instances": inst}
json.dump(out, open(pathlib.Path(__file__).parent / "replay_targets.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "instances"}, ensure_ascii=False, indent=1))
