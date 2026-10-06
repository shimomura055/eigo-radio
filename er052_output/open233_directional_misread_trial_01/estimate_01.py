"""委任_02 見積script(¥0、API不使用)。dry-runのprompt群から構成別low/mid/highを算出し estimate_01.md を書く。"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import er052_open233_directional_trial_01 as T

D = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(D, "testset_01.json"), encoding="utf-8"))["items"]
IN, OUT = 10.7, 81.7  # 円/1M tokens(01a逆算, gpt-6-luna)
OUT_TOK = {"low": 300, "mid": 650, "high": 1500}
MULT = {"gpt-6-luna": (1, 1), "gpt-5.6-luna": (2, 2.4), "gpt-5.6-sol": (50, 60)}  # (in倍率, out倍率) vs gpt-6-luna単価USD比


def toks(s):
    na = sum(1 for c in s if ord(c) > 127)
    return na * 0.8 + (len(s) - na) / 4.0


def collect(cfg):
    rn = T.Runner(cfg, dry_run=True, ledger_repeat=3, model_article=("dummy-model-B" if cfg == "split_blind" else None))
    for r in rows:
        rn.process_row(r)
    led = [toks(p) for p in rn.prompts if p.startswith("次のfact block") or "【対照群】" in p]
    art = [toks(p) for p in rn.prompts if p.startswith("次の文は対象X")]
    return led, art


def cost(tk, model, out_tok):
    mi, mo = MULT[model]
    return sum(t * IN * mi / 1e6 + out_tok * OUT * mo / 1e6 for t in tk)


res, lines = {}, []
for cfg in ("same_blind", "same_nonblind", "split_blind"):
    led, art = collect(cfg)
    res[cfg] = (len(led), len(art), sum(led) / max(len(led), 1), sum(art) / max(len(art), 1))
    lines.append(f"- {cfg}: Ledger/両側call {len(led)}件(平均入力約{res[cfg][2]:.0f}tok)、記事側call {len(art)}件(平均入力約{res[cfg][3]:.0f}tok)")
tab = {}
for lvl, ot in OUT_TOK.items():
    led_sb, art_sb = collect("same_blind")
    led_nb, _ = collect("same_nonblind")
    tab[lvl] = {"same_blind": cost(led_sb + art_sb, "gpt-6-luna", ot), "same_nonblind": cost(led_nb, "gpt-6-luna", ot)}
    for m in ("gpt-5.6-luna", "gpt-5.6-sol"):
        tab[lvl]["split_ledger_" + m] = cost(led_sb, m, ot)  # Ledger側30call(記事側は再利用で0)
    tab[lvl]["split_ledger_5calls_x1_gpt-5.6-sol"] = cost(led_sb[:5], "gpt-5.6-sol", ot) 
md = ["# estimate_01(委任_02、¥0、API不使用)", "",
      "前提: 入力tokは文字種近似(非ASCII 0.8tok/字+ASCII 1/4tok)、単価はgpt-6-luna逆算(入力¥10.7/1M・出力¥81.7/1M)。"
      "effort=medium想定の出力(推論込み)tok/call: low300/mid650/high1500。5.6-luna(出典DECISION_LOG_HISTORY.md:5893 入力$0.2/出力$1.2)=単価2.0倍/2.4倍、"
      "5.6-sol($5/$30)=50倍/60倍で換算。", "", "## call構成", *lines, "", "## 費用(円)", "",
      "| 構成 | low | mid | high |", "|---|---|---|---|"]
for k in ("same_blind", "same_nonblind", "split_ledger_gpt-5.6-luna", "split_ledger_gpt-5.6-sol",
          "split_ledger_5calls_x1_gpt-5.6-sol"):
    md.append(f"| {k} | " + " | ".join(f"{tab[l][k]:.2f}" for l in OUT_TOK) + " |")
core = {l: tab[l]["same_blind"] + tab[l]["same_nonblind"] + tab[l]["split_ledger_gpt-5.6-luna"] for l in OUT_TOK}
core_sol = {l: tab[l]["same_blind"] + tab[l]["same_nonblind"] + tab[l]["split_ledger_gpt-5.6-sol"] for l in OUT_TOK}
md += ["", "## 合計", "", "| 案 | low | mid | high |", "|---|---|---|---|",
       "| 3構成(split=gpt-5.6-luna, Ledger 30call) | " + " | ".join(f"{core[l]:.2f}" for l in OUT_TOK) + " |",
       "| 3構成(split=gpt-5.6-sol, Ledger 30call) | " + " | ".join(f"{core_sol[l]:.2f}" for l in OUT_TOK) + " |", ""]
md.append(f"判定: mid={core['mid']:.2f}円(5.6-luna案) / {core_sol['mid']:.2f}円(sol案、予算超過なら不可)。"
          f"mid<=15円={'OK(実行)' if core['mid'] <= 15 else 'STOP'}。")
open(os.path.join(D, "estimate_01.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md))
