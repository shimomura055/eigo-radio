# -*- coding: utf-8 -*-
"""委任_31: 補強Trial(Trial_06有料run)の新規出力を対象にした盲検表・メトリクス・二重判定集計(API 0、DEV専用)。
cmd:
  build   -> TRIAL_06/blind_06b.md(arm伏せ・ラベル欄なし)+ blind_06b_key.json(arm・継承ラベル。判定後にのみ開く)+ OPUS_EVAL_REQUEST_06.md
  metrics -> TRIAL_06/METRICS_06.md(call数・token・円・時間・B0p比・retry数・持ち込み検出)
  agree --labels2 <json> [--labels1 <json>]
          -> 一致率と、arm別 PASS/THIN/FAIL/FAIL_LIT 分布(厳しい方採用)、退行/改善件数
labels形式: {"<row>:<col>": "PASS|THIN|FAIL|FAIL_LIT"}。labels1=Fable一次(未指定なら継承ラベルのみ)、labels2=第二評価者(Opus)。
"""
import argparse, collections, json, random, sys
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_06 as T6
import er112_kp_gm_trial_05 as T5
import er112_kp_gm_trial_05_report as R5

TD = T6.RD / "TRIAL_06"
NL = chr(10)
RANK = {"PASS": 2, "THIN": 1, "FAIL": 0, "FAIL_LIT": 0}
NCOL = 6
RECHECK = ("add up", "reach for someone's wallet")
CONTROL = ("sheltered from the rain",)


def _rows():
    return [r for r in T5.read_jsonl(T6.RES6) if r.get("is_eval") and r.get("gloss")]


def set_of(k, hc):
    return "HC" if k in hc else ("R" if k in T5.R_KEYS else "S2")


def _inherit():
    out = dict(R5.known_labels())
    try:
        la = [json.load(open(T6.RD / "TRIAL_05" / f, encoding="utf-8")) for f in ("fable_labels_05.json", "fable_labels_05c.json", "fable_labels_05d.json", "fable_labels_05e.json")]
        out, _ = R5.label_lookup(*la)
    except Exception as e:  # noqa
        print("WARN label_lookup:", e)
    return out


