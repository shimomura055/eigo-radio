# OPEN-238 決定論Regression(修正前/後、¥0、同一プロセス、実行中モジュールへinstall)

runs=26 / 修正前fires合計=2 / 修正後fires合計=0 / 差分run=1
保存済ベースライン(precheck_baseline.json)のfires == 本実行の修正前fires: True
bit単位不変(O2): loose抽出(runner L2838/coverage L475型,文別)=True / 台帳loose抽出=True / L322(changed_number_is_natural_rounding_only 全fact×全文)=True / number_mismatch以外の全finding=True
カウンタ(修正後実行): {'strict_foreign': 2, 'strict_locate': 0, 'loose_extract_percentages': 9803, 'v2_calls': 408}

## run別

| run_id | 修正前fires | 修正後fires | 同一 | strict≠looseの文数 |
|---|---|---|---|---|
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 | 2 | 0 | False | 1 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/meta/nb/p2/rep1 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep1 | 0 | 0 | True | 0 |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2 | 0 | 0 | True | 0 |
| polysemy04_control:open233_polysemy_trial_04/runs/ai_control/control/rep1 | 0 | 0 | True | 0 |
| polysemy04_control:open233_polysemy_trial_04/runs/hormuz/control/rep1 | 0 | 0 | True | 0 |
| polysemy04_control:open233_polysemy_trial_04/runs/meta/control/rep1 | 0 | 0 | True | 0 |
| polysemy04_control:open233_polysemy_trial_04/runs/sewer/control/rep1 | 0 | 0 | True | 0 |
| polysemy04_control:open233_polysemy_trial_04/runs/space_weapons/control/rep1 | 0 | 0 | True | 0 |
| meta_ent01:open233_meta_allfact_note_ent_01/runs/meta/nb/p1/rep1 | 0 | 0 | True | 0 |
| meta_ent01:open233_meta_allfact_note_ent_01/runs/meta/nb/p2/rep1 | 0 | 0 | True | 0 |
| prod_e2e02:bgroup_B3 | 0 | 0 | True | 0 |
| prod_e2e02:hormuz_run03_advanced | 0 | 0 | True | 0 |
| prod_e2e02:hormuz_run03_standard | 0 | 0 | True | 0 |
| prod_e2e02:meta_run03_advanced | 0 | 0 | True | 0 |
| prod_e2e02:meta_run03_standard | 0 | 0 | True | 0 |
| prod_e2e02:neg1_meta_b3prod_a2 | 0 | 0 | True | 0 |
| prod_e2e02:neg2_meta_refresh_a2 | 0 | 0 | True | 0 |
| prod_e2e02:neg3_hormuz_prodrunner_b1b | 0 | 0 | True | 0 |
| prod_e2e02:neg7_meta_prodrunner_b1b | 0 | 0 | True | 0 |

## 差分run

- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2
  - 修正前: [{"fact_id": "EVID-006", "foreign_values": [33.3], "sentence": "The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.", "method": "precheck_number_locate"}, {"fact_id": "CONTROL-004", "foreign_values": [33.3], "sentence": "The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.", "method": "precheck_number_locate"}]
  - 修正後: []

## strict抽出がlooseと異なる文(全run)

- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 #6 loose=[33.3] strict=[] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.

## O3: 'percentage point(s)' 走査(報告のみ・修正しない)

走査テキスト数=36(全run EN + prod_e2e_02 cycles の en_text_before/after_rewrite、重複含む)、該当文=0件

補足走査(別手順・同日): er052_output配下の全 `b1b/article.md` 48本 + prod_e2e_02 runs/*.json の cycles en_text_before/after_rewrite 10本 = 58テキストでも "percentage point(s)" は0件。設計docの91テキスト(重複含む別集合)は再構成していないが、上記2集合とも0件。PERCENT_REの`percent`語境界欠如(5 percentage points→5%)は現実コーパスでは顕在化していない。修正は別管理ID。
