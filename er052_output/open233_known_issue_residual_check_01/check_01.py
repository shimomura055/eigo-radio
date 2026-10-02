# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_49 作業2-6: 既知問題集合による「見逃しの疑い」の一覧(分析専用)。

LLM/API/TTS/Web Search/Trial再実行なし。標準ライブラリのみ。既存モジュール(runner等)はimportしない。

定義(類似度は使わない。空白の正規化以外の正規化もしない=大文字小文字・引用符は逐語のまま):
- 既知問題集合: 既存の全実行記録(er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json)から、
  記事(instance_id)ごとに「過去に1回でも最終BLOCKING(Stage 2の最終materiality==BLOCKING)になった確定範囲」を集める。
  確定範囲 = stage2_resultsの`claim_span_text`(新方式=委任_42以降の記録)があればそれ。無ければ、指摘文字列
  (`claim_text`)から外側を囲む1組の引用符を外したもの(旧記録。逐語・空白正規化のみ。説明文を含む長文は
  最終本文に逐語で残ることがほぼ無いので結果に影響しない)。複数範囲は改行区切りで1件ずつに分解する。
  12文字未満は短すぎて偶然一致しうるため集合へ入れない(件数を results に記録)。
- 見逃しの疑い: 指定した実行ディレクトリの合格系instance(final_stateがRESOLVED_*/ACCEPTABLE_STAGE1、人間確認なし)について、
  「最終英語本文にその範囲が逐語で残り(空白正規化のみ)、かつその実行で一度もBLOCKINGで指摘されていない」もの。
  「その実行で指摘されていない」= その実行のBLOCKING指摘(claim_text)の空白正規化文字列が、範囲を包含する/範囲に包含される
  (どちらか。12文字以上同士)のいずれにも当たらない。
- 最終英語本文: 最後のcycleの`en_text_after_rewrite`(書き換えがあった場合)。書き換えが無かった実行は元記事=同一
  instance_idの他の実行のcycle1`en_text_before_rewrite`(1種類に定まる場合のみ借用)。得られない場合は
  「本文記録なし(判定不能)」として別に数える。
出力: 同ディレクトリの results_<tag>.json と cases_<tag>.csv(tagは--targetのディレクトリ名の`_01_`以降。例 rep22)。
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ER = os.path.join(ROOT, "er052_output")
PASS_STATES = ("ACCEPTABLE_STAGE1", "RESOLVED_STAGE2_DOWNGRADE", "RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE")
MIN_LEN = 12
PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def strip_pair(s):
    s = (s or "").strip()
    if len(s) >= 2:
        for o, c in PAIRS:
            if s[0] == o and s[-1] == c:
                return s[1:-1].strip()
    return s


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def all_instances():
    out = []
    for dd in sorted(glob.glob(os.path.join(ER, "open233_self_recovery_flow_runner_01_*"))):
        for f in sorted(glob.glob(os.path.join(dd, "instances_*", "*.json")) + glob.glob(os.path.join(dd, "instances", "*.json"))):
            try:
                d = load(f)
            except Exception:  # noqa: BLE001
                continue
            if "cycles" in d and "final_state" in d:
                out.append((os.path.relpath(f, ER).replace("\\", "/"), d))
    return out


def blocking_ranges(d):
    """1実行の最終BLOCKING確定範囲(逐語)と、その実行のBLOCKING指摘文字列の一覧。"""
    ranges, claims = [], []
    for c in d.get("cycles", []):
        for s in c.get("stage2_results", []):
            if s.get("materiality") != "BLOCKING":
                continue
            ct = s.get("claim_text") or ""
            claims.append(ws(ct))
            span = s.get("claim_span_text")
            for part in (span.split("\n") if span else [strip_pair(ct)]):
                if ws(part):
                    ranges.append((ws(part), "claim_span_text" if span else "claim_text_stripped"))
    return ranges, claims


