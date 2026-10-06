# T04 L2 要素Trial結果(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04 委任_L2、最終要素ループ P4_paraphrase)

作成: Sonnet(実行層)。成立判定・SSOT反映はFable。Production変更なし(Trial/DEVのみ)。P4を1回だけ実行(再実行・基準後付け変更なし)。ラベルはSonnet仮ラベル(人手確認前)。
詳細: `er052_output/open233_polysemy_trial_03/eval/t04l2_eval_table_p04.md` / `t04l2_funnel.md` / `t04l2_P4_paraphrase_content_label_sheet.md` / `t04l2_labels.json`(+`t04l2_labels.py`) / `runs/cost_t04_l2.json` / `runs/P4_paraphrase/<slug>/`。

## 1. 実装(H11〜H13)
- H11: `patterns/P4_paraphrase/stage1_prompt.txt`(`_common/stage1_prompt_p4.txt`を単一仕様として宣言、lintは`pattern.json`の`common_stage1`で照合)。predicate_direction_explicit=falseは、曖昧表記を平易な言い換え2つ以上(`paraphrase_readings`)×対象が有る/無い両方向で読み、台帳と矛盾する側をRとして列挙(最大4)、polarity最優先。R文末は「〜した/〜になった」。examples.txtに方向不明示の合成正例(図書貸出サービスの運用見直し)を追加(固有名なし)。判定役は high+medium、pred=false+polarityは素通り(維持)。
- H12: stage1へ既存notesを戻す(`pattern.json` stage1_existing_notes=true、`gen_notes_p03.py`は条件1行のみ)。Rの列挙は既存notes非依存・別の読みも検討、と明記。coverはrecord-only(trueでも除外せずstage2へ送る、`dup_of_existing`を記録)。stage2へ「繰り返さない一覧」は渡さない。
- H13: (a)r_echo照合の末尾句読点正規化 (b)R lintの語内一致除外(直前直後がともに漢字の出現は除外、例「市街化調整区域」) (c)stage2テンプレートを「表記'X'=状態。Rのではない。」(R=〜した名詞句+「のではない」) (d)台帳外英語照合で大文字略語を許可 (e)判定役のverdict欠落は1回再問合せ(コード、今回の欠落は0件で未発動)。
- 検証: pytest 52件PASS(新規7件追加)、衛生PASS(72 file)、lint PASS(P4 4prompt)、T-0 PASS。

## 2. 結果(P4。7台帳+A01、各1回)
| 台帳 | 付与/fact | 率 | 対象捕捉 |
|---|---|---|---|
| meta | 2/15 | 13% | 2/2 |
| hormuz | 4/12 | 33% | 1/2 |
| space_weapons | 1/22 | 5% | 0/4 |
| sewer | 3/20 | 15% | 1/3 |
| ai_control | 11/16 | 69% | 2/3 |
| A02(holdout) | 5/19 | 26% | 1/2 |
| small_bag(holdout) | 13/17 | 76% | - |
| A01(holdout) | 1/30 | 3% | - |
- コア5台帳: 捕捉6/14、付与21/85=平均25%(24.7%)。対象外付与15件: 妥当V12/変質D2/誤りH1(HF-004 試算↔確定)、捏造0(目視+数値の台帳照合で不一致0)、曖昧語流用0。
- 内容一致(主=生成のみ、対象付与6件): Y4/P1/N1 → Y率67%、(Y+P)83%。うち3件(F-011/EVID-004/EVID-006)は既存notesと同趣旨(dup_of_existing)。副: 既存notes禁止文転記との和集合Y10/14(生成のみ4・既存のみ9)。
- holdout: 期待超過 計15(A02 +3、small_bag +12、A01 0)、誤りH/X 3(A02 PILOT-03 X・PILOT-05 H、small_bag F009 H)。字数 平均84/最大104。実費45.39円。

## 3. P1'/B2との比較(コア5台帳。P1'はT04_element_trial_result.md、B2はTRIAL-03記録)
| 指標 | P1' | B2 | P4 |
|---|---|---|---|
| 捕捉(対象) | 2/14 | 10/14 | 6/14 |
| 付与率(平均) | 21% | 42% | 25% |
| 内容一致 主Y / (Y+P) | 0/2 | 8/10(Y基準) | 4/6=67% / 83% |
| holdout 期待超過 / 誤り | 6 / 1 | (B2記録参照) | 15 / 3 |
| 捏造 | 0 | 0 | 0 |
| 実費 | 43.75円 | - | 45.39円 |

