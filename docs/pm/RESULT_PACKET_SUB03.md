# RESULT_PACKET SUB03 (SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_03、調査・是正設計、API 0、公開物変更0)
- 結論: 選定UIの機能コードは当初要求どおり実在(同じ公開JSにbatch付与=PC/mobile 14セット28チェックPASS、全Done→1回コピーで14SET、restore_batch全件受入)。未達の直接原因=公開articles.jsonにbatchキー未設定→公開は全35枠の旧単体画面(Done/コメント欄/一括コピー/残り全選択が全て非表示)。分類=実装済みだが未公開(R1-R5)+仕様解釈の誤り(batch無し=全枠フォールバック、新機能のbatch限定)+未実装(報告単位の状態分離、`?batch=`、batch供給の運用)+受入側不備(公開実操作を欠いた)。
- 公開実操作(PC1280/mobile390): 選択肢35・BS=null・進捗/一覧/Done/一括コピー/コメント欄=非表示・「選定結果をコピー」=1セットのみ。
- 成果物: docs/research/SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01/GAP_ANALYSIS_03.md、DESIGN_03.md、gap03_probe*.py、gap03_result*.json、gap03_batch_copy_{pc,mobile}.txt、gap03_shots/。原文=docs/pm/delegation_log/2026-10-30_SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01_USER_02_REOPEN.md。
- 設計(DESIGN_03): data/batches/<id>.json+`?batch=`+状態キー名前空間+batch無し=記事非表示(`?dev=all`のみ)+機能のbatch限定撤廃+固定フッタ(mobile)+er128 batchファイル解決(追加のみ)+tools/publish_selection_batch_01.py(live smoke必須)+Regression(node/Playwright A18・B5・C/live smoke/ガード)。実装=Sonnet 1委任約3-3.5h、API 0、追加単価0。Opus条件A推奨(新構造)。
- 次の一手(改善見込み高): 実装委任→公開live実操作→Fable独立受入。Fable所管の規則案=HR/報告の選定URLはbatch URL必須、選定UI受入は公開URL live smoke+PC/mobileスクショ必須。
- 判断候補: なし(D=0。batch無し非表示=A既判断[再開原文§3①]、batchファイル/URL/名前空間/dev=all/batch_latest=B)。
- 環境: C:ドライブ空き2.5GB(100%)で通常worktree checkoutがNo space失敗→sparse worktree(wt_sub)で実施。ディスク逼迫は別途要対処(Fable向け注意)。
- (1)既存仕様整合: 当初原文:51-139,143-185/再開原文§3-§6、DESIGN_01.md:17,35,37、form_logic.js:6,371-475、index.html:16-25,34,76,84,95-96,277、er128:661,833、export_form_data_01.py:304,344。 (2)未承認機能の既定値: 本委任はコード/公開物変更0(SSOT/docsのみ)。実装時の既定=batch未指定で記事非表示。 (3)失敗終了時の成果物: 公開は旧単体画面のまま(ユーザー観察と一致)。本委任の最終成果=上記docs(調査・設計)。ユーザー要求(複数記事を1画面で選定→全Done→1回コピー)は**未達のまま(実装は次委任)**。 (4)撤去/残置: なし(DESIGN_03で廃止予定=全35枠フォールバック[form_logic.js:446-447,index.html:277-284]、旧STORE_KEY[index.html:34]。Grep残存=実装時)。
- 判定整合: 重大NG=なし(本委任は調査・設計。選定UI未達=ユーザー確認済みの既知事項で是正対象=R1-R5,公開受入)
