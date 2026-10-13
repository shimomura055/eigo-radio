# before_after_02.json -> before_after_tables_02.md(自動生成、¥0)
import json
OUT = "er066_output/ja_asr_orthographic_equivalence_01"
d = json.load(open(f"{OUT}/before_after_02.json", encoding="utf-8"))
s = d["summary"]
L = []
L.append("# 事例別 Before/After 詳細 02(自動生成、er066_..._eval_02.py の出力 before_after_02.json から)\n")
L.append("列は累積: Stage 1=署名一致の表記差のみ / Stage 1'=署名スパンを同一不透明記号へ置換し既存`classify_ja_asr_match`へ委ねる(読み表不使用) / Stage 2=読み展開(Stage1+1'+2)。\n")
L.append("## A. コーパス(実転写1,002ペア)\n")
L.append("| 指標 | Before(現行Production) | Stage 1 | Stage 1' | Stage 2 |\n|---|---|---|---|---|")
a = s["after_pass"]; r = s["rescued_real_by_stage_cumulative"]
L.append(f"| 通過ペア数 | {s['before_pass']} | {a['S1']} | {a['S1P']} | {a['S2']} |")
L.append(f"| 実run由来の新規救済(累積) | 0 | {r['S1']} | {r['S1P']} | {r['S2']} |")
L.append(f"| 既存PASSの取消(Candidate E署名ガード) | -- | {s['vetoed_prod_pass']} | {s['vetoed_prod_pass']} | {s['vetoed_prod_pass']} |")
L.append(f"\n実run救済{s['rescued_real_total']}件の内訳: 不規則読み署名を含む(PASS_WITH_WARNING候補){s['rescued_real_with_warning']}件 / 含まない{s['rescued_real_without_warning']}件。真値確認済み(ユニーク組){s['truth_confirmed_unique_pairs']}組のみ。合成fixture由来の救済{s['rescued_synthetic_fixture']}件は別掲。\n")
L.append("## B. 新規救済された過去事例(全件)\n")
L.append("| 由来 | 段階 | 警告 | 真値 | 原稿(先頭) | ASR(先頭) |\n|---|---|---|---|---|---|")
for x in d["corpus"]:
    if (not x["before_pass"]) and x["verdict"] in ("TRIAL_NOTATION_MATCH", "TRIAL_READING_MATCH"):
        L.append(f"| {'実run' if x['is_real'] else '合成fixture'} | {x['stage']} | {'WARN' if x['warning'] else '-'} | {'確認済み' if x['truth_confirmed'] else '未確認'} | {x['canonical'][:34]} | {x['asr'][:34]} |")
L.append("\n## C. 正常例(合成%d件)の段階別通過\n" % s["positive_total"])
p = s["positive_after_pass_by_stage"]
L.append("| Before | Stage 1 | Stage 1' | Stage 2 | うちWARN(不規則読み署名) |\n|---|---|---|---|---|")
L.append(f"| {s['positive_before_pass']} | {p['S1']} | {p['S1P']} | {p['S2']} | {s['positive_warning']} |\n")
L.append("| 原稿 | ASR | 種別 | 救済段階 | WARN |\n|---|---|---|---|---|")
for x in d["positive"]:
    L.append(f"| {x['canonical']} | {x['asr']} | {x['kind']} | {x['stage'] or ('Production通過' if x['before_pass'] else x['verdict'])} | {'WARN' if x['warning'] else '-'} |")
L.append("\n## D. 敵対的反例(合成%d件=旧%d+新規%d)\n" % (s["negative_total"], s["negative_v1"], s["negative_v2"]))
n = s["negative_after_false_pass_by_stage"]
L.append("| 指標 | Before | Stage 1 | Stage 1' | Stage 2 |\n|---|---|---|---|---|")
L.append(f"| 誤PASS件数 | {s['negative_before_false_pass']} | {n['S1']} | {n['S1P']} | {n['S2']} |")
L.append(f"\nBeforeの誤PASS{s['negative_before_false_pass']}件は全て現行Production Candidate E(三日間->三日目/さんにち間 型)で、Trial署名ガードで全件取消({s['negative_vetoed']}件)。Trial層が新たに救済した反例は{s['negative_trial_rescued']}件。\n")
L.append("| 集合 | 原稿 | ASR | 種別 | Before | After |\n|---|---|---|---|---|---|")
for x in d["negative"]:
    L.append(f"| {x['set']} | {x['canonical']} | {x['asr']} | {x['kind']} | {'PASS' if x['before_pass'] else 'NG'} | {x['verdict']} |")
L.append("\n## E. 既存Production由来の誤PASS(範囲/列挙: normalize_jaが〜/、を除去)。Trial無変更・修正対象外\n")
L.append("| 原稿 | ASR | 種別 | 現行Production | Trial追加の救済 |\n|---|---|---|---|---|")
for x in d["prodbug"]:
    L.append(f"| {x['canonical']} | {x['asr']} | {x['kind']} | {x['before_class']}(PASS={x['before_pass']}) | {x['trial_rescued']} |")
L.append(f"\n実コーパス(1,002ペア)の原稿内に『数字+〜/、+数字』は{s['corpus_canonical_with_digit_separator_digit']}件(実害の既知事例なし)。\n")
L.append("## F. 曖昧語(一時/一月/一分/N分の/十分)の非救済確認\n")
L.append("| 原稿 | ASR | 判定 |\n|---|---|---|")
for x in d["ambiguity"]:
    L.append(f"| {x['canonical']} | {x['asr']} | {x['verdict']} |")
L.append("\n## G. 不規則読み署名の扱い別の救済件数(ユーザー判断事項(a)/(b))\n")
L.append("| 方針 | 実run救済 | 備考 |\n|---|---|---|")
L.append(f"| (a) 救済しPASS_WITH_WARNING(最終試聴リストへ) | {s['rescued_real_total']} | うちWARN {s['rescued_real_with_warning']}件を試聴リスト化 |")
L.append(f"| (b) 不規則読み署名は対象外 | {s['rescued_real_without_warning']} | 真値確認済みの1組(Melos Std 三日間)も対象外になる |")
open(f"{OUT}/before_after_tables_02.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok")