## 4. 基準照合(6項目)
| 項目 | P4 | 判定 |
|---|---|---|
| 捕捉>=9/14 | 6/14 | NG |
| 付与率<=25% | 全体24.7%(ai_control 69%、hormuz 33%は台帳別NG) | OK(全体)/台帳別NG |
| holdout誤付与<=1 | 期待超過15・誤りH/X 3 | NG |
| 捏造0 | 0 | OK |
| 内容一致>=70% | Y率67%(Y+P 83%、n=6) | NG(Y基準) |
| 迎合なし | 台帳別件数は大きく不一致(5%〜76%) | OK |

## 5. rollback Gate(MUSE-HC-012)
- 捕捉: Y(pred=false+polarityの素通り経路)。
- R列挙に「復活/再提供」型が含まれたか: **含まれない**。stage1は`paraphrase_readings`で「一時的に止めた(有:残り後で再開できる/無:自体がなくなる)」「以前の状態に戻した(有:使える状態に戻る/無:使えない状態に戻る)」の両方向を書いたが、R(polarity)は「Metaは人間コンシェルジュ機能を完全に廃止した」1件のみ(有る側の読みはRにされず)。
- Note全文: 注意(逆転): 表記'ロールバックした'=Metaの人間コンシェルジュ機能は当面提供されていない。Metaは人間コンシェルジュ機能を完全に廃止したのではない。
- 機械チェック: FAIL候補(A:取り下げ系語なし、B:復活・再提供・再開・復旧の否定なし)。「復元ではない」型の誤禁止は不出現。
- 3値仮ラベル: 軸ずれ(時期軸の「完全廃止ではない」止まりで、「機能そのものを復活・再提供した意味ではない」を保持せず)。Fable最終判定要。
- 付記: 今回の評価対象8台帳のうちpred_direction_explicit=falseはHC-012の1件のみで、H11の言い換え列挙が働く場面は実質この1件。

## 6. 段別ファネル(詳細 t04l2_funnel.md)
- 未捕捉8件の段: stage1 reversible=false で落ちた5件(space F-001/F-002、sewer F-010/F-016、ai CONTROL-001)、判定役low 3件(HF-009 blocking「高水準」、F-009 blocking「開発」、F-007 blocking「開発中」)。cover起因の脱落は0(record-only)。stage2却下は全台帳で0(r_echo・R被覆・lint・英語照合とも通過)。
- 全体のdropped_by: reversible=false 93、判定役low 16、R lint 1(「変更」、A02 POL-06のR文言)。判定役verdict欠落0(再問合せ未発動)。
- 付与済み対象6件はいずれもstage1でR採用→判定役(high 2/medium 3)または素通り1→stage2 ok。

## 7. 実費
45.39円(上限55円。台帳別 meta 3.41/hormuz 5.57/space 2.84/sewer 3.56/ai_control 9.14/A02 6.11/small_bag 8.95/A01 5.81)。A01は予算残(約15円)>8円のため実行。累計 330.73+45.39=376.12円。

## 8. 所見
1. H12(既存notes復帰)で捕捉はP1'の2/14から6/14へ上がり、判定役・stage2段の脱落はほぼ解消したが、基準(9/14、holdout誤付与、台帳別付与率)は未達。ai_controlとsmall_bagは過剰付与(69%/76%)で、「25%のために正しいNoteを落とさない」方針と台帳別の過剰付与は両立しておらず、損失の主因は引き続きstage1のreversible判定(93件脱落)と判定役lowによる取りこぼしとの両極に分かれる。
2. rollback GateはH11を入れても未達。Rに復活・再提供型が乗らない原因は、言い換え列挙は書かれるが「有る」側の読みがRへ昇格しない点で、促し方(プロンプト)の範囲では改善が確認できなかった。今回はpred=false対象が1件のみで、効果の一般性は検証不能(n=1)。
