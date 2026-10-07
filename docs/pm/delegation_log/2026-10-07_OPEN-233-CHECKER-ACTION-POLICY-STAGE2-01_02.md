# 2026-10-07 OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_02(①②のTrial実装[スイッチ既定OFF]→dev offline replay→rubric調整≤2版→held-out 1回→事前登録判定)

## 管理ID
OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01(委任_02)

## 並行タスク
なし。直前: 委任_01(W1/W2、Stage1候補化率、replay_targets)完了・未commit。設計v2・事前登録(`docs/pm/checker_action_policy_01/{design_02.md,preregistration_stage2.md,human_review_priority_v1.md}`)完了・未commit。

## 性質/到達上限Status/禁止事項
- 性質: Trial実装+offline replay(API有料)。**全新規挙動は環境変数スイッチ既定OFF**、Production既定不変。Production配線・SSOT編集・CURRENT_SPEC変更禁止。
- 予算: **段階2合計¥200、¥180でSTOP**。夜間総予算¥1000のうち消費済み≈¥21。
- 事前登録(`preregistration_stage2.md`)の合否ライン・測定順序・rubric調整≤2版・held-out 1回を厳守。**held-out(`er052_output/open233_stage0_01/reclass/split.json`)は手順(4)まで開かない。**
- 並列: offline replayはAPI callのみなので最大4並列(単層)。同時プロセス≤4。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-0=本委任文を保存+check.json)。

