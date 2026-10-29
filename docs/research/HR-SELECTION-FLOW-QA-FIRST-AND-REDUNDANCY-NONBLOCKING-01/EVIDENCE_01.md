# EVIDENCE_01(委任_03A 2節。runtime evidence、copy-run方式。2026-10-29)

方式: `C:\Users\tensh\eigo-radio-evidence\hrq3a\`(使い捨て・正式runを汚さない・git管理外)。X/Y/Z共通の正式経路関数 `er119_kp_wiring_01.run_kp_with_review`(runnerのKP stageが呼ぶ共通入口。X=er019:1022、Z=er026:2171[src_fn付き]、Y=er121:_kp_review_step)を、**実LLM**・runnerと同じ引数形で新しいkp_dirに呼ぶ(tool=`tools/evidence_hrq3a_01.py`: gen→select→finalize)。runner本体は実行・編集していない。本文は既存copy-run(NXW02C)の本文(review.text_sha256一致を検証)。使用モデルは正式経路の既定(`routing.require_model`: SUPPORT系=最新世代の承認済みモデル。評価用の別モデルは使っていない)。人間選定はCLI相当の `rv.op_select`(ranks指定)で再現し、重複しやすい組合せを選んで最終Redundancy QA(実LLM)を発火させた。
STOP確認: 各有料run前に `tools/stop_scope_check_01.py --managed-id HR-SELECTION-FLOW-... --run-dir <evidence>`(stopchk*.json): rc=0(非停止)。

## 6組合せ(仕様①=presentable_filter、仕様②=redundancy_alarm.json+続行)
kp_dir=`<evidence>/hrq3a/<fam>/key_phrases/<lv>/`(Z Advの別作品=`z_tth2`)。行は kp_candidates.json:presentable_filter の行 / redundancy_alarm.json の `telemetry` / kp_selection_final.json の `redundancy_telemetry` の行。
| 組合せ | 仕様①: presentable_filter(checked/dropped/presentable) | 仕様②: 人間選定(KP/Vocab)→最終Redundancy QA(実LLM)→アラーム | KP stage通過 | Status |
|---|---|---|---|---|
| X Std(a2、月のしわ本文) | kp_candidates.json:998 `checked 9, dropped 0, presentable 9` | 選定: to blame/work out/hold heat in + insulation/shrinkage。**REDUNDANCY_ALARM**(`hold heat in`×`insulation`、候補QA1+最終1=alarm_count 2、blocking=false)redundancy_alarm.json:46、final.json:92 | `reached_next_stage=runner_kp_stage_passed`、state=FINALIZED | **PASS(実LLM ALARM)** |
| X Adv(b1b) | :1213 `checked 11, dropped 0, presentable 11` | `keep heat in`×`insulation` **REDUNDANCY_ALARM** alarm_count 2。redundancy_alarm.json:46 | 同上 | **PASS(実LLM ALARM)** |
| Y Std(a2、NXW02C Y本文) | :888 `checked 8, dropped 0, presentable 8` | `when it suits someone`×`handy` **REDUNDANCY_ALARM**(使用場面・概念上の役割がFAIL)alarm_count 2。redundancy_alarm.json:46 | 同上 | **PASS(実LLM ALARM)** |
| Y Adv(b1b) | :1199 `checked 15, QA/gloss除外0、presentable 11`(提示上限でcap。生成段階の既存除外=CMU辞書未登録語redeliveriesを`dropped`に1件記録) | 選定: doesn't sit right/take the trouble to/end up receiving it + beforehand/repeatedly=**REDUNDANCY_PASS**(アラーム0)。final.json:42 | 同上 | PASS(PASS分岐。ALARM分岐は実記事 `er121_output/.../surname_choice/run_02/key_phrases/b1b/redundancy_alarm.json:53` alarm_count 2[③本文意味を含む。委任_02r、読取のみ])+委任_02rの複製run test |
| Z Std(a2、メロス Std本文) | :1035 `checked 9, dropped 0, presentable 9` | 2回選定(pull someone under/lose one's life/in someone's place等)とも REDUNDANCY_PASS(アラーム0)。redundancy_alarm.json:8 | 同上 | PASS(PASS分岐。ALARMは下のZ Advで実LLM取得) |
| Z Adv(b1b、別作品=tell-tale heart。メロスb1bは2回選定とも重複なし) | `z_tth2` kp_candidates.json:1165 `checked 13, canonicalization_qa_dropped 1(rescue_unverified=M8の未検査救済候補を提示前に除外)、presentable 10` | `never stir`×`motionless` **REDUNDANCY_ALARM**(意味・使用場面FAIL)alarm_count 2。redundancy_alarm.json:46、final.json:92 | 同上 | **PASS(実LLM ALARM + 実LLMでのQA不合格相当の提示前除外)** |

- 仕様①の「QA不合格候補が提示されない」: 実LLM生成でQA/gloss不合格が生じたのは Z Adv(z_tth2)の1件(`rescue_unverified`=救済候補のQA再判定が通らず提示前に除外、M8)。他の5組合せは除外0件(全候補がQA PASS)で、`presentable_filter`は0件でも記録される(version=presentable_v1_2026-10-29)。QA FAIL/gloss HR待ち候補の除外そのものは `er119_hr_selection_flow_test_01`(U1/M1/M8)とgolden(KP-PHRASE7-WORD5-PRODUCTION-01/golden_03 s04/s06/s07/s10)で固定。
- 仕様②の非停止: 全6組合せで `blocking=false`、finalize後に `state=FINALIZED`(KP stage通過)。**resume**: Z Advのfinalizeを同一引数で再実行 → API 0(raw_usage_log 12行→12行、費用不変)・FINALIZED・`wrote=[]`(ALARMキャッシュ再利用=M5)。**revoke→再選定**(Z 2回選定時)も確定ロック→revoke→select→finalizeで動作(KP側retry/regenerationの経路)。
- テレメトリ値(`redundancy_telemetry`): `final_qa_status`/`final_qa_alarm_pairs`/`candidate_qa_alarm_pairs`/`alarm_count`/`nonblocking=true`/`review_status`/`filter_version`/`reached_next_stage` を上記file:lineで確認済み。
- 後続stage(gate/assemble/音声/page)到達そのもの: 本evidenceはKP stage通過(`runner_kp_stage_passed`)までの共通関数。runner全工程(TTS等の有料)は費用上限と03B占有のため実行していない。runnerの該当箇所は重複で止める経路を持たない(NUANCE_REDUNDANCY_CONSISTENCY_01.md)。

## ニュアンス解説経路(1節で修正した3経路の発火証拠。API 0・mock)
`tools/nuance_evidence_hrq3a_01.py`(4 test実行、一時dirを `<evidence>/hrq3a/nuance_mock/case_01..04` へ複製)。
| case | 内容 | 証跡 |
|---|---|---|
| 01 | 重複するKP/Wordを選んだまま採用 → 確定継続(旧: ISSUEで拒否) | `case_01/run1/b1b/study_text/confirmed_nuance.json`(redundancy_alarms 1件)、`nuance_redundancy_alarm.json`(alarm_count=1、nonblocking=true)、`nuance_result.json`(`final_overlap_check.verdict=alarm`、ADOPTED、ページ生成成功) |
| 02 | 重複なし → アラーム0を記録(0件でもファイルを書く)、verdict=pass | `case_02/.../nuance_redundancy_alarm.json`(alarm_count=0) |
| 03 | 確定後にKP/Word確定集合が変化 → 旧: NuanceStale STOP / 新: 続行+`kp_word_set_changed_after_confirm=true` | `case_03/.../nuance_result.json` |
| 04 | 候補単位のpool_conflicts(②で選択)→ 確定+アラーム、ISSUEファイルなし | `case_04/.../nuance_redundancy_alarm.json` |
候補段階の除外(KP/Word重複=NG→提示前に破棄)は既存test(`test_kp_word_overlap_is_discarded_before_hr_and_not_replaced`)で不変を確認。

## 費用(実LLM。`raw_usage_log.jsonl`をpricing_snapshot×USD_JPY=160で換算、docs/pm/tools/daily_dev_cost_01.pyのprice_record)
合計 **¥20.87**(X 3.84 / Y 4.80 / Z(メロス)4.55 / Z tell-tale heart 候補生成2回+最終QA 約7.7[うち1回は私の環境変数設定ミスで別本文の候補を生成した無駄打ち約¥0.6を含む])。上限¥30以内・都度¥50目安内。
