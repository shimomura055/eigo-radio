# ============================================================
# er091_asr_three_way_trial_01_report.py (API 0) 集計: Phase 1/2/3・安定性・速度・原価 -> results/tables.md, results/summary.json
# ============================================================
from __future__ import annotations
import collections
import json
import math
import os
import statistics
import sys

sys.path.insert(0, ".")
import er091_asr_three_way_trial_01_analyze as an  # noqa: E402

OUT = an.OUT
RES = an.RES
METHODS = ["openai", "azure", "whisper", "whisper_medium"]
ML = {"openai": "OpenAI gpt-4o-mini-transcribe", "azure": "Azure Speech en-US", "whisper": "faster-whisper small", "whisper_medium": "faster-whisper medium(追加)"}


def tier(m):
    s = m["label_strength"]
    if m["label"] == "normal":
        if s.startswith("human"):
            return "N_human"      # 記事試聴PASS / HR承認
        return "N_constructed"
    if s.startswith("human"):
        return "P_human"
    if m["label_class"].startswith("problem_constructed_splice"):
        return "P_splice"
    return "P_constructed"


def pct(a, b):
    return f"{a}/{b} ({(100.0 * a / b):.0f}%)" if b else "n/a"


def main():
    man = {r["id"]: r for r in an.manifest() if not r["duplicate_of"]}
    for m in man.values():
        m["tier"] = tier(m)
    P12 = json.load(open(os.path.join(RES, "phase12_item_results.json"), encoding="utf-8"))
    P3 = json.load(open(os.path.join(RES, "phase3_item_results.json"), encoding="utf-8"))
    raw = an.raw()
    L = []
    S = {}
    # ---------------- 台帳構成
    L.append("## A. 評価データ構成(重複除外後)\n")
    cnt = collections.Counter((m["tier"], m["kind"]) for m in man.values())
    L.append("| tier | KP | 本文 | 計 | 音声秒(合計) |\n|---|---|---|---|---|")
    for t in ("N_human", "N_constructed", "P_human", "P_constructed", "P_splice"):
        ids = [m for m in man.values() if m["tier"] == t]
        L.append(f"| {t} | {cnt[(t,'kp')]} | {cnt[(t,'body')]} | {len(ids)} | {sum(m['duration_s'] for m in ids):.0f}s |")
    S["dataset_counts"] = {f"{k[0]}|{k[1]}": v for k, v in cnt.items()}
    fam = collections.Counter((m["label"], m["family"], m["level"]) for m in man.values())
    L.append("\nlabel x family x level: " + "; ".join(f"{k[0]}/{k[1]}/{k[2]}={v}" for k, v in sorted(fam.items())))
    L.append(f"\nPhrase List(Ledger hint)有の音声: {sum(1 for m in man.values() if m['ledger_phrases'])}件 (KPは0件=全KPがPL空)。")

    # ---------------- 構成ラベルの監査(TTS/splice)
    L.append("\n## B. 構成ラベル音声の監査(3方式の転写 vs 台本/読ませた文面)\n")
    L.append("| id | 誤り種別 | 台本(canonical) | 読ませた文面 | OpenAI(prod) | Azure(prod) | Whisper | 全方式が台本一致=ラベル疑義 |\n|---|---|---|---|---|---|---|---|")
    eff = an.effective(raw)
    doubt = []
    for m in man.values():
        if m["tier"] not in ("P_constructed", "P_splice") or m["id"].startswith("plw_"):
            continue
        tx = {k: " ".join(((eff.get((m["id"], k)) or {}).get("prod") or {}).get("text", "").split()) for k in METHODS}
        allcanon = all(an.norm_tokens(tx[k]) == an.norm_tokens(m["canonical"]) for k in METHODS)
        if allcanon:
            doubt.append(m["id"])
        L.append(f"| {m['id']} | {m.get('problem_type')} | {m['canonical'][:40]} | {(m.get('spoken_text_requested') or '(splice)')[:40]} | {tx['openai'][:45]} | {tx['azure'][:45]} | {tx['whisper'][:45]} | {'疑義' if allcanon else ''} |")
    S["label_doubt_ids"] = doubt

    # ---------------- Phase1/2 単体
    def p12_table(cond):
        out = []
        rows = [r for r in P12 if r["cond"] == cond]
        for kind in ("kp", "body"):
            out.append(f"\n### {kind.upper()} / 条件={cond}\n")
            out.append("| tier | n | " + " | ".join(f"{ML[m]}: PASS/NG(NG=検出)" for m in METHODS) + " |\n|---|---|---|---|---|")
            for t in ("N_human", "N_constructed", "P_human", "P_constructed", "P_splice"):
                ids = [m["id"] for m in man.values() if m["tier"] == t and m["kind"] == kind]
                if not ids:
                    continue
                cells = []
                for meth in METHODS:
                    sel = [r for r in rows if r["method"] == meth and r["id"] in ids]
                    p = sum(1 for r in sel if r["verdict_pass"])
                    cells.append(f"PASS {p} / NG {len(sel)-p}")
                out.append(f"| {t} | {len(ids)} | " + " | ".join(cells) + " |")
        return out

    L.append("\n## C. Phase 1(中立条件: OpenAI prompt無し・Azure Phrase List無し)単体verdict\n(verdict=Production分類器`val.classify_asr_match`+`_step_alternate_pass`を転写に適用。NG=その方式単独ではPASSさせない)")
    L += p12_table("neutral")
    L.append("\n## D. Phase 2(Production運用条件: OpenAI KP=Production prompt・Azure=Ledger hint有ならPhrase List重み2.0)単体verdict")
    L += p12_table("prod")

    # WER/CER
    L.append("\n### 文字起こし正確性(正常音声のみ、canonicalとの正規化WER/CER、Production条件)\n")
    L.append("| 種別 | " + " | ".join(f"{m} WER平均/CER平均/完全一致" for m in METHODS) + " |\n|---|---|---|---|")
    for kind in ("kp", "body"):
        for lab in ("N_human",):
            ids = {m["id"] for m in man.values() if m["tier"] == lab and m["kind"] == kind}
            cells = []
            for meth in METHODS:
                sel = [r for r in P12 if r["cond"] == "prod" and r["method"] == meth and r["id"] in ids and r["wer"] is not None]
                cells.append(f"{statistics.mean(r['wer'] for r in sel):.3f} / {statistics.mean(r['cer'] for r in sel):.3f} / {sum(1 for r in sel if r['exact_norm_match'])}/{len(sel)}")
            L.append(f"| {kind} N_human(n={len(ids)}) | " + " | ".join(cells) + " |")

    # 種別別(タグ)
    L.append("\n### 種別別(Production条件, 正常=N_human+N_constructed のPASS率 / 問題=NG検出率、tag別)\n")
    tags = ["number", "negation", "proper_noun", "hyphen_or_contraction", "kp_single_word", "kp_short_2w", "kp_phrase_3w+", "body_short", "body_mid", "body_long", "hr_approved_hard"]
    L.append("| tag | 正常n | " + " | ".join(f"{m} 正常PASS" for m in METHODS) + " | 問題n | " + " | ".join(f"{m} 問題検出" for m in METHODS) + " |\n|---|---|---|---|---|---|---|---|---|")
    for tg in tags:
        nid = [m["id"] for m in man.values() if m["label"] == "normal" and tg in m["tags"]]
        pid = [m["id"] for m in man.values() if m["label"] == "problem" and tg in m["tags"]]
        if not nid and not pid:
            continue
        cn, cp = [], []
        for meth in METHODS:
            sn = [r for r in P12 if r["cond"] == "prod" and r["method"] == meth and r["id"] in nid]
            cn.append(pct(sum(1 for r in sn if r["verdict_pass"]), len(sn)))
            sp = [r for r in P12 if r["cond"] == "prod" and r["method"] == meth and r["id"] in pid]
            cp.append(pct(sum(1 for r in sp if not r["verdict_pass"]), len(sp)))
        L.append(f"| {tg} | {len(nid)} | " + " | ".join(cn) + f" | {len(pid)} | " + " | ".join(cp) + " |")
    # family/level
    L.append("\n### Family/Level別(Production条件、正常PASS率 / 問題NG検出率)\n")
    L.append("| group | 正常n | " + " | ".join(f"{m}" for m in METHODS) + " | 問題n | " + " | ".join(f"{m}" for m in METHODS) + " |\n|---|---|---|---|---|---|---|---|---|")
    for fk, fn in (("family", ("X", "Z")), ("level", ("Standard", "Advanced"))):
        for v in fn:
            nid = [m["id"] for m in man.values() if m["label"] == "normal" and m[fk] == v]
            pid = [m["id"] for m in man.values() if m["label"] == "problem" and m[fk] == v]
            cn = []
            cp = []
            for meth in METHODS:
                sn = [r for r in P12 if r["cond"] == "prod" and r["method"] == meth and r["id"] in nid]
                cn.append(pct(sum(1 for r in sn if r["verdict_pass"]), len(sn)))
                sp = [r for r in P12 if r["cond"] == "prod" and r["method"] == meth and r["id"] in pid]
                cp.append(pct(sum(1 for r in sp if not r["verdict_pass"]), len(sp)))
            L.append(f"| {fk}={v} | {len(nid)} | " + " | ".join(cn) + f" | {len(pid)} | " + " | ".join(cp) + " |")

    # Phrase List 有無 (Azure + Whisper/OpenAI 参考)
    L.append("\n### Phrase List有無(Azure、Ledger hint有の音声のみ。N_human+N_constructed正常の転写PASS)\n")
    pl_ids = [m["id"] for m in man.values() if m["ledger_phrases"]]
    L.append("| 条件 | 正常PASS | 問題NG検出 |\n|---|---|---|")
    for cond in ("neutral", "prod"):
        sn = [r for r in P12 if r["method"] == "azure" and r["cond"] == cond and r["id"] in pl_ids and r["label"] == "normal"]
        sp = [r for r in P12 if r["method"] == "azure" and r["cond"] == cond and r["id"] in pl_ids and r["label"] == "problem"]
        L.append(f"| Azure {'PLなし(neutral)' if cond=='neutral' else 'PL重み2.0(prod)'} | {pct(sum(1 for r in sn if r['verdict_pass']), len(sn))} | {pct(sum(1 for r in sp if not r['verdict_pass']), len(sp))} |")
    # OpenAI KP prompt effect
    L.append("\n### OpenAI KP: Production prompt有無の差(KPのみ、全KP)\n")
    for cond in ("neutral", "prod"):
        sn = [r for r in P12 if r["method"] == "openai" and r["cond"] == cond and r["kind"] == "kp" and r["label"] == "normal"]
        sp = [r for r in P12 if r["method"] == "openai" and r["cond"] == cond and r["kind"] == "kp" and r["label"] == "problem"]
        L.append(f"- {cond}: 正常PASS {pct(sum(1 for r in sn if r['verdict_pass']), len(sn))} / 問題NG検出 {pct(sum(1 for r in sp if not r['verdict_pass']), len(sp))}")

    # ---------------- 安定性
    L.append("\n## E. 安定性(同一音声の反復: 短尺KP 20本 x 3回、Production条件。独立音声の検証ではない)\n")
    sids = json.load(open(os.path.join(RES, "stability_ids.json")))
    L.append("| 方式 | 対象音声数 | 転写が3回とも同一 | 転写が変動した音声 | verdict(PASS/NG)が反転した音声 |\n|---|---|---|---|---|")
    stab_detail = {}
    for meth in METHODS:
        same = var = flip = 0
        det = []
        for sid in sids:
            e = eff.get((sid, meth))
            if not e or len(e["reps"]) < 3:
                continue
            txts = [" ".join((e["reps"][k].get("text") or "").split()) for k in (1, 2, 3)]
            vs = [an.verdict(man[sid]["canonical"], t)[0] for t in txts]
            if len(set(txts)) == 1:
                same += 1
            else:
                var += 1
                det.append((sid, txts, vs))
            if len(set(vs)) > 1:
                flip += 1
        stab_detail[meth] = det
        L.append(f"| {ML[meth]} | {same+var} | {same} | {var} | {flip} |")
    L.append("\n変動実例:")
    for meth in METHODS:
        for sid, txts, vs in stab_detail[meth][:6]:
            L.append(f"- {meth} {sid} (canonical='{man[sid]['canonical']}'): {txts} verdict={vs}")
    S["stability"] = {m: {"variable": len(stab_detail[m])} for m in METHODS}

    # ---------------- 速度
    L.append("\n## F. 処理速度(音声1本あたり、実測)\n")
    L.append("| 方式 | KP平均wall(s) | 本文平均wall(s) | 本文 wall/音声秒 | 備考 |\n|---|---|---|---|---|")
    S["speed"] = {}
    for meth in METHODS:
        rr = [r for r in raw if r["method"] == meth and r["rep"] == 1 and r["id"] in man and r.get("wall_s") is not None]
        if not meth.startswith("whisper"):
            rr = [r for r in rr if r["cond"] in ("neutral",)]
        kpw = [r["wall_s"] for r in rr if man[r["id"]]["kind"] == "kp"]
        bw = [(r["wall_s"], r["audio_s"]) for r in rr if man[r["id"]]["kind"] == "body"]
        if meth.startswith("whisper"):
            cpu_note = f"CPU時間/音声秒(本文)={sum(r['cpu_s'] for r in rr if man[r['id']]['kind']=='body')/max(1e-9,sum(r['audio_s'] for r in rr if man[r['id']]['kind']=='body')):.2f}"
        else:
            cpu_note = "API(6並列ThreadPool実行時の個別wall)"
        S["speed"][meth] = {"kp_mean_s": statistics.mean(kpw), "body_mean_s": statistics.mean(b[0] for b in bw), "body_s_per_audio_s": sum(b[0] for b in bw) / sum(b[1] for b in bw)}
        L.append(f"| {ML[meth]} | {statistics.mean(kpw):.2f} | {statistics.mean(b[0] for b in bw):.2f} | {sum(b[0] for b in bw)/sum(b[1] for b in bw):.3f} | {cpu_note} |")
    wp = os.path.join(RES, "whisper_parallel.jsonl")
    if os.path.exists(wp):
        L.append("\nWhisper同時実行(別process、同一24音声[各8秒以下]、モデルロード込み、16論理CPU):")
        for l in open(wp, encoding="utf-8"):
            x = json.loads(l)
            L.append(f"- {x['n_processes']}process: 全体wall {x['parallel_total_wall_incl_model_load_s']}s vs 直列合計{x['serial_sum_wall_s(first pass, same items)']}s(モデルロード別)、1件平均wall {x['per_item_mean_wall_s']}s(直列1.82s)、process別CPU時間 {x['per_process_total_cpu_s']}")

    # ---------------- Phase 3
    L.append("\n## G. Phase 3 構成別の最終判定(Production判定関数をそのまま呼ぶ。入替構成は現行ルール流用の参考値)\n")
    # 派生構成: KPだけ厳格化(本文は現行のまま) = 追加原価を最小化した案
    for base_c, new_c in (("C1d", "C1dK"), ("C5", "C5K")):
        for r in list(P3):
            if r["config"] == (base_c if r["kind"] == "kp" else "C1"):
                rr_ = dict(r)
                rr_["config"] = new_c
                P3.append(rr_)
    cfgs = ["C1", "C1d", "C1dK", "C2", "C3", "C4", "C5", "C5K", "C3m", "C4m", "C5m"]
    desc = {"C3m": "Whisper medium→OpenAI", "C4m": "Whisper medium→Azure", "C5m": "現行+Whisper medium不一致時Secondary必須", "C1dK": "KPのみ両方PASS必須(本文は現行)", "C5K": "KPのみWhisper不一致時Secondary必須(本文は現行)", "C1": "現行 OpenAI→Azure", "C1d": "現行+両方PASS必須", "C2": "Azure→OpenAI", "C3": "Whisper→OpenAI", "C4": "Whisper→Azure", "C5": "現行+Whisper不一致時のみSecondary必須"}
    tmap = {m["id"]: m["tier"] for m in man.values()}
    S["phase3"] = {}
    L.append("### G-1 混同行列(正常/問題 x PASS/NG)、tier別\n")
    L.append("| 構成 | N_human: 正PASS/過剰NG | N_constr: 正PASS/過剰NG | P_human(take part): 誤PASS/検出 | P_constructed(TTS+plw): 誤PASS/検出 | P_splice(参考): 誤PASS/検出 | 正常全体の過剰NG率 | 問題全体の誤PASS率 | Secondary(Azure/OpenAI)呼出率 |\n|---|---|---|---|---|---|---|---|---|")
    for c in cfgs:
        rows = [r for r in P3 if r["config"] == c]
        def cell(t, lab):
            sel = [r for r in rows if tmap[r["id"]] == t]
            if lab == "normal":
                ok = sum(1 for r in sel if r["verified"])
                return f"{ok}/{len(sel)-ok}", len(sel), len(sel) - ok
            fp = sum(1 for r in sel if r["verified"])
            return f"{fp}/{len(sel)-fp}", len(sel), fp
        nh, nhn, nhng = cell("N_human", "normal")
        nc, ncn, ncng = cell("N_constructed", "normal")
        ph, phn, phfp = cell("P_human", "problem")
        pc, pcn, pcfp = cell("P_constructed", "problem")
        ps, psn, psfp = cell("P_splice", "problem")
        ntot = nhn + ncn
        nng = nhng + ncng
        ptot = phn + pcn
        pfp = phfp + pcfp
        secrate = sum(1 for r in rows if r.get("secondary_called") or r.get("secondary_cached")) / max(1, len(rows))
        S["phase3"][c] = {"normal_n": ntot, "over_ng": nng, "problem_n_excl_splice": ptot, "false_pass_excl_splice": pfp, "splice_n": psn, "splice_false_pass": psfp,
                          "N_human_over_ng": nhng, "N_human_n": nhn, "secondary_call_rate": round(secrate, 3)}
        L.append(f"| {c} {desc[c]} | {nh} (n={nhn}) | {nc} (n={ncn}) | {ph} (n={phn}) | {pc} (n={pcn}) | {ps} (n={psn}) | {pct(nng, ntot)} | {pct(pfp, ptot)} | {secrate:.0%} |")
    L.append("\n(各セルは `PASS数/NG数` [正常]または `誤PASS数/検出数` [問題]。splice(P_splice)は語の欠落が切断断片で残る可能性がありラベル確度が低いため、headlineの誤PASS率には含めない。)")

    L.append("\n### G-2 種別別(Phase 3、C1/C1d/C3/C4 のみ。KP/本文、family、問題種別)\n")
    L.append("| 区分 | " + " | ".join(f"{c} 過剰NG/正常n" for c in cfgs) + " |\n|---|---|---|---|---|---|---|")
    for lab, f in (("KP正常", lambda m: m["label"] == "normal" and m["kind"] == "kp"), ("本文正常", lambda m: m["label"] == "normal" and m["kind"] == "body"),
                   ("本文正常 Family X", lambda m: m["label"] == "normal" and m["kind"] == "body" and m["family"] == "X"),
                   ("本文正常 Family Z", lambda m: m["label"] == "normal" and m["kind"] == "body" and m["family"] == "Z"),
                   ("Std正常", lambda m: m["label"] == "normal" and m["level"] == "Standard"), ("Adv正常", lambda m: m["label"] == "normal" and m["level"] == "Advanced")):
        ids = {m["id"] for m in man.values() if f(m)}
        cells = []
        for c in cfgs:
            sel = [r for r in P3 if r["config"] == c and r["id"] in ids]
            cells.append(f"{sum(1 for r in sel if not r['verified'])}/{len(sel)}")
        L.append(f"| {lab} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("| 問題区分(splice除く) | " + " | ".join(f"{c} 誤PASS/n" for c in cfgs) + " |\n|---|---|---|---|---|---|---|")
    ptypes = collections.OrderedDict()
    for m in man.values():
        if m["label"] == "problem" and m["tier"] in ("P_human", "P_constructed"):
            key = (m.get("problem_type") or "").split("(")[0] or "other"
            ptypes.setdefault(key, set()).add(m["id"])
    for k, ids in ptypes.items():
        cells = []
        for c in cfgs:
            sel = [r for r in P3 if r["config"] == c and r["id"] in ids]
            cells.append(f"{sum(1 for r in sel if r['verified'])}/{len(sel)}")
        L.append(f"| {k} | " + " | ".join(cells) + " |")

    L.append("\n### G-3 誤PASS実例(問題音声がPASSした)と過剰NG実例(正常音声がNGになった)、構成別\n")
    for c in ("C1", "C1d", "C2", "C3", "C4", "C5"):
        rows = [r for r in P3 if r["config"] == c]
        fp = [r for r in rows if r["label"] == "problem" and r["verified"]]
        on = [r for r in rows if r["label"] == "normal" and not r["verified"]]
        L.append(f"\n**{c} {desc[c]}** — 誤PASS {len(fp)}件 / 過剰NG {len(on)}件")
        L.append("誤PASS:")
        for r in fp:
            L.append(f"- [{tmap[r['id']]}] {r['id']} state={r['state']}/{r['reason_code']} | 台本『{r['canonical'][:50]}』 | Primary『{(r['primary_text'] or '')[:55]}』 | Secondary『{(r['secondary_text'] or '')[:55]}』")
        L.append("過剰NG:")
        for r in on:
            L.append(f"- [{tmap[r['id']]}] {r['id']} state={r['state']}/{r['reason_code']} | 台本『{r['canonical'][:50]}』 | Primary『{(r['primary_text'] or '')[:55]}』 | Secondary『{(r['secondary_text'] or '')[:55]}』")
    # ---------------- G-4 kind別・HR難例除外・Wilson区間
    def wilson(k, n, z=1.96):
        if n == 0:
            return (0, 0)
        ph = k / n
        d = 1 + z * z / n
        c = (ph + z * z / (2 * n)) / d
        h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
        return (max(0, c - h), min(1, c + h))

    def fmt(k, n):
        lo, hi = wilson(k, n)
        return f"{k}/{n} [{lo*100:.0f}-{hi*100:.0f}%]"
    L.append("\n### G-4 区分別の混同行列(Wilson95%区間付き)。KPと本文を分け、HR難例(人間が個別承認した6本)を除いた『通常記事音声』も併記\n")
    L.append("| 構成 | KP正常 過剰NG | KP問題(human+constructed) 誤PASS | 本文 通常記事音声(HR難例除く) 過剰NG | 本文 HR難例+plw正常 過剰NG | 本文問題(TTS+plw+human, splice除く) 誤PASS |\n|---|---|---|---|---|---|")
    S["phase3_by_kind"] = {}
    for c in cfgs:
        rows = {r["id"]: r for r in P3 if r["config"] == c}

        def sel(f):
            return [rows[m["id"]] for m in man.values() if f(m) and m["id"] in rows]
        kpn = sel(lambda m: m["label"] == "normal" and m["kind"] == "kp")
        kpp = sel(lambda m: m["label"] == "problem" and m["kind"] == "kp" and m["tier"] in ("P_human", "P_constructed"))
        bn = sel(lambda m: m["label"] == "normal" and m["kind"] == "body" and m["tier"] == "N_human" and "hr_approved_hard" not in m["tags"])
        bh = sel(lambda m: m["label"] == "normal" and m["kind"] == "body" and ("hr_approved_hard" in m["tags"] or m["tier"] == "N_constructed"))
        bp = sel(lambda m: m["label"] == "problem" and m["kind"] == "body" and m["tier"] in ("P_human", "P_constructed"))
        x = {"kp_normal": (sum(1 for r in kpn if not r["verified"]), len(kpn)), "kp_problem_fp": (sum(1 for r in kpp if r["verified"]), len(kpp)),
             "body_normal_general": (sum(1 for r in bn if not r["verified"]), len(bn)), "body_hard_normal": (sum(1 for r in bh if not r["verified"]), len(bh)),
             "body_problem_fp": (sum(1 for r in bp if r["verified"]), len(bp))}
        S["phase3_by_kind"][c] = x
        L.append(f"| {c} {desc[c]} | {fmt(*x['kp_normal'])} | {fmt(*x['kp_problem_fp'])} | {fmt(*x['body_normal_general'])} | {fmt(*x['body_hard_normal'])} | {fmt(*x['body_problem_fp'])} |")

    # ---------------- H. 原価・時間モデル(記事B相当1セット)
    L.append("\n## H. 1記事セット換算(記事B構成: KP 10音声[計11.5秒]、英語本文 Std5+Adv10=15セグメント[計388.7秒])\n")
    JPY_USD = 160.0
    kp_secs = [1.0, 1.12, 1.28, 1.12, 1.5, 1.0, 0.88, 1.02, 1.5, 1.12]
    body_secs = [7.4, 53.4, 41.9, 54.2, 13.6, 8.2, 14.2, 4.8, 7.7, 12.9, 10.5, 51.6, 44.2, 50.3, 13.8]

    def reg(xs, ys):
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
        return my - b * mx, b
    regs = {}
    for meth in METHODS:
        rr = [r for r in raw if r["method"] == meth and r["rep"] == 1 and r["id"] in man and r.get("wall_s") is not None and (meth.startswith("whisper") or r["cond"] == "neutral")]
        regs[meth] = reg([r["audio_s"] for r in rr], [r["wall_s"] for r in rr])
    wcpu = [r for r in raw if r["method"] == "whisper" and r["rep"] == 1 and r["id"] in man]
    cpu_per_s = sum(r["cpu_s"] for r in wcpu) / sum(r["audio_s"] for r in wcpu)
    wcpu_m = [r for r in raw if r["method"] == "whisper_medium" and r["id"] in man]
    cpu_per_s_m = sum(r["cpu_s"] for r in wcpu_m) / max(1e-9, sum(r["audio_s"] for r in wcpu_m))
    oai = [r for r in raw if r["method"] == "openai" and r["cond"] == "neutral" and r["id"] in man]
    oai_kp = statistics.mean(r["jpy"] for r in oai if man[r["id"]]["kind"] == "kp")
    oai_body = statistics.mean(r["jpy"] for r in oai if man[r["id"]]["kind"] == "body")
    S["time_regs"] = {k: {"a": round(v[0], 3), "b": round(v[1], 4)} for k, v in regs.items()}
    S["whisper_cpu_s_per_audio_s"] = round(cpu_per_s, 3)
    S["openai_jpy_per_call"] = {"kp": round(oai_kp, 5), "body": round(oai_body, 5)}
    L.append("実測回帰(wall秒 = a + b×音声秒): " + "; ".join(f"{ML[k]}: a={v[0]:.2f}, b={v[1]:.3f}" for k, v in regs.items()) + f"。Whisper CPU時間={cpu_per_s:.2f}s/音声秒。OpenAI実測原価=KP約JPY{oai_kp:.4f}/回・本文約JPY{oai_body:.4f}/回(トークン実測)。")

    def azj(sec):
        return math.ceil(sec) / 3600.0 * JPY_USD
    TTS_JPY_PER_S = 25 * 6.0 / 1e6 * JPY_USD   # Standard同期(25 tok/s x $6/M)。Batchは半額
    L.append("\n前提: 1記事セット=KP10+本文15の初回検証(再生成なし)を基準。構成別のSecondary呼出率は本Trialの通常記事音声(N_human)での実測(KP/本文別)。過剰NG→TTS再生成は『過剰NG率×音声のTTS原価』(Standard同期単価$6/M・25tok/s、Batchはその半額)。\n")
    L.append("| 構成 | ASR API原価/記事(JPY) | 検査時間/記事(直列合計, 秒) | うちWhisper CPU時間(秒) | 過剰NG期待数(KP/本文)[通常記事音声のレート] | 過剰NG由来の追加TTS原価(JPY, Standard単価) | HR到達期待(独立仮定の下限〜過剰NGが全枠NG確定の上限) |\n|---|---|---|---|---|---|---|")
    S["article_model"] = {}
    for c in cfgs:
        rowsc = [r for r in P3 if r["config"] == c and r["label"] == "normal" and tmap[r["id"]] == "N_human"]

        def prate(kind):
            sel_ = [r for r in rowsc if r["kind"] == kind]
            return sum(1 for r in sel_ if r.get("secondary_called") or r.get("secondary_cached") or r.get("sec_fn_calls")) / max(1, len(sel_))
        pk, pb = prate("kp"), prate("body")
        prim = {"C1": "openai", "C1d": "openai", "C1dK": "openai", "C5": "openai", "C5K": "openai", "C5m": "openai", "C2": "azure", "C3": "whisper", "C4": "whisper", "C3m": "whisper_medium", "C4m": "whisper_medium"}[c]
        sec_ = {"C1": "azure", "C1d": "azure", "C1dK": "azure", "C5": "azure", "C5K": "azure", "C5m": "azure", "C2": "openai", "C3": "openai", "C4": "azure", "C3m": "openai", "C4m": "azure"}[c]
        veto_engine = {"C5": "whisper", "C5K": "whisper", "C5m": "whisper_medium"}.get(c)
        veto_kinds = ("kp",) if c == "C5K" else ("kp", "body")
        cpu_rate = {"whisper": cpu_per_s, "whisper_medium": cpu_per_s_m}
        cost = 0.0
        tm = 0.0
        cpu = 0.0
        for kind, secs, p, oj in (("kp", kp_secs, pk, oai_kp), ("body", body_secs, pb, oai_body)):
            for sx in secs:
                pc = {"openai": oj, "azure": azj(sx), "whisper": 0.0, "whisper_medium": 0.0}
                tw = {m: regs[m][0] + regs[m][1] * sx for m in METHODS}
                cost += pc[prim] + p * pc[sec_]
                tm += tw[prim] + p * tw[sec_]
                if prim.startswith("whisper"):
                    cpu += cpu_rate[prim] * sx
                if veto_engine and kind in veto_kinds:
                    cpu += cpu_rate[veto_engine] * sx
                    tm += tw[veto_engine]
        ek = S["phase3_by_kind"][c]["kp_normal"]
        eb = S["phase3_by_kind"][c]["body_normal_general"]
        rk, rb = ek[0] / max(1, ek[1]), eb[0] / max(1, eb[1])
        e_kp, e_body = rk * len(kp_secs), rb * len(body_secs)
        tts_cost = rk * sum(kp_secs) * TTS_JPY_PER_S + rb * sum(body_secs) * TTS_JPY_PER_S
        hr_low = len(kp_secs) * rk ** 4 + len(body_secs) * rb ** 3
        hr_up = e_kp + e_body
        L.append(f"| {c} {desc[c]} | {cost:.2f} (Secondary率 KP{pk:.0%}/本文{pb:.0%}) | {tm:.0f} | {cpu:.0f} | {e_kp:.2f}/{e_body:.2f} | {tts_cost:.3f} | {hr_low:.3f}〜{hr_up:.2f} |")
        S["article_model"][c] = {"asr_jpy": round(cost, 3), "time_s": round(tm, 1), "p_sec_kp": round(pk, 3), "p_sec_body": round(pb, 3), "tts_regen_jpy": round(tts_cost, 4),
                                  "over_ng_rate_kp": round(rk, 4), "over_ng_rate_body_general": round(rb, 4), "hr_low": round(hr_low, 4), "hr_up": round(hr_up, 3)}
    L.append("\n注: 時間は『各音声を1件ずつ直列に検査した場合の合計』(Productionは音声生成と検査が交互のため近似)。API方式は並列化可能(本Trialの221呼出を6スレッドで69秒=1呼出あたり実効0.31秒)。Whisperは別process同時実行でも約1.2倍の短縮に留まる(smallが自身で複数CPUスレッドを使うため)。")
    # ---------------- I. take part 10回反復(旧Trial保存転写)にPhase 3構成を適用
    tp = json.load(open(os.path.join(RES, "takepart10_phase3.json"), encoding="utf-8"))
    L.append("\n## I. 『take part』旧NG音声(ユーザー聴感tart)×10回独立実行(旧Trial FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01の保存転写)にPhase 3構成を適用(同一音声の反復=安定性の証拠、独立10音声ではない)\n")
    L.append("OpenAI Primaryの転写分布(旧Trial 10回): " + ", ".join(f"『{k}』x{v}" for k, v in collections.Counter(o["openai"] for o in tp if o["config"] == "C1").items()) + "。Azure 10/10『Take Tart.』、Whisper small 10/10『Take Tarte.』。本Trial今回の再測定(OpenAI x4=『Take tart.』4/4、Azure x3、Whisper x3 同様)も整合。\n")
    L.append("| 構成 | 誤PASS(見逃し)/10 | 検出NG/10 | 備考 |\n|---|---|---|---|")
    notes = {"C1": "OpenAI PASS時はSecondary不要のため見逃す", "C1d": "force_secondaryでAzureが常に拒否", "C2": "Azure Primary NG後のOpenAI Secondaryが『part』で許容集合PASS",
             "C3": "Whisper NG後のOpenAI Secondaryが『part』で救済", "C4": "Whisper NG後のAzure Secondaryが拒否", "C5": "Whisper不一致でforce_secondary→Azure拒否"}
    for cc in ("C1", "C1d", "C2", "C3", "C4", "C5"):
        rr_ = [o for o in tp if o["config"] == cc]
        L.append(f"| {cc} {desc[cc]} | {sum(1 for o in rr_ if o['verified'])} | {sum(1 for o in rr_ if not o['verified'])} | {notes[cc]} |")
    L.append("\n含意: 『OpenAIが合意すればPASS』となる構成(C1/C2/C3)は、OpenAIが言語priorで『part』と補正する確率(旧Trial 3/10)だけ誤PASSする。Azureの拒否を必須にする構成(C1d/C4/C5)は本音声では10/10検出。ただしAzureが常に正しい保証はなく、本音声1本の観測(Azureはこの音声で10/10 tart)に限る。")
    # ---------------- J. Whisper small -> medium
    L.append("\n## J. Whisper small→medium(容量由来の確認、追加1サイズ)\n")
    sm_ = {r["id"]: r for r in P12 if r["method"] == "whisper" and r["cond"] == "prod"}
    md_ = {r["id"]: r for r in P12 if r["method"] == "whisper_medium" and r["cond"] == "prod"}
    cnt2 = collections.Counter()
    for i, r in md_.items():
        if i in sm_:
            cnt2[(man[i]["label"], man[i]["kind"], sm_[i]["verdict_pass"], r["verdict_pass"])] += 1
    L.append("| 区分 | small PASS→medium PASS | small PASS→medium NG | small NG→medium PASS | small NG→medium NG |\n|---|---|---|---|---|")
    for lab in ("normal", "problem"):
        for kd in ("kp", "body"):
            L.append(f"| {lab}/{kd} | {cnt2[(lab,kd,True,True)]} | {cnt2[(lab,kd,True,False)]} | {cnt2[(lab,kd,False,True)]} | {cnt2[(lab,kd,False,False)]} |")
    L.append("\n改善例: " + "; ".join(f"{i}: small『{' '.join((sm_[i]['transcript'] or '').split())[:30]}』→medium『{' '.join((md_[i]['transcript'] or '').split())[:30]}』" for i in md_ if i in sm_ and not sm_[i]["verdict_pass"] and md_[i]["verdict_pass"]))
    mw = [r for r in raw if r["method"] == "whisper_medium"]
    L.append(f"\nmedium処理時間: 1件平均 {statistics.mean(r['wall_s'] for r in mw):.2f}s(small {statistics.mean(r['wall_s'] for r in raw if r['method']=='whisper'):.2f}s)、CPU {cpu_per_s_m:.2f}s/音声秒(small {cpu_per_s:.2f})。")
    text_ = "\n".join(L).split("\n")
    for k_ in range(1, len(text_)):
        if text_[k_].startswith("|---") and text_[k_ - 1].startswith("|"):
            ncol = text_[k_ - 1].count("|") - 1
            text_[k_] = "|" + "---|" * ncol
    open(os.path.join(RES, "tables.md"), "w", encoding="utf-8").write("\n".join(text_))
    json.dump(S, open(os.path.join(RES, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", len(L), "lines")


if __name__ == "__main__":
    main()
