# SPEC_LEDGER_02: ユーザー§3 検証要件の充足(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02)と台帳追記

2026-10-26 / 原文=`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_USER.md` §3(12要件)。Family別の未検証項目は明示。Fable独立受入(項10)・SSOT更新(項11)・Dangling Reference(項12)はFable側確認を含む。

## 1. §3 要件チェックリスト(本委任の自己確認。判定はFable)
| # | 要件 | 状態 | 証拠(path) |
|---|---|---|---|
| 1 | Family XYZそれぞれの正式初回Production経路へ適用 | 充足(共通`generate_candidates`へ配線。X/Y/Zの正式runner KP stageをfreshで実行) | `WIRING_01.md`、`evidence_runs/*.log`、`EVIDENCE_01.md` §1-2 |
| 2 | Standard/Advancedへの適用 | 充足(KP段は共通。a2=Std・b1b=Advをレベル別に実行) | `EVIDENCE_01.md` §2 |
| 3 | Human Reviewあり/なし両経路との整合 | 充足(HRあり=候補表に`rescue_note`・旗、HRなし=`rescue_auto_ok`でauto判定[M1=QA PASSでauto、revert=NOT_REJUDGEDでauto不可]、`resolve_gloss`後もauto不可のまま戻さない) | `er119_kp_rescue_wiring_test_01.py::test_w1`・`test_w6`、`er125_kp_rescue_production_test_01.py::TestFlowAndPersistence`、replay |
| 4 | retry/fallback/regeneration/resumeでの救済結果の一貫性 | 充足(resume=読み戻し・API 0[fresh再起動でsha不変]、gate内retry非消費、外側retryはM3、provenance driftはlogのみ。regenerationは新roundの候補ファイル再生成=既存仕組み) | `test_w2`・`test_w2b`・`test_w6`、`EVIDENCE_01.md` §2 |
| 5 | 本文一致・5語以下・自然さ・意味の保持などの既存品質条件を維持 | 充足(救済後の句は選定段の通常検査・最終Gateと同一引数のvalidator・CMUを再通過。品質規則の緩和なし。M1=重複再照合) | `er125 _default_selection_check`/`_gate`、`test_w5`、`TestAdversarialNoFalseAccept` |
| 6 | 不当候補の誤受理を防ぐRegression/Validator/integration test PASS | 充足 | `RESULT_PACKET_KPRW2.md`(3) |
| 7 | 既存敵対的テスト85件・実データ315種の回帰確認 | 充足(敵対的85件=`er105_kp_rule_compliance_test_01.py::TestAdversarial85`+`TestAdversarialNoFalseAccept`PASS。実データ=`rescue_eval_prod_02.json`: 351対中gate合格348のうち救済で変化0、不合格3は救済対象外。量化詞parity `quant_parity_02.json` n_mismatch=0) | `rescue_eval_prod_02.json`、`quant_parity_02.json` |
| 8 | 各Familyの正式runtime evidence | **Family別**: Y=自然発火あり(選定段の慣用句の核+revert)で最も充足。Z=fresh発火なし+replay M1で補完。X=fresh発火なし+replay(通常フロー/短縮非救済)。**X/Zは自然発火の実run証拠なし**(経路到達は全6 level-runで確認) | `EVIDENCE_01.md` §2-3,5 |
| 9 | actual model_id・routing・Prompt等の必要な証拠 | 充足(全call`gpt-6-luna`、routing`B1_SUPPORT/A2_SUPPORT`、Prompt 2/2-V sha固定値一致、canonicalization等のtemplate/schemaは無変更[git diff空]) | `evidence_01.json`、`EVIDENCE_01.md` §2 |
| 10 | Fable独立受入 | Fable側 | - |
| 11 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新、Git反映 | SSOT=Fable(文案は`RESULT_PACKET_KPRW2.md`(9))。Git=本委任でcommit/push | commit hash |
| 12 | Dangling Referenceなし | 旧testの`TestUnwiredInProduction`等の旧規則を撤去/改訂(FIX_01 M4)。残存は下記§3 | §3 |

## 2. QA再判定の限界(Opus論点2(a)の明記要求)
救済後のQA 12項目再判定は、承認済みfulltext canonicalization promptを無変更で使い、**`display_phrase`に救済後keyを渡す**。したがって元の表層形→救済後keyの変換を評価する4項目(`qa_meaning_or_usage_unchanged`/`qa_core_meaning_preserved`/`qa_no_semantic_role_loss`/`qa_not_over_minimized`)は**救済後keyの自己比較**となり、ほぼ必ずPASSする。変換の正しさ(原形化が妥当か)は、(a)最終Gateと同一引数の決定論validator+CMU(`_gate`)、(b)M1の{display語, LLM提案語}への選択限定(新しい語形を作らない)、(c)revertは表層形そのもの、で担保される。QA再判定が担保するのは「救済後keyが学習単位として自然か」「返却keyが救済後keyと一致するか(一致しなければNOT_REJUDGED=HRのみ)」であり、変換の意味保持そのものではない。evidence実測: M1=一致(2/2)、revert=不一致(0/1)。
- 影響: M1救済はHRなしでもauto採用され得る(決定論validator+M1限定+QA PASSの3条件)。revert救済は実質HRのみ採用。

## 3. 旧規則の撤去・残置のGrep
- 撤去/改訂: `er105_kp_rule_compliance_test_01.py::test_idiom_exceptions_are_not_wired`→`test_idiom_exceptions_only_inside_candidate_generation_context`、`test_rescue_flow_not_wired_in_er105`→`test_rescue_wiring_in_er105_is_limited_to_approved_hooks`、`er125_kp_rescue_production_test_01.py::TestUnwiredInProduction`→`TestWiringSites`、`test_7b_without_h1_wiring…`→`test_7b_outside_generate_candidates_context_not_rescued_M2`。
- 残置(意図): `test_lexical_have_not_blocked_but_modals_and_be_remain_blocked`の拒否側assert(`will be missed`/`could not bear`/`time is money`/`is money`)、敵対的15件の`expect:blocked`、互換名`_wired_h1`(恒等context。呼出3か所とtools/make_rescue_eval_prod_01.pyが参照)。
- Grep(`idiom_exceptions_are_not_wired|rescue_flow_not_wired|TestUnwiredInProduction|without_h1_wiring`, *.py): 旧名は改訂注記のdocstring(`er105_kp_rule_compliance_test_01.py:85,178`)のみ。実体なし。

## 4. Opus台帳(Fable sync用文案)
`OF-KPRW-M1〜M4`=IMPLEMENTED→TESTED(FIX_01、test名)。`R1`〜`R7`: R1/R2/R4/R5/R6=IMPLEMENTED(test済み)、R3=EVIDENCED(報告のみ。revert QA省略案はFable判断)、R7=OPEN追記案(`RESULT_PACKET_KPRW2.md`(9))。既存`OF-KPRS-M1〜M6/R1〜R4`・`OF-KPRS2`: IMPLEMENTED→EVIDENCED(M2は『文脈限定』へ変更して採用[OF-KPRW-M2]、M5は『救済済みauto不可はretry条件に数えるがF1累積除外には入れない、救済失敗のみF1累積』[OF-KPRW-M3]、R3は未実装[観測のみ]のまま)。
