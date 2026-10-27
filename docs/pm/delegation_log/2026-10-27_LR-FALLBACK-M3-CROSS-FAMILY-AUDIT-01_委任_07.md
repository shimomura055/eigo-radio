# 委任_07: SSOT同期(LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 監査結果・是正4件・UD-1〜3登録 + FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 第1報/文法0件調査の反映、API 0)

Fable→sonnet-worker、2026-10-27。Fable判定済み内容を**転記する作業**であり、判断を加えない。全文読込禁止(Grep+該当行のみ)。既存行は書き換えず「追記」。

## 1. 入力(Fable確定事項)
- 監査成果物: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/{W1_LR_DATAFLOW_01,W2_SIX_ROUTES_01,W3_M3_LR_HR_01,W4_ROLE_COVERAGE_01,FIX_A_01,FIX_A_02}.md`。commit 7dab92aba(F1/F2/OPEN-564)、8fbfae04c(人間承認原文採用時のLR正解原稿解決)。
- ユーザー原文: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_USER.md`。
- Fableのユーザー向け報告内容(本委任で転記する結論):
  - 真因=LRはTTS入力のみ書換える設計(本文への書込み経路なし)、X/Y/Z共通、バグではない。本文反映の可否は承認原文に記載なし(暗黙)。「読む英文=聞く英文」原則は2026-10-27原文が初出、方式未承認。
  - M3 `LOCAL_REWRITE_RECOVERY`: ユーザー明示承認原文なし(2026-10-12 Opus条件A+Fable/Sonnet設計)。導入根拠(LR再TTSのStyle脱落)は統一仕様で消滅。残る実効=本文と音声の語差の人確認。停止範囲は不均一(X本文Std/Adv・Adv Preview・Y本文のみ。X/Y topic_intro・Adv comment・in_one_line、Z全体は無停止。Zはページ注記あり、X/Yなし)。HR Lockとの二重化なし。
  - 6経路: HEAD=統一仕様一致。AI島で統一フロー実データ確認。未観測=Y chunk/Zセリフ終端Std/X STOP(STOP_ALL絶対pathのみ)/Y・Z kill→resume/Z narrator減速後再検証/Y・Z自然発生③LR。
  - LR対象=英語5 role。公開済み不一致=AI島以外3件(X Word Gacha Adv you've→you have[UDR#183(a)承認済・注記なし]、Z メロス Adv Melos→He[注記あり]、Z 猿の手 Std guest→visitor[注記あり])。非本文roleの公開済み不一致なし。
  - 是正(A、API 0、Gate/音声/Prompt/閾値不変): F1 er127 LR block記録保全(深さ別merge+③close)、F2 Std L4 `LR_REWRITTEN`警告(LR block内v1伝播)、OPEN-564 `_merge` fallback_used実採用attempt準拠(M3 BLOCK不変をtest固定)、委任_06 `resolve_expected_text_after_local_rewrite`が`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`真なら原文を返す(定数単一化、test 5件)。runtime evidenceは次回LR自然発生時に採取(未観測)。
  - USER_DECISION_REQUIRED 3件(Fable推奨付き): UD-1 本文と音声の一致方式[(a)X/Yへページ注記/(b)LR変更箇所の本文局所パッチをHR選択肢に(自動書換えなし、sha再バインド・照合コード・ページ再生成実装、Opus条件A)/(c)LR不採用で原稿側を人が修正し再TTS。推奨(b)、確定KP/KW/文法に触れる場合(c)。既存公開3件への遡及要否も判断]。UD-2 AI島最終処理[(i)本文1語を音声に合わせ更新(AI agents/AI systems、再バインド可、再TTS不要)/(ii)音声承認で本文AIs維持+注記。推奨(i)。hr_02 Q1を置換]。UD-3 M3 LR項とGate範囲[(A)現状維持/(B)全LR role+Zへ検知拡張/(C)警告化=緩和。推奨(B)、緩和不採用]。
  - 新規Open候補: Gate範囲不均一(UD-3)、表示と音声の乖離(UD-1)、Z LR Gateなし(C、CURRENT_SPEC:1622整合)、派生ファイルのLR旗残存(C)、Adv ③NG attemptのStyle未記録(C、W2 F4)、Z Style実測Gate後の統一flow未観測(C、W2 F5)、確定KPとLR書換え範囲の重なりが記録のみ(C、W1 F-6)。
- 告げ口心臓: `docs/pm/RESULT_PACKET_FZTTR1.md`・`RESULT_PACKET_FZTTR2.md`、`docs/research/FZ-TELL-TALE-HEART-RESELECT-REMAKE-01/{FIXATION_01,BUDGET_PLAN_01,BUDGET_LOG_01,AUDIO_PHASE1_01,GRAMMAR_ZERO_INVESTIGATION_01}.md`。原文=`…_FZ-TELL-TALE-HEART-RESELECT-REMAKE-01_USER.md`/`USER_02.md`。結論: 正本=run_sf_prod_02(Adv e11b84dd…/Std b94c7305…)、新run `run_reselect_01`、V3フォーム公開(KP/KW Std9/Adv9、文法0件)、本文TTSは選定後(runner入口がKP確定前提)、実費4.87円/Cap150。文法0件=正常(Trial-08方式どおり、不具合なし、再送不要)。判断候補D-1(0件確定、推奨)・D-2(Z/物語文向け抽出Prompt対象定義新設=新仕様、推奨見送り)。軽微: フォーム文言「事前生成は実施済み」の0件時表示(`export_form_data_01.py:275`、未着手)。

## 2. 作業
1. `OPEN_ITEMS.md`: OPEN-561(AI島)=hr_02 Q1をUD-2へ置換・本案件結論を追記。OPEN-563(AIs)=据置、関連追記。OPEN-564=CLOSED(7dab92aba)。OPEN-312=統一仕様で解消済み/M3 LR項の根拠消滅をUD-3へ(UDR #6 Deferred更新)。OPEN-499=公開不一致1件としてUD-1遡及対象に追記。**新規OPEN**を起票(番号は末尾の次番号): (1)本案件親項目 LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01[Status=AUDITED+分類A是正済み(2 commit)、UD-1〜3待ち、11-8分類=ユーザー判断要] (2)Gate範囲不均一+表示/音声乖離の公開3件(UD-1/UD-3連動) (3)C項目まとめ(Adv③Style未記録/Z統一flow未観測/LR旗残存/KP重なり記録のみ)=実害なし(任意)。OPEN-503(告げ口心臓)=再選定案件へ追記(新管理ID、run_reselect_01、フォームURL、文法0件正常、D-1/D-2、実費)。文法フォーム文言は新規OPEN(軽微・実害なし)。
2. `DECISION_LOG.md`: 本体末尾(直近エントリ形式に従う)へ2エントリ: (a)LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 監査結果とFable 11-8判定(A4件是正、B/C→UD-1〜3、commit hash、成果物path、API 0) (b)FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 第1報(固定正本・新run・フォーム公開・文法0件正常判定・実費)。
3. `CURRENT_SPEC.md`: 統一仕様節(`:3148-3220`)の末尾へ**追記**(既存行不変): 「【2026-10-27 LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01】LRはTTS入力のみを書換え本文は不変(設計、承認原文に明記なし)。M3 `LOCAL_REWRITE_RECOVERY`はユーザー明示承認原文なし・Gate範囲不均一(詳細W3/W4)。本文と音声の一致方式=UD-1(未承認)。是正F1/F2/OPEN-564/HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG(commit)。Gate・QA blocking条件は無変更」。`:2857-2858`付近のAI島適用例に「hr_02 Q1はUD-2へ置換」を追記。`:2925`付近へ「人間承認で原文採用した音声はフラグ真で原文を正解とする(8fbfae04c)」を追記。
4. `docs/pm/USER_DECISION_REGISTER_01.md`: 末尾追記節「2026-10-27 LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01」にUD-1/UD-2/UD-3(区分D、Fable推奨付き、根拠path)と告げ口心臓D-1/D-2を登録、「次工程をブロックするUDR」にUD-2(AI島完成)とD-1(告げ口心臓文法)を追記。UDR #6はUD-3へ統合と記載。
5. `docs/pm/ACTIVE_TASK.md`: 両案件のStatus更新(監査=SSOT同期完了・UD待ち/告げ口心臓=第1報済み・ユーザー選定待ち)。
6. 整合: 追記後に`OPEN-564`/`UD-1`/`UD-2`/`UD-3`/`run_reselect_01`をGrepしてdangling無し、OPEN番号重複なしを確認。
7. Git: 変更ファイルのみ`git add`(SSOT 3件+UDR+ACTIVE_TASK+本委任文)。commit「PM-SSOT-SYNC-28: LR横断監査結果・分類A是正4件・UD-1〜3登録・告げ口心臓第1報/文法0件正常(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`。
8. 最終応答: 変更ファイル一覧とcommit hash、新規OPEN番号、raw.githubusercontent.com URL(`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`)を列挙。
