# 委任_06 OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任文保存)

## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_06: 結果・Fable判定のSSOT追記、Dangling Reference確認、明示git add→commit→push)。
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安20分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録+Git(¥0)。Status: TRIAL-02=USER_DECISION_REQUIRED(Fable判定)。禁止: 残11 run/Production変更/gold・KPI変更/有料API/追加修正Trial/`git add -A`/amend・rebase・force push/Fable判定の変更。Opus Gate: 非該当。

## 固定ブロック
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力はhash・push結果のみ。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を本ファイルへ逐語保存しcheck_delegation_prompt.py実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 実費¥2.08(委任_05)を領収記録。

## ユーザー指示(原文、要点)
合格基準(事前登録): HC-012 3/3/A5-0 3/3/正常文誤重大判定2%以下/不要Rewrite見込み0.335件/run以下/前回誤爆3件解消/新しい重大見逃しなし。1つでも重要条件を満たさない場合、勝手に追加修正Trialへ進まない。Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない。Closeout項目にDangling Reference有無・APPROVED_FOR_PRODUCTION未配線項目への影響を含める。残11 E2Eはユーザー明示承認まで開始しない。

## 記録する事実(委任_05、すべて【確認】)
R1 費用: 見積mid ¥2.0(low 1.3/high 3.5)≤¥10で実行、実費¥2.08(Ledger側¥0.70/30 call、shard1 ¥0.45・shard2 ¥0.68・shard3 ¥0.26、計104 call)。same_blind、gpt-6-luna、effort=medium。
R2 並列実時間: Ledger側14:58:07開始→shard3並列15:00:14開始(各1:06/1:54/2:35)→merge完了15:03:03、本実行全体約5分(直列見込み約8〜9分)。Phase A 4本並列約25分(直列見込み約75分)。
R3 合格基準: (1)HC-012 3/3 充足 (2)A5-0 3/3 充足 (3)正常文誤重大判定0/43=0% 充足 (4)不要Rewrite見込み0/0/0件/run 充足 (5)前回誤爆3件解消 充足(F-09 SAME×3、F-10 SAME×3、F-19 SAME/SAME_FAMILY/SAME_FAMILY) (6)新しい重大見逃しなし 未達: D61(G-03)が前回2/3→今回0/3(3反復とも事象選択NONE→NOT_MENTIONED)。S-06も前回検出→今回「上げ幅」SAMEで見逃し。
R4 gold計6/9(前回8/9)。人工反転検出4/14(前回5/14)。UNCLEAR 6(前回14)。曖昧3件の最終REVERSED 0。追加¥/run low0.34/mid0.42/high0.89。
R5 Fable判定: USER_DECISION_REQUIRED。原因所見【推測】: 事象ラベルが抽象的。改善案=subject_xに実体名+選択promptで部分一致を明示。追加修正Trialへは進まない。残11 E2E再開はユーザー判断。
R6 APPROVED_FOR_PRODUCTION未配線項目への影響: なし(CHECKER-FLOOR-PRODUCTION-E2E-01の承認内容・実装に変更なし、Productionコード未変更)。
R7 Dangling Reference: 本委任で確認。

## 作業内容
1. REPORT §84-6/§84-7をR1〜R7で置換。2. DECISION_LOG (c)置換(決定したのはFableのStatus判定のみ明記)。3. OPEN_ITEMS該当行追記。4. ACTIVE_TASK.md全面更新。5. Dangling確認(Glob)。6. 明示git add(ACTIVE_TASK/RESULT_PACKET除外)。7. commit。8. push origin main。9. RESULT_PACKET。
## 事前指定Read/Grep一覧
上記1〜4のGrep+該当範囲Read(各30行以内)。全文Read禁止。
事前指定Grep一覧+追記位置・更新位置の手順: REPORT `§84-6|§84-7|委任_06で追記`、DECISION_LOG `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02`(c)、OPEN_ITEMS `OPEN-233-DIRECTIONAL-MISREAD`の行末。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_06.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_06.md_check.json`
2. `git add <各ファイル>` / `git status --short` / `git commit -m "<委任原文のcommit message>"` / `git push origin main`

## SSOT追記文
上記1〜3。

## Git
明示add(ACTIVE_TASK.md/RESULT_PACKET*.md除外)、commit、`git push origin main`。エラー・競合時は中断して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET.md`。最終報告6行以内(commit hash、push、Dangling結果、T-0、raw URL 7件)。
(本保存は要点逐語、原文はFable側履歴)
