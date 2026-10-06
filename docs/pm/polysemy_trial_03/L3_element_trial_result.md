# L3 要素Trial結果(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 / ループ3・最終)
性質: DEV要素Trial(Production非接続)。評価のみ(Sonnet)。成立判定はFable。実費 **¥34.01 / 上限¥60**(`er052_output/open233_polysemy_trial_03/runs/cost_l3.json`)。累計 L1 ¥75.42 + L2 ¥50.70 + L3 ¥34.01 = ¥160.13。
入力: 5台帳(core)+holdout2(A02, small_bag)、web_search=none、各call上限¥5、B3は1回のみ(n=1、再実行なし)。

## 1. 仮説(pattern.jsonのhypothesisに逐語記録)と変更
- H5(付与率): 新stage1.5=圧縮判定役。入力はfact_id・compressed_claim・Rだけ(claim全文/scope/notesは渡さない)。「この圧縮文だけを読んだ執筆者がRで書く見込み」をhigh/medium/lowで判定、通過=highのみ(medium=warning記録して落とす、low=落とす)。1 call/台帳。
- H6(ゆらぎ): stage1を2回実行、reversible通過の和集合(各回のRを保持、同一Rは統合)を1.5へ。いずれかhighなら通過、highのRを採用。
- H7(字数): max_chars=120。不変: 共通定義(i)〜(iv)、stage2(B2同一・既存notesヒントあり・derivable_only)、テンプレート、examples、prefix。
- 実装: `gen_notes_p03.py`に`twostage_gate`モード(`run_gate`/`build_s15_input`/`apply_s15`/`jaccard`)。予算ガードはper-call化(累計<=budget×call数。累計5円固定だと多段で後段が止まるため)。pytest 18 PASS(L3追加2: 1.5入力/採用ロジック、gate E2E)。prompt衛生 PASS(29ファイル)。
- 重要な発見(prompt欠陥): B2/B3の`stage1_prompt.txt`は、L2作成時にH3の新形式(reverse_propositions)の本文がL1-Bの旧形式本文に連結された状態(【出力】が2か所、Fact一覧は末尾のみ)。L2/B2のstage1_raw 121件・L3の242件は**全て旧形式(単一reverse_proposition)**で、H3(R最大2列挙)は実質未検証。指示どおり「B2と同一」を継承し、修正しない(再実行不可のため)。ハーネスは旧形式にも対応し動作は正常。

## 2. 結果(core5。()はholdout)
| 指標 | L1-B | B2(hint) | B3(gate) |
|---|---|---|---|
| 対象捕捉(正解14) | 6/14(救済9) | 10/14 | **1/14**(F-001のみ) |
| 内容一致 一致/部分/不一致 | 2/2/2 | 6/2/2 | 0/0/1 |
| 付与数(付与率) | 19(22%) | 36(42%) | **2(2.4%)** |
| 対象外付与 妥当/変質止まり/誤り | 9/2/2 | 17/5/4 | 0/1/0 |
| 台帳に無い事実の混入/曖昧語流用 | 0/0 | 0/0 | 0/0 |
| 字数 平均/最大 | 72.9/91 | 70.3/88 | 89.5/107 |
| 付与 台帳別(meta/hormuz/space/sewer/ai) | 3/11/0/5/0 | 8/5/9/6/8 | 1/0/1/0/0 |
| holdout small_bag 付与 | 0 | 0 | 0 |
| holdout A02 付与 / 参考対象POL-01/06 | 10 / 2/2 | 4 / 0/2 | 0 / 0/2 |
| 実費(全7台帳) | ¥27.9 | ¥26.5 | ¥34.0(1台帳平均4.9) |
- 付与2件: meta MUSE-HC-003(設計説明↔実運用稼働、変質止まり)、space F-001(防護用途↔攻撃用途の取違え=妥当だが既知誤読「初めて認めた発言→初めて配備」とは不一致)。字数は2件(107, 72)。
- 台帳別の付与数が0〜1件の台帳が5つ(件数迎合なし、ただし過少)。

