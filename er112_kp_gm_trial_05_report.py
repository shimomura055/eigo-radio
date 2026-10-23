# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_22: Trial_05 盲検表・決定論的集計・Fable判定後の集計 (DEV専用、API 0)。
サブコマンド:
  blind   : fable_blind_05.md + fable_blind_05_key.json(arm伏せ。ラベル済み文字列約10件を混在=OF-KP1-08)
  metrics : 決定論的集計(0円、OF-KP1-05): gloss==naive_ja率、文字数比、説明文型語尾、validate互換、conveys分布、reasoning_tokens、1call費用
  report  : --labels <json> でFable判定後の集計(R基準・held-out・control一致率・Before/After)
"""
from __future__ import annotations

import argparse, collections, json, os, random, re, sys
os.environ.setdefault("KP04_INSPECT_VERSION", "v2")
os.environ.setdefault("KP04_INSPECT_EFFORT", "low")
import er112_kp_gm_trial_05 as T5                      # noqa: E402
import er112_kp_gm_trial_04_report as R4               # noqa: E402
import er112_kp_gm_trial_04_gen as G4                  # noqa: E402
import er112_kp_gm_trial_04 as X4                      # noqa: E402

OUT5 = T5.OUT5
RD = T5.RD
sys.stdout.reconfigure(encoding="utf-8")
RANK = {"PASS": 2, "THIN": 1, "FAIL": 0, "FAIL_LIT": 0}
NCOL = 14


def known_labels():
    """Trial_02〜04でFable確定済みの文字列ラベル {(key_phrase, sent, gloss): label}。"""
    labels = json.load(open(RD / "TRIAL_04/fable_labels_04.json", encoding="utf-8"))
    return R4.label_table(labels)


def new_cells():
    return {(r["arm"], r["key"], r["rep"]): r for r in T5.read_jsonl(T5.RES5) if r.get("gloss")}


def ref_cells(keys):
    """参照(Trial_04): M rep1-2 / Cp rep1 / B0 既存。{(arm,key,rep): gloss}"""
    out = {}
    for (arm, k, rep), r in G4.load_res().items():
        if k in keys and r.get("gloss"):
            if arm == "M":
                out[("M_t4", k, rep)] = r["gloss"]
            elif arm == "Cp":
                out[("Cp_t4", k, rep)] = r["gloss"]
    for (k, rep), r in G4.b0_outputs(set(keys)).items():
        out[("B0_t4", k, rep)] = r["gloss"]
    return out


def blind_keys():
    held = [k for k in T5.heldout_order() if any(r["key"] == k for r in new_cells().values())]
    return T5.R_KEYS + held


def cmd_blind(a):
    A = T5.all_kps5()
    keys = blind_keys()
    known = known_labels()
    nc = new_cells()
    rc = ref_cells(set(keys))
    cells = collections.defaultdict(lambda: collections.defaultdict(list))   # key -> gloss -> [cellname]
    for (arm, k, rep), r in nc.items():
        cells[k][r["gloss"]].append("%s/rep%d" % (arm, rep))
    for (arm, k, rep), g in rc.items():
        cells[k][g].append("%s/rep%d" % (arm, rep))
    rnd = random.Random("blind05")
    # control(OF-KP1-08): 既知ラベル済み文字列を約10件、arm伏せで混在。R+heldの既知文字列(最大6、ラベル層別)+S KPの既知文字列(最大4、ラベル層別)
    known_in_rows = [(k, g, known[(A[k]["key"], A[k]["sent"], g)]) for k in keys for g in cells[k] if (A[k]["key"], A[k]["sent"], g) in known]
    by_lab = collections.defaultdict(list)
    for t in sorted(known_in_rows):
        by_lab[t[2]].append(t)
    controls = []
    for lab in ("FAIL_LIT", "FAIL", "THIN", "PASS"):
        pool = by_lab.get(lab, [])
        rnd.shuffle(pool)
        controls += pool[: (3 if lab in ("FAIL_LIT", "PASS") else 2)]
    controls = controls[:6]
    st = json.load(open(RD / "TRIAL_04/strata_04.json", encoding="utf-8"))
    S_keys = [k for k in st["trial_set"] if k not in T5.R_KEYS]
    S_known = []
    for k in sorted(S_keys):
        for (kk, sent, g), lab in known.items():
            if kk == A[k]["key"] and sent == A[k]["sent"]:
                S_known.append((k, g, lab))
    S_by = collections.defaultdict(list)
    for t in sorted(S_known):
        S_by[t[2]].append(t)
    ctl_extra = []
    for lab in ("THIN", "FAIL", "FAIL_LIT", "PASS"):
        pool = S_by.get(lab, [])
        rnd.shuffle(pool)
        ctl_extra += pool[: (2 if lab in ("THIN", "PASS") else 1)]
    ctl_extra = ctl_extra[: max(0, 10 - len(controls))]
    ctl_set = {(k, g) for k, g, _ in controls}
    ctl_extra_by_key = collections.defaultdict(list)
    for k, g, lab in ctl_extra:
        ctl_extra_by_key[k].append((g, lab))
    lines = ["# fable_blind_05: Std日本語gloss盲検表(委任_22 Trial_05 Stage 1+held-out。arm伏せ)\n",
             "行=Key Phrase、列A〜=この表で見る日本語glossの**文字列**(同じ文字列は1列。arm・repの帰属は`fable_blind_05_key.json`に分離)。**判定してからkeyを開くこと。**",
             "判定: PASS / 薄(THIN=意味は誤りでないがフレーズ全体より弱い・含意欠落) / FAIL(用法取り違え・語義誤認・誤訳) / FAIL_LIT(比喩・慣用を字義の像で訳した字義訳)。",
             "難例(draw a line, take the wheel 等)は`GOLD_LABELS_FINAL_01.md`のgold。通常は本文文の用法とフレーズ全体の意味への一致が基準。",
             "Trial_02〜04でFable確定済みの文字列のうち約10件は**再判定用に混ぜてあります**(どれかは不明、前回ラベルは見ないで判定)。それ以外のラベル済み文字列は表に含めません(継承)。\n",
             "| # | 区分 | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(NCOL)) + " |", "|---|---|---|---|" + "---|" * NCOL]
    keymap = {}
    n = 0
    rows = [(k, "R" if k in T5.R_KEYS else "held-out", False) for k in keys] + [(k, "S(control)", True) for k in sorted(ctl_extra_by_key)]
    rnd.shuffle(rows)    # 行順もarm・区分から推測できないように並べ替え
    maxcols = 0
    for k, sect, is_ctl_row in rows:
        kp = A[k]
        show = collections.OrderedDict()
        tags = {}
        if not is_ctl_row:
            for g, cs in cells[k].items():
                lab = known.get((kp["key"], kp["sent"], g))
                if lab is None:
                    show[g] = cs
                elif (k, g) in ctl_set:
                    show[g] = cs
                    tags[g] = ("control", lab)
        else:
            for g, lab in ctl_extra_by_key[k]:
                show[g] = ["control-S"]
                tags[g] = ("control", lab)
        if not show:
            continue
        n += 1
        strs = list(show)
        random.Random("blind05-" + k).shuffle(strs)
        maxcols = max(maxcols, len(strs))
        assert len(strs) <= NCOL, (k, len(strs))
        keymap[str(n)] = {"key": k, "section": sect, "cols": {chr(65 + i): dict(gloss=s, cells=show[s], **({"control_prior_label": tags[s][1]} if s in tags else {})) for i, s in enumerate(strs)}}
        lines.append("| %d | %s | %s | %s | %s |" % (n, "-", kp["key"], kp["sent"].replace("|", "/")[:160], " | ".join(s.replace("|", "/") for s in strs + [""] * (NCOL - len(strs)))))
    (OUT5 / "fable_blind_05.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT5 / "fable_blind_05_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    nctl = sum(1 for v in keymap.values() for c in v["cols"].values() if "control_prior_label" in c)
    print("blind rows", n, "max cols", maxcols, "cells", sum(len(c["cells"]) for v in keymap.values() for c in v["cols"].values()), "controls", nctl)


def cmd_blind_c(a):
    """委任_23: Cp追加後に新たに出現した文字列のみの追加盲検表(fable_blind_05c.md)。既出文字列(既知ラベル+fable_labels_05)はラベル継承、arm伏せ。"""
    A = T5.all_kps5()
    labels = json.load(open(RD / "TRIAL_05" / "fable_labels_05.json", encoding="utf-8"))
    tab, _ = label_lookup(labels)
    nc = new_cells()
    orig = {v["key"] for v in json.load(open(OUT5 / "fable_blind_05_key.json", encoding="utf-8")).values()}
    keys = [k for k in blind_keys() if k in orig]
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    for (arm, k, rep), r in nc.items():
        if k in keys and arm == "Cp":
            cells[k][r["gloss"]].append("%s/rep%d" % (arm, rep))
    lines = ["# fable_blind_05c: Cp追加後に新たに出現したStd日本語gloss文字列(委任_23。arm伏せ)\n",
             "行=Key Phrase、列=この表で見る日本語glossの**文字列**(既出でラベル済みの文字列は含めず継承)。**判定してからkeyを開くこと。** keyは`fable_blind_05c_key.json`。",
             "判定: PASS / 薄(THIN) / FAIL / FAIL_LIT(字義訳)。ラベル形式 `{\"<row#>:<col>\": LABEL}`。\n",
             "| # | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(6)) + " |", "|---|---|---|" + "---|" * 6]
    keymap = {}
    n = 0
    ks = list(keys)
    random.Random("blind05c").shuffle(ks)
    for k in ks:
        kp = A[k]
        strs = [g for g in cells[k] if tab.get((kp["key"], kp["sent"], g)) is None]
        if not strs:
            continue
        random.Random("blind05c-" + k).shuffle(strs)
        assert len(strs) <= 6
        n += 1
        keymap[str(n)] = {"key": k, "cols": {chr(65 + i): dict(gloss=g, cells=cells[k][g]) for i, g in enumerate(strs)}}
        lines.append("| %d | %s | %s | %s |" % (n, kp["key"], kp["sent"].replace("|", "/")[:160], " | ".join(g.replace("|", "/") for g in strs + [""] * (6 - len(strs)))))
    (OUT5 / "fable_blind_05c.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT5 / "fable_blind_05c_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("blind_c rows", n, "strings", sum(len(v["cols"]) for v in keymap.values()))


def cmd_blind_d(a):
    """委任_25: X2p(THIN対策)で新たに出現した文字列のみの追加盲検表(fable_blind_05d.md)。既出文字列(既知+05+05c)はラベル継承、arm伏せ。"""
    A = T5.all_kps5()
    labels = json.load(open(RD / "TRIAL_05" / "fable_labels_05.json", encoding="utf-8"))
    labels_c = json.load(open(RD / "TRIAL_05" / "fable_labels_05c.json", encoding="utf-8"))
    tab, _ = label_lookup(labels, labels_c)
    nc = new_cells()
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    for (arm, k, rep), r in nc.items():
        if arm == "X2p":
            cells[k][r["gloss"]].append("%s/rep%d" % (arm, rep))
    lines = ["# fable_blind_05d: X2p(委任_25)で新たに出現したStd日本語gloss文字列(arm伏せ)\n",
             "行=Key Phrase、列=この表で見る日本語glossの**文字列**(既出でラベル済みの文字列は含めず継承)。**判定してからkeyを開くこと。** keyは`fable_blind_05d_key.json`。",
             "判定: PASS / 薄(THIN) / FAIL / FAIL_LIT(字義訳)。ラベル形式 `{\"<row#>:<col>\": LABEL}`。\n",
             "| # | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(6)) + " |", "|---|---|---|" + "---|" * 6]
    keymap = {}
    n = 0
    ks = list(cells)
    random.Random("blind05d").shuffle(ks)
    inherited = 0
    for k in ks:
        kp = A[k]
        strs = [g for g in cells[k] if tab.get((kp["key"], kp["sent"], g)) is None]
        inherited += len(cells[k]) - len(strs)
        if not strs:
            continue
        random.Random("blind05d-" + k).shuffle(strs)
        assert len(strs) <= 6
        n += 1
        keymap[str(n)] = {"key": k, "cols": {chr(65 + i): dict(gloss=g, cells=cells[k][g]) for i, g in enumerate(strs)}}
        lines.append("| %d | %s | %s | %s |" % (n, kp["key"], kp["sent"].replace("|", "/")[:160], " | ".join(g.replace("|", "/") for g in strs + [""] * (6 - len(strs)))))
    (OUT5 / "fable_blind_05d.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT5 / "fable_blind_05d_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("blind_d rows", n, "strings", sum(len(v["cols"]) for v in keymap.values()), "inherited(ラベル継承)", inherited)


def cmd_blind_s2(a):
    """委任_23 Stage 2準備(API 0): non-R KP x X2 1rep(新規、T5 results)・B0/CpはTrial_04再利用の盲検表。X2未実行なら件数見積のみ。"""
    A = T5.all_kps5()
    st = json.load(open(RD / "TRIAL_04/strata_04.json", encoding="utf-8"))
    keys = [k for k in st["trial_set"] if k not in T5.R_KEYS]
    arts = collections.defaultdict(list)
    for k in keys:
        arts[G4.art_id(A[k])].append(k)
    x2 = {k: r for (arm, k, rep), r in new_cells().items() if arm == "X2" and rep == 1 and k in keys}
    est = len(arts) * 0.1254
    print("Stage2 non-R KP %d, X2 calls %d, 見積 %.2f円(X2実測単価0.1254円/call)、X2済み %d KP" % (len(keys), len(arts), est, len(x2)))
    if len(x2) < len(keys):
        print("X2未実行のため盲検表は未生成(Fableの「Stage 1通過」連絡後に gen --arm X2 --set S2 --reps 1 を実行)")
        return
    known = known_labels()
    rc = ref_cells(set(keys))
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, r in x2.items():
        cells[k][r["gloss"]].append("X2_t5/rep1")
    for (arm, k, rep), g in rc.items():
        if arm in ("B0_t4", "Cp_t4"):
            cells[k][g].append("%s/rep%d" % (arm, rep))
    NL = chr(10)
    lines = ["# fable_blind_05s2: Stage 2 Std日本語gloss盲検表(委任_23準備。arm伏せ。既ラベル済み文字列は継承して非掲載)" + NL,
             "判定: PASS / 薄(THIN) / FAIL / FAIL_LIT。ラベル形式 {row#:col: LABEL}。keyは fable_blind_05s2_key.json。" + NL,
             "| # | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(6)) + " |", "|---|---|---|" + "---|" * 6]
    keymap = {}
    n = 0
    ks = sorted(keys)
    random.Random("blind05s2").shuffle(ks)
    for k in ks:
        kp = A[k]
        strs = [g for g in cells[k] if (kp["key"], kp["sent"], g) not in known]
        if not strs:
            continue
        random.Random("blind05s2-" + k).shuffle(strs)
        strs = strs[:6]
        n += 1
        keymap[str(n)] = {"key": k, "cols": {chr(65 + i): dict(gloss=g, cells=cells[k][g]) for i, g in enumerate(strs)}}
        lines.append("| %d | %s | %s | %s |" % (n, kp["key"], kp["sent"].replace("|", "/")[:160], " | ".join(g.replace("|", "/") for g in strs + [""] * (6 - len(strs)))))
    (OUT5 / "fable_blind_05s2.md").write_text(NL.join(lines) + NL, encoding="utf-8")
    (OUT5 / "fable_blind_05s2_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("blind_s2 rows", n)


# ------------------------------------------------------------------ 決定論的集計(0円、OF-KP1-05)
_EXPL = re.compile(r"(こと|もの|ようす|様子|という|とき|ため|場合|状態|ところ)$")


def norm(s):
    return re.sub(r"[\s　～〜]", "", s or "")


def cmd_metrics(a):
    nc = new_cells()
    A = T5.all_kps5()
    lines = ["# Trial_05 決定論的集計(API 0、OF-KP1-05)\n"]
    b0_len = collections.defaultdict(list)
    for (arm, k, rep), r in nc.items():
        if arm == "B0":
            b0_len[k].append(len(r["gloss"]))
    lines.append("| arm | n出力 | callあたり円(平均) | reasoning_tokens平均/call | output_tokens平均/call | validate互換 valid/検査 | gloss==naive_ja | 文字数比>1.5(対B0平均) | 説明文型語尾 | 30字超 | conveys yes/partly/no |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    ledger = T5.read_jsonl(T5.LEDGER5)
    for arm in T5.ARMS:
        rs = [r for (ar, k, rep), r in nc.items() if ar == arm]
        if not rs:
            continue
        calls = [x for x in ledger if x.get("arm") == arm and x.get("kind") == "gen"]
        cost = sum(x["cost_jpy"] for x in calls) / max(1, len(calls))
        rt = [x["usage"].get("reasoning_tokens") for x in calls if x["usage"].get("reasoning_tokens") is not None]
        ot = [x["usage"].get("output_tokens") for x in calls]
        vs = [r["validate"]["valid"] for r in rs if r.get("validate")]
        eq = sum(1 for r in rs if r["fields"].get("naive_ja") and norm(r["fields"]["naive_ja"]) == norm(r["gloss"]))
        has_naive = sum(1 for r in rs if r["fields"].get("naive_ja"))
        over = 0
        cmp_n = 0
        for r in rs:
            if r["key"] in b0_len and arm != "B0":
                cmp_n += 1
                if len(r["gloss"]) > 1.5 * (sum(b0_len[r["key"]]) / len(b0_len[r["key"]])):
                    over += 1
        expl = sum(1 for r in rs if _EXPL.search(r["gloss"]))
        long_ = sum(1 for r in rs if len(r["gloss"]) > 30)
        cv = collections.Counter(r["fields"].get("naive_ja_conveys") for r in rs if r["fields"].get("naive_ja_conveys"))
        lines.append("| %s | %d | %.4f | %s | %.0f | %d/%d | %s | %s | %d | %d | %s |" % (
            arm, len(rs), cost, ("%.0f" % (sum(rt) / len(rt))) if rt else "n/a", sum(ot) / max(1, len(ot)), sum(vs), len(vs),
            ("%d/%d" % (eq, has_naive)) if has_naive else "-", ("%d/%d" % (over, cmp_n)) if arm != "B0" else "-", expl, long_,
            ("%d/%d/%d" % (cv.get("yes", 0), cv.get("partly", 0), cv.get("no", 0))) if cv else "-"))
    lines.append("")
    inval = [(r["arm"], r["key"], r["rep"], r["validate"]["reasons"]) for r in nc.values() if r.get("validate") and not r["validate"]["valid"]]
    lines.append("validate不合格の出力: %d件 %s" % (len(inval), inval[:10]))
    lines.append("")
    lines.append("## OF-KP1-03 reasoning_tokens(B0 vs Cp、新規実行で計測。Trial_04の既存ledgerのluna gen行には未記録のため過去分は比較不可)")
    for arm in T5.ARMS:
        calls = [x for x in ledger if x.get("arm") == arm and x.get("kind") == "gen"]
        if calls:
            lines.append("- %s: %d call、reasoning_tokens平均=%s、output_tokens平均=%.0f、1call平均費用=%.4f円" % (
                arm, len(calls), ("%.0f" % (sum(x["usage"].get("reasoning_tokens") or 0 for x in calls) / len(calls))), sum(x["usage"].get("output_tokens") or 0 for x in calls) / len(calls),
                sum(x["cost_jpy"] for x in calls) / len(calls)))
    (OUT5 / "metrics_05.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ------------------------------------------------------------------ Fable判定後の集計
def label_lookup(labels, labels_c=None, labels_d=None):
    A = T5.all_kps5()
    known = known_labels()
    keymap = json.load(open(OUT5 / "fable_blind_05_key.json", encoding="utf-8"))
    tab = dict(known)
    ctl = []
    for rk, v in keymap.items():
        for col, c in v["cols"].items():
            lab = labels.get("%s:%s" % (rk, col))
            if lab is None:
                continue
            kp = A[v["key"]]
            if "control_prior_label" in c:
                ctl.append((v["key"], c["gloss"], c["control_prior_label"], lab))
                # 再判定ラベルは使わず前回ラベルを維持(集計の一貫性)。差異は一致率で別掲
                continue
            tab[(kp["key"], kp["sent"], c["gloss"])] = lab
    if labels_c:
        kc = json.load(open(OUT5 / "fable_blind_05c_key.json", encoding="utf-8"))
        for rk, v in kc.items():
            for col, c in v["cols"].items():
                lab = labels_c.get("%s:%s" % (rk, col))
                if lab is not None:
                    tab[(A[v["key"]]["key"], A[v["key"]]["sent"], c["gloss"])] = lab
    if labels_d:
        kd = json.load(open(OUT5 / "fable_blind_05d_key.json", encoding="utf-8"))
        for rk, v in kd.items():
            for col, c in v["cols"].items():
                lab = labels_d.get("%s:%s" % (rk, col))
                if lab is not None:
                    tab[(A[v["key"]]["key"], A[v["key"]]["sent"], c["gloss"])] = lab
    return tab, ctl


def cmd_report(a):
    labels = json.load(open(a.labels, encoding="utf-8"))
    labels_c = json.load(open(a.labels_c, encoding="utf-8")) if a.labels_c else None
    labels_d = json.load(open(a.labels_d, encoding="utf-8")) if a.labels_d else None
    tab, ctl = label_lookup(labels, labels_c, labels_d)
    A = T5.all_kps5()
    nc = new_cells()
    rc = ref_cells(set(T5.R_KEYS) | set(T5.heldout_order()))

    def lab_of(k, g):
        return tab.get((A[k]["key"], A[k]["sent"], g))

    L = ["# Trial_05 集計(ラベル=%s)\n" % a.labels]
    # control一致率(OF-KP1-08)
    agree = sum(1 for _, _, p, n in ctl if p == n)
    coarse = lambda x: "OK" if x == "PASS" else ("NG" if x in ("FAIL", "FAIL_LIT") else "THIN")
    agree_c = sum(1 for _, _, p, n in ctl if coarse(p) == coarse(n))
    L.append("## OF-KP1-08 盲検の再現性(既存ラベル済み文字列の再判定)\n")
    L.append("- 厳密一致 %d/%d、粗区分(PASS/THIN/NG)一致 %d/%d" % (agree, len(ctl), agree_c, len(ctl)))
    for k, g, p, n in ctl:
        L.append("  - %s | %s | 前回=%s 今回=%s %s" % (k, g, p, n, "" if p == n else "**不一致**"))
    L.append("")
    # R基準
    arms = ["B0", "M", "X1", "X2", "Cp", "X2p", "Cp_t4"]    # Cp_t4=Trial_04の既存Cp rep1(参照)

    def outs(arm, keys, reps):
        rows = []
        for k in keys:
            for rep in reps:
                if arm == "Cp_t4":
                    g = rc.get(("Cp_t4", k, rep))
                elif arm in ("M",):
                    g = nc.get(("M", k, rep), {}).get("gloss") if rep == 3 else rc.get(("M_t4", k, rep))
                else:
                    g = (nc.get((arm, k, rep)) or {}).get("gloss")
                if g:
                    rows.append((k, rep, g, lab_of(k, g)))
        return rows

    L.append("## R(hard-core 4KP x 3rep=12出力/arm) と 事前宣言基準(TRIAL_DESIGN_06 §4)\n")
    L.append("| arm | n | PASS | THIN | FAIL | FAIL_LIT | 未ラベル | (FAIL_LIT+FAIL) | 2rep以上失敗のKP | 基準(<=1/12 かつ 2rep以上失敗KP=0 かつ THIN<=B0+1) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    summ = {}
    for arm in arms:
        rows = outs(arm, T5.R_CORE, (1, 2, 3))
        c = collections.Counter(r[3] or "unlabeled" for r in rows)
        fails = collections.Counter(r[0] for r in rows if r[3] in ("FAIL", "FAIL_LIT"))
        bad_kp = [k for k, v in fails.items() if v >= 2]
        summ[arm] = (c, bad_kp, len(rows))
    b0_thin = summ["B0"][0]["THIN"]
    for arm in arms:
        c, bad_kp, n = summ[arm]
        nf = c["FAIL"] + c["FAIL_LIT"]
        ok = nf <= 1 and not bad_kp and c["THIN"] <= b0_thin + 1
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %s | %s |" % (arm, n, c["PASS"], c["THIN"], c["FAIL"], c["FAIL_LIT"], c["unlabeled"], nf, bad_kp or "なし",
                                                                     ("**満たす**" if ok else "満たさない") + ("(n<12参考)" if n < 12 else "") if arm != "B0" else "-"))
    L.append("\n(Mは Trial_04の既存rep1-2 + 新規rep3。X1対M=H5の比較。)\n")
    L.append("### R co-KP(come down / behind the scenes / sound no one asked for)の悪化確認\n")
    L.append("| KP | rep | " + " | ".join(arms) + " |\n|---|---|" + "---|" * len(arms))
    for k in ["come down", "behind the scenes", "sound no one asked for"]:
        for rep in (1, 2, 3):
            row = []
            for arm in arms:
                rr = outs(arm, [k], (rep,))
                row.append("%s (%s)" % (rr[0][2], rr[0][3] or "?") if rr else "-")
            L.append("| %s | %d | %s |" % (k, rep, " | ".join(row)))
    L.append("\n### R Before/After (KP x arm x rep)\n")
    L.append("| KP | rep | " + " | ".join(arms) + " |\n|---|---|" + "---|" * len(arms))
    for k in T5.R_CORE:
        for rep in (1, 2, 3):
            row = []
            for arm in arms:
                rr = outs(arm, [k], (rep,))
                row.append("%s / %s" % (rr[0][2], rr[0][3] or "?") if rr else "-")
            L.append("| %s | %d | %s |" % (k, rep, " | ".join(row)))
    # held-out
    L.append("\n## held-out(各1rep、B0/X2/Cp/X2p)\n")
    L.append("| KP | B0 | X2 | Cp | X2p | 悪化(B0=PASSでX2/Cp/X2p=THIN/FAIL/FAIL_LIT) |\n|---|---|---|---|---|---|")
    worse = {"X2": [], "Cp": [], "X2p": []}
    for k in T5.heldout_order():
        row, labs = [], {}
        for arm in ("B0", "X2", "Cp", "X2p"):
            r = nc.get((arm, k, 1))
            if not r:
                row.append("-")
                continue
            lab = lab_of(k, r["gloss"])
            labs[arm] = lab
            row.append("%s / %s" % (r["gloss"], lab or "?"))
        if not row or all(x == "-" for x in row) or row[0] == "-":
            continue
        w = []
        for arm in ("X2", "Cp", "X2p"):
            if labs.get("B0") == "PASS" and labs.get(arm) in ("THIN", "FAIL", "FAIL_LIT"):
                worse[arm].append(k)
                w.append(arm)
        L.append("| %s | %s | %s |" % (k, " | ".join(row), ",".join(w) or "なし"))
    L.append("\nheld-out 悪化: X2=%s Cp=%s X2p=%s(基準: 0)\n" % (worse["X2"] or "なし", worse["Cp"] or "なし", worse["X2p"] or "なし"))
    (OUT5 / ("report_05_%s%s.md" % (os.path.basename(a.labels).replace(".json", ""), ("_withcd" if a.labels_d else "_withc") if a.labels_c else ""))).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--labels", default="")
    ap.add_argument("--labels_c", default="")
    ap.add_argument("--labels_d", default="")
    a = ap.parse_args()
    {"blind": cmd_blind, "metrics": cmd_metrics, "report": cmd_report, "blind_c": cmd_blind_c, "blind_d": cmd_blind_d, "blind_s2": cmd_blind_s2}[a.cmd](a)
