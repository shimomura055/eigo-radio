## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_04: ACTIVE_TASK更新+SSOT先行起票。合格基準の事前登録、結果欄はプレースホルダ)。並列委任_01/02/03が`er052_output/open233_directional_misread_trial_02/`と新規scriptを作成中(触れない)。**書込先: `docs/pm/ACTIVE_TASK.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§84新設)、`DECISION_LOG.md`(同日エントリ新設)、`OPEN_ITEMS.md`(進捗1行)、`docs/pm/RESULT_PACKET_TRIAL02_04.md`、`docs/pm/delegation_log/`。git操作なし。**
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: TRIAL-02=実行中(分類は結果後にFable)。禁止: 結果の予測・創作/Production変更/gold・KPI変更/有料API/「決定」の創作。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_04.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、逐語)
> 管理ID: OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02。目的: 前回Trialで判明した、1つのFactに複数の事象がある場合、記事側がどの事象について述べているか選ばず、全事象と比較してしまうことで正常文を誤って重大扱いする問題を修正し、方向反転専用チェックを再検証する。ユーザー承認: 修正版限定Trialを実施/費用上限¥10/残り11 E2Eは引き続き停止/Production変更はまだ行わない。
> 重要警告: 報告フォーマット違反。前回報告は、ユーザー指定の★★★★報告ここから★★★★〜★★★★報告ここまで★★★★の正式報告フォーマットを守っていません。これは運用ルール違反です。今後、ユーザー向け正式報告は必ず★★★★報告ここから★★★★で開始し、★★★★報告ここまで★★★★で終了すること。中間作業メモや通常チャットと、正式報告を混同しないこと。再発させないよう、今回closeout時に必ず確認する。
> 今回の修正: 前回のsame_blind構成を維持する。ただし、記事側AIに「この文がLedger側のどの事象について述べているか」をまず選ばせる。その後、選択された事象だけについてLedger側の状態と記事側の状態を比較する。複数事象すべてとの総当たり比較は禁止。
> Trial条件: 前回と同じ主要テスト群(HC-012/A5-0/D61・HF-009系/正常文43件相当/曖昧例/前回誤爆3件)。重要例は3回反復。
> 合格基準(事前登録): HC-012 3/3検出/A5-0 3/3検出/正常文の誤重大判定2%以下/不要Rewrite見込み現行0.67件/runの半分以下/前回誤爆3件解消/新しい重大見逃しを発生させない。1つでも重要条件を満たさない場合、勝手に追加修正Trialへ進まない。
> 費用: Trial上限¥10。¥10以内なら追加承認を待たず実行してよい。超過見込みならSTOPして報告する。
> 時短・並列化: 正式ルールに従い並列化。開始時に所要時間見込み/クリティカルパス/並列化作業/短縮見込みを報告。
> 今回やらないこと: Production変更/残り11 E2E再開/gold変更/KPI変更/floor復活/新しいSafety原則の追加/Trial結果を理由に自動でProduction採用。
> Trial終了時: VALIDATED/REJECTED/USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない。
> Closeout報告(正式フォーマット): HC-012結果/A5-0結果/前回誤爆3件の結果/正常文誤爆率/不要Rewrite見込み/AI揺れ/1 runあたり追加処理件数/追加コスト/前回Trialとの差/Trial Status/Production採否でユーザー判断が必要か/残11 E2Eを再開可能か/今回の並列化内容と実際の所要時間短縮/未解決事項/APPROVED_FOR_PRODUCTION未配線項目への影響/Dangling Reference有無。残11 E2Eはユーザーの明示承認まで開始しない。

## Fable開始時計画(記録用)
所要見込み約65〜75分(直列なら約2時間超)。Phase A(¥0、4本並列・約30分): script修正(事象選択・shard実行)/testset_02+正解データ複数事象対応/集計script+合格判定+regression+template/SSOT先行起票。Phase B(≤¥10・約15分): 見積→Ledger側30 call→記事側3 process shard並列→merge。Phase C(約20分、直列・前工程依存): 集計→Fable判定→SSOT→commit→Closeout正式報告。短縮見込み約60分。

## 作業内容
1. `docs/pm/ACTIVE_TASK.md` 全面更新: 管理ID=TRIAL-02(進行中)/TRIAL-01(USER_DECISION_REQUIRED→ユーザーがTRIAL-02実施を承認)/DESIGN-01(設計承認済み)/CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・残11待機・PRODUCTION_WIRED未)。Status=TRIAL-02 Phase A。予算¥10。合格基準6項目(逐語)。禁止事項。**報告フォーマット: 正式報告は必ず★★★★報告ここから★★★★〜★★★★報告ここまで★★★★(PM_GOVERNANCE 9-8)、closeout時に自己確認**。UDR-blocking=残11 run再開はユーザー明示待ち。UDR-deferred=U2/U3/STAGE4、OPEN-235/236未着手。次アクション=Phase A→B→C。
2. REPORT: Grep `^## §83` →§83末尾の直後に「## §84 限定Trial 2(事象選択修正): OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(2026-10-06)」新設: §84-1 目的・ユーザー承認・禁止事項/§84-2 修正内容(事象選択→選択事象のみ比較、総当たり禁止、same_blind維持)/§84-3 合格基準(事前登録、6項目逐語)/§84-4 Trial条件(対象群・反復)/§84-5 並列化計画(Fable計画)/§84-6 結果「(委任_06で追記)」/§84-7 Status・判断「(委任_06で追記)」/§84-8 参照ファイル(予定パス: `er052_open233_directional_trial_02.py`、`er052_output/open233_directional_misread_trial_02/`配下)。
3. DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01` →同日エントリ直後に新エントリ「2026-10-06 OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02」: (a)ユーザー指示(逐語要点、承認4点・報告フォーマット警告・修正内容・合格基準・¥10・禁止)(b)Fable計画(c)結果・Status「(委任_06で追記)」。既存書式に従う。
4. OPEN_ITEMS: Grep `OPEN-233-DIRECTIONAL-MISREAD` →該当行の進捗へ「TRIAL-02開始(事象選択修正、¥10上限、合格基準事前登録)」を表セル内に短く追記。
5. `docs/pm/RESULT_PACKET_TRIAL02_04.md`: 追記位置(行番号)、プレースホルダ位置、T-0結果。

## 事前指定Read/Grep一覧
`docs/pm/ACTIVE_TASK.md` 全文。REPORT: Grep `^## §8[0-9]` →§83末尾範囲(20行)。DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01` →エントリ末尾範囲(30行)。OPEN_ITEMS: 該当1行のみ。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_04.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_04.md_check.json`

## SSOT追記文
上記2〜4。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL02_04.md`。最終報告4行以内。
