# -*- coding: utf-8 -*-
"""委任_30 OF-KP2-03(d): 二重判定(第二評価者=Opus / 新contextのFable)用の盲検表 fable_blind_06.md(API 0)。
対象: X2pで文字列が変わった KP(Stage 2: X2p文字列がB0_t4どちらのrepとも異なる / R hard-core+co-KP / held-out)。各行にX2p文字列とB0文字列を arm伏せで混在。
出力: docs/.../TRIAL_05/fable_blind_06.md(盲検表。ラベル欄なし)、fable_blind_06_key.json(arm・既存Fableラベル。判定が終わるまで開かない)。
cmd: build / agree --labels <json>  (labels形式 {"row:col": "PASS|THIN|FAIL|FAIL_LIT"}。THIN理由の持ち込み種別は {"row:col": "THIN"} と別ファイルnotesに自由記述でよい)
"""
import argparse, collections, json, random, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_05_report as R5
import er112_kp_gm_trial_05 as T5
import er112_kp_gm_trial_04_gen as G4

OUT = T5.RD / "TRIAL_05"
NL = chr(10)
NCOL = 6
RECHECK = ("add up", "reach for someone's wallet")


def _L(f):
    return json.load(open(OUT / f, encoding="utf-8"))


def collect():
    """戻り={set名: {key: {gloss: [cellname...]}}}。"""
    A = T5.all_kps5()
    nc = R5.new_cells()
    st = json.load(open(T5.RD / "TRIAL_04/strata_04.json", encoding="utf-8"))
    s2 = [k for k in st["trial_set"] if k not in T5.R_KEYS]
    held = [k for k in T5.heldout_order() if any(r["key"] == k for r in nc.values())][:10]
    out = {"S2": {}, "R": {}, "H": {}}
    rc = R5.ref_cells(set(s2))
    for k in s2:
        cells = collections.defaultdict(list)
        for (arm, kk, rep), r in nc.items():
            if arm == "X2p" and kk == k and rep == 1:
                cells[r["gloss"]].append("X2p/rep1")
        for (arm, kk, rep), g in rc.items():
            if arm == "B0_t4" and kk == k:
                cells[g].append("B0_t4/rep%d" % rep)
        x = {g for g, c in cells.items() if any(s.startswith("X2p") for s in c)}
        b = {g for g, c in cells.items() if any(s.startswith("B0") for s in c)}
        if x and not (x & b):          # X2p文字列がB0のどのrepとも異なる = 変化
            out["S2"][k] = dict(cells)
    for name, keys, reps in (("R", T5.R_KEYS, (1, 2, 3)), ("H", held, (1,))):
        for k in keys:
            cells = collections.defaultdict(list)
            for (arm, kk, rep), r in nc.items():
                if kk == k and arm in ("B0", "X2p") and rep in reps:
                    cells[r["gloss"]].append("%s/rep%d" % (arm, rep))
            x = {g for g, c in cells.items() if any(s.startswith("X2p") for s in c)}
            b = {g for g, c in cells.items() if any(s.startswith("B0") for s in c)}
            if x and not (x == (x & b)):   # X2p文字列のうちB0に無いものがある
                out[name][k] = dict(cells)
    return A, out


HEAD = """# fable_blind_06: 二重判定(第二評価者)用 盲検表(委任_30。OPUS_REVIEW_08 OF-KP2-03。**arm・既存ラベルは伏せてある**)

評価者: Opus または新しいcontextのFable。**判定してから** `fable_blind_06_key.json` を開く(開くのは集計時のみ)。

## 判定基準(明示。『範囲を超えた持ち込み=THIN』を含む)
行=Key Phrase(key_phrase と、それが使われた本文の文)。列=この表で見る日本語glossの**文字列**(同じ文字列は1列)。各セルに次のいずれかを付ける。
- **PASS**: 学習カードに『key_phrase = gloss』と書いたとき、**key_phrase全体の意味**を過不足なく表している。本文での語義(字義か比喩か)に合っている。
- **THIN**: 意味は概ね合うが、次のいずれかがある。
  1. **範囲を超えた持ち込み**: key_phraseに含まれていない、本文側の**否定・主語・時制・具体的な対象・場面**がglossに入っている(例の型: key_phrase『work out』= gloss『うまくいかなかった』[否定と過去を本文から持ち込み])。
  2. 意味が狭い/ずれている(key_phraseの一側面だけ、または別の語義方向へ移動)。
  3. 説明文的で長く、key_phraseと同じ品詞・長さの句になっていない。
- **FAIL**: key_phraseの意味と違う、または重要な語の意味が欠ける。
- **FAIL_LIT**: 字義(語の置換)の像のままで、本文での意味が日本語読者に伝わらない。
- 迷ったら**厳しい側**(THIN)に倒し、理由を1語(持ち込み:否定/主語/時制/対象/場面、狭い、説明的、字義)でメモする。
- **持ち込みテスト**: 『key_phrase = gloss』と学習カードに書いたとき、key_phrase単体では言えない内容(否定・過去・特定の人物/物/場面)が入っていないかを必ず確認する。
- 一次評価(Fable、委任_23〜29)と**同じ4ラベル**だが、本表では上記の『持ち込み』を明示的にTHINとして扱う点が異なる(一次評価の水準が緩い方向に揺れたことの確認が目的)。

## 再照合対象(Opus条件Cレビューの指摘。通常の判定に加え、理由を必ず書く)
- `add up`: 本文は 'that doesn't add up'。glossに否定が含まれる文字列について、key_phrase『add up』の範囲か否かを判断する。
- `reach for someone's wallet`: 過去のユーザー判断は『見出し語に忠実な訳(人の財布に手を伸ばす)でPASS』。本表の基準(本文での語義を選ぶが範囲はkey_phraseだけ)で、各文字列をどう評価するかと、過去判断と矛盾するかを書く。

## 盲検表
"""


