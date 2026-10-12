# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01: 比較ページ生成(静的HTML、API無し、音声なし)。"""
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er059_output", "melos_sol_b3z_trial_01")
PAGE = os.path.join(ROOT, "user_test", "family_z_melos_sol_b3z_01", "index.html")
SEED = os.path.join(ROOT, "er018_output", "fiction_external_seed_selection_criteria_trial_02", "stories", "03_japanese_lit_2")
E = html.escape


def rd(p):
    return open(p, encoding="utf-8").read()


def jl(p):
    return json.load(open(p, encoding="utf-8"))


def story_html(t):
    out = []
    for para in t.strip().split("\n\n"):
        s = para.strip()
        if s.startswith("#"):
            out.append(f"<h4>{E(s.lstrip('# ').strip())}</h4>")
        else:
            out.append(f"<p>{E(s).replace(chr(10), '<br>')}</p>")
    return "\n".join(out)


def main():
    pc = jl(f"{OUT}/page_content_01.json")
    met = jl(f"{OUT}/metrics_01.json")["metrics"]
    ev = jl(f"{OUT}/eval_summary_01.json")["summary"]
    c2, c3 = jl(f"{OUT}/m2_sol_only/chain_meta.json"), jl(f"{OUT}/m3_sol_b3z/chain_meta.json")
    b3m = jl(f"{OUT}/m3_sol_b3z/b3z_meta_attempt1.json")
    brief_md = rd(f"{OUT}/m3_sol_b3z/b3z_brief.md")
    brief = jl(f"{OUT}/m3_sol_b3z/b3z_brief.json")
    t1 = rd(f"{SEED}/story.md")
    t2, t3 = rd(f"{OUT}/m2_sol_only/r2.md"), rd(f"{OUT}/m3_sol_b3z/r2.md")
    cost2, cost3 = sum(m["cost_jpy"] for m in c2), sum(m["cost_jpy"] for m in c3) + b3m["cost_jpy"]
    sec2, sec3 = sum(m["elapsed_sec"] for m in c2), sum(m["elapsed_sec"] for m in c3) + b3m["elapsed_sec"]
    gen = jl(f"{OUT}/gen_summary.json")
    items = [("hook", "引き込み"), ("development", "展開"), ("emotion", "感情"), ("central_story", "中心Story"), ("ending", "結末")]
    names = {"M1": "(1) 従来方式", "M2": "(2) Sol変更のみ", "M3": "(3) Sol+B3Z"}

    def row(cells, th=False):
        tag = "th" if th else "td"
        return "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"

    h = []
    h.append("""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>走れメロス 3方式比較 (Trial)</title><style>
body{font-family:sans-serif;max-width:1200px;margin:1em auto;padding:0 1em;line-height:1.55;color:#222}
table{border-collapse:collapse;margin:.6em 0;font-size:.92em}td,th{border:1px solid #aaa;padding:4px 8px;vertical-align:top}th{background:#eee}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.col{border:1px solid #ccc;padding:8px 12px;background:#fafafa}
.warn{background:#fff3cd;padding:6px 10px;border:1px solid #e0c36a}h4{margin:.4em 0}details{margin:.5em 0}pre{white-space:pre-wrap;background:#f4f4f4;padding:8px}
@media(max-width:900px){.cols{grid-template-columns:1fr}}</style></head><body>""")
    h.append("<h1>『走れメロス』3方式比較 (Trial)</h1>")
    h.append('<p class="warn">FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 / 2026-10-12。Trial(Production未採用、音声なし、テキスト生成と品質比較のみ)。'
             '評価はAI(gpt-6-luna、方式を伏せたN=2)と機械指標によるもので、<b>ユーザー実読評価ではありません</b>。N=2で差は小さく、有意差とは言えません。</p>')
    h.append("<h2>1. 方式と工程</h2><table>")
    h.append(row(["方式", "使用モデル", "工程", "費用(円)", "処理時間"], True))
    h.append(row([names["M1"], "gpt-5.6-luna (effort=high)", "Seed -> Story 単発1call(既存Trial成果物を再利用。R0/R1/R2/B3は存在しない)", "既存(約1.8円は全体10call分の既存記録)", "-"]))
    h.append(row([names["M2"], "gpt-6.1-sol (effort=high)", "R0(Seed->Story) -> R1(より面白く) -> R2(さらに) = 3 call", f"{cost2:.2f}", f"{sec2:.0f}秒"]))
    h.append(row([names["M3"], "gpt-6.1-sol (effort=high)", "B3Z Brief -> R0(Seed+Brief) -> R1 -> R2 = 4 call", f"{cost3:.2f}", f"{sec3:.0f}秒"]))
    h.append("</table><p>(2)(3)は同一のR0/R1/R2 Prompt・モデル・effortで、差分はB3Z Brief有無のみ。「GPT-6 Sol」はroutingに登録された最新のgpt-6.1-solと解釈(gpt-6-solは未登録)。"
             f"評価(gpt-6-luna 2call)費用約0.49円。生成合計{gen['spent_jpy']:.2f}円+評価0.49円=約{gen['spent_jpy'] + 0.49:.2f}円(上限50円)。</p>")
    h.append("<h2>2. 英語Story全文(並列)</h2><div class='cols'>")
    for k, t in (("M1", t1), ("M2", t2), ("M3", t3)):
        h.append(f"<div class='col'><b>{names[k]}</b> ({met[k]['words_body']}語)\n{story_html(t)}</div>")
    h.append("</div>")
    h.append("<h2>3. AI評価(5項目、1〜5、N=2平均)</h2><table>")
    h.append(row(["方式"] + [n for _, n in items] + ["平均", "順位(rep1,rep2)"], True))
    for k in ("M1", "M2", "M3"):
        h.append(row([names[k]] + [str(ev[k][i]) for i, _ in items] + [str(ev[k]["total_avg"]), ",".join(map(str, ev[k]["ranks"]))]))
    h.append("</table><p>1〜5点(5=優れる)。順位は1位が最良。傾向: (2)は引き込み・展開、(3)は感情・結末、(1)は中心Story維持が高い。</p>")
    h.append("<h3>機械指標</h3><table>")
    h.append(row(["指標", names["M1"], names["M2"], names["M3"]], True))
    for lab, key in (("語数(本文)", "words_body"), ("文数", "sentences"), ("平均語数/文", "avg_words_per_sentence"), ("最長文(語)", "max_sentence_len"),
                     ("18語超の文", "sentences_over_18"), ("長語率(9字以上, %)", "long_word_rate_pct")):
        h.append(row([lab] + [str(met[k][key]) for k in ("M1", "M2", "M3")]))
    h.append(row(["本文中のmarkdown記号"] + [E(", ".join(met[k]["markdown_symbols_in_body"]) or "なし") for k in ("M1", "M2", "M3")]))
    h.append("</table><p>全方式A2基準(平均11語以下・最長18語以下・280〜420語)内。(2)(3)は(1)より更に短文化しておりA2難化はありません。</p>")
    h.append("<h3>原作の重要場面との対応(AI=Claudeの手動確認)</h3><table>")
    h.append(row(["場面", names["M1"], names["M2"], names["M3"]], True))
    for r in pc["scene_table"]:
        h.append(row([E(x) for x in r]))
    h.append("</table>")
    h.append("<h3>(2)と(3)の具体的な差(文単位)</h3><table>")
    h.append(row(["観点", "(2) Sol変更のみ", "(3) Sol+B3Z", "所見"], True))
    for r in pc["diff_examples"]:
        h.append(row([E(x) for x in r]))
    h.append("</table>")
    h.append("<h3>R0 -> R1 -> R2 の変化</h3><table>")
    h.append(row(["区間", "語数・同一文数", "内容"], True))
    for r in pc["r_changes"]:
        h.append(row([E(x) for x in r]))
    h.append("</table>")
    h.append("<h2>4. B3Z Brief 全文((3)のR0入力に追加)</h2>")
    h.append(f"<details open><summary>brief_text</summary><pre>{E(brief['brief_text'])}</pre></details>")
    h.append("<details><summary>B3Z 5項目の構造化出力(central_conflict / key_scenes / engaging_progression / climax_and_aftertaste / preservation_conditions)</summary>"
             f"<pre>{E(json.dumps(brief, ensure_ascii=False, indent=2))}</pre></details>")
    h.append("<h2>5. (2)(3)のR0 / R1 / R2 全文(折りたたみ)</h2>")
    for lab, d in (("(2) Sol変更のみ", "m2_sol_only"), ("(3) Sol+B3Z", "m3_sol_b3z")):
        for r in ("r0", "r1", "r2"):
            h.append(f"<details><summary>{lab} {r.upper()}</summary><pre>{E(rd(f'{OUT}/{d}/{r}.md'))}</pre></details>")
    h.append("<details><summary>R0 Prompt((2): Seedのみ / (3): Seed+Brief)</summary>"
             f"<pre>{E(rd(f'{OUT}/m3_sol_b3z/r0_prompt.txt'))}</pre></details>")
    h.append("<details><summary>R1/R2 Prompt(共通)</summary>"
             f"<pre>{E(rd(f'{OUT}/m2_sol_only/r1_prompt.txt')[-420:])}</pre></details>")
    h.append("<h2>6. 暫定所見(Production採用提案ではない)</h2><ul>")
    for c in pc["conclusion"]:
        h.append(f"<li>{E(c)}</li>")
    h.append("</ul><p>残る判断(ユーザー): 実読評価、「GPT-6 Sol」=gpt-6.1-solの確認、Sol・B3Z・R0/R1/R2工程をFamily Zへ採用するか(未採用。Production Writer/Prompt/Routingは変更していません)。</p>")
    h.append("<p>証跡: er059_output/melos_sol_b3z_trial_01/ (BASELINE_01.md, B3Z_DESIGN_01.md, COST_ESTIMATE_01.md, metrics_01.json, eval/, eval_summary_01.json)</p></body></html>")
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    open(PAGE, "w", encoding="utf-8", newline="").write("\n".join(h))
    print("written", PAGE, len("\n".join(h)))


if __name__ == "__main__":
    main()
