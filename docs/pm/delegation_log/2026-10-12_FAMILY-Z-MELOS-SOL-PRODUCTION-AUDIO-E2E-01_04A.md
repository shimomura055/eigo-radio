# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04A(er061 意味保持Validator)2026-10-12

Status: Validator実装+実呼出calibration PASS(`validator_calibration_01.json` all_ok=true)。**PRODUCTION_WIRED未達**(er026統合は後続)。実費 **約¥4.03**(上限¥8以内、実測)。

## 1. 実装概要
- `er061_family_z_semantic_validator_01.py`(Family Z一般仕様、story_key非依存の構造。anchors/seed置き場のみMelos定数)
- `validator_anchors`: `build_validator_anchors(seed_dir)` は候補稿を引数に取らない(構造的に新稿を見られない)。`er026_output/family_z_production_e2e_01/melos/validator/anchors.json`(sha256_self=`9aafa24d...bb5`、seed_sha256=Seed凍結shaと一致)。`freeze_anchors`は既存ファイルを上書きせずshaのみ照合、`load_anchors`は改ざん/seed不一致で`AnchorsIntegrityError`。`SEED_PROVENANCE.json`の`validator_anchors*`欄のみ更新(seed.json/primary_text_excerpt.mdのshaは不変、test確認)。
- anchor 18件: 人物役割・関係3(R1-R3)/重要出来事6(E1-E6、順序付き)/因果4(C1-C4)/順序1(S1)/結末1(N1)/魅力2(M1,M2)/新Fact無し1(X1)。禁止結末family3(FE1間に合わない/FE2友が死ぬ/FE3王が改心しない、末尾3段落のみ走査=高精度化)。名前は必須にしない(Melosのみ、WARN止まり)。
- 第1層(決定論): hard FAILは禁止結末・外国人名ルール(`foreign_name_rules.full_names`にフルネーム列挙、Melosは対象無し)・主要アンカー全欠落のみ。個別アンカー欠落は WARN。順序判定なし。
- 第2層: routing `FAMILY_Z_SEMANTIC_JUDGE`(gpt-6-luna、`require_model`)、Responses API、JSON schema strict(全フィールドrequired/additionalProperties=false)、項目別 preserved/altered/missing × minor/major、`evidence_quote`の逐語存在を決定論検証(引用符/空白/大小/Markdown強調のみ正規化)。捏造引用・coverage欠落・category不一致は応答を無効扱い(1回再要求→なお無効ならNEEDS_REVIEW)。`missing`のみ「無いこと」を引用できないため空引用を許容(引用を書いた場合は検証)。重大改変(major)=FAIL、軽微=WARN。FAIL時は再判定1回、2回一致(FAIL categoryが重なる)でFAIL、不一致NEEDS_REVIEW。第1層FAIL×第2層非FAIL=NEEDS_REVIEW(自動では通さない、`stop_required=True`)。
- 設計書(M8)カテゴリに **`added_fact`(新Fact追加なし、anchor X1)を追加**(F8「新Fact追加」を実LLMで判定するため。要Fable承認/追認)。
- Std追加: `std_vs_adv_checks`(一致文率>=50%でFAIL、平均文長>Adv×0.85でWARN、段落数不一致=FAIL、アンカー初出段落の順序逆転=WARN)。**段落数不一致をFAIL**にしたのは04Bの境界写像(b1,b2をそのまま写像)が壊れる構造問題のため(設計書は「検証=段落数一致」のみでFAIL/WARN未規定、Fable判断で変更可)。
- `revalidate_after_local_rewrite(text_before, text_after)`: 第1層再実行+文単位diff記録+`regressed_to_fail`。第2層は実施しない。
- 公開API: `validate_semantic_preservation(candidate_text, level, *, client, anchors, adv_text, tracker, out_dir)` -> `validator_result.json`+`validator_summary.md`(`schema_version=er061_validator_result_v1`、layer1/layer2/std_checks/verdict/stop_required/model.actual_model_ids/usage_total/cost_jpy/candidate_sha256/anchors_sha256)。`CostTracker(cap_jpy)`で上限超過見込みSTOP(`JudgeBudgetExceeded`)、actual model不一致STOP(`JudgeModelMismatch`)。
- 互換: `check_character_name_rule`/`restore_character_names` の互換ラッパ(DeprecationWarning、前者は第1層へ委譲(ok, hard_fail_ids)、後者は本文無変更)。**er026本体の旧関数は削除・編集していない**(禁止範囲)。superseded注記はer061側に記載、er026側の注記/置換は統合時。