def final_en(d, borrowed):
    for c in reversed(d.get("cycles", [])):
        if c.get("en_text_after_rewrite") is not None:
            return c["en_text_after_rewrite"], "after_rewrite"
    return borrowed, ("borrowed_original" if borrowed is not None else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="指定する実行ディレクトリ(例 er052_output/open233_self_recovery_flow_runner_01_rep22)")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    target = os.path.abspath(a.target)
    tag = a.tag or os.path.basename(target).split("_01_", 1)[-1]

    insts = all_instances()
    # 既知問題集合(記事=instance_idごと)
    known = defaultdict(lambda: defaultdict(set))  # iid -> range -> {run paths}
    too_short = 0
    borrow_en = defaultdict(set)
    for path, d in insts:
        iid = d["instance_id"]
        c0 = d["cycles"][0] if d.get("cycles") else None
        if c0 and c0.get("en_text_before_rewrite") is not None:
            borrow_en[iid].add(c0["en_text_before_rewrite"])
        rngs, _ = blocking_ranges(d)
        for r, _src in rngs:
            if len(r) < MIN_LEN:
                too_short += 1
                continue
            known[iid][r].add(path)
    borrow = {k: next(iter(v)) for k, v in borrow_en.items() if len(v) == 1}

    cases, n_pass, n_nodata, n_pass_with_known = [], 0, 0, 0
    tpaths = [(p, d) for p, d in insts if os.path.abspath(os.path.join(ER, p)).startswith(target + os.sep)]
    for path, d in tpaths:
        if d["final_state"] not in PASS_STATES:
            continue
        n_pass += 1
        iid = d["instance_id"]
        text, src = final_en(d, borrow.get(iid))
        if text is None:
            n_nodata += 1
            cases.append({"run": path, "instance": iid, "final_state": d["final_state"], "range": None,
                          "verdict": "本文記録なし(判定不能)", "known_in_runs": None})
            continue
        ft = ws(text)
        _r, claims = blocking_ranges(d)
        any_known = False
        for rng, runs in known.get(iid, {}).items():
            if rng not in ft:
                continue
            any_known = True
            flagged = any((rng in c or (len(c) >= MIN_LEN and c in rng)) for c in claims)
            cases.append({"run": path, "instance": iid, "final_state": d["final_state"], "range": rng,
                          "verdict": "指摘済み(疑いなし)" if flagged else "見逃しの疑い",
                          "known_in_runs": sorted(runs)[:6], "n_known_runs": len(runs), "final_text_source": src})
        n_pass_with_known += 1 if any_known else 0

    suspects = [c for c in cases if c["verdict"] == "見逃しの疑い"]
    res = {
        "tag": tag, "target": os.path.relpath(target, ROOT).replace("\\", "/"),
        "n_all_runs_scanned": len(insts), "known_set_size_by_article": {k: len(v) for k, v in sorted(known.items())},
        "known_ranges_skipped_too_short(<12字)": too_short,
        "n_pass_family_instances_in_target": n_pass, "n_pass_no_text_record(判定不能)": n_nodata,
        "n_pass_with_any_known_range_remaining": n_pass_with_known,
        "n_suspect_cases(見逃しの疑い)": len(suspects),
        "n_suspect_instances": len({c["run"] for c in suspects}),
        "suspects_by_article": dict(Counter(c["instance"] for c in suspects)),
        "suspects": suspects,
        "n_flagged_cases(指摘済み)": sum(1 for c in cases if c["verdict"].startswith("指摘済み")),
    }
    json.dump(res, open(os.path.join(HERE, f"results_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, f"cases_{tag}.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["run", "instance", "final_state", "verdict", "range", "n_known_runs", "known_in_runs"])
        for c in cases:
            w.writerow([c["run"], c["instance"], c["final_state"], c["verdict"], c["range"],
                        c.get("n_known_runs"), ";".join(c.get("known_in_runs") or [])])
    print(json.dumps({k: v for k, v in res.items() if k != "suspects"}, ensure_ascii=False, indent=1))
    for c in suspects:
        print("SUSPECT", c["run"], "|", c["range"])


if __name__ == "__main__":
    main()
