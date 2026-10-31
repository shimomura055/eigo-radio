import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8")); conds = list(m["by_cond"])
print("| 条件 | 改善 | 悪化(率) | 悪化の重大度(M側) | G1 | G2 | 表示OK/軽/中/重大/非表示 | fail-closed part/文 | call比 | 実費(円) 対A | call中央値wall比 | 追加費/記事(円) | 1回目訳のみ 改善/悪化 | 混入候補 | 訳語種類(M/A平均) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in conds:
    b = m["by_cond"][c]; t = b["table_sentences"]
    tab = "/".join(str(t.get(k, 0)) for k in ("表示正しい(OK)", "表示正しい(軽)", "表示誤り(中)", "表示誤り(重大)", "非表示(fail-closed)"))
    if c == "A":
        print(f"| A(基準) | - | - | - | - | - | {tab} | {b['fail_closed_parts']}/{b['fail_closed_sentences']} | 1.0 | {b['cost_jpy']} | 1.0 | - | - | - | - |")
        continue
    mm = m["cmp"][f"{c}_vs_A"]["main"]; fo = m["cmp"][f"{c}_vs_A__first_translation_only"]["main"]
    print(f"| {c} | {mm['imp']} | {mm['worse']} ({mm['worse_rate']*100:.1f}%) | {mm['worse_by_Msev']} | {mm['G1_A_le1_to_M3']} | {mm['G2_worse_to_ge2']} | {tab} | {b['fail_closed_parts']}/{b['fail_closed_sentences']} | {b['G4_calls_ratio']} | {b['cost_jpy']} ({b['C1_total_cost_ratio']}) | {b['T1_call_wall_median_ratio']} | {b['C1_extra_cost_per_article_jpy']} | {fo['imp']}/{fo['worse']} | {m['mix_candidates_counts'].get(c, '-')} | {b.get('B1b_M_mean', '-')}/{b.get('B1b_A_mean', '-')} |")
if "PUB_vs_A" in m["cmp"]:
    p = m["cmp"]["PUB_vs_A"]["main"]; print(f"\n公開版(A'')対A: n={p['n']} 改善{p['imp']} 悪化{p['worse']}({p['worse_rate']*100:.1f}%) G2={p['G2_worse_to_ge2']}")
