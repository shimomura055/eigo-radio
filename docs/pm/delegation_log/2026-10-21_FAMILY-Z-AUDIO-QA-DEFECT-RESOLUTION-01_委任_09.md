# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_09(関連: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_02、FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01)— Family Z「走れメロス」ユーザー試聴PASS(Std/Adv)の正式記録と最終Closeout。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: 記録・SSOT整合のみ。**JPY0**。有料API・TTS/ASR再生成・再組立・test/Production Wiring再実行は禁止(ユーザー§2「既に確認済みのテストやProduction Wiringを無意味に再実行しない」)。
- 到達Status: メロス記事=`USER_ACCEPTED_FINAL(2026-10-21、run_e2e_06版)`。`USER_LISTENING_PENDING`解消。Azure Phrase List重み2.0=`PRODUCTION_WIRED`(Fable判定確定、下記)。
- 禁止: 未承認の発音判定ルール追加・A/A'/P1/P2・OPEN-330/OPEN-371等の別課題の再開・OPEN-283を「実証済み」と書くこと(live未観測のまま維持)・コード/Prompt変更・`git add -A`/`-u`/stash/amend/rebase/force push/branch操作・新規Open Item起票。
- Opus独立技術レビューGate: 非該当(記録のみ。PL 2.0の採用提案前レビューはOpus_J[OF-PLW-J-01〜13]で実施済み、内容不変のため再利用)。
- 時間見込み: 30分。直列(同一SSOT)。

## Fable判定(転記する事実。Sonnetは再判定しない)
- Azure Phrase List重み2.0=**PRODUCTION_WIRED**。根拠: (1)ユーザーAPPROVED_FOR_PRODUCTION 2026-10-20(原文=docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_USER.md)/(2)`er006_secondary_asr_01.py` `AZURE_PHRASE_LIST_WEIGHT=2.0`+`setWeight`、test 7件PASS(`er006_azure_phrase_list_weight_test_01.py`)/(3)wire evidence `speech.context.dgi.bias=2.000000`(docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/wire_evidence_prod_01.json)/(4)正式runner run_e2e_06でaudit `azure_phrase_list_weight=2.0` 記録(3 clip)/(5)ユーザー2026-10-21に「正式採用済み、PRODUCTION_WIRED」を確認。
- メロス記事: Std/Advユーザー試聴PASS 2026-10-21。Std 6%減速=承認。完成版=run_e2e_06(`er026_output/family_z_production_e2e_01/melos/run_e2e_06/`、試聴ページ `user_test/family_z_melos_02/`)。追加修正・Trial不要。
- OPEN-283(Rewrite後原稿同期): 配線済み・offline/統合test PASS・live発火未観測(run_e2e_05/06でLR発火0)のまま維持(monitor)。「実証済み」と書かない。
- PLW Trial(OPEN-424): Fable最終ラベル=REJECTED(2026-10-20確定済み。Status角括弧が未更新なら整合させる)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_09.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、N=本委任文[「委任_09」と「走れメロス」を含む最新、直前189は中東E2E-02 委任_04])し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。
T-2: TTSなし。

## ユーザー指示(原文・2026-10-21)
`docs/pm/delegation_log/2026-10-21_FAMILY-Z-MELOS-FINAL-CLOSEOUT-01_USER.md` へ逐語保存(先頭に `# ユーザー指示原文(2026-10-21)` と `管理ID: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_09 / FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 / REGISTER #23` の2行、以降は一字一句変えない。文字数・sha256を報告)。
--- 原文ここから ---
# Family Z「走れメロス」— ユーザー試聴PASS・最終Closeout指示

## 1. ユーザー正式承認

**メロス記事のStandard／Advanced両方について、ユーザー試聴PASSを正式確定する。**

- Standard：試聴PASS
- Advanced：試聴PASS
- Standardの6%減速：適用確認済み、承認
- Azure Phrase List重み2.0：正式採用済み、PRODUCTION_WIRED
- 追加の音声修正・Trial：不要

今回の完成音声を正式な完成版として確定する。

## 2. 最終Closeout作業

1. Standard／Advancedのユーザー試聴PASSを正式記録する。
2. `USER_LISTENING_PENDING` を解消する。
3. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／USER_DECISION_REGISTER／REPORT_LEDGERを必要十分な範囲で更新する。
4. 関連する承認済み仕様の配線漏れ・未処理判断がないか確認する。
5. 必要なGit commit／pushを実施する。
6. Fableが最終Closeoutを独立評価する。

**既に確認済みのテストやProduction Wiringを無意味に再実行しないこと。**

## 3. 留意事項

- Rewrite後の原稿同期について、今回のrunでは自然発火していないことを既存記録どおり維持する。実証済みと誇張しない。
- 今回の完成承認を理由に、未承認の発音判定ルールを追加しない。
- 既存の別課題を、本件完了のために不必要に再開しない。
- 今回の完成版を追加生成・再組立しない。
- 品質 ＞ 速度 ＞ 量産単価を遵守し、最小限の記録作業でCloseoutする。

## 4. 完了報告

以下を簡潔に報告する。

1. **メロス記事の最終Closeout完了可否**
2. Standard／Advancedのユーザー試聴PASS記録
3. Azure Phrase List 2.0のPRODUCTION_WIRED維持確認
4. SSOT／Git反映結果
5. 未処理事項（ある場合のみ）

**本件はユーザーによる最終品質承認済み。新たなユーザー判断は不要。**

既存承認範囲内で最終Closeoutまで完了させること。
--- 原文ここまで ---