## 3. 基準照合(Fable事前固定。判定はFable)
| 基準 | B3 |
|---|---|
| 捕捉≥9/14 | **NG(1)** |
| 付与率≤25% | OK(2.4%) |
| holdout small_bag≤1 | OK(0) |
| 捏造0件 | OK(0) |
| 内容一致(一致+部分)≥捕捉の70% | **NG(0/1)**(分母1でn不足) |
| 件数迎合なし(台帳ごとに同一件数でない) | OK(0〜1件で揃っていない) |
- 満たす: 4/6。付与率25〜30%の参考(対象外の誤り件数)は該当せず(誤り0)。

## 4. stage1の2回の一致率と和集合の効果(H6)
- Jaccard(reversible通過fact集合、台帳別): meta 0.29 / hormuz 0.62 / space 0.56 / sewer 0.60 / ai_control 0.80 / A02 0.44 / small_bag 0.88。meta・A02で再現性が低い。
- 全85fact(core)で通過数 run1=33、run2=40、和集合46。**対象14のstage1通過**: run1=9、run2=11、和集合12(+1〜3件)。和集合はstage1の取りこぼし(F-001, HC-014, F-010, F-016)を拾った。未通過はEVID-004, CONTROL-001のみ(L1/L2と同じ)。
- 和集合で付与側の母数が膨らむが、1.5で絞られるため付与率には響かない。

## 5. stage1.5の判定内訳とFN残
- 判定(core fact単位、highがあれば high): high 2 / medium 15 / low 29(stage1.5到達46件)。holdout: high 0 / medium 12 / low 18。小バグ: small_bag F007, F008はverdict欠落(missing、落とす扱い)。
- 対象14の内訳: high通過1(F-001) / **medium 6**(HF-007, F-002, F-010, F-011, F-016, EVID-006) / **low 5**(HC-012, HC-014, HF-009, F-007, F-009) / stage1未通過2(EVID-004, CONTROL-001)。
- 非対象(71件): stage1通過(和集合)34、うちhigh 1 / medium 9 / low 24。残り37件はstage1未通過。
- FN残(13件): 上記medium 6件・low 5件・stage1未通過2件(計13、付与は14中1)。lowの理由の多くは「圧縮文に『当面』『計画』『模擬』等の限定語が残っており読者は取り違えない」。stage1が出す`compressed_claim`がscope/conditionsの語を保持しがちで、「原資料を見ない圧縮後の読者」を模擬できていない可能性。
- 参考(事後試算、API未実行・Fable判断用): 通過をhigh+mediumに緩めた場合、通過=対象7/14(HF-007, F-001, F-002, F-010, F-011, F-016, EVID-006)+非対象10=17件(20%)。捕捉は7/14で基準9に届かない。medium以上の通過率は対象7/12(58%)、非対象10/34(29%)で、1.5は対象と非対象をある程度分離している(弁別力あり、閾値が厳しすぎる)。
- holdout: A02 POL-01 low、POL-06 medium(いずれも落ちる)。small_bag 付与0。

## 6. 所見(Sonnet、判定はFable)
- B3はノイズ(付与率2.4%、誤り0、small_bag 0)を抑えたが、捕捉1/14で過剰に絞り込み、正しく拾う目的を大きく損なった。highのみ通過の閾値は厳しすぎ、mediumに対象6件が集中。stage1の和集合(捕捉の母数12/14)は有効だが、1.5が最大の取りこぼし要因。
- 1.5の弁別力は一定(対象58%/非対象29%がmedium以上)だが、n=1・Sonnetラベルで確度は限定的。入力のcompressed_claimがscope語を含む(圧縮の忠実性が弱い)ため、「圧縮文のみ」を厳密に保つには圧縮を別callにする等の設計見直しが要る(未実施)。
- 限界: B2/B3共通のstage1 prompt欠陥(新旧連結、H3未検証)、n=1、人手確認前ラベル、2件の付与では内容一致率は参考にならない。最終ループのため再実行・調整は未実施。

## 7. 逐語一覧・証跡
- `er052_output/open233_polysemy_trial_03/eval/B3_twostage_gate_content_label_sheet.md`(逐語・ラベル・stage1.5判定・FN)、`l3_labels.py`、`l3_label_summary.json`
- 生run: `runs/B3_twostage_gate/<theme>/`(`stage1_raw_r1/r2.json`、`stage1_5_raw.json`、`stage1_5_prompt.txt`、`judgments_all.json`、`provenance.json`)、`runs/run_l3.log`、`runs/cost_l3.json`
- パターン: `patterns/B3_twostage_gate/`。L1/L2のsheetは未変更。