## 2. Calibration結果(実呼出、gpt-6-luna実測、`er060_output/melos_production_e2e_01/validator_calibration_01.json`、各fixtureの`validator_result.json`/`validator_summary.md`は`validator_calibration_01/<Fx>/`)
| fixture | 期待 | 最終verdict | 第1層 | 第2層(judge有効呼出) | FAIL category(第2層確定) | 費用 |
|---|---|---|---|---|---|---|
| F1 Trial②R2 | PASS | PASS | PASS | PASS(1) | - | ¥0.22 |
| F2 既存Luna | PASS | WARN* | PASS | WARN(1) | -(minor: 魅力M2『日没でなく夜明け描写』) | ¥0.24 |
| F3 名前省略 | PASS | WARN* | PASS | WARN(1) | -(minor 4件) | ¥0.28 |
| F4 友の関係欠落 | FAIL(role_relation/event) | FAIL | WARN | FAIL N=2一致 | role_relation,event,causality,ending,charm,added_fact | ¥0.52 |
| F5 間に合わない | FAIL(ending) | FAIL | FAIL(FE3 trust is for fools) | FAIL N=2一致 | ending,event,causality,sequence,charm,added_fact | ¥0.68(無効1回再要求含む3 call) |
| F5b 王が改心しない | FAIL(ending) | FAIL | PASS | FAIL N=2一致 | ending,causality,event,sequence,charm,added_fact | ¥0.64(無効1回含む3 call) |
| F6 因果反転 | FAIL(causality) | FAIL | PASS | FAIL N=2一致 | causality,ending,event,role_relation,sequence,charm,added_fact | ¥0.48 |
| F7 帰路の困難なし | FAIL(event) | FAIL | WARN | FAIL N=2一致 | event,causality,sequence,charm,added_fact | ¥0.44 |
| F8 新Fact追加 | FAIL(added_fact/event) | FAIL | PASS | FAIL N=2一致 | added_fact,event,ending,causality,role_relation,sequence,charm | ¥0.53 |
- 実費合計 **¥4.0265**(17 call、input 44,896 / cached 21,064 / output 45,143 tokens)、model_id実測 `gpt-6-luna`(要求と一致)。上限¥8に対し約50%。
- *F2/F3は期待PASSに対しverdict=WARN(`stop_required=False`、非ブロック)。judgeが軽微指摘(F2「帰路が夜明けで日没でない」、F3「川の位置が結婚式前後」「Std的な公正な裁判の追記」等)を出したため。FAILではなく通過可なのでacceptance(F1〜F3が通過)は満たすが、字義どおりの『PASS』ではない点を明記。
- FAIL系の受入: 期待categoryが2回(初回+再判定)とも含まれること(any-of)。全6 fixtureで充足。

## 3. 受入条件充足
- anchors sha凍結・原作Seedのみ作成・改ざん検知: 充足(test: AnchorsTest 5件)。
- 第1層/第2層構造、schema strict、引用逐語検証、NEEDS_REVIEW、互換ラッパ、Std同一本文(境界0.5/0.25 test)、Local Rewrite再検証: mock test 55件(`er061_family_z_semantic_validator_01_test_01.py` 54件+calibration整合1件)。
- 実呼出calibration: F1〜F3通過、F4〜F8(+F5b)が期待categoryでFAIL・N=2一致、費用¥4.03<¥8: 充足(judge変更なし)。
- Regression(新規failure 0): `er061_..._test_01`+`er060_family_z_foundation_test_01`+`er006_model_routing_gpt6_wiring_test_01` 72件PASS、`er026_family_z_fiction_production_runner_01_test` 19件PASS。

## 4. er026統合時に必要な変更点
1. `run_text_stage`の `check_character_name_rule`/`restore_character_names` 呼出を `validate_semantic_preservation`(Adv: level=`b1b`、Std: level=`a2`+`adv_text`)へ置換。旧関数は残置し `superseded` 注記(`known_gap`文言と合わせ更新)。`verdict in (FAIL, NEEDS_REVIEW)` は `stop_required` でSTOP(自動で通さない)。
2. Validatorの`CostTracker`を統合runnerのBudgetGuard(上限¥300)と接続(per-call実測をBudgetGuardへ加算)。1回のvalidateでjudge呼出は最大4(PASS時1、FAIL時2、無効応答の再要求で最大4)。
3. Local Rewrite採択後は `revalidate_after_local_rewrite`(第1層)を呼び、`audio_text_deviation`と合わせて保存(M6、04C連携)。KP source gateへは原稿(canonical)のまま渡す。
4. Std検証は 04Bの`std_adjust`後に `level='a2', adv_text=<Adv最終稿>`。段落数不一致はFAIL。
5. 外国人名ルール: story追加時は anchors の `foreign_name_rules.full_names` にフルネームを列挙(Melosは対象無し)。他storyは別anchorsファイルを `freeze_anchors`で作成(`ANCHORS_PATH`等はMelos定数)。

## 5. 残リスク・判断依頼
- **category特異性が低い**: judgeは一つの根本改変から複数カテゴリへFAILを波及させる(F7は『event欠落』のみの改変でcausality/charm/sequence/added_factもFAIL)。期待categoryが含まれることは確認できたが、「どのcategoryが根本原因か」の厳密な分離はできていない。人間レビュー時は最初の改変箇所をsummaryの`evidence_quote`から確認すること。
- **無効応答率**: 17 callのうち2 call(約12%、F5/F5b)で`evidence_quote`が逐語不一致となり再要求。再要求で回復したが、コスト約+¥0.2/回、2回続くとNEEDS_REVIEW。
- F2/F3はWARN(誤読を含む軽微指摘)。WARNは非ブロックだが、実運用でminorが多発する場合はWARN内容の目視が必要。
- 第1層の禁止結末regexは高精度化のため末尾3段落限定・'laughed'は除外。F5の'too late'(末尾4段落目)は第1層では検知されず第2層(確定FAIL)が担当。
- `added_fact`カテゴリ追加(設計書M8のカテゴリ6種+1)と、Std段落数不一致=FAILはFable判断/追認が必要。
- 各fixtureの`validator_calibration_01/<Fx>/validator_result.json`の`cost_jpy`/`usage_total`は共有トラッカー累積値(コード修正前の実行のため)。fixture別の正しい値は`validator_calibration_01.json`の`rows[].cost_jpy`。コードは修正済み(`test_cost_is_per_validation_with_shared_tracker`)。
- Validator品質の最終検証(Std作成稿・Trial③稿への適用)は実Writer出力後。