def cmd_build(a):
    A = T6.all_kps6()
    hc = T6.hc_kps()
    known = _inherit()
    by = collections.defaultdict(lambda: collections.defaultdict(list))   # key -> gloss -> [cell]
    for r in _rows():
        by[r["key"]][r["gloss"]].append("%s/rep%d" % (r["arm"], r["rep"]))
    rows = []
    for k, cells in by.items():
        kp = A[k]
        b = {g for g, c in cells.items() if any(s.startswith("B0p") for s in c)}
        x = {g for g, c in cells.items() if any(s.startswith("X2pp") for s in c)}
        unl = [g for g in cells if (kp["key"], kp["sent"], g) not in known]
        if (b == x and not unl) and k not in RECHECK + CONTROL:
            continue
        rows.append((set_of(k, hc), k, dict(cells)))
    random.Random("blind06b").shuffle(rows)
    head = ["# blind_06b: 補強Trial_06(委任_31)の新規出力 盲検表。**arm・継承ラベルは伏せてある**", "",
            "評価者: Opus(別context)または新しいcontextのFable。判定してから `blind_06b_key.json` を開く(集計時のみ)。",
            "判定基準・再照合対象は `TRIAL_05/fable_blind_06.md` の「判定基準」「再照合対象」節と**同一**(PASS/THIN[範囲を超えた持ち込みを含む]/FAIL/FAIL_LIT、迷ったら厳しい側、持ち込みテスト)。",
            "字義が正解のKP(`sheltered from the rain`等)は、字義のままの訳がPASS。解釈訳への書き換え(本文側の事情の持ち込み・比喩化)は過剰解釈としてTHIN以下。",
            "", "| # | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(NCOL)) + " |", "|---|---|---|" + "---|" * NCOL]
    lines, keymap = list(head), {}
    for n, (sn, k, cells) in enumerate(rows, 1):
        kp = A[k]
        strs = list(cells)
        random.Random("b06b-" + k).shuffle(strs)
        strs = strs[:NCOL]
        cols = {chr(65 + i): dict(gloss=g, cells=cells[g], fable_label=known.get((kp["key"], kp["sent"], g))) for i, g in enumerate(strs)}
        keymap[str(n)] = dict(key=k, set=sn, cols=cols, recheck=k in RECHECK, control=k in CONTROL)
        mark = " **[再照合対象]**" if k in RECHECK else (" **[字義が正解の対照]**" if k in CONTROL else "")
        lines.append("| %d | %s%s | %s | %s |" % (n, kp["key"], mark, kp["sent"].replace("|", "/")[:200], " | ".join(g.replace("|", "/") for g in strs + [""] * (NCOL - len(strs)))))
    TD.mkdir(parents=True, exist_ok=True)
    (TD / "blind_06b.md").write_text(NL.join(lines) + NL, encoding="utf-8")
    (TD / "blind_06b_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(keymap)
    ns = sum(len(v["cols"]) for v in keymap.values())
    nin = sum(1 for v in keymap.values() for c in v["cols"].values() if c["fable_label"])
    req = ["# OPUS_EVAL_REQUEST_06: 補強Trial_06 新規出力の独立評価依頼(委任_31)", "",
           "管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 評価対象=`TRIAL_06/blind_06b.md`(%d行・%d文字列)。arm・既存ラベルは伏せてある。" % (n, ns), "",
           "## 依頼",
           "1. `TRIAL_06/blind_06b.md` の各セルにPASS/THIN/FAIL/FAIL_LITを付け、JSON `{\"<行>:<列>\": \"LABEL\"}` で返す(例 `\"3:B\":\"THIN\"`)。THINには理由1語(持ち込み:否定/主語/時制/対象/場面、狭い、説明的、字義)。",
           "2. 判定基準は `TRIAL_05/fable_blind_06.md` の「判定基準」節(範囲を超えた持ち込み=THIN、迷えば厳しい側)。**ラベル付け前に key JSON を開かない**。",
           "3. 再照合対象を明示: `add up`(否定の持ち込み疑い)、`reach for someone's wallet`(過去ユーザー判断『見出し語忠実でPASS』との整合を理由付きで)。",
           "4. 過剰解釈の確認: 字義が正解のKP(`sheltered from the rain`/`smile through one's tears`/`keep one's eyes on them`等)で、解釈訳へ書き換えた文字列があれば理由に書く。",
           "5. 評価はarmを推測せず文字列のみで行う。", "",
           "## 集計(Fable側)", "`py er112_kp_gm_trial_06_blind2.py agree --labels2 <opus.json> --labels1 <fable.json>`(labels1省略時は継承ラベルのみ)。"]
    (TD / "OPUS_EVAL_REQUEST_06.md").write_text(NL.join(req) + NL, encoding="utf-8")
    print("rows", n, "strings", ns, "継承ラベル有", nin, "sets", dict(collections.Counter(v["set"] for v in keymap.values())))


def cmd_metrics(a):
    rows = T5.read_jsonl(T6.RES6)
    calls = T5.read_jsonl(T6.LEDGER6)
    hc = T6.hc_kps()
    out = ["# METRICS_06: 補強Trial_06 実測(委任_31。API 0で台帳から集計)", ""]
    gens = [c for c in calls if c.get("kind") == "gen"]
    out.append("総call(台帳行)=%d / 総費用=%.3f円 / 総wall(call合計)=%.1fs" % (len(gens), sum(c["cost_jpy"] for c in gens), sum(c["wall_s"] for c in gens)))
    out.append("")
    out.append("## arm x set x 構成(level/call単位。重複行を除く)")
    out.append("| set | arm | level(call group)数 | call数(retry込) | 評価KP出力 | 対象KP総数(sibling込) | 入力tok | 出力tok | reasoning tok | 円 | wall合計s | wall/group平均s |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    agg, seen = {}, set()
    for r in rows:
        k = (r["arm"], r["gid"], r["rep"])
        sn = "S2" if str(r["gid"]).startswith("lvl:") else "HC/R"
        g = agg.setdefault((sn, r["arm"]), dict(lv=set(), calls=0, ev=0, tg=0, it=0, ot=0, rt=0, c=0.0, w=0.0))
        if k not in seen:
            seen.add(k)
            g["lv"].add(k)
            g["calls"] += r["level_calls"]
            g["tg"] += r["n_in_call"]
            g["it"] += r["level_in_tokens"]
            g["ot"] += r["level_out_tokens"]
            g["rt"] += r["level_reasoning_tokens"]
            g["c"] += r["level_cost_jpy"]
            g["w"] += r["level_wall_s"]
        g["ev"] += 1 if r.get("is_eval") else 0
    for (sn, arm), g in sorted(agg.items()):
        out.append("| %s | %s | %d | %d | %d | %d | %d | %d | %d | %.3f | %.1f | %.1f |" % (sn, arm, len(g["lv"]), g["calls"], g["ev"], g["tg"], g["it"], g["ot"], g["rt"], g["c"], g["w"], g["w"] / max(1, len(g["lv"]))))
    out.append("")
    s2 = {arm: g for (sn, arm), g in agg.items() if sn == "S2"}
    if "B0p" in s2 and "X2pp" in s2:
        b, x = s2["B0p"], s2["X2pp"]
        pb, px = b["c"] / b["tg"], x["c"] / x["tg"]
        out += ["## Stage 2(本番構成)単価・B0p比",
                "- B0p: 総%.3f円 / 対象KP%d -> %.4f円/KP / wall/level %.1fs / 出力tok/KP %.0f / reasoning tok/KP %.0f" % (b["c"], b["tg"], pb, b["w"] / len(b["lv"]), b["ot"] / b["tg"], b["rt"] / b["tg"]),
                "- X2pp: 総%.3f円 / 対象KP%d -> %.4f円/KP / wall/level %.1fs / 出力tok/KP %.0f / reasoning tok/KP %.0f" % (x["c"], x["tg"], px, x["w"] / len(x["lv"]), x["ot"] / x["tg"], x["rt"] / x["tg"]),
                "- 1記事セット(約10KP想定、sibling込み)換算: B0p %.3f円 / X2pp %.3f円 / 増分 %.3f円(=%.2f%% of 70円目標)。X2pp/B0p費用比=%.1f倍" % (10 * pb, 10 * px, 10 * (px - pb), 100 * 10 * (px - pb) / 70, px / pb),
                "- level(1 call)あたりwall増分 %.1fs(X2pp %.1fs - B0p %.1fs)。1記事セットのlevel数が1(約10KP/level)の場合の増分に等しい。" % ((x["w"] - b["w"]) / len(x["lv"]), x["w"] / len(x["lv"]), b["w"] / len(b["lv"])), ""]
    out.append("## 機械的事実(判定しない)")
    nflag = collections.Counter((r["arm"], f) for r in rows if r.get("is_eval") for f in (r.get("flags") or []))
    out.append("- 持ち込み検出(record-only detect_import、評価KP出力): %s" % (dict(nflag) or "なし"))
    unres = {(r["arm"], r["gid"], r["rep"]) for r in rows if (r.get("meta") or {}).get("status") != "ALIGN_PASS"}
    rt = {(r["arm"], r["gid"], r["rep"]) for r in rows if (r.get("meta") or {}).get("attempts", 1) > 1}
    out.append("- ALIGN_PASS以外のgroup: %d / retry(attempts>1)のgroup: %d" % (len(unres), len(rt)))
    out.append("- 評価KP出力行数: %s" % dict(collections.Counter((r["arm"], set_of(r["key"], hc)) for r in rows if r.get("is_eval"))))
    (TD / "METRICS_06.md").write_text(NL.join(out) + NL, encoding="utf-8")
    print(NL.join(out))


def cmd_agree(a):
    keymap = json.load(open(TD / "blind_06b_key.json", encoding="utf-8"))
    l2 = json.load(open(a.labels2, encoding="utf-8")) if a.labels2 else {}
    l1 = json.load(open(a.labels1, encoding="utf-8")) if a.labels1 else {}
    lab = {}
    tot = ex = co = 0
    for rk, v in keymap.items():
        for col, c in v["cols"].items():
            ids = "%s:%s" % (rk, col)
            cand = [x for x in (c["fable_label"], l1.get(ids), l2.get(ids)) if x]
            if not cand:
                continue
            lab[(v["key"], c["gloss"])] = min(cand, key=lambda z: RANK[z])
            a1 = l1.get(ids) or c["fable_label"]
            b2 = l2.get(ids)
            if a1 and b2:
                tot += 1
                ex += a1 == b2
                co += (a1 == "PASS") == (b2 == "PASS")
    print("一次(Fable/継承)対第二評価者: 比較可能%d 厳密一致%d(%.0f%%) PASS/非PASS一致%d(%.0f%%)" % (tot, ex, 100 * ex / max(1, tot), co, 100 * co / max(1, tot)))
    rows = _rows()
    hc = T6.hc_kps()
    dist, miss = collections.defaultdict(collections.Counter), 0
    for r in rows:
        l = lab.get((r["key"], r["gloss"]))
        if l is None:
            miss += 1
            continue
        dist[(set_of(r["key"], hc), r["arm"])][l] += 1
    print("ラベル欠落の出力行: %d(盲検表から除外した同一文字列行を含む。同一文字列は継承で埋まる)" % miss)
    for k in sorted(dist):
        print(k, dict(dist[k]))
    bykey = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        l = lab.get((r["key"], r["gloss"]))
        if l:
            bykey[r["key"]][r["arm"]].append((r["rep"], l, r["gloss"]))
    ref = R5.ref_cells({k for k in bykey})
    A = T6.all_kps6()
    known = _inherit()
    reg = collections.defaultdict(list)
    for k, d in bykey.items():
        sn = set_of(k, hc)
        bl = [RANK[l] for _, l, _ in d.get("B0p", [])]
        if sn == "S2":
            for (arm, kk, rep), g in ref.items():
                if kk == k and arm == "B0_t4":
                    kl = known.get((A[k]["key"], A[k]["sent"], g))
                    if kl:
                        bl.append(RANK[kl])
        for rep, l, g in d.get("X2pp", []):
            if not bl:
                continue
            best = max(bl)
            if sn == "HC":
                b_same = [RANK[x] for r2, x, _ in d.get("B0p", []) if r2 == rep]
                if b_same and b_same[0] == 2 and RANK[l] < 2:
                    reg[("HC", "B0p=PASS -> X2pp<=THIN")].append((k, rep, l, g))
            if best == 2 and RANK[l] == 1:
                reg[(sn, "PASS->THIN")].append((k, rep, l, g))
            if best >= 1 and RANK[l] == 0:
                reg[(sn, "(PASS|THIN)->FAIL系")].append((k, rep, l, g))
            if best == 0 and RANK[l] == 2:
                reg[(sn, "FAIL系->PASS(改善)")].append((k, rep, l, g))
            if best == 1 and RANK[l] == 2:
                reg[(sn, "THIN->PASS(改善)")].append((k, rep, l, g))
    for k in sorted(reg):
        print(k, len(reg[k]))
        for x in reg[k]:
            print("    ", x)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--labels1", default="")
    ap.add_argument("--labels2", default="")
    a = ap.parse_args()
    {"build": cmd_build, "metrics": cmd_metrics, "agree": cmd_agree}[a.cmd](a)
