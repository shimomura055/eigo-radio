## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03(委任_01d: ACTIVE_TASK更新+SSOT先行起票。Opus結果欄はプレースホルダ)。並列委任_01a/01b/01cが`docs/pm/evidence_opus_review_03/`を作成中(触れない)。**書込先: `docs/pm/ACTIVE_TASK.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§85新設)、`DECISION_LOG.md`(同日エントリ新設)、`OPEN_ITEMS.md`(進捗1行)、`docs/pm/RESULT_PACKET_OR03_01D.md`、`docs/pm/delegation_log/`。git操作なし。**
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」を含む形で保存)。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: OPUS-REVIEW-03=進行中(到達上限DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIRED)。禁止: 結果の予測/TRIAL-03実行/Production変更/gold・KPI変更/有料API/「決定」の創作。Opus Gate: 本管理IDの主目的(ユーザー指示による必須レビュー)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01d.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、逐語要点)
> 管理ID: OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03。目的: TRIAL-02で残ったD61見逃しについて、TRIAL-03へ進む前にOpus独立レビューを実施する。今回は実装・有料Trialをまだ行わない。まず「原因分析と修正方針が本当に正しいか」を確認する。
> Opusに必ずレビューさせる論点: 1. D61見逃しの原因分析は正しいか(仮説: Ledger側の事象名が「上げ幅」「水準」のように抽象的すぎたため、記事側AIが対象文と対応付けられずNONE/NOT_MENTIONEDと判断した)。2. 現在の修正案(Ledger側事象へ対象の実体名を含める/記事側の事象選択で意味上の部分一致を許容)で本当に改善する見込みがあるか(D61を拾える可能性/HC-012・A5-0を壊さないか/前回解消した正常文誤爆3件を再発させないか/事象名を具体化しすぎて別表現を拾えなくならないか)。3. 別の見逃し・誤爆を増やさないか(同義表現/主語省略/比較表現/方向表現/一つのFactに複数事象/記事側の言い換え)。4. TRIAL-03へ進む価値があるか(そのままTRIAL-03へ/設計修正後にTrial/現方式を見直すべき、のいずれかを明確に判定)。
> 追加: 今回の修正は根本原因に対する修正なのか、D61だけを通すための過学習的patchなのか。「Ledger側の事象抽出→記事側blind事象選択→機械比較」という全体構造自体に直すべき問題がないか。
> 今回やらないこと: TRIAL-03実行/有料LLM Trial/Production変更/残11 E2E再開/Prompt修正の本実装/gold・KPI変更/新しいSafety仕様の採用。
> Status: DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIREDまで。Opusが良いと言っても自動的にVALIDATEDやAPPROVED_FOR_PRODUCTIONにしない。
> 正式報告は★★★★報告ここから★★★★〜★★★★報告ここまで★★★★。closeout前の自己チェック項目に入れる。
> Closeout: D61見逃しの主因/現修正案が根本対策か局所patchか/修正でD61が改善する見込み/HC-012・A5-0への影響/正常文誤爆再発リスク/新しい見逃しリスク/Opusの最終判定/TRIAL-03を実施すべきか/実施するなら修正内容と合格基準/TRIAL-03の費用見込み/時間見込み/残11 E2Eの扱い/未解決事項。Opusレビュー結果を受け取った時点でSTOPし、ユーザーへ報告する。TRIAL-03は開始しない。

## Fable計画(記録用)
所要見込み約60〜70分。Phase A(¥0、4本並列、約25分): Evidence packet①D61 trace/②HC-012・A5-0+誤爆3件再発リスク/③TRIAL-01/02差分+全体構造/④本SSOT先行起票。Phase B(約15〜20分、直列): Opusレビュー(Evidence揃い後)。Phase C(約15分、直列): Fable照合→SSOT→commit→Closeout正式報告→STOP。

## 作業内容
1. `docs/pm/ACTIVE_TASK.md` 全面更新: 管理ID=OPUS-REVIEW-03(進行中)/TRIAL-02(USER_DECISION_REQUIRED、ユーザーはTRIAL-03前のOpusレビューを指示)/TRIAL-01・DESIGN-01(完了)/CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・残11待機・PRODUCTION_WIRED未)。到達上限、禁止事項、Opus論点4+追加2、報告フォーマット9-8自己確認欄、UDR-blocking=残11 run再開はユーザー明示待ち・TRIAL-03はOpus後STOP、UDR-deferred=U2/U3/STAGE4、OPEN-235/236未着手。次アクション=Phase A→B→C→STOP。
2. REPORT: Grep `^## §84` →§84末尾の直後に「## §85 Opus独立レビュー: D61見逃しの原因分析と修正方針(OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03、2026-10-06)」新設: §85-1 目的・禁止事項/§85-2 レビュー論点(4+追加2、逐語)/§85-3 Evidence packet一覧(予定パス`docs/pm/evidence_opus_review_03/01_d61_trace.md`、`02_hc012_a5_fp3.md`、`03_trial01_02_diff.md`)/§85-4 Opusレビュー結果「(委任_03で追記)」/§85-5 Fable照合・Status・判断「(委任_03で追記)」。
3. DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02` →同日エントリ直後に新エントリ「2026-10-06 OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03」: (a)ユーザー指示(逐語要点)(b)Fable計画(c)結果・Status「(委任_03で追記)」。
4. OPEN_ITEMS: Grep `OPEN-233-DIRECTIONAL-MISREAD` →該当行進捗へ「OPUS-REVIEW-03開始(D61原因分析・修正方針のOpusレビュー、TRIAL-03は未開始)」を表セル内に短く追記。
5. `docs/pm/RESULT_PACKET_OR03_01D.md`: 追記位置(行番号)、プレースホルダ位置、T-0結果。

## 事前指定Read一覧
`docs/pm/ACTIVE_TASK.md` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
REPORT: Grep `^## §8[0-9]` →§84末尾範囲(20行)Read→直後に§85をEdit追記。DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02` →エントリ末尾範囲(30行)Read→直後に新エントリEdit追記。OPEN_ITEMS: Grep該当1行のみRead→同行セル内Edit。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01d.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_01d.md_check.json`

## SSOT追記文
上記2〜4。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_OR03_01D.md`。最終報告4行以内。
