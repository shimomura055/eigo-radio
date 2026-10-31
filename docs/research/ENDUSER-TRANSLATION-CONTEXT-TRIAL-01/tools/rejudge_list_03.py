# Fable再裁定リスト作成(TRIAL_PLAN_02 §4 M-8(3)): 10%乱数 + 採点3全件 + 最終候補のA対M改善/悪化 + G2寄与(M側採点>=2) 。ブラインド抽出シートと一次採点の写しを出す。
import json, os, random, re, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out_md = ["# FABLE_REJUDGE_LIST_02(Fable再裁定が必要な項目の一覧、API 0)\n", "ブラインド再裁定用抽出シート(方式名なし)と、一次裁定(実行層Sonnet)の採点写しを対にして出す。再裁定の食い違いは保守側(M-8(2))で扱う。\n"]
for sp, d, final in (("dev", "ev05_dev", "EV"), ("heldout", "ev06_heldout", "EV")):
    sheet = json.load(open(os.path.join(D, d, f"sheet_{sp}.json"), encoding="utf-8")); key = json.load(open(os.path.join(D, d, f"sheet_key_{sp}.json"), encoding="utf-8"))
    gfile = os.path.join(D, d, f"grades_{sp}.txt" if sp == "dev" else "grades_heldout.txt")
    gr = {}
    for ln in open(gfile, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        t = ln.split(); gr[t[0]] = {m.group(1): int(m.group(2)) for x in t[1:] for m in [re.match(r"([A-Z])([0-3])", x)] if m}
    sid2row = {v["sid"]: r for r, v in key.items()}
    detail = json.load(open(os.path.join(D, d, f"cmp_detail_{sp}.json"), encoding="utf-8"))
    rows = {}
    def add(r, why):
        rows.setdefault(str(r), set()).add(why)
    for r, v in key.items():
        for L, labs in v["map"].items():
            g = gr.get(r, {}).get(L, 0)
            if g == 3: add(r, "採点3(重大)")
            if g >= 2 and any(lab.endswith(":final") for lab in labs): add(r, "採点2以上(G2寄与候補)")
    for M in ([final] if final in detail else []):
        for e in detail[M]:
            add(sid2row[e["sid"]], f"最終候補{final}対Aの{'改善' if e['status']=='imp' else '悪化'}")
    rng = random.Random(20261031 + (1 if sp == "heldout" else 0))
    allr = sorted(key, key=int)
    for r in rng.sample(allr, max(1, round(len(allr) * 0.1))):
        add(r, "10%乱数抽出")
    sel = sorted(rows, key=int)
    with open(os.path.join(D, d, f"rejudge_sheet_{sp}.txt"), "w", encoding="utf-8") as f:
        for r in sel:
            s = sheet[int(r) - 1]
            f.write(f"#{r} EN: {s['en']}\n   (ctx: {(s['prev'][-1][:90] + '｜') if s['prev'] else ''}…{('｜' + s['next'][0][:90]) if s['next'] else ''})\n")
            for L, t in s["variants"].items():
                f.write(f"  {L}: {t}\n")
    with open(os.path.join(D, d, f"rejudge_primary_grades_{sp}.txt"), "w", encoding="utf-8") as f:
        f.write("# 一次裁定(実行層Sonnet)の採点。省略した文字は0=OK。形式: <row> <文字><0-3>[類型]\n")
        for ln in open(gfile, encoding="utf-8"):
            if ln.startswith("#") or not ln.strip():
                continue
            if ln.split()[0] in rows:
                f.write(ln)
    by = {}
    for r, ws in rows.items():
        for w in ws:
            by.setdefault(w, []).append(int(r))
    out_md.append(f"\n## {sp}(総行{len(allr)}、再裁定対象{len(sel)}行 = {len(sel)/len(allr)*100:.0f}%)\n- 抽出シート: `{d}/rejudge_sheet_{sp}.txt` / 一次採点: `{d}/rejudge_primary_grades_{sp}.txt`(全採点: `{os.path.basename(gfile)}`、対応表 `sheet_key_{sp}.json`は再裁定後に開く)\n")
    for w, rs in sorted(by.items()):
        out_md.append(f"- {w}: {len(rs)}行 = {sorted(rs)}\n")
# B1(a)
out_md.append("\n## B1(a)(5項目×A3回・M3回の全variant)\n- `ev07_b1a/b1a_sheet.json`(ブラインド)・`b1a_grades.txt`(一次採点)・`b1a_key.json`(再裁定後)。合否に効く全5行を再裁定対象とする。\n")
open(os.path.join(D, "FABLE_REJUDGE_LIST_02.md"), "w", encoding="utf-8").write("".join(out_md))
print("".join(out_md))
