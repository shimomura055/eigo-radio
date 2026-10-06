# 00c Before Evidence固定(OPEN-233-LEDGER-CLARITY-P-TRIAL-01 Phase 0、¥0、2026-10-06)
固定ファイル: `er052_output/open233_ledger_clarity_p_trial_01/phase0/FREEZE_P01.json`(sha256 26件)。比較対象はmetaテーマ1本。hormuz/small_bagはheld-out候補、今回は対象外。コード・台帳・SSOT未変更。

## 1 Before台帳(meta run_03、15 fact: MUSE-HC-001〜015)
| 項目 | 内容 |
|---|---|
| 台帳 | `er019_output/meta/run_03/ledger/verified_fact_ledger.txt`(research_ledger配下と同一sha) |
| HC-012 claim(逐語) | MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 |
| B3 brief | `storyline_b3/selected_brief.md`: 「…機能を当面ロールバックした」(片仮名のまま、曖昧さ未解消) |
| JA R0 | `ja_writer/original.md`: 「人間コンシェルジュ機能を当面、以前の状態に戻しました」(**誤読はJA R0で既に発生**) |
| EN記事 | b1b: "restored ... to the way it had been before"(誤) / a2: "changed ... back to how it was before"(曖昧) |

## 2 meta Before run(e2e_02、現行構成。e2e_01 baseline_old9は旧仕様frozen)
| run | 記事由来 | final_state | cycle | Rewrite | human_review | 円 |
|---|---|---|---|---|---|---|
| meta_run03_advanced | er019 b1b | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 | 0 | 2.41 |
| meta_run03_standard | er019 a2 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | 2 | 0 | 4.73 |
| neg1_meta_b3prod_a2 | b3prod a2 | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 | 0 | 3.07 |
| neg2_meta_refresh_a2 | refresh a2 | RESOLVED_REWRITE_THEN_DOWNGRADE | 2 | 1 | 0 | 4.58 |
| neg7_meta_prodrunner_b1b | prodrunner b1b | RESOLVED_STAGE2_DOWNGRADE | 1 | 0 | 0 | 2.51 |

## 3 HC-012 Rollback型(e2e_02)
| run | 文(逐語) | Checker | 最終 | 真ラベル |
|---|---|---|---|---|
| advanced | The company also restored the human concierge feature to the way it had been before, at least for now. | 機械(negation_polarity_mismatch)検出、LLM/S1二次=ACCEPTABLE | ACCEPTABLE | **Y(重大、A5-0型)=出口で見逃し** |
| standard | The company also restored its human help feature to its earlier form, at least for now. | 候補にならず(stage2_resultsに無し) | 未判定、文は最終記事に残存 | 未ラベル |
| neg2 | The company also changed the human concierge feature back to how it was before, at least for now. | 機械検出、LLM=ACCEPTABLE | ACCEPTABLE | N(G-06曖昧型) |
| neg1 | For now, Meta has pulled back the human concierge feature. | Stage1 BLOCKING→downgrade | ACCEPTABLE | 忠実(復元型でない) |
| neg7 | Meta then temporarily put the human-call feature back on hold. | Stage1 BLOCKING→downgrade | ACCEPTABLE | 忠実(復元型でない) |
要約: 復元型3/5 run、Checker候補2/3、重大(Y)1/5、human_review到達0。e2e_01旧仕様でも同3 runで復元型出現(機械検出あり、全てACCEPTABLE、未ラベル)。

## 4 meta関係gold(runner L9817-9900)
| ID | related_fact | text_substring | 期待 |
|---|---|---|---|
| A5-0 | HC-012 | temporarily put back the feature | BLOCKING |
| A4-0 | HC-006 | completed the exchanges with users | BLOCKING |
| A4-1 | HC-012 | actually speaking with human staff | ACCEPTABLE(監視、委任_57) |
| B4-a | HC-002 | take over when AI alone has trouble | BLOCKING |
| Meta-1 | HC-010 | needed user information to continue | QUALITY(監視、委任_55) |
| Meta-2 | HC-012 | needed user information to continue | QUALITY(監視、委任_55) |
非meta(除外): B3/B3-same@neg5(HF-007)、A2A3-0(HF-003)。

## 5 Entertainment基準値(決定論、Before)
| 記事 | 文数 | 語数 | 平均文長 | TTR | EN逐語率(8語) |
|---|---|---|---|---|---|
| er019 b1b | 26 | 362 | 13.92 | 0.4917 | 0.0 |
| er019 a2 | 31 | 349 | 11.26 | 0.4900 | 0.0 |
| e2e02 standard最終 | 35 | 335 | 9.57 | 0.5134 | 0.0 |
| e2e02 neg2最終 | 31 | 351 | 11.32 | 0.4872 | 0.0 |
注意: 台帳が日本語のためEN逐語率は構造上0.0で指標として無効。代替としてJA original.mdの台帳との12文字連続一致率=0.1518(731字)。advanced/neg1/neg7最終記事は全文未保存(advancedはb1bと同一由来、neg1/neg7は除外)。Phase 1ではJA側逐語率を主指標にすることをPMへ提案。
