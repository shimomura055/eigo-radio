## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_04: ACTIVE_TASK更新+SSOT先行起票。ユーザー訂正事項の明記、合格基準の事前登録、結果欄はプレースホルダ)。並列委任_01/02/03が`er052_output/open233_directional_misread_trial_03/`と新規scriptを作成中(触れない)。**書込先: `docs/pm/ACTIVE_TASK.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§86新設)、`DECISION_LOG.md`(同日エントリ新設)、`OPEN_ITEMS.md`(進捗1行)、`docs/pm/RESULT_PACKET_T03_04.md`、`docs/pm/delegation_log/`。git操作なし。CURRENT_SPEC.mdには触れない(新カテゴリ・新原則を追加しない)。**
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: TRIAL-03=実行中(分類は結果後にFable)。禁止: 結果の予測/Production変更/新しい重大基準・Product原則の追加/gold・KPI変更/有料API/「決定」の創作。Opus Gate: 設計はOPUS-REVIEW-03で承認済み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_04.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、逐語要点)
> 管理ID: OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03。ユーザー決定: Opusレビューで修正された設計でTRIAL-03を実施する/残り11 E2EはTRIAL-03終了まで停止継続/Trial予算は上限¥8/Production変更はまだ行わない。
> 重要な訂正: D61型について新しい重大基準・新しいProduct仕様を作るのではない。D61/HF-009型は、もともと既存基準で重大Fact誤りとして扱っている対象である。「限定語なしの方向表現を最終結果として読む」ことも、新しいProduct基準として採用する話ではない。今回はあくまで、既存の重大Fact誤りを正しく検出するためのTrial上の判定方法として検証する。CURRENT_SPEC等に新しい重大カテゴリやProduct原則を追加しないこと。
> Trialする修正版: 前回の誤った修正案(事象名をさらに具体化/意味上の部分一致を広げる)は採用しない。修正1: 時間的位置を区別する(Ledger側INTERIM/FINAL/SINGLE、記事側INTERIM/FINAL/UNSPECIFIED、同じ時間的位置に属する事象同士だけを方向比較)。修正2: NONE時の限定フォールバック(factとの対応が既に分かっている記事文で通常の事象選択がNONEになった場合のみ各事象を個別に確認。無条件に全事象総当たりへ戻さない)。
> 既存重大基準は変更しない: 「途中と最終の取り違え」という新Productカテゴリを作らない/gold・KPIの重大性基準を新設しない/既存の重大Fact誤り基準のまま評価する。内部分析上D61型と呼ぶのは構わない。限定語なし表現の解釈はTrial上の検証に留め、一般原則として自動採用しない。
> Trial構成: 構成X=NONEフォールバック中心/構成Y=時間的位置の区別+NONEフォールバック。実行前にheld-out検証セットを固定(HC-012/A5-0/D61・HF-009/正常文43件/前回誤爆3件/held-out重大例/held-out正常例)。実行後にtestsetや正解を変更しない。
> 合格基準(実行前固定): HC-012 3/3維持/A5-0 3/3維持/D61 2/3以上/held-out重大例 平均2/3以上かつ全例最低1/3以上/正常43件+held-out正常例 不要な重大判定0/不要Rewrite見込み0件/run/新たな重大見逃し0/前回解消した誤爆3件を再発させない。未達でも自動でTRIAL-04へ進まない。
> 費用上限¥8(見込み約¥6)。上限内なら追加承認なし。超過見込み時のみSTOP。
> 禁止: Production変更/残り11 E2E再開/新しい重大基準追加/gold・KPIの重大性基準変更/floor復活/Trial結果から自動的にProduction採用/TRIAL-04への自動移行/Opus承認のない新構造追加。
> Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない。残り11 E2Eはユーザー明示承認まで開始しない。正式Closeout報告は★★★★報告ここから★★★★〜★★★★報告ここまで★★★★、closeout前に自己チェック。TRIAL-03完了後はSTOP。

## Fable計画(記録用)
所要見込み約45〜50分。Phase A(¥0、4本並列、約25分): script_03(phase照合+NONE限定フォールバック+X/Y)/held-out固定+testset_03+正解(phase付き)+sha256凍結/集計(合格基準8項目・X/Y比較・regression)/SSOT先行起票。Phase B(≤¥8、約10分): 見積→Ledger側phase付き再抽出(固定キャッシュ)→記事側X/Y×3 shard=6 process同時→merge→集計。Phase C(約12分、直列): Fable判定→SSOT→commit→Closeout正式報告→STOP。

## 作業内容
1. `docs/pm/ACTIVE_TASK.md` 全面更新: TRIAL-03(進行中、Phase A)/OPUS-REVIEW-03(完了、ユーザーが修正設計を承認)/TRIAL-02・TRIAL-01・DESIGN-01(完了)/CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・残11待機・PRODUCTION_WIRED未)。予算¥8。合格基準8項目(逐語)。**ユーザー訂正事項(新カテゴリ・新原則を作らない、既存重大Fact誤り基準のまま)**。禁止事項。9-8自己確認欄。UDR-blocking=残11 run再開はユーザー明示待ち。UDR-deferred=U2/U3/STAGE4、OPEN-235/236未着手。
2. REPORT: Grep `^## §85` →§85末尾の直後(=ファイル末尾)に「## §86 限定Trial 3(時間的位置の区別+NONE限定フォールバック): OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(2026-10-06)」新設: §86-1 ユーザー決定・訂正事項(逐語要点。**D61は既存重大Fact誤り基準で評価、新カテゴリ・新原則なし**)/§86-2 修正1・2の内容と不採用の前回修正案/§86-3 合格基準8項目(事前登録)/§86-4 Trial構成(X/Y、held-out固定・凍結)/§86-5 並列化計画/§86-6 結果「(委任_06で追記)」/§86-7 Status・判断「(委任_06で追記)」/§86-8 参照(予定パス`er052_open233_directional_trial_03.py`、`er052_output/open233_directional_misread_trial_03/`)。
3. DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03` →同日エントリ直後に新エントリ「2026-10-06 OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03」: (a)ユーザー決定4点+訂正事項(逐語要点)(b)修正内容・合格基準・禁止(c)Fable計画(d)結果・Status「(委任_06で追記)」。
4. OPEN_ITEMS: Grep `OPEN-233-DIRECTIONAL-MISREAD` →該当行進捗へ「TRIAL-03開始(ユーザー承認、phase区別+NONE限定フォールバック、X/Y、上限¥8、held-out固定。D61は既存重大基準のまま評価・新カテゴリなし)」を表セル内に短く追記。
5. `docs/pm/RESULT_PACKET_T03_04.md`: 追記位置(行)、プレースホルダ位置、T-0。

## 事前指定Read一覧
`docs/pm/ACTIVE_TASK.md` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
REPORT: Grep `^## §8[0-9]` →§85末尾範囲(20行)Read→末尾にEdit追記。DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03` →エントリ末尾範囲(30行)Read→直後にEdit追記。OPEN_ITEMS: 該当1行Read→同行セル内Edit。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_04.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_04.md_check.json`

## SSOT追記文
上記2〜4。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_T03_04.md`。最終報告4行以内。