def cmd_build(a):
    A, out = collect()
    known, _ = R5.label_lookup(_L("fable_labels_05.json"), _L("fable_labels_05c.json"), _L("fable_labels_05d.json"), _L("fable_labels_05e.json"))
    rows = []
    for setname in ("S2", "R", "H"):
        for k, cells in out[setname].items():
            rows.append((setname, k, cells))
    random.Random("blind06").shuffle(rows)
    lines = [HEAD, "| # | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(NCOL)) + " |", "|---|---|---|" + "---|" * NCOL]
    keymap, n = {}, 0
    for setname, k, cells in rows:
        kp = A[k]
        strs = list(cells)
        random.Random("blind06-" + k).shuffle(strs)
        strs = strs[:NCOL]
        n += 1
        cols = {}
        for i, g in enumerate(strs):
            prior = known.get((kp["key"], kp["sent"], g))
            cols[chr(65 + i)] = dict(gloss=g, cells=cells[g], fable_label=prior)
        keymap[str(n)] = dict(key=k, set=setname, cols=cols, recheck=k in RECHECK)
        mark = " **[再照合対象]**" if k in RECHECK else ""
        lines.append("| %d | %s%s | %s | %s |" % (n, kp["key"], mark, kp["sent"].replace("|", "/")[:200], " | ".join(g.replace("|", "/") for g in strs + [""] * (NCOL - len(strs)))))
    (OUT / "fable_blind_06.md").write_text(NL.join(lines) + NL, encoding="utf-8")
    (OUT / "fable_blind_06_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    ncell = sum(len(v["cols"]) for v in keymap.values())
    nx = sum(1 for v in keymap.values() for c in v["cols"].values() if any(s.startswith("X2p") for s in c["cells"]))
    print("rows", n, "sets", dict(collections.Counter(v["set"] for v in keymap.values())), "strings", ncell, "X2p strings", nx,
          "既存Fableラベル有", sum(1 for v in keymap.values() for c in v["cols"].values() if c["fable_label"]))


def cmd_agree(a):
    """第二評価者ラベルとFable一次ラベルの一致率。X2p文字列について: 厳密一致・PASS/非PASS一致・厳しい/緩い方向、Stage 2の基準(PASS->THIN<=2)の再計算(第二評価者ラベルのみ)。"""
    labels = json.load(open(a.labels, encoding="utf-8"))
    keymap = json.load(open(OUT / "fable_blind_06_key.json", encoding="utf-8"))
    rank = {"PASS": 2, "THIN": 1, "FAIL": 0, "FAIL_LIT": 0}
    ex = co = tot = stricter = looser = 0
    diffs = []
    for rk, v in keymap.items():
        for col, c in v["cols"].items():
            l2 = labels.get("%s:%s" % (rk, col))
            l1 = c["fable_label"]
            if l2 is None or l1 is None:
                continue
            tot += 1
            ex += l1 == l2
            co += (l1 == "PASS") == (l2 == "PASS")
            if rank[l2] < rank[l1]:
                stricter += 1
            elif rank[l2] > rank[l1]:
                looser += 1
            if l1 != l2:
                diffs.append((v["key"], c["gloss"], c["cells"], l1, l2))
    print("比較可能な文字列 %d: 厳密一致 %d (%.0f%%), PASS/非PASS一致 %d (%.0f%%), 第二評価者が厳しい %d / 緩い %d" % (tot, ex, 100 * ex / max(1, tot), co, 100 * co / max(1, tot), stricter, looser))
    for d in diffs:
        print("  不一致:", d)
    # Stage 2 strict 再計算(第二評価者ラベルのみ。B0_t4の良い方repに対するX2pの悪化)
    s2 = collections.defaultdict(dict)
    for rk, v in keymap.items():
        if v["set"] != "S2":
            continue
        for col, c in v["cols"].items():
            l2 = labels.get("%s:%s" % (rk, col))
            if l2 is None:
                continue
            for cell in c["cells"]:
                s2[v["key"]][cell] = l2
    p2t = p2f = 0
    for k, d in s2.items():
        x = d.get("X2p/rep1")
        b = [rank[d[c]] for c in d if c.startswith("B0")]
        if x is None or not b:
            continue
        best = max(b)
        if best == 2 and rank[x] == 1:
            p2t += 1
        if best >= 1 and rank[x] == 0:
            p2f += 1
    print("Stage 2(変化した%dKPのみ、第二評価者ラベル): B0良い方rep基準で PASS->THIN %d / (PASS|THIN)->FAIL系 %d  (基準: PASS->THIN<=2, PASS->FAIL 0)" % (len(s2), p2t, p2f))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--labels", default="")
    a = ap.parse_args()
    {"build": cmd_build, "agree": cmd_agree}[a.cmd](a)
