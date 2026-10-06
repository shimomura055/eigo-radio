## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_03a: Trial結果に依存しないSSOT記録の先行起票。結果欄は「(委任_03bで追記)」のプレースホルダ)。並列委任_02がTrial実行中(`er052_output/open233_directional_misread_trial_01/`とtrial scriptを使用中。**それらは読まない・触れない**)。**書込先: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§83新設)、`DECISION_LOG.md`(同日エントリ新設)、`docs/pm/RESULT_PACKET_TRIAL_03A.md`、`docs/pm/delegation_log/`。OPEN_ITEMS/ACTIVE_TASKは触らない(03bで更新)。git操作なし。**
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: TRIAL-01=実行中(分類は結果後にFable)。禁止: 結果の予測・創作/Production変更/gold・KPI変更/有料API/「決定」の創作。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_03a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 管理ID OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01。目的: ユーザー承認済みの設計案について、Production変更は行わず、限定Trialで有効性を確認する。残り11 E2Eは引き続き停止する。Trial仕様: (1)Ledger全FactをAIが確認(状態変化・方向性の有無、結果状態を固定分類で抽出)(2)方向性ありFactだけ記事側を別AI判定(Ledger側の答えを見せない)(3)機械比較(同方向→通過/逆方向→重大候補/抽出不能・曖昧→記録のみ)。同じAI・同じrubricの繰り返し構成にしない。まず¥0で母集団再集計。費用上限¥15(見積超過時のみSTOP)。比較: 同一model/Ledger側と記事側でmodel分離/blind分離あり・なし。Production変更禁止(Checker・後段AI・floor復活・残11 E2E・KPI・gold・Human Review振替・自動Production採用)。副産物2件は別管理ID。Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED(VALIDATEDでもProduction採用ではない)。

## 記録する確定事実(結果に依存しない部分)
A. 母集団(委任_01a、`population_01.md`、¥0): Ledger全Fact 123件/9 run(平均13.67、実体はLedger 2種: hormuz 12 fact×4 run、meta 15 fact×5 run。前回の「Stage 1候補123件」とは別物で偶然の一致。Stage 1候補は66件=7.33/run)。状態変化Fact(語彙近似、精度未検証)30件=24.4%(3.33/run)。単位→fact対応はE2E出力に未保存(`support_fact_ids` 0件)。記事側確認件数/run: 下限3.33/近似7.46/上限30.56(判定単位全数、全単位40.44)。単価(gpt-6-luna effort=high、call_log 135件から逆算): 入力約¥10.7/1M、出力約¥81.7/1M。追加コスト/run(同一model): Ledger側¥0.155/0.166/0.512、記事側¥0.034/0.084/1.127、合計¥0.19/0.25/1.64(low/mid/high)、現行E2E約¥3.50/run。注: low/midは推論ほぼ無し前提。記事本文は修正前fixture本文で計数。
B. 対象セット(委任_01b、`testset_01.md`、¥0): 63項目=真の反転gold 3(HC-012 restored/A5-0/D61合成)+曖昧3(K16/K19/HC-012「changed back to how it was before」)+忠実(状態変化語あり)21+忠実(HC-012同fact・状態言及なし)17+非該当5+人工反転14(決定論置換、厳密6/許容8)。repeat=3はgold 3+曖昧3。call見込み75/構成。Ledger側正解10 factを逐語根拠付きで事前登録(方向性あり: HC-012=STOPPED[PAUSED許容]、HF-009=UNCHANGED[一時縮小→復帰]、HF-007=ENDED、HF-002=STARTED、HF-011=INCREASED)。enum=AVAILABLE/STOPPED/PAUSED/INCREASED/DECREASED/UNCHANGED/STARTED/ENDED/EXPANDED/NARROWED/NOT_MENTIONED/UNCLEAR、方向対4組、PAUSED vs STOPPEDは逆転扱いしない。未特定: 委任_61の個別文(D61合成で代替)。ホルムズ側Ledgerは`family_x_refresh_e2e_01/hormuz/run_03`を代表使用(新9 runの実Ledgerと同一かは未確認)。
C. Trial script(委任_01c、`er052_open233_directional_trial_01.py`、¥0): Ledger側抽出(factごと1回・記事を見せない・キャッシュ)→記事側blind抽出(対象X+記事文+前後文のみ、Ledger本文・stateを渡さないことをunit testでassert)→Python比較(REVERSEDは方向対該当かつ両側quote非空のみ、quote欠落・enum外・対応外はUNCLEARで重大化しない)。3構成: same_blind/split_blind/same_nonblind(対照群: 1 callで両側)。`--budget-yen`で累計停止。unit test 8件PASS、dry-run 3構成完走。既定model gpt-6-luna。
D. Fable実行方針(委任_02): effort=medium(再分類Trialと同じ、費用優先)、実行順same_blind(Ledger側10 fact×repeat 3+記事側75)→same_nonblind(75)→split_blind(記事側はsame_blindの結果を再利用、Ledger側のみ別model)、累計¥15で強制停止、見積mid>¥15ならSTOP。
E. 副産物: OPEN-235(数字floor配線漏れ)、OPEN-236(two_of_two潜在不具合)を別管理IDで起票済み(委任_01d)。
F. 前管理ID(DESIGN-01)でユーザーが設計案(案E')の限定Trialを承認(2026-10-06)。残11 runは停止継続。

## 作業内容
1. REPORT: Grep `^## §82` →§82末尾の直後に「## §83 限定Trial: 系統的読み違い専用Safety(OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01、2026-10-06)」を新設。§83-1 目的・禁止事項(ユーザー指示要点)/§83-2 母集団(A)/§83-3 対象セット(B)/§83-4 Trial構成(C・D)/§83-5 結果(**プレースホルダ「(委任_03bで追記)」のみ**)/§83-6 Status・判断(同プレースホルダ)/§83-7 参照ファイル一覧。各3〜8行の箇条書き。
2. DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01` →同日エントリの直後に新エントリ「2026-10-06 OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01」: (a)ユーザー指示要点(逐語に近く、禁止事項・¥15・Status 3分類)(b)Phase 0結果(A・B・C要点)(c)Fable実行方針(D)(d)副産物の別ID化(E)(e)結果・Status=「(委任_03bで追記)」。ヘッダチェーン等の既存書式に従う(Grep `^## 2026-10-06`で直近エントリ書式を確認)。
3. `docs/pm/RESULT_PACKET_TRIAL_03A.md`: 追記位置(行番号)、プレースホルダ位置、T-0結果。

## 事前指定Read/Grep一覧
REPORT: Grep `^## §8[0-9]` →§82の末尾行範囲のみRead(20行以内)。DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01|^## 2026-10-06` →該当エントリ末尾範囲(30行以内)。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_03a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_03a.md_check.json`

## SSOT追記文
上記1・2。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL_03A.md`。最終報告4行以内。
