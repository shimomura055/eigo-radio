# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01: measure/samples_measured.json から cell別/take別表と判定(DESIGN_01 §3の規則そのまま)を作る。API 0。
使い方: py -X utf8 yvp_summarize_01.py  (先に yvp_measure_all_01.py)。出力: measure/summary.json, RESULT_MATRIX_01.md"""
import glob, hashlib, json, os, statistics as stt, sys
from collections import defaultdict

T = "docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yvp_measure_lib_01 as lib

VN = {1: "V1 Algieba", 2: "V2 Zephyr", 3: "V3 Schedar"}
LV = {"a2": "Standard(a2)", "b1b": "Advanced(b1b)"}
TRIAL = "er121_output/family_y_voice_pause_trial_01"


def mean(x):
    return sum(x) / len(x) if x else float("nan")


def sd(x):
    return stt.pstdev(x) if len(x) > 1 else 0.0


def cells_of(rows, lv, first_only=False):
    c = defaultdict(list)
    for r in rows:
        if r["level"] == lv and r["kind"] == "main" and (not first_only or r["attempt"] == 1):
            c[(r["body"], r["voice"])].append(r)
    return c


def cell_stats(rs):
    if not rs:
        return None
    occ = [r["occ_pct"] for r in rs]
    return {"n": len(rs), "n_fresh": sum(1 for r in rs if r["src"] == "trial"), "n_reuse": sum(1 for r in rs if r["src"] != "trial"),
            "occ_mean": round(mean(occ), 2), "occ_max": max(occ), "occ_min": min(occ), "occ_sd": round(sd(occ), 2),
            "ge1000_mean": round(mean([r["ge1000"] for r in rs]), 2), "ge1000_max": max(r["ge1000"] for r in rs),
            "r1_mean": round(mean([r["ge1000_per100w"] for r in rs]), 3), "max_ms_worst": max(r["max_ms"] for r in rs),
            "max_ms_mean": round(mean([r["max_ms"] for r in rs])), "share_with_long": round(sum(1 for r in rs if r["ge1000"] >= 1) / len(rs), 2),
            "dur_mean": round(mean([r["dur_s"] for r in rs]), 1), "speech_wpm_mean": round(mean([r["speech_wpm"] for r in rs]), 1),
            "gross_wpm_mean": round(mean([r["gross_wpm"] for r in rs]), 1), "mid500_mean": round(mean([r["mid_ge500"] for r in rs]), 2),
            "asr_verified_share": round(mean([1.0 if r.get("asr_verified") else 0.0 for r in rs]), 2),
            "rep_flag_share": round(mean([1.0 if r.get("rep_flag") else 0.0 for r in rs]), 2)}


def judge(cs):
    """cs: {(b,v): stats}. DESIGN_01 §3 を実装。"""
    out = {}
    need = [(b, v) for b in (1, 2, 3) for v in (1, 2, 3)]
    thin = [k for k in need if k not in cs or cs[k]["n"] < 3]
    occ = lambda b, v: cs[(b, v)]["occ_mean"]
    r1 = lambda b, v: cs[(b, v)]["r1_mean"]
    if any(k not in cs for k in need):
        return {"error": "cell欠落", "thin": thin}
    Occ_v = {v: mean([occ(b, v) for b in (1, 2, 3)]) for v in (1, 2, 3)}
    R1_v = {v: mean([r1(b, v) for b in (1, 2, 3)]) for v in (1, 2, 3)}
    Occ_b = {b: mean([occ(b, v) for v in (1, 2, 3)]) for b in (1, 2, 3)}
    # H1
    a_ok = [b for b in (1, 2, 3) if occ(b, 1) > mean([occ(b, 2), occ(b, 3)])]
    d_occ = Occ_v[1] - max(Occ_v[2], Occ_v[3])
    ratio_ok = R1_v[1] >= 1.5 * max(R1_v[2], R1_v[3]) and (R1_v[1] - max(R1_v[2], R1_v[3])) >= 0.3
    if len(a_ok) == 3 and d_occ >= 2.0 and ratio_ok:
        h1 = "支持"
    elif d_occ < 1.0 or len(a_ok) <= 1:
        h1 = "否定"
    else:
        h1 = "未確定"
    out["H1"] = {"raw": h1, "bodies_V1_above_others": a_ok, "Occ_v": {k: round(x, 2) for k, x in Occ_v.items()}, "R1_v": {k: round(x, 3) for k, x in R1_v.items()},
                 "Occ1_minus_maxOthers": round(d_occ, 2), "r1_ratio_ok": ratio_ok}
    # H2
    topv = {}
    for v in (1, 2, 3):
        topv[v] = max((1, 2, 3), key=lambda b: occ(b, v))
    h2 = "未確定"
    best = None
    for B in (1, 2, 3):
        nv = sum(1 for v in (1, 2, 3) if topv[v] == B)
        gap = Occ_b[B] - max(Occ_b[x] for x in (1, 2, 3) if x != B)
        if nv >= 2 and gap >= 2.0:
            best = B
    rng = max(Occ_b.values()) - min(Occ_b.values())
    if best:
        h2 = "支持"
    elif max(sum(1 for v in (1, 2, 3) if topv[v] == B) for B in (1, 2, 3)) < 2 or rng < 2.0:
        h2 = "否定"
    out["H2"] = {"raw": h2, "top_body_per_voice": topv, "Occ_b": {k: round(x, 2) for k, x in Occ_b.items()}, "range_pt": round(rng, 2), "supported_body": best}
    # H3
    allr = cs
    c11 = cs[(1, 1)]
    ss_tot = 0.0
    ss_within = 0.0
    return out, thin, Occ_v, Occ_b


def judge_full(rows, lv):
    cs_rows = cells_of(rows, lv)
    cs = {k: cell_stats(v) for k, v in cs_rows.items()}
    res = judge(cs)
    if isinstance(res, dict) and "error" in res:
        return {"error": res["error"], "thin": [list(x) for x in res["thin"]], "cells": {f"b{b}v{v}": x for (b, v), x in cs.items()}}
    out, thin, Occ_v, Occ_b = res
    # H3
    allocc = [r["occ_pct"] for k in cs_rows for r in cs_rows[k]]
    gm = mean(allocc)
    ss_tot = sum((x - gm) ** 2 for x in allocc)
    ss_w = sum(sum((r["occ_pct"] - mean([q["occ_pct"] for q in rs])) ** 2 for r in rs) for rs in cs_rows.values())
    share_w = ss_w / ss_tot if ss_tot else float("nan")
    c11 = cs[(1, 1)]
    rng11 = c11["occ_max"] - c11["occ_min"]
    if c11["n"] >= 6 and rng11 >= 5.0 and share_w >= 0.5:
        h3 = "支持"
    elif c11["n"] >= 6 and (rng11 < 3.0 or share_w < 0.25):
        h3 = "否定"
    else:
        h3 = "未確定"
    out["H3"] = {"raw": h3, "V1b1_n": c11["n"], "V1b1_occ_range": round(rng11, 2), "within_cell_SS_share": round(share_w, 3)}
    # H5
    D = {b: cs[(b, 1)]["occ_mean"] - mean([cs[(b, 2)]["occ_mean"], cs[(b, 3)]["occ_mean"]]) for b in (1, 2, 3)}
    spread = max(D.values()) - min(D.values())
    h5 = "支持" if spread >= 3.0 else ("否定" if spread < 1.5 else "未確定")
    out["H5"] = {"raw": h5, "D_b": {k: round(x, 2) for k, x in D.items()}, "spread_pt": round(spread, 2)}
    # n要件(H3以外=全9cell n>=3)
    for h in ("H1", "H2", "H5"):
        if thin and out[h]["raw"] in ("支持", "否定"):
            out[h]["verdict"] = "未確定(n不足: " + ",".join(f"b{b}v{v}" for b, v in thin) + f"。規則上の暫定={out[h]['raw']})"
        else:
            out[h]["verdict"] = out[h]["raw"]
    out["H3"]["verdict"] = out["H3"]["raw"]
    out["thin_cells"] = [f"b{b}v{v}" for b, v in thin]
    out["cells"] = {f"b{b}v{v}": s for (b, v), s in cs.items()}
    return out


def slowdown_pairs():
    """Std: 減速前(*_original.wav)と最終wavの対。"""
    pairs = []
    R = lib.RUN01
    cand = []
    for i in (1, 2, 3):
        cand.append((f"run_01 final V{i}", f"{R}/a2/narration/y_voice_{i}_original.wav", f"{R}/a2/narration/y_voice_{i}.wav", i, "reuse"))
    for k in (2, 3):
        d = f"{R}/a2/hr_adopt_prep/voice1_candidates/take{k}/narration"
        cand.append((f"V1候補take{k}", f"{d}/y_voice_1_original.wav", f"{d}/y_voice_1.wav", 1, "reuse"))
    for d in sorted(glob.glob(f"{TRIAL}/a2/body*_voice*/take*/narration")):
        import re
        m = re.search(r"body(\d)_voice(\d)[\\/]take(\d+)", d)
        b = int(m.group(1))
        cand.append((f"trial b{m.group(1)}v{m.group(2)}t{m.group(3)}", f"{d}/y_voice_{b}_original.wav", f"{d}/y_voice_{b}.wav", int(m.group(2)), "fresh"))
    for name, a, b_, v, src in cand:
        if os.path.exists(a) and os.path.exists(b_):
            bodyn = int(os.path.basename(b_).split("_")[2].split(".")[0])
            t = lib.body_text("a2", bodyn)
            pre, post = lib.measure_wav(a, t), lib.measure_wav(b_, t)
            pairs.append({"name": name, "voice": v, "src": src, "pre_occ": pre["occ_pct"], "post_occ": post["occ_pct"], "pre_ge1000": pre["ge1000"], "post_ge1000": post["ge1000"],
                          "pre_max": pre["max_ms"], "post_max": post["max_ms"], "pre_dur": pre["dur_s"], "post_dur": post["dur_s"], "ratio": round(post["dur_s"] / pre["dur_s"], 4)})
    return pairs


def pos_kind(after):
    c = after[-1] if after else ""
    return "sentence_end" if c in ".?!" else ("comma" if c in ",;:" else "mid_clause")



def perm_test(rows, lv, metric, n_perm=5000, seed=20261026, A=(1,), B=(2, 3)):
    """[事後・探索] 本文を層としてVoiceラベルを置換し、V1とV2+V3の平均差(metric)が偶然で出る確率を片側で見る。標本=main raw sample(同一takeのattemptは完全独立ではない=p値は目安)。"""
    import random
    rnd = random.Random(seed)
    by_b = defaultdict(list)
    for r in rows:
        if r["level"] == lv and r["kind"] == "main" and r["voice"] in A + B:
            by_b[r["body"]].append(r)
    def stat(assign):
        a = [r[metric] for b in by_b for r, v1 in zip(by_b[b], assign[b]) if v1]
        o = [r[metric] for b in by_b for r, v1 in zip(by_b[b], assign[b]) if not v1]
        return mean(a) - mean(o)
    obs_assign = {b: [r["voice"] in A for r in by_b[b]] for b in by_b}
    obs = stat(obs_assign)
    ge = 0
    for _ in range(n_perm):
        asg = {}
        for b in by_b:
            lab = [r["voice"] in A for r in by_b[b]]
            rnd.shuffle(lab)
            asg[b] = lab
        if stat(asg) >= obs:
            ge += 1
    return {"metric": metric, "A": list(A), "B": list(B), "obs_diff_A_minus_B": round(obs, 3), "p_one_sided": round((ge + 1) / (n_perm + 1), 4)}


def qa_table(lv):
    out = []
    for b in (1, 2, 3):
        for v in (1, 2, 3):
            rs = []
            if b == v == 1:
                for k in (1, 2, 3):
                    p = f"{lib.RUN01}/{lv}/hr_adopt_prep/voice1_candidates/take{k}/result.json"
                    if os.path.exists(p):
                        rs.append(json.load(open(p, encoding="utf-8")))
            for p in sorted(glob.glob(f"{TRIAL}/{lv}/body{b}_voice{v}/take*/result.json")):
                rs.append(json.load(open(p, encoding="utf-8")))
            if rs:
                att = []
                for r in rs:
                    w = r.get("wav") or ""
                    d = os.path.join(os.path.dirname(w), "attempts")
                    att.append(len(glob.glob(os.path.join(d, "*.wav"))))
                out.append({"cell": f"b{b}v{v}", "takes": len(rs), "OK": sum(1 for r in rs if r.get("status") == "OK"), "STOPPED_or_other": sum(1 for r in rs if r.get("status") != "OK"),
                            "attempts_per_take_mean": round(mean(att), 2) if att else None})
    return out


def main():
    rows = json.load(open(f"{T}/measure/samples_measured.json", encoding="utf-8"))
    S = {"generated": "yvp_summarize_01", "levels": {}}
    md = ["# RESULT_MATRIX_01 — FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(自動生成。判定規則=DESIGN_01 §3、観測後の変更なし)\n",
          "サンプル=raw attempt wav(1=独立TTS draw)。main=Std custom/Adv wide_margin。fresh=src trial(本Trial新規)/reuse=src run01_prod・v1cand。Std rawは減速前。\n"]
    for lv in ("a2", "b1b"):
        J = judge_full(rows, lv)
        S["levels"][lv] = J
        md.append(f"\n## {LV[lv]}\n")
        if "error" in J:
            md.append(f"cell欠落: {J}\n")
            continue
        md.append("### cell別(本文×Voice)。n(fresh+reuse)・停止占有率occ%(平均[最小-最大])・>=1000ms個数(平均/最大)・最長停止ms(最悪)・>=1s停止を含むsample割合・発話速度\n")
        md.append("| 本文＼Voice | " + " | ".join(VN[v] for v in (1, 2, 3)) + " |\n|---|---|---|---|")
        for b in (1, 2, 3):
            row = []
            for v in (1, 2, 3):
                c = J["cells"][f"b{b}v{v}"]
                row.append(f"n={c['n']}({c['n_fresh']}+{c['n_reuse']}) occ {c['occ_mean']}[{c['occ_min']}-{c['occ_max']}] n1 {c['ge1000_mean']}/{c['ge1000_max']} 最長{c['max_ms_worst']} 長有{int(c['share_with_long']*100)}% wpm{c['speech_wpm_mean']}")
            md.append(f"| 本文{b} | " + " | ".join(row) + " |")
        md.append("\n### 判定(DESIGN_01 §3)\n")
        for h, nm in (("H1", "Voice固有(Algieba)"), ("H2", "本文固有"), ("H3", "生成ばらつき"), ("H5", "Voice×本文 相互作用")):
            j = J[h]
            md.append(f"- **{h} {nm}: {j['verdict']}** — " + ", ".join(f"{k}={v}" for k, v in j.items() if k not in ("verdict", "raw")))
        md.append(f"- n<3のcell(Phase 2対象): {J['thin_cells']}\n")
        # 感度: attempt1のみ
        c1 = {k: cell_stats(v) for k, v in cells_of(rows, lv, first_only=True).items()}
        md.append("\n感度(各takeの最初のattemptのみ。1 take=1 sample): " + "; ".join(f"b{k[0]}v{k[1]} n={s['n']} occ {s['occ_mean']} n1 {s['ge1000_mean']}" for k, s in sorted(c1.items())) + "\n")
        S["levels"][lv]["first_attempt_only"] = {f"b{k[0]}v{k[1]}": s for k, s in c1.items()}
        # Voice別プール
        pv = defaultdict(list)
        for r in rows:
            if r["level"] == lv and r["kind"] == "main":
                pv[r["voice"]].append(r)
        md.append("\n### Voice別プール(全main sample。本文は混在=本文の重み付き。参考)\n\n| Voice | n | occ平均 | occ最大 | n1平均 | n1最大 | 最長停止(最悪) | 長有割合 |\n|---|---|---|---|---|---|---|---|")
        for v in (1, 2, 3):
            c = cell_stats(pv[v])
            md.append(f"| {VN[v]} | {c['n']} | {c['occ_mean']} | {c['occ_max']} | {c['ge1000_mean']} | {c['ge1000_max']} | {c['max_ms_worst']} | {int(c['share_with_long']*100)}% |")
        for met in ("ge1000_per100w", "occ_pct", "max_ms"):
            pt = perm_test(rows, lv, met)
            S["levels"][lv].setdefault("posthoc_perm", {})[met] = pt
        S["levels"][lv]["posthoc_pairs"] = {}
        for A, B in (((1,), (2,)), ((1,), (3,)), ((3,), (2,))):
            S["levels"][lv]["posthoc_pairs"][f"V{A[0]}-V{B[0]}"] = perm_test(rows, lv, "ge1000_per100w", A=A, B=B)
        md.append("\n[事後・探索(事前登録の判定規則には含めない)] V1 vs V2+V3(本文層別の置換検定、標本=main raw attempt、p値は目安): " + "; ".join(f"{m}: 差={x['obs_diff_A_minus_B']} p={x['p_one_sided']}" for m, x in S["levels"][lv]["posthoc_perm"].items()))
        md.append("[事後・探索] Voice対ごとの >=1s停止率(100語あたり)平均差と置換検定p(片側、本文層別): " + "; ".join(f"{k}: 差={x['obs_diff_A_minus_B']} p={x['p_one_sided']}" for k, x in S["levels"][lv]["posthoc_pairs"].items()))
        qa = qa_table(lv)
        S["levels"][lv]["qa"] = qa
        md.append("\n### ASR/QA(正式経路のtake単位。OK=ASR判定PASSで完走 / それ以外=STOPPED[人間確認待ち相当])\n\n| cell | take数 | OK | STOPPED等 | attempt/take平均 |\n|---|---|---|---|---|")
        for q in qa:
            md.append(f"| {q['cell']} | {q['takes']} | {q['OK']} | {q['STOPPED_or_other']} | {q['attempts_per_take_mean']} |")
        # 停止位置
        md.append("\n### >=1000ms停止の位置(句読点との関係。位置は推定±2〜3語)\n\n| Voice | >=1s停止数 | 文末直後 | カンマ直後 | 文中(句読点なし) | 平均ms |\n|---|---|---|---|---|---|")
        recur = defaultdict(lambda: defaultdict(int))
        for v in (1, 2, 3):
            ps = [(p, r) for r in rows if r["level"] == lv and r["kind"] == "main" and r["voice"] == v for p in r["pause_list"] if p["ms"] >= 1000]
            kinds = [pos_kind(p["after"]) for p, r in ps]
            md.append(f"| {VN[v]} | {len(ps)} | {kinds.count('sentence_end')} | {kinds.count('comma')} | {kinds.count('mid_clause')} | {round(mean([p['ms'] for p, r in ps])) if ps else '-'} |")
        for r in rows:
            if r["level"] == lv and r["kind"] == "main":
                for p in r["pause_list"]:
                    if p["ms"] >= 1000:
                        recur[(r["body"], p["after"], p["before"])][r["voice"]] += 1
        md.append("\n本文別・同一位置(after|before)の>=1s停止: 該当sample数/そのVoice×本文のsample数(Voice別)。**複数Voiceで同位置が出る=本文位置依存の示唆**(合計>=2のみ表示):\n")
        nsamp = defaultdict(int)
        for r in rows:
            if r["level"] == lv and r["kind"] == "main":
                nsamp[(r["body"], r["voice"])] += 1
        hot = defaultdict(lambda: defaultdict(set))
        for i, r in enumerate(rows):
            if r["level"] == lv and r["kind"] == "main":
                for p in r["pause_list"]:
                    if p["ms"] >= 1000:
                        hot[(r["body"], p["after"], p["before"])][r["voice"]].add(i)
        S["levels"][lv]["hotspots"] = []
        for key, vv in sorted(hot.items(), key=lambda kv: -sum(len(x) for x in kv[1].values())):
            if sum(len(x) for x in vv.values()) < 2:
                continue
            cells = {v: f"{len(vv.get(v, ()))}/{nsamp[(key[0], v)]}" for v in (1, 2, 3)}
            S["levels"][lv]["hotspots"].append({"body": key[0], "pos": f"{key[1]} | {key[2]}", **{f"V{v}": c for v, c in cells.items()}})
            md.append(f"- 本文{key[0]} `{key[1]} | {key[2]}`: " + ", ".join(f"V{v} {c}" for v, c in cells.items()))
    pairs = slowdown_pairs()
    S["slowdown_pairs"] = pairs
    md.append("\n## H4a 減速前後(Std, 6%減速。同一音声の減速前=*_original.wav と最終wav)\n\n| 対 | 出所 | 尺 前→後 (倍率) | occ 前→後 | >=1000ms個数 前→後 | 最長ms 前→後 |\n|---|---|---|---|---|---|")
    for p in pairs:
        md.append(f"| {p['name']} | {p['src']} | {p['pre_dur']}→{p['post_dur']} ({p['ratio']}) | {p['pre_occ']}→{p['post_occ']} | {p['pre_ge1000']}→{p['post_ge1000']} | {p['pre_max']}→{p['post_max']} |")
    if pairs:
        docc = mean([p["post_occ"] - p["pre_occ"] for p in pairs])
        dn = mean([p["post_ge1000"] - p["pre_ge1000"] for p in pairs])
        h4a = "支持(減速が停止量に影響)" if (docc >= 1.0 or dn >= 1.0) else ("否定(影響なし)" if (abs(docc) < 0.5 and dn < 0.5) else "未確定")
        S["H4a"] = {"verdict": h4a, "mean_delta_occ": round(docc, 2), "mean_delta_ge1000": round(dn, 2), "n_pairs": len(pairs)}
        md.append(f"\n- **H4a: {h4a}** 対平均 Δocc={round(docc,2)}pt, Δ(>=1000ms個数)={round(dn,2)} (n={len(pairs)}対。時間伸長で停止長が機械的に約1.06倍になる分を含む)")
    # H4b
    def pooled(lv, vs):
        x = [r["occ_pct"] for r in rows if r["level"] == lv and r["kind"] == "main" and r["voice"] in vs]
        return mean(x), len(x)
    d1 = pooled("a2", (1,))[0] - pooled("b1b", (1,))[0]
    d23 = pooled("a2", (2, 3))[0] - pooled("b1b", (2, 3))[0]
    h4b = "支持" if (abs(d1) >= 2 and abs(d23) >= 2 and d1 * d23 > 0) else ("否定" if (abs(d1) < 1 and abs(d23) < 1) else "未確定")
    S["H4b"] = {"verdict": h4b, "std_minus_adv_occ_V1": round(d1, 2), "std_minus_adv_occ_V2V3": round(d23, 2)}
    md.append(f"\n## H4b レベル差(Std−Adv, occ平均差)\n- **H4b: {h4b}** V1: {round(d1,2)}pt / V2+V3: {round(d23,2)}pt(Std/Advは別文・別Style指示で交絡。単独Style効果とは言えない)")
    # fallback付表
    fb = [r for r in rows if r["kind"] == "fallback"]
    md.append(f"\n## 付表: minimal_fallback attempt(別条件のため本体から除外) n={len(fb)}\n" + "; ".join(f"{r['level']} b{r['body']}v{r['voice']} {r['src']} a{r['attempt']} occ {r['occ_pct']} n1 {r['ge1000']} max {r['max_ms']}" for r in fb))
    json.dump(S, open(f"{T}/measure/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(f"{T}/RESULT_MATRIX_01.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("ok", f"{T}/RESULT_MATRIX_01.md")


if __name__ == "__main__":
    main()
