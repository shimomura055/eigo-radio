# RESULT_PACKET_CNT_03 — SELECTION-UI-OCCURRENCE-COUNT-01 委任_03(2026-10-31)
詳細: `docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/{TEST_TRIAGE_01,RUNTIME_EVIDENCE_01}.md`・`evidence_03/`・`shots_03/`。原文=`docs/pm/delegation_log/2026-10-31_SELECTION-UI-OCCURRENCE-COUNT-01_USER_02.md`。AI API 0円(追加量産費0)。

## 1. 最終Status(Family x Level)= PRODUCTION_WIRED_PENDING_FABLE(Fable独立受入後にPRODUCTION_WIRED)
| | Standard | Advanced |
|---|---|---|
| X | evidence有(9候補/9 occ、確定16) | evidence有(12/12、確定15+Title1) |
| Y | evidence有(10/10、確定17・保留2・adopted自己検査警告=想定) | evidence有(12/12、確定17・adopted警告) |
| Z | evidence有(7/7、確定7) | evidence有(10/10、確定11) |
Production正式経路=exporter CLI(`export_form_data_01.py:449 main`→`:513 convert(occurrence=OCC_AUTO)`→`:371 attach_occurrence`)。runnerはKP候補docまで(X `er019_family_x_audio_production_runner_01.py:915-951`、Y `er121_family_y_runner_01.py:614`)で、exporter呼出はrunner内に無い(=CLIが全6水準共通の唯一の正式経路。代替ではなく正式経路そのもの)。既定ON(`:162 OCC_AUTO`)、`--without-occurrence`の使用箇所0。

## 2. 既存テスト8件(TEST_TRIAGE_01.md): 原因確定・全件是正。今回の出現回数変更を唯一原因とする失敗0
変更前3d4d8ef7c(同一sparse構成)と比較して同一失敗集合。固定値古い(#1: 10 vs 38/28、#3: run_kp75固定、#5: batches subdir/文法名判定)、test試作と正本の乖離(#8: proto06→er128正本)、資材未commit(#2,#3: run_kp75 8fileがgit未追跡→追跡化)・sparse外(#4)・autocrlf(#6,#7)、資材ドリフト(jwst/surname_choice: sourceが書出し後に更新=仕様上正常、許容リストで固定)。今回起因は`occ_userfive`(synthetic)の混入のみ(除外)。結果: form1 22 passed、er128 restore 83 passed(WordNetはsparse外=環境)、er138+er136 58 passed(sparse外資材)、er140 79 passed、node 92 ALL PASS。

## 3. runtime evidence(RUNTIME_EVIDENCE_01.md)
6水準でexporter CLI実行(rc=0)、全候補に`occurrence`・`occurrence_meta`。手計算(規則表)13項目(Phrase6/Word7、各水準にPhrase・Word)=13/13一致、承認3項目6/6。M4 guard rc=5・file無変更。再export sha完全一致、本文変更(thankful 4→3)への追従+自己検査警告。

## 4. 公開URL(`https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/`、UI sel-v3-rev06-b)
Playwright PC 56/56・mobile 56/56 PASS(計112)、console/pageerror 0。新batch(occ-a-test: 回数・内訳・保留・未集計・確認不能・タイトルのみ)、旧batch(twotier-a/b: 中立色「旧データ・出現回数なし」)、M4警告維持(データ1byte改変でバナー)、集計失敗(meta有・0件)のみ赤警告、Done/コメント/保存復元/一括コピー(回数は入らない・er128 dry受入)/Topへ戻る/?set=直接 退行なし。live smoke PASS x2。

## 5. 量産単価影響 0円
集計=決定論(`er140_*`はre/unicodedata/json/hashlib/osのみ)、LLM/TTS/ASR stage未起動、既定ON追加でAPI呼出0、runner/KP生成に変更なし(量産追加費0=現行量産単価70円目標に無影響)。

## 6. Fable受入用の証拠(file:line)
exporter `export_form_data_01.py:162,371,392(M4),449,481,513`/`er140_selection_occurrence_count_01.py:345 count_entry`/`er140_selection_occurrence_sections_01.py:55 load_sections`/UI `user_test/selection_form_v3/form_logic.js` `occurrencePage`(legacy/failed)・`ASSET_VERSION`、`index.html` occHint分岐/evidence_03/{exports,hand_check_03_result.json,approved3_check_03_result.json,occ_live03_both.json,smoke_*.json,m4_guard_03.*,six_levels_summary_03.json}・shots_03/。

## 7. SSOT/Git
OPEN-632=PRODUCTION_WIRED_PENDING_FABLE、DECISION-LOG `OCCURRENCE-COUNT-01-DECISION-02`、CURRENT_SPEC選定フォームv3節(occ-v1、配線状態=Fable受入待ち)。commit: cd49297ae(SSOT先行)、d086921fc(UI rev06-b+test是正+kp75追跡化)、7e19fa537(evidence+SSOT完)。**注意**: 他Workerのmerge `37edbd86e` でOPEN-632行が旧「設計中」へ退行していたため、委任_02/03版へ復元。

## 8. 残Open Item: なし(新規OPEN登録なし)
判定整合: 重大NG=なし
RESULT_PACKET(4行): (1)既存仕様整合=`RULES_01.md`規則表無変更・OPEN-632/CURRENT_SPEC:3254 (2)既定値=`export_form_data_01.py:162 OCC_AUTO`既定ON、`--without-occurrence`のGrep使用0、集計moduleは環境変数/flag非参照(Grep os.environ 0)。承認済み(APPROVED_FOR_PRODUCTION 2026-10-31) (3)最終成果物=出力data JSON(`evidence_03/exports/*__cli.json`)+公開フォーム。失敗終了時: 区分本文取得不能は`occurrence_meta.error`+旧データと区別した警告(目的適合: 選定・コピーに影響しない表示専用) (4)撤去・残置=旧M6赤字案内(旧データ分)を撤去し`occurrencePage.legacy/failed`へ分離(残存Grep: 赤字「集計できませんでした」はfailed分岐のみ)。
## 判断候補
なし(承認済み事項の再質問なし。Fable独立受入でPRODUCTION_WIREDへの格上げのみ)。
