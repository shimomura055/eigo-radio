# -*- coding: utf-8 -*-
"""委任_07: 最終集計(API 0)→ er112_output/kp_gm_trial_02/summary_02.json と Fable目視用サンプル。"""
import json, sys, random, collections, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_report_02 as R, er112_kp_gm_trial_02 as T, er112_kp_gm_judge_01 as jd
OUT = T.OUT
V = R.verdicts(["sonnet"]); A = T.kpset(); res = T.load_res()
hard = [k for k, v in A.items() if v["tier"] == "hard"]
n30 = open(OUT / "e4_normal30.txt", encoding="utf-8").read().split("|")
sub = hard + n30
def p3(x):
    s = x[1]["sonnet"]; return s["sense_ok"] == 1 and s["core"] == 1 and s["single"] == 1
summ = {}
for arm in ["E0@G0", "E0@prod", "E1", "E1c", "E4", "E0@G2", "E0@G3"]:
    ks = [k for k in sub if (arm, k, 1) in V]
    if not ks: continue
    f = {fld: sum(1 for k in ks if V[(arm, k, 1)][1]["sonnet"][fld] == jd.GOOD[fld]) for fld in ("sense_ok", "core", "single", "over_general")}
    pas = sum(1 for k in ks if p3(V[(arm, k, 1)])); lo, hi = R.wilson(pas, len(ks))
    cf = len(ks) - f["core"]; clo, chi = R.wilson(cf, len(ks))
    summ[arm] = dict(n=len(ks), pass3=pas, pass3_ci=[round(lo, 2), round(hi, 2)], sense_ok=f["sense_ok"], core_ok=f["core"], core_fail_rate=round(cf / len(ks), 3), core_fail_ci=[round(clo, 2), round(chi, 2)], single=f["single"], over_general_ok=f["over_general"])
print(json.dumps(summ, ensure_ascii=False, indent=1))
json.dump(summ, open(OUT / "summary_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# Fable目視サンプル: E3/G行(ユニーク)から無作為20% + 2系統Judge不一致全行。armは伏せ、keyは別file。
RM = json.load(open(OUT / "row_map_02.json", encoding="utf-8"))
rows, _ = __import__("er112_kp_gm_judge_02").build()
cs, cl = jd.load_cache("sonnet"), jd.load_cache("sol")
rnd = random.Random(20261023)
ids = sorted(i for i in rows if rows[i]["kind"] in ("E3", "G", "P") and i in cs)
sample = set(rnd.sample(ids, max(1, len(ids) // 5)))
dis = set()
for i in ids:
    if i in cl:
        a, b = cs[i]["verdict"], cl[i]["verdict"]
        if any(a[f] != b[f] for f in jd.FIELDS[rows[i]["kind"]]): dis.add(i)
pick = sorted(sample | dis, key=lambda i: hashlib.sha256(i.encode()).hexdigest())
lines = ["# Fable目視サンプル(arm伏せ。arm対応は fable_sampling_key_02.json)", "", "無作為20%(seed固定)+2系統Judge不一致全行。各行のJudge判定を併記(悪い側の項目を提示)。", ""]
for n, i in enumerate(pick, 1):
    r = rows[i]
    txt = r.get("explanation") or r.get("gloss") or (r.get("gloss_ja", "") + " || " + r.get("explanation_en", ""))
    v = cs[i]["verdict"]; bad = [f for f in jd.FIELDS[r["kind"]] if v[f] != jd.GOOD[f]]
    vs = ""
    if i in cl:
        vb = cl[i]["verdict"]; bs = [f for f in jd.FIELDS[r["kind"]] if vb[f] != jd.GOOD[f]]; vs = " / Sol悪側=%s" % (",".join(bs) or "なし")
    lines.append(f"{n}. [{r['kind']}] {r['key_phrase']} | 文: {r['source_sentence'][:80]} | {txt} | Sonnet悪側={','.join(bad) or 'なし'}{vs}{' [Judge不一致]' if i in dis else ''}")
(OUT / "fable_sampling_list_02.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
json.dump({str(n): RM.get(i) for n, i in enumerate(pick, 1)}, open(OUT / "fable_sampling_key_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("sample", len(pick), "disagree", len(dis), "of", len(ids))
