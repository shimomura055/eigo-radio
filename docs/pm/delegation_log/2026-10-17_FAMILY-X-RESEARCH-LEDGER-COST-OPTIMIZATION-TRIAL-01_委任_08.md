## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08(Opus条件Aレビュー逐語保存+評価手順の是正反映[JPY0]→Stage 1a補正の有料実行[inbound_tourism M2c/M3c、確認パスのみ]→修正前後差分記録+R-07人手判定→SSOT→commit)。Stage 1bは本委任で**実行しない**(別日2026-10-18 JST以降)。並行タスク衝突: なし(BAPEは#106待ち、S3Wは試聴待ち)。commitを伴う作業は本委任のみ。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済みTrial(#104費用承認・#107設計是正(b))の承認範囲内実行。到達上限Status=`STAGE_1A_CORRECTED_PENDING_FABLE`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDに到達しない。
- Fable判定(11-3): Opusレビュー_B=GO(コード修正なし、評価手順・注記の反映のみ)。Claude案と一致、承認済み仕様内、新Product原則なし → Fable判断で次工程(本委任)へ進む。
- 費用上限(T-3定型): 「上限¥60(Guardrail、本委任の有料部分=inbound M2c/M3cの確認B3 2回≒22円+新規Fact検証が入った場合の上積み)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」 harnessの実費ガード(1a上限493、累計1,040、日次soft 1,000)はそのまま有効。`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`、`--other-spend-today-jpy 71.3`(本日のRLCT外支出=SJS4 41.6+S3W 18.5+その他≒71.3。harnessがraw_usage_logから当日RLCT支出212.80+10.88を自動計上する場合は二重計上しないよう既存実装を確認し、使った値と根拠をRESULT_PACKETに書く)。
- 禁止: Stage 1b・任意Aの実行禁止。Production runner/Prompt/Style変更禁止。既存1a成果(`coffee_prices/*`, `inbound_tourism/M0,M0b,M0p,M1,M2,M3`)の変更・削除禁止(sha前後IDENTICAL必須)。Research再生成禁止。Coffee M2/M3の再生成禁止(conform PASS)。B3 Prompt文言(lib.py:504の`UNVERIFIED_PHRASE`等)の変更禁止(1aとの条件維持、Opus R-B9-1)。有料runの再起動禁止(26節、rc≠0・外部停止ならSTOP報告)。git add -A/-u/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。
- 時間見込み: 全体約60分。直列(有料実行は1回、同一出力dir)。
- 費用/日次: 当日(JST 2026-10-17)既使用約JPY284.1(出典: ACTIVE_TASK.md L4)/残約715.9/本委任見積JPY22(期待)〜60(上限)/改善見込み高/承認区分: C(承認済みscope内。#104 1a上限493の残280.2、#107 §3「追加費用見込み：約JPY22」)。
- 前委任(委任_07)QDC記録・受入記録: ACCEPTED(文言修正は本委任で実施)。判定整合: 重大NG=なし / 主因=なし / 是正対象=D1(ii)文言 / STOP理由=なし / 提示=可。

## ユーザー指示(原文)
全文=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`。本委任の直接根拠=§3「Stage 1aの訪日客統計について、案2・案1＋案2に新しい最終B3確認パスを追加実行する。既存のResearch・Ledger・初回B3を再利用し、必要な確認パスだけを実行すること。追加費用見込み：約JPY22。既存成果を破壊せず、修正前後のBrief・採用Fact・品質・費用の差を記録する。Coffeeについても同じ最終確認条件への適合を照合し、既に検証結果が反映済みなら不要な再生成を行わない。」§8「追加確認パスの費用を必ず計上する。既存の上限に収まらない見込みが生じた場合はSTOPする。」§6「AMBIGUOUSの断定が残っていないか」「Verifierの判定ばらつきによる問題と、案1・案2の方式固有の問題を区別する。」

## Opusレビュー_B(条件A、2026-10-17、総合判定GO)の反映指示(Fable採択分)
- OP-1(R-B4): TRIAL_DESIGN_03.md D1(ii)の文言を「Ledgerではタグ+notes(Researcherのambiguity欄があればそれを優先描画)、Verifierのverification_notesはextra_noteで渡す(確認対象AMBIGUOUSは600字、他の検証済みは300字で切り詰め)」に修正。コード変更なし。
- OP-2(R-B9-1、高): inbound M2/M3の実測Storylineが「【独立検証前の編集仮説】」ラベルで始まる(inbound_tourism/M2/result.json:62、M3:61)。Prompt文言は変更しない。評価手順へ反映: (a)ブラインド評価時はラベルをマスク、(b)R-07人手判定ではラベルをFact固有の留保として数えない、(c)ラベル出現件数を方式別に「方式固有の欠陥候補」として記録。STAGE_1A_EVAL_01.md末尾に「§追補(委任_08): 評価手順の是正」として追記し、1b評価にも適用する旨をTRIAL_DESIGN_03.mdに1節追加。
- OP-3(R-B5): M2c↔M3cの確認B3は同じsel・ほぼ同じ判定を入力にした独立2回の呼出のため、両者のBrief差は「B3出力の揺らぎの標本」であり案1上限の効果ではない旨を、補正結果の記録と設計文書に明記。
- OP-4(R-B2): 未成立はunmet内訳(REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMED)で分けて示す。「確定条件のもとでの成立率」は案2系のみの指標である旨を注記。上限到達時のBriefを成立扱いに戻さない。
- OP-5(R-B6、JPY0): conform_check.pyに「最終選定=前回選定−REJECTEDの集合か(bool)」「Storyline変更あり(bool、sha比較)」の2列を追加し、_conform_check_1a_02.jsonを再出力(1a_01は残置)。
- OP-6(R-B7): 5記事集計での方式列=Coffee M2/M3(経路は新設計と同一、conform PASS)+inbound M2c/M3c+1b新設計。inbound旧M2/M3は「旧設計・参考」行のみ。注記文をTRIAL_DESIGN_03.mdに記載。
- OP-7(R-B1): R-07人手判定は全方式同一基準。判定NGは「確定条件は満たしたが断定が残った」として別集計(Trial後のユーザー判断事項、新仕様は入れない)。
- Opus逐語保存: docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPUS_REVIEW_B_01_VERBATIM.md(subagent transcript agent-ac34cea031256ef8b.jsonlから既存extract方式で抽出、内容改変禁止、sha256記録、抽出不可なら「抽出不可」と記録)。
- Opus台帳: docs/pm/OPUS_FINDINGS_LEDGER.mdへ OF-RLCT-RB-01(R-B1)〜OF-RLCT-RB-09(R-B9-1)を追加、各行に状態(FABLE_DECIDED→IMPLEMENTED/EVIDENCED)。

## 有料実行(Stage 1a補正)
1. 事前snapshot→`_stage1a_tree_sha_before_08.json`。
2. `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --stage 1a --out er082_output/rlct_trial_01 --article inbound_tourism --correct-from M2,M3 --other-spend-today-jpy <確認値>` 実行は1回。rc≠0・外部停止・BudgetStopならば再起動せず報告。
3. 事後snapshot→`_stage1a_tree_sha_after_08.json`→IDENTICAL確認(before集合限定)。
4. 結果記録: M2c/M3c result.jsonから、確認パス発火、新規選定Factと検証結果、最終選定Fact、Storyline(前後)、status(COMPLETED/UNRESOLVED+unmet)、cost_correction_only/cost_production_equivalent、ambiguous_central、contract。
5. 修正前後差分: STAGE_1A_CORRECTION_01.md(新規)に、M2→M2c・M3→M3cのBrief/Storyline(全文)/採用Fact/verdict/費用/F05の扱い(R-07人手判定、ラベルは留保に数えない)/B3構成差(3段階、OP-2マスク)/M2c↔M3c差=B3揺らぎ標本の注記(OP-3)/未成立のunmet内訳(OP-4)/削減率の再計算(M0/M0p/M0b基準で別表)/5記事集計での扱い(OP-6)。
6. aggregate再実行→aggregate.md更新(M2c/M3cを「確認パス後」、旧M2/M3は参考行)。
7. test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er082*_test_*.py"`。

## 事前指定Read一覧 / Grep一覧 / SSOT追記文 / Git / 報告(RESULT_PACKET項目)
(原委任文の当該節に従う。要点: OPEN_ITEMS.md OPEN-410/403追記・OPEN-411新規[RLCT-B3-UNVERIFIED-LABEL-IN-STORYLINE-01、OPEN・非Blocking・Trial観測・改修なし、POST_USER_VALIDATION]、DECISION_LOG.md末尾追記、REPORT_LEDGER.md委任_08行、ACTIVE_TASK.md上書き、明示addのみ、commit message先頭=`FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_08: ...`、trailer `Managed-ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01`、報告先=docs/pm/RESULT_PACKET_RLCT8.md。)

注記: 本ファイルは受領した委任文のうち実行手順・禁止・承認範囲・反映指示を保存したもの。SSOT追記文および報告項目の細目は受領原文(会話ログ)に基づく。
