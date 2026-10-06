# L2 要素Trial結果(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 / ループ2)
性質: DEV要素Trial(Production非接続)。評価のみ(Sonnet)。成立判定はFable。実費 **¥50.70 / 上限¥70**(`er052_output/open233_polysemy_trial_03/runs/cost_l2.json`)。
入力: 5台帳(core)+holdout2(A02, small_bag)、web_search=none、各call上限¥5、各変種1回(n=1)。

## 1. 仮説(pattern.jsonのhypothesisに記録)と変更
- H1(ハーネス): 接頭辞比較を空白正規化(全角/半角・末尾空白無視)、接頭辞後の空白はコード側で正規化(`normalize_prefix`)。L1-Bのbad_prefix却下8件(space_weapons、対象3件)が原因。`--reuse-raw`相当は無く、L1-Bの再集計は省略しL2結果で評価。
- H2(stage2過剰却下): `R_is_natural_reading=false`は警告のみ(採用しnotes.json/judgments_allのwarningsに記録)。却下は`correct_statement_derivable_from_ledger=false`のみ。L1-Bはai_controlで10件全落ち。
- H3(内容ずれ): stage1で各factにRを最大2つ列挙(`reverse_propositions:[{R,flipped_component,contradicts_ledger_field,ledger_quote,changes_conclusion,conclusion_change_reason}]`)。コード側で「changes_conclusion=trueかつledger_quoteが台帳に部分一致する先頭」を採用(`pick_reverse`)。B2のみstage2へ既存notes_for_writerを「手がかり(独立判定の後に参照)」として渡す。B2nは渡さず、stage2のFact一覧からもnotes_for_writerを除く。stage1は両者同一(L1と同じく既存notes入り)。
- H4(型の抜け): examples.txtに合成正例1件(模擬環境での検証結果→実環境で実際に発生。架空・固有名なし)。
- 不変: 共通定義(i)〜(iv)、テンプレート、100字、負例。
- 実装・検証: pytest 16 PASS(L2追加4: 接頭辞正規化、R選択、B2のwarning/hint、B2nのnotes除去)。prompt衛生 PASS(23ファイル)。

## 2. 結果(core5。()はholdout)
| 指標 | L1-B | B2(hint) | B2n(nohint) |
|---|---|---|---|
| 対象捕捉(正解14) | 6/14(接頭辞救済で9) | **10/14** | 6/14 |
| 内容一致 一致/部分/不一致 | 2/2/2 | 6/2/2 | 5/0/1 |
| 付与数(付与率) | 19(22%) | 36(42%) | 33(39%) |
| 対象外付与 妥当/変質止まり/誤り | 9/2/2 | 17/5/4 | 15/6/6 |
| 台帳に無い事実の混入 | 0 | 0 | 0 |
| 曖昧語流用 | 0 | 0 | 0 |
| 字数 平均/最大 | 72.9/91 | 70.3/88 | 77.1/99 |
| 警告(R不自然) | - | 0 | 0(holdout A02に2) |
| 却下 | bad_prefix8/self_check10 | too_long2(対象外) | too_long4(うち対象2: HF-007, F-009) |
| 付与 台帳別(meta/hormuz/space/sewer/ai) | 3/11/0/5/0 | 8/5/9/6/8 | 5/1/12/6/9 |
| holdout A02/small_bag 付与 | 10/0 | 4/0 | 4/1 |
| holdout A02参考対象(POL-01/06) | 2/2 | 0/2 | 0/2 |
| 実費(全7台帳) | ¥27.9 | ¥26.5 | ¥24.2 |
- 内容一致は「一致+部分」/捕捉数: B2 8/10、B2n 5/6。「誤り」型(B2 4件=HF-004,HF-012,F-019,F-020 / B2n 6件=F-003,F-004,F-005,F-019,F-020+sewer F-004)。
- 対象外付与の増加が目立つ: B2は台帳ごとに5〜9件付与(空白修正+警告化で却下が消え、stage1の再現率寄り判定がそのまま通る)。

