# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01b: PROMPT_TRIAL_01.md を narr_template.md + results から組み立てる (API 0)
import os, sys, json, hashlib
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, BASE)
import nuance_trial_01 as nt
from nuance_prompt_v2 import PROMPT_V2
tpl = open(sys.argv[1], encoding="utf-8").read()
def L(f): return json.load(open(os.path.join(OUT, f), encoding="utf-8"))
v1 = L("results_v1.json"); v1c = L("results_v1_control.json"); v2 = L("results_v2.json"); probe = L("judge_probe_01.json")
usage = [json.loads(l) for l in open(os.path.join(OUT, "usage_log_01.jsonl"), encoding="utf-8") if l.strip()]
data = L("prompt_trial_01.json")
T = nt.load_targets()
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
cs = lambda pre, f=None: round(sum(u["cost_jpy"] for u in usage if u["tag"].startswith(pre) and (f is None or f(u["tag"]))), 4)
real = lambda t: "control" not in t
rows = []
for k, t in T.items():
    rows.append(f"| {t['article']} {t['level']} ({t['family']}) | {len(t['body'])}字 | " + " / ".join(x['expr'] for x in t['kp']) + f" | {t['basis']['status']}: {t['basis']['source_path']} |")
def cand_block(ver, rs):
    out = []
    for k, r in rs.items():
        c = r.get("candidate_raw")
        out.append(f"#### {ver} / {r['article']} {r['level']} ({k})")
        if not c:
            out.append(f"- 候補: 0件。理由: {r.get('no_candidate_reason')}")
            rj = r.get("rejected_candidates") or []
            out.append("- 検討して外した候補: " + ("; ".join(f"{x['expression']} ({x['reason']}: {x.get('note')})" for x in rj) if rj else "なし")); out.append(""); continue
        s1 = r["stage1_structural"]; s2 = r["stage2_llm"]
        out += [f"- 表現: **{c['expression']}**", f"- 焦点: {c['focus']}", f"- 本文引用: {c['quote_en']}", f"- 和訳: {c['quote_ja']}", f"- 解説({r['explanation_len']}字): {c['explanation_ja']}",
                f"- KP/Wordと焦点が異なる理由(生成時): {c.get('differs_from_kp_word_ja')}", f"- 価値の理由(生成時): {c.get('learning_value_reason_ja')} / 自己評価={c.get('learning_value_self_rating')}"]
        if c.get("criteria_check"): out.append(f"- criteria_check: {json.dumps(c['criteria_check'], ensure_ascii=False)}")
        out.append(f"- 重複検査: 段1構造={s1['verdict']}{(' ' + json.dumps(s1['matched'], ensure_ascii=False)) if s1['matched'] else ''} / 段2LLM={s2['verdict']} / 引用逐語={'OK' if r['quote_verbatim'] else 'NG'} → **最終 {r['final_overlap_verdict'].upper()}**")
        out.append(f"  - 段2理由: {s2['reason']}")
        for p in s2.get("per_item") or []: out.append(f"  - {p.get('item')}: same_focus={p.get('same_focus')} ({p.get('note')})")
        rj = r.get("rejected_candidates") or []
        out.append("- 検討して外した候補: " + ("; ".join(f"{x['expression']} ({x['reason']}: {x.get('note')})" for x in rj) if rj else "なし")); out.append("")
    return "\n".join(out)
cands = "### 6-1. v1\n\n" + cand_block("v1", v1) + "\n#### v1 / control(人工平易文。診断用)\n\n" + cand_block("v1", v1c) + "\n### 6-2. v2\n\n" + cand_block("v2", v2)
pt = ["| probe | 対象 | 段1構造 | 段2LLM | 理由(段2) |", "|---|---|---|---|---|"]
for p in probe: pt.append(f"| {p['id']} | {p['target']} / 候補 `{p['candidate']['expression']}` | {p['stage1']['verdict']} | {p['stage2'].get('verdict')} | {p['stage2'].get('reason')} |")
ct = ["| tag | 入力tok | 出力tok | 推論tok | 秒 | 円 |", "|---|---|---|---|---|---|"]
for u in usage: ct.append(f"| {u['tag']} | {u['input_tokens']} | {u['output_tokens']} | {u['reasoning_tokens']} | {u['elapsed_sec']} | {u['cost_jpy']:.4f} |")
rep = {"TOTAL": f"{sum(u['cost_jpy'] for u in usage):.4f}", "V1_SET": f"{cs('v1_', real) / 4:.3f}", "V2_SET": f"{cs('v2_', real) / 4:.3f}", "SHA_V1": sha(nt.PROMPT_V1), "SHA_V2": sha(PROMPT_V2), "SHA_J": sha(nt.PROMPT_JUDGE),
       "PROMPT_V1": nt.PROMPT_V1.rstrip("\n"), "PROMPT_V2": PROMPT_V2.rstrip("\n"), "PROMPT_J": nt.PROMPT_JUDGE.rstrip("\n"), "TARGET_ROWS": "\n".join(rows),
       "TABLE_V1": open(os.path.join(OUT, "_table_v1.md"), encoding="utf-8").read(), "TABLE_V2": open(os.path.join(OUT, "_table_v2.md"), encoding="utf-8").read(),
       "PROBE_TABLE": "\n".join(pt), "CANDIDATES": cands, "COST_TABLE": "\n".join(ct), "C_V1": f"{cs('v1_', real):.4f}", "C_V1C": f"{cs('v1_control'):.4f}", "C_V2": f"{cs('v2_', real):.4f}",
       "C_V2C": f"{cs('v2_control'):.4f}", "C_PR": f"{cs('probe_'):.4f}", "NCALL": str(len(usage))}
for k, v in rep.items(): tpl = tpl.replace("{" + k + "}", v)
open(os.path.join(OUT, "PROMPT_TRIAL_01.md"), "w", encoding="utf-8", newline="\n").write(tpl)
os.remove(os.path.join(OUT, "_table_v1.md")); os.remove(os.path.join(OUT, "_table_v2.md"))
print("written", len(tpl), "chars; leftover placeholders:", [x for x in ("{TOTAL}", "{TABLE_V1}", "{CANDIDATES}") if x in tpl])