## 事前指定Read一覧
- `docs/pm/checker_action_policy_01/design_02.md`(§1 ①、§2 ②、M1〜M4・O1〜O3)、`preregistration_stage2.md`、`human_review_priority_v1.md`
- `er052_output/open233_stage2_01/precheck/{stage1_candidate_rate.md,replay_targets.json,replay_off_identity.json,r3_support_ids_inventory.md}`
- runner `er052_open233_self_recovery_flow_runner_01.py`(Stage2判定・2nd opinion・cycle再利用・`rewrite_ranges_ladder`・構造要素処理・actor_guard)、`er052_open233_stage1_coverage_checker_01.py`、`er052_open233_stage2_w1w2_test_01.py`
- `er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl`(dev項目のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep: runner内 `STAGE2_SECOND_OPINION`/`STAGE2_VERDICT_REUSE_NONBLOCKING`/`rewrite_ranges_ladder`/`actor_guard`/`structural_element_reasons`。
- 追記位置: runner `run_stage2`(②A)・`apply_stage2_second_opinion`・reuse登録/参照部(e)・`rewrite_ranges_ladder`(①B)。新規関数は新モジュール `er052_open233_checker_action_policy_stage2_01.py`。
- 更新位置: `docs/pm/ACTIVE_TASK.md`固定ヘッダ+本文1行、`docs/pm/RESULT_PACKET.md`上書き(12行以内)。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は編集しない。

## 実装(すべてスイッチ既定OFF、単体テスト付き)
A. ②「読者信念テスト」`OPEN233_STAGE2_READER_BELIEF=1`: (a) ガード対象を決定論で付与(`guard_target`: 否定・不在/全称/方向・極性/主体の新規出現・置換/数値。M3) (b) Stage2 promptにreader_beliefとbelief_vs_ledger(contradicts/unsupported_new_claim/consistent/unclear)を出力させる追記+語り手の枠(一人称・you・問いかけ)は世界主張として扱わない項(M2) (c) 同一call内でcontradictsなのに非BLOCKINGの出力は無効→再判定1回、再度矛盾ならBLOCKING扱い(Rewrite増側と記録) (d) guard_targetの格下げは2nd opinion両callがconsistentのときのみ成立。2回目は文を見せずreader_beliefとLedgerのみで判定(O1) (e) cycle2での前回判定再利用はguard_targetで禁止 (f) r3 support_fact_ids保存ON(`OPEN233_SAVE_R3_SUPPORT_IDS=1`)。
B. ①構造要素Rewrite規則 `OPEN233_STRUCTURAL_REWRITE_RULES=1`: (a) 構造要素=タイトル・見出し・一行要約・Hook (b) 全書換え手段に4照合必須(主体・代名詞集合が元の部分集合/極性不変/数値不変/形式)。主体語の差し替えは禁止 (c) 不通過→再生成1回→不通過なら元のまま+QUALITY記録、削除はHook以外不可・Hookは最終手段 (d) 書換えた単位はW2経由でRecheckへ。
C. 単体テスト: A/Bそれぞれ ON/OFF、M1(1語追加は許可・主体差し替えは不通過)、M2(一人称タイトルがBLOCKINGにならない判定の入力例)、(c)(d)(e)の分岐。既存テスト全件PASSを確認。

## 測定(順序厳守、各段階で費用記録)
(0) Stage1候補化率: 委任_01の結果を転記(済)。
(1) W1/W2回帰replay: スイッチONでqvqc rep2を決定論部分+Recheck 1回で再生し、タイトルがT単位としてRecheck対象になることを確認。
(2) ②replay dev: 33本のうちdev項目に紐づく記事でStage1候補を固定、Stage2のみ新構成で再判定(2nd opinion含む)。ライン2/3/4/5/7/8。不合格ならrubric調整(最大2版)。2版で未達なら「②不合格=rubric追記打ち止め(O3)」として記録しSTOP(①は続行)。
(3) ①Rewrite→Recheck再実行: 構造要素にBLOCKING findingがある単位を対象に新規則でRewrite→4照合→Recheck。ライン1/6、構造要素由来STOP≤3%、Checker由来の新規NG。
(4) held-out 1回: (2)(3)の最終構成でheld-out記事(Checkerログあり分のみ)を1回だけreplay。結果を見てからの調整禁止。
(5) 事前登録判定+人間確認パック `er052_output/open233_stage2_01/eval/HUMAN_REVIEW_PACK_STAGE2.md`。
(6) 面白さ代理指標: `docs/pm/stage0_01/narrative_count.py`、ユーザー盲検読み比べ用ペアを `eval/pairs_for_user/` に匿名で用意。「非劣性未確認」と明記。

## 実行コマンド全文
- テスト: `python -m unittest er052_open233_checker_action_policy_stage2_01_test_01 er052_open233_stage2_w1w2_test_01 --verbose`(+既存runner/checker全テスト)
- replay: `python er052_output/open233_stage2_01/replay_stage2.py --stage dev --budget-jpy 180 --max-workers 4`(他stageも同スクリプトの`--stage`引数)
- 既存回帰: `python -m unittest er052_open233_self_recovery_flow_runner_01_test_01 er052_open233_stage1_coverage_checker_01_test_01 er052_open233_recheck_coverage_test_01 --verbose`

## SSOT追記文
SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は編集しない(委任範囲外)。結果は `er052_output/open233_stage2_01/eval/STAGE2_RESULT.md` に保存、反映はFable。

## 出力・記録
- `er052_output/open233_stage2_01/{replay_dev/,replay_heldout/,eval/}`、`eval/STAGE2_RESULT.md`、`cost.json`。
- `docs/pm/ACTIVE_TASK.md` 固定ヘッダ+本文1行、`docs/pm/RESULT_PACKET.md` 上書き(12行以内)。

## Git(2回)
(i) 実装+テスト完了時点で個別add(runner・checker・tests、`docs/pm/checker_action_policy_01/*`、`docs/pm/opus_l2_review_checker_action_policy_01.md`、`er052_output/open233_stage2_01/precheck/`、delegation_log STAGE2-01_01/_02、DESIGN-01_02)→commit→push。(ii) 測定完了時点で `er052_output/open233_stage2_01/` の残りを個別add→commit→push。trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。`git add -A`禁止。

## 報告
22行以内: 実装要点とテスト件数、(1)〜(4)の結果(ライン別の数値とPASS/FAIL)、rubric版数、②の打ち止め有無、構造要素由来STOP率、削除文数、Checker由来新規NG、面白さ代理指標、人間確認パック件数、費用、commit hash×2、raw URL。

## 固定ブロック
- E-1: 既存テスト全件PASS確認+新規テスト件数を報告。
- D-1: 無関係な既存差分を編集・stageしない(個別addのみ)。
- G-1: Production配線・APPROVED_FOR_PRODUCTION・SSOT編集を行わない。
- F-1: 予算¥180でSTOP。held-outは手順(4)まで開かない。
- T-0: 本委任文を保存+check.json。T-1: runtime evidenceを実取得。T-2: 結果は`er052_output/open233_stage2_01/`へ。T-3: RESULT_PACKETは短い要約のみ。
