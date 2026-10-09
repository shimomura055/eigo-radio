# CASEBANK_01: Risk Flagger評価用ケースバンク(WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01A、API¥0)

全ての文・台帳・ラベルは過去成果物からの逐語抽出で、新規生成はない。ラベルは過去成果物の記録に従い、本書では再判定していない。機械可読の正本は `casebank_01.json`(生成: `build_casebank_01.py` → `render_casebank_md_01.py`)。

## 1. 件数

- 実記事由来ケース: 61件(重大 17 / 非重大 44)。別枠で合成参考セット 14件(人工反転、KPI本体には入れない)。
- 重大のラベル根拠区分: ユーザー確認 4, Sonnet判定 10, Fable確定 3
- 非重大のラベル根拠区分: ユーザー確認 6, Sonnet判定 24, 機械抽出(弱ラベル) 14
- **人間確認済み重大: 4件**(ユーザー確認C: K01・K02・K03の3件 + ユーザー判断『C寄り、Bの余地あり』: K11の1件)。目標≥5件に**1件不足**(§7参照)。

### 事故タイプ別(重大)

| 事故タイプ | 件数 | 開発 | 保留 |
|---|---|---|---|
| rollback方向反転 | 2 | 1 | 1 |
| 主体対象入替 | 7 | 3 | 4 |
| 否定反転 | 0 | 0 | 0 |
| 数量時系列 | 1 | 0 | 1 |
| 不在断定 | 1 | 0 | 1 |
| その他 | 6 | 2 | 4 |
| 合計 | 17 | 6 | 11 |

注: 『否定反転』は実記事由来の確定重大が0件(K02は不在断定を主、否定反転を副に分類)。否定反転・数量時系列・Rollbackの**タイプ別能力**は合成参考セット(14件、`synthetic_reference`)で別途測る。

### 非重大

| 区分 | 件数 |
|---|---|
| ユーザー確認 | 6 |
| Sonnet判定 | 24 |
| 機械抽出(弱ラベル) | 14 |
| 合計 | 44(開発 18 / 保留 26) |

## 2. 開発セット / 保留セットの事前分割

- 乱数seed: case_id生成 20261009 / 分割 20261010 / 機械抽出 20261011。
- 規則: (label,事故タイプ)層別の乱数分割。保留目標≈60%。人間確認済み重大4件は K03のみ開発、K01/K02/K11は保留(同型近接: K01とK03は同一Fact・同型=near_dup_group rollback_hc012)。K08/K09=保留、K12=開発。合成参考セットは別途7/7。
- 分割は検出器開発の前に確定し、`casebank_01.json` の `split` に固定した(以後変更しない。変更が必要な場合は理由つきで新版を作り、保留セットのscoreを再利用しない)。
- 保留セットは最終評価1回のみに使う。開発セットで検出器を調整し、保留セットでKPI 1〜4を確定する。

## 3. 重大ケース一覧

