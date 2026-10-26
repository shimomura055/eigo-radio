# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: 付録(事後・探索。判定規則には使わない。API 0)。
 (1) Voice×本文×レベル cell別の主要指標平均(交互作用の確認) (2) fresh takeの最終status・1 takeあたりTTS生成回数(=retry/費用の代理)
 (3) 最終音声(takeが採用するwav。Stdは6%減速後)に文中≥1秒停止が残る率 (4) 全≥1秒(位置非依存)でのVoice順位
使い方: py ym7_extra_01.py --summary measure/summary_01.json --samples measure/samples_01.json --out RESULT_EXTRA_01.md --json measure/extra_01.json"""
import argparse, collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ym7_measure_01 as m7   # noqa: E402
lib = m7.lib
VOICES = ["Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager"]
FRESH = "er121_output/family_y_voice1_male7_trial_01"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--samples", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args(argv)
    S = json.load(open(a.summary, encoding="utf-8"))
    rows = [r for r in json.load(open(a.samples, encoding="utf-8")) if r["kind"] == "main"]
    takes = json.load(open(a.samples.replace(".json", "_takes.json"), encoding="utf-8"))
    texts = {(lv, b): lib.body_text(lv, b) for lv in ("a2", "b1b") for b in (1, 2, 3)}
    L = ["# RESULT_EXTRA_01(事後・探索の付録。判定規則(DESIGN_01 §6/§7)には使っていない)", ""]
    # (1) cell別
    L += ["## 1. Voice×本文×レベル cell別: 文中≥1秒の停止 回/sample (n)", "", "| Voice | " + " | ".join(f"{lv}-本文{b}" for lv in ('Std', 'Adv') for b in (1, 2, 3)) + " |", "|---|" + "---|" * 6]
    cells = [("a2", 1), ("a2", 2), ("a2", 3), ("b1b", 1), ("b1b", 2), ("b1b", 3)]
    for v in VOICES:
        cs = []
        for lv, b in cells:
            x = S["by_cell"][f"{lv}_b{b}"].get(v)
            cs.append(f"{x['mid_long1000']['mean']:.2f} ({x['n']})" if x else "-")
        L.append(f"| {v} | " + " | ".join(cs) + " |")
    L += ["", "Algieba未満の本文×レベルcell数(主要指標の平均が厳密に小さいcell/6):"]
    alg = {c: S["by_cell"][f"{c[0]}_b{c[1]}"]["Algieba"]["mid_long1000"]["mean"] for c in cells}
    for v in VOICES[1:]:
        k = sum(1 for c in cells if S["by_cell"][f"{c[0]}_b{c[1]}"].get(v) and S["by_cell"][f"{c[0]}_b{c[1]}"][v]["mid_long1000"]["mean"] < alg[c])
        eq = sum(1 for c in cells if S["by_cell"][f"{c[0]}_b{c[1]}"].get(v) and S["by_cell"][f"{c[0]}_b{c[1]}"][v]["mid_long1000"]["mean"] == alg[c])
        L.append(f"- {v}: {k}/6 cell でAlgieba未満(同値 {eq})")
    # (2) take level
    byv = collections.defaultdict(list)
    for t in takes:
        byv[t["voice"]].append(t)
    att = collections.Counter()
    for r in rows:
        if r["origin"] == "fresh":
            att[(r["voice"], r["level"], r["body"], r["take"])] += 1
    L += ["", "## 2. fresh takeの最終statusと1 takeあたりの生成回数(retry/費用の代理)", "",
          "| Voice | fresh take数 | 最終OK率 | 平均attempt数/take(main route) | 備考 |", "|---|---|---|---|---|"]
    ex = {}
    for v in VOICES:
        ts = byv.get(v, [])
        if not ts:
            L.append(f"| {v} | 0 | (今回新規なし。前回Trial再利用のみ) | - | |")
            continue
        ok = sum(1 for t in ts if t.get("status") == "OK")
        na = [n for k, n in att.items() if k[0] == v]
        L.append(f"| {v} | {len(ts)} | {ok}/{len(ts)} = {100 * ok / len(ts):.0f}% | {sum(na) / len(na):.2f} | |")
        ex[v] = {"fresh_takes": len(ts), "ok": ok, "mean_attempts_per_take": sum(na) / len(na)}
    # (3) 最終音声
    fin = collections.defaultdict(list)
    for t in takes:
        if t.get("wav") and os.path.exists(t["wav"]) and t.get("status") == "OK":
            m = lib.measure_wav(t["wav"], texts[(t["level"], t["body"])])
            m7.add_metrics(m)
            fin[t["voice"]].append((t, m))
    L += ["", "## 3. 最終音声(OK takeの採用wav。Stdは6%減速後=ユーザーが聴く音)に残る文中≥1秒停止", "",
          "| Voice | OK take数 | 文中≥1秒が1回以上 | 率 | 全≥1秒が1回以上 | 率 | 最長停止(最悪) |", "|---|---|---|---|---|---|---|"]
    for v in VOICES:
        f = fin.get(v)
        if not f:
            L.append(f"| {v} | 0 | - | - | - | - | - |")
            continue
        n = len(f)
        b1 = sum(1 for _, m in f if m["mid_long1000"] >= 1)
        b2 = sum(1 for _, m in f if m["long1000_n"] >= 1)
        L.append(f"| {v} | {n} | {b1} | {100 * b1 / n:.0f}% | {b2} | {100 * b2 / n:.0f}% | {max(m['max_ms'] for _, m in f) / 1000:.2f}s |")
        ex.setdefault(v, {})["final_mid_bad"] = b1 / n
        ex[v]["final_any_bad"] = b2 / n
        ex[v]["final_n"] = n
    L += ["", "注: 最終音声は1 take=1本。Stdは減速で停止が1.06倍になるため閾値付近(約943ms以上)の停止が1.0秒に届く。Algieba/Schedarの前回Trial takeは本表に含まない(fresh takeのみ)。", ""]
    # (4) 位置非依存
    L += ["## 4. 位置非依存の補助指標(全≥1.0秒 回/sample [95%区間])での順位", ""]
    rk = sorted(VOICES, key=lambda v: S["pooled"][v]["long1000_n"]["mean"])
    for v in rk:
        x = S["pooled"][v]["long1000_n"]
        L.append(f"- {v}: {x['mean']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(ex, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
