# -*- coding: utf-8 -*-
"""比較ページ生成: user_test/writer_detective_trial_01/index.html(Baseline/A/B/C のAdvanced・Standard本文を並べる)。"""
import html
import json
import os
import sys

import er086_writer_detective_avoidance_trial_01_lib as lib
import er086_writer_detective_avoidance_trial_01_eval as ev

ROOT = lib.ROOT
OUT = os.path.join(ROOT, "user_test", "writer_detective_trial_01", "index.html")


def md_to_html(t):
    out = []
    for para in t.strip().split("\n\n"):
        para = para.strip()
        if para.startswith("# "):
            out.append(f"<h3>{html.escape(para[2:])}</h3>")
        elif para.startswith("## "):
            out.append(f"<h4>{html.escape(para[3:].splitlines()[0])}</h4><p>{html.escape(chr(10).join(para.splitlines()[1:]))}</p>")
        else:
            out.append(f"<p>{html.escape(para)}</p>")
    return "".join(out)


def main():
    root = os.path.join(ROOT, "er086_output", "writer_detective_avoidance_trial_01")
    base = os.path.join(ROOT, "er019_output", "middle_east_yemen_saudi", "run_mey_02")
    res = json.loads(lib.read_text(os.path.join(root, "eval", "results.json")))
    V = res["variants"]
    arts = {v: ev.load_variant(root, base, v) for v in V}
    ptxt = {"Baseline": "(追加指示なし。既存の完成記事)", **lib.PATTERN_TEXT}
    h = ["<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Writer Detective単語回避 Trial 比較</title>",
         "<meta name='viewport' content='width=device-width, initial-scale=1'><style>body{font-family:sans-serif;max-width:1500px;margin:1em auto;padding:0 1em;line-height:1.5}",
         "table{border-collapse:collapse;width:100%;margin-bottom:1.5em;table-layout:fixed}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left;font-size:.92em}",
         ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.pat{background:#eef6ff;padding:4px;font-size:.85em}h3{margin:.2em 0}p{margin:.4em 0}</style></head><body>",
         "<h1>Writer「Detective」単語回避 Trial 比較(FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01)</h1>",
         "<div class='note'>題材=中東記事E2E-02(同一Research/Ledger/B3入力を再利用)。Baseline=既存の完成記事、A/B/C=追加指示だけを変えてWriter(JA R0/R1/R2→Advanced英訳→Standard)を再生成。"
         "<b>Trial(TRIAL)であり、Production採用はユーザーの別途明示承認が必要です。</b>テキストのみ(音声は生成していません)。"
         "「detective」件数は大小文字不問・本文(Advanced/Standard、In one line含む)。</div>"]
    h.append("<table><tr><th>項目</th>" + "".join(f"<th>{v}</th>" for v in V) + "</tr>")

    def row(name, f):
        h.append(f"<tr><th>{name}</th>" + "".join(f"<td>{f(v)}</td>" for v in V) + "</tr>")
    row("追加指示(英文原文)", lambda v: f"<div class='pat'>{html.escape(ptxt[v])}</div>")
    row("detective件数 Adv/Std(JA R2『探偵』)", lambda v: f"{res['detective'][v]['Adv']['substring_ci']}/{res['detective'][v]['Std']['substring_ci']}(JA {res['detective'][v]['R2']['ja_tantei']})")
    row("類似語観測 Adv/Std(件数のみ)", lambda v: f"{res['similar_observation'][v]['Adv']['count']}/{res['similar_observation'][v]['Std']['count']}")
    if "entertainment" in res:
        row("Entertainment平均 Adv/Std(LLM,1-5)", lambda v: f"{res['entertainment']['Adv'][v]['mean']}/{res['entertainment']['Std'][v]['mean']}")
        row("LLM事実検査 new_major_error Adv/Std", lambda v: f"{res['fact_llm']['Adv'][v].get('new_major_error_count')}/{res['fact_llm']['Std'][v].get('new_major_error_count')}")
    row("Writer実費(JPY)", lambda v: str(res['qcd'][v]['writer_total_jpy']))
    h.append("</table>")
    for level, st, title in (("Adv", "Adv", "Advanced本文(b1b)"), ("Std", "Std", "Standard本文(a2)")):
        h.append(f"<h2>{title}</h2><table><tr>" + "".join(f"<th>{v}</th>" for v in V) + "</tr><tr>")
        for v in V:
            h.append("<td>" + md_to_html(arts[v][st] or "(なし)") + "</td>")
        h.append("</tr></table>")
    h.append("<h2>JA R2(参考、日本語原稿)</h2><table><tr>" + "".join(f"<th>{v}</th>" for v in V) + "</tr><tr>")
    for v in V:
        h.append("<td>" + "".join(f"<p>{html.escape(x)}</p>" for x in (arts[v]["R2"] or "(なし)").strip().split("\n\n")) + "</td>")
    h.append("</tr></table></body></html>")
    lib.write_text(OUT, "".join(h))
    print("wrote", OUT, os.path.getsize(OUT))


if __name__ == "__main__":
    sys.exit(main())