| case_id | 旧ID | 区分 | タイプ | 分割 | Fact | 対象文(先頭) | 文の所在 |
|---|---|---|---|---|---|---|---|
| rf_y84g5r | WE-K01 | ユーザー確認 | rollback方向反転 | holdout | MUSE-HC-012 | The company also restored the human concierge feature to the… | er019_output/family_x_refresh_e2e_01/meta/run_03/b1b/article.md:17 |
| rf_ur5649 | WE-K03 | ユーザー確認 | rollback方向反転 | dev | MUSE-HC-012 | They also temporarily put back the feature in which humans h… | er045_output/family_x_no_heading_segmentation_trial_01/meta/trial_tran… |
| rf_emcgyx | WE-K02 | ユーザー確認 | 不在断定 | holdout | EVID-008 | Nor has anyone reported that an AI got out of the test envir… | er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_c… |
| rf_hdr8y4 | WE-K11 | ユーザー確認 | 主体対象入替 | holdout | F-001 | 宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。 | er052_output/open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2… |
| rf_7suvyn | ai-p2r1-01,E2E02-P2-重大 | Sonnet判定 | その他 | holdout | EVID-008 | In other words, it was like a heavily guarded prison whose b… | er052_output/open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1/b1… |
| rf_5qddqw | ai-p2r2-07,E2E02-P2-重大 | Sonnet判定 | その他 | dev | EVID-006 | In a simulated safety evaluation, Claude Opus 4 attempted bl… | (記事ファイルでは逐語未特定。label_src内の引用) |
| rf_fmu3aa | RC-K20 | Sonnet判定 | その他 | holdout | MUSE-HC-006 | The idea was practical: when AI struggled, a person could he… | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:468(R… |
| rf_p4mtyd | Safety-B3 | Fable確定 | その他 | holdout | HF-007 | Concerns about US-Iran attacks, the sea blockade, and tanker… | er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.… |
| rf_g7k93w | Safety-B4-a | Fable確定 | その他 | dev | MUSE-HC-002 | A person can take over when AI alone has trouble. | (記事ファイルでは逐語未特定。label_src内の引用) |
| rf_vph9nb | w1-11 | Sonnet判定 | その他 | holdout | MUSE-HC-009 | AIが電話をかけ、相手に切られることもある。そこで人間が電話を担当する。 | (記事ファイルでは逐語未特定。label_src内の引用) |
| rf_sq5c2g | meta-p2r2-02,E2E02-P2-重大 | Sonnet判定 | 主体対象入替 | dev | MUSE-HC-012 | But the humans who ended up in the main role had not been to… | er052_output/open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2/b1b/arti… |
| rf_qupxd4 | ai-p2r1-02,E2E02-P2-重大 | Sonnet判定 | 主体対象入替 | dev | CONTROL-002 | We need to check whether the AI has enough ability, whether … | er052_output/open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1/b1… |
| rf_apqtyt | sw-p2r2-02,E2E02-P2-重大 | Sonnet判定 | 主体対象入替 | dev | F-001 | It is that preparations to secure space have come into publi… | er052_output/open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2… |
| rf_665ga9 | hormuz-T0M0r2-01 | Sonnet判定 | 主体対象入替 | holdout | HF-002 | Mr. Trump posted that for all cargo passing through the Stra… | er052_output/open233_note_transfer_matrix_01/runs/hormuz/nb/T0M0/rep2/… |
| rf_nck2y6 | RC-K18,Safety-A2A3-0 | Sonnet判定 | 主体対象入替 | holdout | HF-002 | The idea was that those carrying the cargo would repay the m… | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:413(R… |
| rf_tcdxe4 | Safety-A4-0 | Fable確定 | 主体対象入替 | holdout | MUSE-HC-006 | Through Muse, trained human contract workers made some calls… | (記事ファイルでは逐語未特定。label_src内の引用) |
| rf_t9nxuv | RC-K16 | Sonnet判定 | 数量時系列 | holdout | HF-009 | The fee plan left the stage, but the events driving oil pric… | er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring… |

## 4. 非重大ケース一覧

| case_id | 旧ID | 区分 | 分割 | Fact | 対象文(先頭) | 文の所在 |
|---|---|---|---|---|---|---|
| rf_w3ucr6 | B-02,w1-49 | Sonnet判定 | dev | F-001 | 性能表は伏せたまま | er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/new/ja_wri… |
| rf_xkgmt5 | B-03,w1-61 | Sonnet判定 | dev | F-001 | 明らかにされていません | er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/ja_wri… |
| rf_ptrj37 | B-09,w3-85 | Sonnet判定 | dev | F5 | 会社が示した次の数字は、AI半導体売上高の予想ではありません。次の四半期の連結売上高の見通しです。 | er052_output/factlock_astra_e2e_trial_01/runs/semiconductor_earnings/n… |
| rf_mytfwc | B-10,w3-86 | Sonnet判定 | holdout | F5 | 今回の発表を整理すると、登場するのは三つ。AI半導体の実績、会社全体の実績、会社全体の見通し。 | er052_output/factlock_astra_e2e_trial_01/runs/semiconductor_earnings/n… |
| rf_wfzehu | B-11,w3-98 | Sonnet判定 | dev | (特定できず: ledger全体が入力) | 2026年9月23日から新料金です | er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/old/ja_w… |
| rf_hspzde | RC-K01 | Sonnet判定 | holdout | MUSE-HC-006 | A call came from an AI agent. That was what it seemed. But w… | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:91(RC… |
| rf_b2nvsf | RC-K02 | Sonnet判定 | holdout | HF-009 | Oil prices moved briefly, then returned to a high level. | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:109(R… |
| rf_562myt | RC-K03 | Sonnet判定 | holdout | HF-009 | The fee plan vanished, but oil prices stayed high as tension… | er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md:22 |
| rf_zbe99x | RC-K05 | Sonnet判定 | dev | MUSE-HC-011 | human staff made inappropriate comments about race during ca… | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:166(R… |
| rf_75v4en | RC-K08 | Sonnet判定 | dev | MUSE-HC-012 | But sometimes, a human was speaking instead. | er019_output/family_x_refresh_e2e_01/meta/run_03/a2/article.md:11 |
| rf_wrv48r | RC-K09 | Sonnet判定 | dev | MUSE-HC-012 | The problem was telling users who was speaking. | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:243(R… |
| rf_gtwtjt | RC-K11 | Sonnet判定 | holdout | MUSE-HC-012 | A Meta executive admitted the mistake. The test had begun wi… | er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md:29 |
| rf_da6twd | RC-K12 | Sonnet判定 | holdout | MUSE-HC-012 | A user might think the exchange was with AI, even though a p… | er019_output/family_x_audio_production_wiring_01/family_x_b3_productio… |
| rf_7kyezh | RC-K13 | Sonnet判定 | dev | MUSE-HC-012 | The test began without clearly telling users that contract w… | er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md:19 |
| rf_sprwsa | RC-K14 | Sonnet判定 | holdout | HF-002 | トランプ氏は、アメリカがホルムズ海峡の安全確保に使う費用について、海峡を通るすべての貨物に二割の償還を求めると投稿した。 | er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring… |
| rf_pb7rz2 | RC-K15 | Sonnet判定 | dev | HF-009 | During that period, attacks between the United States and Ir… | er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring… |
| rf_rhubds | RC-K17 | Sonnet判定 | holdout | HF-009 | The fee plan may be replaced, but events continuing at the s… | er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring… |
| rf_y45s87 | RC-K23 | Sonnet判定 | dev | MUSE-HC-012 | An AI called. That was what people thought as they spoke. | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:543(R… |
| rf_aennw4 | S0-1,S0_USER_CHECK 確認1 | Sonnet判定 | holdout | MUSE-HC-012 | Meta paused its human-concierge feature after contract worke… | er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md:7 |
| rf_xyw4mp | S0-2,S0_USER_CHECK 確認2 | Sonnet判定 | dev | MUSE-HC-012 | Meta’s AI calling test used human contractors without proper… | er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md:13 |
| rf_8fbz5r | S0-3,S0_USER_CHECK 確認3 | Sonnet判定 | holdout | HF-009 | Oil prices stayed high despite the shift from a proposed Hor… | er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md:19 |
| rf_grqgvt | WE-K04 | Sonnet判定 | dev | MUSE-HC-012 | Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻し… | er019_output/family_x_refresh_e2e_01/meta/run_03/ja_writer/original.md… |
| rf_6j5x2m | WE-K06 | Sonnet判定 | holdout | F-001 | But the name of the device and exactly what it can do in an … | er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/ar… |
| rf_6urnmg | WE-K10 | Sonnet判定 | holdout | EVID-008 | But because of a setup mistake, it was able to connect to th… | er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_c… |
| rf_kkh6ng | RC-K04 | ユーザー確認 | holdout | MUSE-HC-010 | some calls needed user information to continue. | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:147(R… |
| rf_hmpyuu | RC-K10 | ユーザー確認 | holdout | MUSE-HC-012 | They enjoyed AI’s convenience, but a human was on the other … | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:260(R… |
| rf_c3p892 | RC-K19 | ユーザー確認 | holdout | HF-009 | Just after the charge plan disappeared, prices began to fall… | docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:439(R… |
| rf_yjjmk8 | WE-K08 | ユーザー確認 | holdout | HF-007 | Trump announced that he would drop the 20 percent fee plan a… | er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md:9 |
| rf_upps5x | WE-K09 | ユーザー確認 | holdout | HF-002 | On July 13, Trump posted that all cargo passing through the … | er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring… |
| rf_7b6trp | WE-K12 | ユーザー確認 | dev | MUSE-HC-012 | The human concierge feature was then put on hold for the tim… | er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta… |
| rf_nykkru | MECH-byd_recall-old | 機械抽出(弱ラベル) | dev | BYD-RECALL-01 | The recall notice in China covers a total of 183,211 vehicle… | er052_output/factlock_astra_e2e_trial_01/runs/byd_recall/old/b1b/artic… |
| rf_ejrk5u | MECH-central_bank_mortgage-old | 機械抽出(弱ラベル) | dev | F002 | It raised the policy rate by 0.25 percentage points, to 3.75… | er052_output/factlock_astra_e2e_trial_01/runs/central_bank_mortgage/ol… |
| rf_vqhe62 | MECH-central_bank_mortgage-old | 機械抽出(弱ラベル) | dev | F007 | The rate change would add about $376 to each monthly payment… | er052_output/factlock_astra_e2e_trial_01/runs/central_bank_mortgage/ol… |
| rf_e42vt2 | MECH-hormuz-new | 機械抽出(弱ラベル) | holdout | HF-002 | He proposed charging 20% on all cargo passing through the St… | er052_output/factlock_astra_e2e_trial_01/runs/hormuz/new/a2/article.md… |
| rf_6c53hz | MECH-hormuz-new | 機械抽出(弱ラベル) | holdout | HF-002 | He proposed asking for a 20% reimbursement on all cargo pass… | er052_output/factlock_astra_e2e_trial_01/runs/hormuz/new/b1b/article.m… |
| rf_ah9aha | MECH-semiconductor_earnings-ol… | 機械抽出(弱ラベル) | dev | F3 | They were also up 54 percent from the quarter before. | er052_output/factlock_astra_e2e_trial_01/runs/semiconductor_earnings/o… |
| rf_9x3gdn | MECH-semiconductor_earnings-ol… | 機械抽出(弱ラベル) | holdout | F5 | That would be up 236 percent from the same quarter a year ea… | er052_output/factlock_astra_e2e_trial_01/runs/semiconductor_earnings/o… |
| rf_w3dtae | MECH-small_bag-old | 機械抽出(弱ラベル) | holdout | MB-01 | For fall/winter 2026, mini bags are being featured as a tren… | er052_output/factlock_astra_e2e_trial_01/runs/small_bag/old/b1b/articl… |
| rf_rdwghg | MECH-space_weapons-old | 機械抽出(弱ラベル) | holdout | F-003 | In 2021, Russia launched a missile from the ground and destr… | er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/ar… |
| rf_frwds2 | MECH-space_weapons-old | 機械抽出(弱ラベル) | holdout | F-003 | In 2021, Russia launched a missile from the ground. | er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/a2/art… |
| rf_pdmdt5 | MECH-streaming_price-new | 機械抽出(弱ラベル) | dev | F03 | The monthly Premium plan on its own will rise from $18.99 to… | er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/new/a2/a… |
| rf_g4uegk | MECH-streaming_price-new | 機械抽出(弱ラベル) | holdout | F03 | The monthly Premium plan by itself will go from $18.99 to $2… | er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/new/b1b/… |
| rf_qupkjh | MECH-streaming_price-old | 機械抽出(弱ラベル) | holdout | F02 | The monthly price of the standalone plan with ads will rise … | er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/old/b1b/… |
| rf_5cryu9 | MECH-streaming_price-old | 機械抽出(弱ラベル) | holdout | F02 | The standalone plan with ads will cost $11.99 a month. | er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/old/a2/a… |

(全フィールド: 台帳Fact逐語・対象文・前後文・ラベル根拠・出典は `casebank_01.json` を参照。)

## 5. 記事単位セット(1記事あたりFlag数・未知ケース有用性測定用)

FACTLOCK-ASTRA-E2E-TRIAL-01 の新腕・旧腕。JA=`ja_writer/revision2.md`(R2最終)、EN Adv=`b1b/article.md`、EN Std=`a2/article.md`。ファイル無し=その腕でSTOP(未出荷)。sha256・文数・台帳Fact数・labels_merged所見は `casebank_01.json` の `articles`。

| テーマ | 腕 | 台帳Fact数 | JA R2文数 | EN Adv文数 | EN Std文数 | labels_merged件数(重大/軽微/問題なし/所見なし/判断不能) |
|---|---|---|---|---|---|---|
| byd_recall | new | 11 | 37 | 25 | - | 0/14/46/1/0 |
| byd_recall | old | 11 | 26 | 24 | - | 0/13/28/1/0 |
| central_bank_mortgage | new | 11 | - | - | - | 0/5/1/1/0 |
| central_bank_mortgage | old | 11 | 24 | 26 | 30 | 0/0/30/2/0 |
| hormuz | new | 12 | 36 | 33 | 42 | 0/6/28/10/0 |
| hormuz | old | 12 | - | - | - | 0/2/2/1/0 |
| meta | new | 15 | 39 | 29 | 33 | 0/1/12/8/0 |
| meta | old | 15 | - | - | - | 2/3/0/1/0 |
| openai_copyright | new | 8 | 33 | - | - | 0/5/3/0/1 |
| openai_copyright | old | 8 | 20 | 19 | 30 | 0/6/32/0/0 |
| semiconductor_earnings | new | 5 | 41 | - | - | 0/3/6/0/1 |
| semiconductor_earnings | old | 5 | 22 | 22 | 29 | 0/7/30/0/0 |
| small_bag | new | 6 | 38 | 25 | 36 | 0/0/56/2/0 |
| small_bag | old | 6 | 19 | 17 | - | 0/15/26/1/0 |
| space_weapons | new | 22 | 35 | 31 | - | 0/20/25/9/0 |
| space_weapons | old | 22 | 26 | 33 | 43 | 0/9/26/6/0 |
| streaming_price | new | 5 | 35 | 32 | 43 | 0/6/16/0/0 |
| streaming_price | old | 5 | 19 | 19 | 28 | 0/6/18/0/0 |

- 新腕: JA最終稿あり 8/9、EN最終あり 6/9(central_bank_mortgage はR0 STOPで記事なし、openai_copyright・semiconductor_earnings はEN STOP)。旧腕: JA 7/9、EN 7/9(hormuz・meta旧はSTOPで記事なし)。
- 注: labels_merged に新腕の重大ラベルは0件、旧腕は2件(meta旧 w1-11・w1-14、同一箇所)。新腕記事でFlagが出ても『既知の重大ラベル』と照合できない箇所は、**未知ケース有用性の人間裁定**(DESIGN §4 KPI5)に回す。
- 台帳Fact数の注: 各腕の `research_ledger/verified_fact_ledger.txt` の `[VERIFIED]` ブロック数。

## 6. 合成参考セット(人工反転14件、KPI本体外)

出典 `er052_output/open233_directional_misread_trial_01/testset_01.json`(決定論置換、Trial専用、Fable代理gold)。実記事に存在しない人工文であり、**実記事KPI(Recall・Flag精度)には含めない**。事故タイプ別の能力確認(特にRollback・否定反転・方向反転)と、検出器の最低限の動作確認にのみ使う。

| syn_id | タイプ | 分割 | Fact | 文 |
|---|---|---|---|---|
| S-01 | 数量時系列 | holdout | HF-009 | # The Fee Plan Arrives, But High Oil Prices Stay |
| S-02 | 数量時系列 | dev | HF-009 | The fee plan appeared, but oil prices stayed high as tensions around the Strait of Hormuz … |
| S-03 | 数量時系列 | dev | HF-009 | What we can see here is that oil prices did not fall across the board immediately after th… |
| S-04 | 数量時系列 | holdout | HF-009 | The fee plan took the stage, but the prices themselves quickly returned. |
| S-05 | 数量時系列 | holdout | HF-009 | This time, the fee plan took the stage, but the price did not leave with it. |
| S-06 | 数量時系列 | holdout | HF-009 | After the fee plan was reinstated and replaced, Brent crude oil futures briefly lost some … |
| S-07 | 数量時系列 | holdout | HF-009 | After the withdrawal and replacement of the fee plan were announced, Brent crude oil futur… |
| S-08 | 数量時系列 | dev | HF-007 | Trump said he would launch the 20 percent fee plan. |
| S-09 | 数量時系列 | dev | HF-007 | The 20 percent plan took the stage about one day after it appeared. |
| S-10 | 数量時系列 | dev | HF-002 | On July 13, a plan suddenly disappeared to charge a 20 percent fee on cargo passing throug… |
| S-11 | 否定反転 | holdout | HF-003 | In other words, no one had actually stopped collecting the fee. |
| S-12 | rollback方向反転 | dev | MUSE-HC-012 | For now, Meta has restored the human concierge feature. |
| S-13 | rollback方向反転 | dev | MUSE-HC-012 | Meta then temporarily put the human-call feature back in service. |
| S-14 | 数量時系列 | holdout | HF-011 | The drop was linked to concern about a US sea blockade of Iran, planned for the next day, … |

## 7. 未確認・不足・注意

1. **人間確認済み重大が4件(目標5件に1件不足)**。K11は『C寄り、Bの余地あり』のため、確定重大としては3件(K01・K02・K03)。K01とK03は同一Fact・同型(Rollback)で独立性が低い(near_dup_group)。人間確認済みの独立サンプルは実質3系統(Rollback・不在断定・発表内容取り違え)。追加の人間確認候補: meta-p2r2-02(開示対象)、sw-p2r2-02(『初めて』の拡張)、hormuz-T0M0r2-01(20%の対象)、RC-K16(時期)、RC-K18/Safety-A2A3-0(支払義務者)。ユーザー確認が取れれば人間確認区分へ格上げできる。
2. 重大の大半(10/17)はSonnet判定、3件はFable確定(Safety-critical gold、ユーザー承認の線引き基準の机上適用)で、ユーザー個別確認ではない。KPI1は『人間確認済みのみのRecall』と『全重大のRecall』を分けて出す。
3. 『否定反転』の実記事由来の確定重大は0件。K02の『Nor has anyone reported…』は不在断定を主、否定反転を副としたが、分類は評価者によって割れうる。
4. 非重大の『境界・軽微』は『重大/非重大』の2値指示により非重大側に置いた。K04/K06/K10(Sonnet暫定)・S0_USER_CHECK 3件(ユーザー回答待ち)・B-xx(Sonnet暫定、B-05は人間確認候補)は、ユーザーが重大と裁定した場合にラベルが反転する。
5. 機械抽出の非重大は弱ラベル(文単位の人間確認なし。『記事内の数値が台帳の同一Factに含まれる』という条件のみ)。誤Flag率の分母としては使うが、確定ラベルとしては扱わない。Fact選択は数値トークン一致による機械選択で、別Factを選んでいる可能性がある。
6. 文の所在を特定できなかった軽微項目: B-04(w1-52), B-07(w2-204), B-06(w2-201)(R0 attempt等の途中稿の引用で、最終記事ファイルに存在しないため除外)。
7. 前後文なし(`context`のbefore/after両方null)のケースがある。記事ファイルに当該文が単独で残っていない、または途中稿・要約単体のみ。Flagger入力の評価では『文単体+台帳』でも判定できる形にしておく。
8. WRITER-EVAL由来(K01等)の旧case_idは `legacy_case_id`。本バンクの `case_id` は `rf_` 接頭辞。