## KPI provenance欄
該当なし(新規測定なし。既存evidenceの参照のみ)。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md` のOF-PLW-J-01〜13・OF-FZAQ-G-01: 状態が`CLOSEOUT_CONFIRMED`でなければ `CLOSEOUT_CONFIRMED(2026-10-21 ユーザー試聴PASS・PL2.0 PRODUCTION_WIRED)` へ更新(内容は変えない)。

## 事前指定Grep一覧+更新手順(全文Read禁止)
1. `OPEN_ITEMS.md`
   - Grep `^OPEN-422 \|` → 行頭Status角括弧を `[CLOSED・USER_ACCEPTED_FINAL(2026-10-21 Std/Adv試聴PASS、完成版=run_e2e_06)・①不具合0件・②PRODUCTION_WIRED・③配線済み(live未観測=OPEN-283 monitor継続)]` に置換、行末に `【2026-10-21 Closeout】ユーザー試聴PASS(Std/Adv、6%減速承認、原文=docs/pm/delegation_log/2026-10-21_FAMILY-Z-MELOS-FINAL-CLOSEOUT-01_USER.md)。追加修正・Trialなし。` を追記。
   - Grep `^OPEN-426 \|` → 角括弧を `[CLOSED・PRODUCTION_WIRED(Fable判定2026-10-21: 承認2026-10-20+配線+test7+wire evidence dgi.bias=2.0+run_e2e_06 audit記録)・メロス=USER_ACCEPTED_FINAL]` に置換、行末に同趣旨の追記。
   - Grep `^OPEN-424 \|` → 角括弧が`PENDING_FABLE`のままなら `[CLOSED・REJECTED(Fable最終ラベル2026-10-20。重み1.5/2.0の便益小・偽PASS増)・ただしユーザー判断で2.0をProduction採用(OPEN-426)]` に置換。
   - Grep `^OPEN-283 \|` → 角括弧内の「live evidence未観測(run_e2e_05でLR未発火)」を「live evidence未観測(run_e2e_05/06でLR未発火、monitor継続)」へ最小修正。他は不変。
   - 上記以外でメロス/Family Zの`USER_LISTENING_PENDING`を示す行(Grep `USER_LISTENING_PENDING` → ヒット行のうちメロス/melos/run_e2e_0[4-6]/family_z_melosを含む行)を列挙し、該当行は「USER_LISTENING_PENDING→USER_ACCEPTED_FINAL(2026-10-21)」の最小追記で解消(履歴本文は削除しない)。中東記事(OPEN-416)の`USER_LISTENING_PENDING`は対象外(触らない)。
2. `docs/pm/USER_DECISION_REGISTER_01.md`
   - Grep `^- #23\(` → 「判断済み 2026-10-21(Std/Adv試聴PASS、6%減速承認、完成版run_e2e_06、PL2.0 PRODUCTION_WIRED)」へ更新。
   - Grep `^- #126\(`・`^- #124\(`・`^- #116\(` → 既に判断済みなら変更不要(確認のみ報告)。
3. `CURRENT_SPEC.md`: Grep `AZURE_PHRASE_LIST_WEIGHT|Phrase List重み|PhraseList.*2\.0` → 該当行にStatus表記があれば `PRODUCTION_WIRED(2026-10-21 Fable判定確定、ユーザー承認2026-10-20)` を最小追記(仕様本文は変えない)。L2136付近の③注記(Grep `OPEN-283`)は「live未観測」表現を維持(変更不要なら確認のみ)。
4. `DECISION_LOG.md`: 末尾箇条書き形式(Grep `^- 2026-10-2` 末尾3行で書式確認)で1件: メロス最終Closeout(Std/Adv試聴PASS・6%減速承認・PL2.0 PRODUCTION_WIRED確定・追加Trialなし・OPEN-283は未観測維持・原文sha)。
5. `docs/pm/REPORT_LEDGER.md`: 1行追記。
6. 配線漏れ・未処理判断の確認(ユーザー§2-4、**報告のみ・再開しない**): `docs/pm/ACTIVE_TASK.md`先頭の各ヘッダの`APPROVED未配線`欄と、`OPEN_ITEMS.md` Grep `APPROVED_FOR_PRODUCTION[^|]{0,80}(未配線|配線待ち|未実装)` のヒットのうちFamily Z/メロスに関係する行を列挙し、各行に「本件Closeoutに影響なし/あり」を1行で付す。OPEN-330(UDR)/OPEN-371(UDR)/OPEN-283(monitor)は既知として列挙のみ。
7. `docs/pm/ACTIVE_TASK.md`: 先頭に本委任ヘッダ(Status=MELOS_CLOSEOUT_SSOT_DONE_PENDING_FABLE、JPY0)を追記。

## Git
明示add: T-0 2ファイル+USER原文+OPEN_ITEMS.md+USER_DECISION_REGISTER_01.md+DECISION_LOG.md+REPORT_LEDGER.md+CURRENT_SPEC.md(変更時)+OPUS_FINDINGS_LEDGER.md(変更時)。secret scan hits=0。commit `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_09: メロス最終Closeout(Std/Adv試聴PASS記録・USER_LISTENING_PENDING解消・PL2.0 PRODUCTION_WIRED確定・OPEN-422/424/426 Close)`。`git push origin HEAD:main`(force禁止、現origin/main=1e4c3f038からfast-forward)。raw URL列挙。

## 報告(docs/pm/RESULT_PACKET_FZAQ9.md 上書き。ユーザー§4の1〜5の順)
1. Closeout完了可否。2. 試聴PASS記録の所在(ファイル:行)。3. PL2.0 PRODUCTION_WIRED維持確認(根拠5点の所在、再実行していないこと)。4. SSOT編集行の新旧・commit・raw URL・T-0結果・JPY0。5. 未処理事項(§6の列挙。判断候補があれば「判断候補」、USER_DECISION_REQUIREDラベルは付けない)。