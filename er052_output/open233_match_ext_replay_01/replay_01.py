# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_49 作業3-4・作業2-7: 照合の追補(VS_MATCH_EXT)の¥0再生と、
「日本語本文でしか確定しない指摘」の件数集計(分析専用)。

LLM/API/TTS/Web Searchは一切使わない。既存の実行記録(er052_output/open233_self_recovery_flow_runner_01_*/
instances_*/*.json)を読むだけ。既存ファイルは編集しない。

- 対象行: 委任_41の集計(aggregate_01.py)と同じ346行(BLOCKINGのK1 272 + K2 55 + K3 19)。
  行の抽出・本文の取り出し(同一cycleのen/ja_text_before_rewrite、前cycleのafter、cycle1は同一fixtureの
  借用)のロジックは aggregate_01.py(委任_41)からコピーして使う(import・編集はしない)。
- 照合: 現行runnerの`resolve_violation_spans`を、VS_MATCH_EXT=False(委任_42の照合)と True で実行し比較する
  (runnerをimportするが、API呼び出し関数は呼ばない)。claim文字列はstage2の`claim_text`(runnerが
  実際に照合へ渡す値)。
- 出力: 同ディレクトリの results_01.json / cases_01.csv / ja_only_count_01.json。
"""
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
sys.path.insert(0, ROOT)
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402  (照合関数のみ使用。API呼び出しはしない)

TARGET_NAMES = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")  # aggregate_01.pyと同一(委任_41の対象範囲)


# ---------------------------------------------------------------- aggregate_01.pyからコピー(行・本文の取り出し)
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


def cycle_texts(cycles, i):
    c = cycles[i]
    en = c.get("en_text_before_rewrite")
    ja = c.get("ja_text_before_rewrite")
    src_en = "same_cycle_before" if en is not None else None
    src_ja = "same_cycle_before" if ja is not None else None
    if i > 0:
        p = cycles[i - 1]
        if en is None and p.get("en_text_after_rewrite") is not None:
            en, src_en = p["en_text_after_rewrite"], "prev_cycle_after"
        if ja is None and p.get("ja_text_after_rewrite") is not None:
            ja, src_ja = p["ja_text_after_rewrite"], "prev_cycle_after"
    return en, ja, src_en, src_ja


def build_borrow_map(runs):
    en_t, ja_t = defaultdict(set), defaultdict(set)
    for run in runs:
        if not run["d"]["cycles"]:
            continue
        c0 = run["d"]["cycles"][0]
        if c0.get("en_text_before_rewrite") is not None:
            en_t[run["d"]["instance_id"]].add(c0["en_text_before_rewrite"])
        if c0.get("ja_text_before_rewrite") is not None:
            ja_t[run["d"]["instance_id"]].add(c0["ja_text_before_rewrite"])
    return {"en": {k: next(iter(v)) for k, v in en_t.items() if len(v) == 1},
            "ja": {k: next(iter(v)) for k, v in ja_t.items() if len(v) == 1}}


def collect_rows():
    runs, dirs = load_runs()
    borrow = build_borrow_map(runs)
    rows = []
    for run in runs:
        d = run["d"]
        cycles = d["cycles"]
        iid = d["instance_id"]
        for ci, c in enumerate(cycles):
            en, ja, src_en, src_ja = cycle_texts(cycles, ci)
            if ci == 0:
                if en is None and iid in borrow["en"]:
                    en, src_en = borrow["en"][iid], "borrowed_same_fixture"
                if ja is None and iid in borrow["ja"]:
                    ja, src_ja = borrow["ja"][iid], "borrowed_same_fixture"
            for k, s in enumerate(c["stage2_results"]):
                if s["materiality"] != "BLOCKING":
                    continue
                dev = s["dev"]
                if s.get("detected_by") == "precheck":
                    kind = "K3"
                elif dev.get("enumeration_source_claim"):
                    kind = "K2"
                else:
                    kind = "K1"
                claim = s.get("claim_text") or dev.get("claim_in_article", "")
                rows.append({"run": run["path"], "instance": iid, "cycle": c["cycle"], "k": k, "kind": kind,
                             "fact": s.get("related_fact_id"), "origin": s.get("origin"), "claim": claim,
                             "en": en, "ja": ja, "src_en": src_en, "src_ja": src_ja})
    return rows, dirs


# ---------------------------------------------------------------- 再生
def resolve(claim, en, ja, ext):
    runner.VS_MATCH_EXT = ext
    try:
        return runner.resolve_violation_spans(claim, en, ja)
    finally:
        runner.VS_MATCH_EXT = False


def summarize(res):
    return {"status": res["status"], "lang": res.get("lang"), "level": res.get("level"),
            "reason": res.get("reason"), "ranges": list(res.get("ranges") or []),
            "edge_removed": res.get("edge_removed"), "label_only_ranges": res.get("label_only_ranges")}


def transition(off, on):
    if off["status"] == "resolved" and on["status"] != "resolved":
        return "確定→確定不能"
    if off["status"] != "resolved" and on["status"] == "resolved":
        return "確定不能→確定"
    if off["status"] == "resolved" and on["status"] == "resolved":
        if off["ranges"] != on["ranges"] or off["lang"] != on["lang"]:
            return "確定→確定(範囲が変わった)"
        return "確定→確定(同じ範囲)"
    if off["reason"] != on["reason"]:
        return "確定不能→確定不能(理由が変わった)"
    return "確定不能→確定不能(同じ)"


def main():
    rows, dirs = collect_rows()
    out_rows = []
    skipped_no_text = 0
    for r in rows:
        if r["en"] is None and r["ja"] is None:
            skipped_no_text += 1
            r["off"] = r["on"] = None
            r["transition"] = "本文記録なし(再生不能)"
            out_rows.append(r)
            continue
        off = summarize(resolve(r["claim"], r["en"], r["ja"], False))
        on = summarize(resolve(r["claim"], r["en"], r["ja"], True))
        r["off"], r["on"] = off, on
        r["transition"] = transition(off, on)
        out_rows.append(r)

    tr_count = Counter(r["transition"] for r in out_rows)
    by_level = defaultdict(Counter)  # 「OFFの照合レベル→ONの照合レベル」別
    by_article = defaultdict(Counter)
    for r in out_rows:
        if r["off"] is None:
            continue
        lv = f"{r['off']['level'] or ('unverified:' + str(r['off']['reason']))} -> " \
             f"{r['on']['level'] or ('unverified:' + str(r['on']['reason']))}"
        by_level[lv][r["transition"]] += 1
        by_article[r["instance"]][r["transition"]] += 1

    res_to_unres = [r for r in out_rows if r["transition"] == "確定→確定不能"]
    unres_to_res = [r for r in out_rows if r["transition"] == "確定不能→確定"]
    range_changed = [r for r in out_rows if r["transition"] == "確定→確定(範囲が変わった)"]
    reason_changed = [r for r in out_rows if r["transition"] == "確定不能→確定不能(理由が変わった)"]

    def slim(r):
        return {"run": r["run"], "instance": r["instance"], "cycle": r["cycle"], "kind": r["kind"], "fact": r["fact"],
                "claim": r["claim"], "off": r["off"], "on": r["on"]}

    # 委任_45の句読点型(U03・U04・U07)の確認: 記録上、OFFで確定不能だった末尾句読点型
    l5_rows = [r for r in unres_to_res if r["on"]["level"] == "L5_edge_punct"]
    u_marks = {
        "U03": "Trump’s proposed Hormuz fee vanished overnight.",
        "U04": "so the flashy 20% plan left the stage.",
        "U07": "before recovering.",
    }
    u_hits = {u: [slim(r) for r in out_rows if r["claim"].strip().strip("“”").endswith(t)] for u, t in u_marks.items()}

    # 作業2-7: 日本語本文でしか確定しない指摘(OFF=委任_42の照合、EN・JA両方に照合)
    ja_only = [r for r in out_rows if r["off"] is not None and r["off"]["status"] == "resolved"
               and r["off"]["lang"] == "JA"]
    ja_only_by_article = Counter(r["instance"] for r in ja_only)
    ja_only_by_fact = Counter((r["instance"], r["fact"]) for r in ja_only)
    ja_only_by_origin = Counter(r["origin"] for r in ja_only)
    json.dump({
        "scope": "既存のBLOCKING行(委任_41と同じ対象)のうち、OFF(委任_42の照合)でEN本文では確定せずJA本文でのみ確定した行",
        "n_blocking_rows": len(out_rows), "n_replayable": len(out_rows) - skipped_no_text,
        "n_ja_only": len(ja_only), "by_article": dict(ja_only_by_article),
        "by_article_fact": {f"{a}|{f}": n for (a, f), n in ja_only_by_fact.items()},
        "by_origin": dict(ja_only_by_origin),
        "rows": [slim(r) for r in ja_only],
    }, open(os.path.join(HERE, "ja_only_count_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    result = {
        "scope": {"n_dirs": len(dirs), "n_blocking_rows": len(out_rows), "skipped_no_text": skipped_no_text,
                  "kind_counts": dict(Counter(r["kind"] for r in out_rows))},
        "transition_counts": dict(tr_count),
        "by_level_transition": {k: dict(v) for k, v in sorted(by_level.items())},
        "by_article_transition": {k: dict(v) for k, v in sorted(by_article.items())},
        "resolved_to_unresolved_ALL_verbatim": [slim(r) for r in res_to_unres],
        "unresolved_to_resolved": [slim(r) for r in unres_to_res],
        "resolved_range_changed": [slim(r) for r in range_changed],
        "unresolved_reason_changed": [slim(r) for r in reason_changed],
        "L5_edge_punct_new_resolved_count": len(l5_rows),
        "U03_U04_U07_rows": {u: {"n_rows": len(v), "transitions": dict(Counter(x["on"]["level"] if x["on"] else None
                                                                              for x in v))} for u, v in u_hits.items()},
        "n_ja_only_in_346": len(ja_only),
    }
    json.dump(result, open(os.path.join(HERE, "results_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["run", "instance", "cycle", "kind", "fact", "transition", "off_status", "off_lang", "off_level",
                    "off_reason", "on_status", "on_lang", "on_level", "on_reason", "claim"])
        for r in out_rows:
            o, n = r["off"] or {}, r["on"] or {}
            w.writerow([r["run"], r["instance"], r["cycle"], r["kind"], r["fact"], r["transition"],
                        o.get("status"), o.get("lang"), o.get("level"), o.get("reason"),
                        n.get("status"), n.get("lang"), n.get("level"), n.get("reason"), r["claim"]])
    print(json.dumps({k: result[k] for k in ("scope", "transition_counts", "by_level_transition",
                                              "L5_edge_punct_new_resolved_count", "U03_U04_U07_rows",
                                              "n_ja_only_in_346")}, ensure_ascii=False, indent=1))
    print("確定→確定不能 全件:", len(res_to_unres))
    for r in res_to_unres:
        print(json.dumps(slim(r), ensure_ascii=False))


if __name__ == "__main__":
    main()