## 3. 基準照合(Fable事前固定。判定はFable)
| 基準 | B2 | B2n |
|---|---|---|
| 捕捉≥9/14 | OK(10) | NG(6) |
| 付与率≤25%(5台帳平均) | NG(42%) | NG(39%) |
| holdout small_bag≤1件 | OK(0) | OK(1) |
| 捏造0件 | OK(0) | OK(0) |
| 内容一致(一致+部分)≥捕捉の70% | OK(80%) | OK(83%) |
| 台帳ごとの件数が同一でない | OK | OK |
- 満たす: B2 5/6(付与率NG)、B2n 4/6(捕捉・付与率NG)。

## 4. B2とB2nの差(既存notes依存)
- 見かけの差: 捕捉10 vs 6。B2nはmeta(HC-012/014)、sewer F-016がstage1で`reversible=false`、F-009/HF-007は100字超過で却下。
- ただしstage1 promptは両者同一で、reversible=true集合も一致しない(meta 8vs5、hormuz 6vs2、sewer 6vs6だが共通3)。差の大半はstage1の実行ごとのゆらぎ(n=1)で、stage2への既存notes受け渡しの純効果とは分離できない。
- stage2が関与する差(内容): F-010(B2: 不一致/B2n: 一致)のようにhintなしの方が既知誤読に合う例もあり、hintが一方向に有利とは言えない。字数はB2の方が短い(最大88/99)。
- 結論: 判定(stage1)の再現性が今回の主たる不安定要因。既存notes依存度は未決(n=1・stage1ゆらぎ込み)。

## 5. FN残(fact_id・理由)
- B2(4件): hormuz HF-009 / space F-001 / ai EVID-004 / CONTROL-001 → いずれもstage1 `reversible=false`(Rが作れない/台帳引用不可)。
- B2n(8件): meta HC-012, HC-014 / hormuz HF-009 / sewer F-016 / ai EVID-004, CONTROL-001 → stage1 reversible=false。hormuz HF-007, space F-009 → stage2 note生成済みだが100字超過(101/105字)で却下。
- 共通: HF-009、EVID-004、CONTROL-001は全パターン(L1含む)で未捕捉。L1で未捕捉のF-001はB2のみ未捕捉(B2nは捕捉・不一致)。
- L1で落ちていたspace_weapons F-002/F-007/F-009はH1で復活(B2 3件一致)。ai_control EVID-006はH2で捕捉(一致)。

## 6. 所見(Sonnet、判定はFable)
- H1・H2は有効(形式却下の解消、ai_control・space_weaponsの復活)。ただし却下の消失に伴い付与率が22%→39〜42%に増加し、基準2(≤25%)は両変種とも未達。ノイズ側のゲートは別途必要(stage1の絞り込み強化、または付与件数ではなく型での抑制)。
- holdout A02の参考対象(POL-01/06)はL1-B 2/2から0/2へ低下。B2/B2n共に付与は4件のみで、対象外型(POL-02/03/04等)を優先して選び、n=1のゆらぎと過学習の双方が疑われる。small_bagは0〜1件で基準内。
- 100字制約はB2nで対象2件を落とした。字数は構造的リスク(二文構成の説明が長い)。次ループで字数超過時の短縮再生成は不可(prompt変更になるため要判断)。
- 限界: ラベルはSonnet判断・人手確認前。5テーマ固有の目視ラベルでn=1。

## 7. 逐語一覧・証跡
- `er052_output/open233_polysemy_trial_03/eval/B2_twostage_hint_content_label_sheet.md`、`.../B2n_twostage_nohint_content_label_sheet.md`(逐語・ラベル・FN)、`l2_eval_table.md`、`l2_label_summary.json`、`l2_labels.py`
- 生run: `er052_output/open233_polysemy_trial_03/runs/B2_twostage_hint/<theme>/`、`runs/B2n_twostage_nohint/<theme>/`。パターン: `patterns/B2_twostage_hint/`、`patterns/B2n_twostage_nohint/`。
- 注記: eval実行で`eval/B_twostage_content_label_sheet.md`が空欄sheetで上書きされたため、`eval/l1_labels.py`で再生成し復元(内容はL1と同一、l1_label_summary.jsonも同値)。
