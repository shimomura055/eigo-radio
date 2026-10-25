FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_05(追加検証・Closeout: 月・コーヒー回帰+半導体別標本、R5 v4方式、評価は「B3が選んだ切り口」基準)。あなたはsonnet-worker。Fable(PM)からの委任。

## 0. ユーザー承認(2026-10-25、ユーザー指示原文は§9に逐語。`docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_03.md`として逐語保存すること)
- 追加予算200円、**案件累計上限580円**(既使用369.81円→残210.19円)。使い切る必要はない。
- 対象はTrial・検証・Closeoutまで。**Production正式採用・配線は未承認**(VALIDATEDでも配線しない)。
- 評価基準の変更(重要): 「過去記事と同じ数値を残せたか」ではなく、**今回B3が選んだ切り口に対して、重要数値の選定・保持・整理が適切に機能したか**で評価する。既存の事前固定表(PREREGISTERED_CRITERIA_03 §1)はBefore/Afterの参考情報として保持するが、異なる切り口の記事同士を機械的に比較して合否を決めない。前回の半導体(167億+217億)はその切り口に対して妥当と評価済み。
- B3が選んだ数値を無条件に正しいとは扱わず、選定自体の妥当性も評価する。
- Fableによる特別な補足判定工程は新設しない(通常の独立レビューの範囲)。
- Prompt(欄の指示文)修正は報告済み範囲(v3→v4)の最大1回を基本とする。原則としてv4を変更せずに使う。別の仕様変更が必要になったらSTOPしてユーザー判断へ。

## 1. 前提(読むもの、必要箇所のみ)
- `docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/{DESIGN_04,PREREGISTERED_CRITERIA_03,PHASE3_RESULT_01,COMPARISON_04,TRIAL_RESULT_01,ADOPTION_NOTE_01,BUDGET_LOG_01,OPUS_REVIEW_01}.md`、`docs/pm/RESULT_PACKET_FXNR4.md`、`er115_fx_numeric_retention_trial_01.py`(R5 wrapper、`--b3-addendum v4`・欄schema)、`er115_fx_numeric_r5_score_01.py`、前回の月/コーヒー標本(`er115_output/fx_numeric_retention_trial_01/{moon_shrinking/A/v2s1..3, coffee_*/A/p2,p3}`)の設定(DEV runner引数・seed・入力記事)。
- `OPEN_ITEMS.md`はOPEN-507/509行のみGrep(全文読込禁止)。
- 有料runは`.venv\Scripts\python.exe`、無料処理は`py`。

## 2. 事前登録(有料前にcommit): `PREREGISTERED_CRITERIA_04.md`
- 評価4点(ユーザー§5)の判定方法を記事ごとに固定:
  1. B3選定品質: 欄の数値が「B3の切り口(Storyline/見出し/論旨)に対して読者が聞くべき数値か」。判定材料=B3 JSON(Storyline・欄・選定理由)。ユーザー指定の必須数値(月=約42〜46m、コーヒー=4.30ドル/ポンド・41%)は、B3の切り口が従来どおりならば欄に入ることを期待値とする。切り口が変わった場合は「その切り口に対する妥当性」で判定し、ユーザー指定数値の有無は参考記録。
  2. 保持品質: 欄の数値がR0→R1→R2→EN Std→EN Advで保持(既存の保持Gate・再生成枠1回を使用)。
  3. 不要数値の抑制: R2本文のユニーク数値のうち、欄・切り口の論旨に不要な数値の件数(機械分類=固定表の「不要」をまず適用し、切り口が変わった場合は「切り口に必要か」を記事別に記録。合否は切り口基準)。M2新規数値検出0。月は約750m・約1.1km・約11cm/100万年の復活なし、コーヒーは9.14・3%の増加なしを特に記録。
  4. 文章品質: 羅列感・流れ・比喩の維持(Fable読み用に日本語R2本文全文と英語Std/Advの数値含有文を抜粋)。
- 標本数: 月N=2、コーヒーN=2、半導体N=2(別標本=新しいseed/run)、イグ=R5 v4 r5b1を再利用(再実行しない)。
- 予算配分: 1標本=B3(v4欄付き)+フルチェーン(R0→R2→EN Std/Adv)≈20円見込み→6標本≈120円。各起動前に残額(580−累計)を確認し、予約額超過の起動をしない。再生成枠は既存どおり1回まで。
- Prompt修正: 原則なし。欠陥が明確な場合に限り、報告済み範囲(5観点の条件整理、記事固有語なし、新欄/新LLM呼出なし)で最大1回、生成前に追補としてcommitしてから実施。それ以外はSTOP。
- 合格条件(記事別): 1〜4をすべて満たす。Family X共通方式としての評価: 4記事型(数値が答え[月]/比率と価格[コーヒー]/企業数値[半導体]/中核比較で筋書き非依存[イグ])のすべてで合格ならVALIDATED候補、1記事型でも不合格ならその原因が方式か記事固有かを切り分けて報告(USER_DECISION_REQUIRED候補)、方式の欠陥ならREJECTED候補。最終Status判定はFable。

## 3. 実行
- 記事間は独立なので**並列実行可**(別run dir・別process)。ただし比較条件を保つ(同じv4指示文・同じモデル・同じDEV runner設定、前回の月/コーヒー標本と同じ入力記事・seed方針)。Production隔離(sink付替え: attempt_history/HR queue/er021・er025 telemetry/Pronunciation Ledger DEVコピー、sha比較)は前回どおり。TTSは行わない(本文まで)。
- 波ダッシュ(OPEN-509)は出力側正規化(J2、DEVのみ)継続。Production修正はUDR #195のまま触らない。
- 実費はraw usage logで確定し、`BUDGET_LOG_01.md`に標本別に記録。処理時間(R0等の所要秒)も記録。

## 4. 記録・Closeout
- `PHASE4_RESULT_01.md`(標本別の生データ要約)、`COMPARISON_05.md`(記事別: B3切り口・欄・Before[公開版+前回Trial]→After、R0/R1/R2/EN Std/Advの数値、日本語R2本文全文、英語Std/Advの数値含有文抜粋、固定表による参考比較)、`TRIAL_RESULT_01.md`更新(Closeout節: ユーザー§7の全項目、Status候補)、`ADOPTION_NOTE_01.md`更新(量産単価増分の実測ベース、採用時の設計=欄追加・E=欄・Gate・O-2'・M2・J2、Production配線時の受入条件案、Opus条件C依頼書の骨子)、`BUDGET_LOG_01.md`。
- SSOT: OPEN-507(Status・Closeout要点)、OPEN-509(進展があれば)、DECISION_LOG 1件、UDR #194/#195の整合確認(新規UDRはFableが付けるので登録しない)。編集直前に再Read・scratchpadバックアップ・最小Edit・`git diff --stat`(並行agentがOPEN_ITEMS/DECISION_LOGを編集中の可能性、衝突時は再適用)。
- `docs/pm/RESULT_PACKET_FXNR5.md`、`docs/pm/ACTIVE_TASK.md`自行(gitignore)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 526 --out docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_DELEGATION_05.md`(冒頭「FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_05」で照合、不一致なら±5)。`check_delegation_prompt.py`はFAIL想定(非blocking)。
- Git: `git status`→対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。secret grep 0件。raw_usage_log/STOP/lock/telemetry不追跡。commitは最低2回(事前登録・結果)。

## 5. STOP条件
累計580円超過見込み / 品質基準・仕様の変更が必要 / Trial範囲超え(新欄・新LLM呼出・Production変更) / 重大品質・安全問題 / 改善見込みなし。STOP時は現状・原因・試行・代替案・見込みを付けて報告。

## 6. 報告(Fableへ、ユーザー§7順)
(1)記事別のB3切り口・選定した重要数値(標本別) (2)R0→R1/R2→Std/Advの保持状況 (3)不要数値の増減と、各数値が記事(その切り口)に必要かどうかの判断材料 (4)文章品質(日本語R2本文全文は COMPARISON_05 に) (5)Before/After比較 (6)各記事の合否とFamily X共通方式としての評価(Status候補) (7)実費・処理時間・量産単価影響 (8)Fable独立レビュー用の要点(読むべき本文の場所) (9)未解決事項・残存リスク (10)SSOT整合・証跡path・commit hash・raw.githubusercontent.com URL (11)RESULT_PACKET 4行+「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」1行。Production採用・配線は行わない。

## 9. ユーザー指示原文(逐語、USER_03.mdへ保存)
# Claude Codeへの指示
## Family X 中核数値保持Trial｜追加検証・Closeout

### 1. ユーザー承認事項

以下の方針で追加Trialを実施してください。

- **追加予算：200円**
- **案件累計予算上限：580円**（既使用369.81円）
- 今回の対象はTrial・検証・Closeoutまで。Production正式採用・配線は未承認。
- 品質を守りながら最速で実施し、不要な再生成・逐次処理・待機を避ける。

### 2. Trialの目的

**記事の面白さ・読みやすさを維持しながら、重要な数値を保持し、不要な数値を削減すること。**

今回の評価は、過去に制作した記事と同じ数値を残せたかではなく、**今回B3が選んだ記事の切り口に対して、重要数値の選定・保持・整理が適切に機能したか**を基準とする。

### 3. 各工程の役割

- **B3**：記事の切り口を決め、その切り口で読者に伝えるべき重要数値を選定する。
- **R0 Writer**：重要数値を保持し、不要な数値を省き、自然で面白い記事にする。
- **R1/R2・英訳**：重要数値とその意味を保持しながら文章を改善する。
- **Validator**：重要数値の脱落、不適切な数値の追加を検出する。

B3が選定した数値を無条件に正しいとは扱わず、その選定自体の妥当性も検証する。

### 4. 追加検証対象

**① 月の記事**
- 重要数値「約42〜46m」の保持を確認。
- 不要な周辺数値が復活しないことを確認。
- 既存Trialの成功品質を維持できるか検証。

**② コーヒー記事**
- 重要数値「4.30ドル/ポンド」「41%」の保持を確認。
- 不要な数値の増加がないことを確認。
- 既存Trialの成功品質を維持できるか検証。

**③ 半導体記事**
- 別標本でB3の切り口と重要数値の選定を確認。
- Writer以降で重要数値が適切に保持されるか検証。
- 数値が過剰にならず、読みやすさを維持できるか確認。

前回の167億ドル・217億ドルという選定は、今回の切り口に対して妥当な結果と評価する。

過去の記事の切り口を前提とした固定表だけで不合格にしない。

**④ イグ・ノーベル記事**
- R5 v4の成功結果を再利用する。
- 必要な理由がない限り、同一検証を繰り返さない。

### 5. 評価基準

以下の4点を評価する。

1. **B3の選定品質**：切り口に対して重要数値の選定が妥当か。
2. **保持品質**：重要数値がR0→R1/R2→英語Standard/Advancedで保持されるか。
3. **不要数値の抑制**：論旨に不要な数値が増えていないか。
4. **文章品質**：読みやすさ・自然さ・エンターテインメント性を維持しているか。

重要数値が保持されていても、B3の選定が不適切なら合格とはしない。

既存の事前固定表はBefore/Afterの参考情報として保持する。ただし、異なる切り口の記事同士を機械的に比較して合否を決定しない。

**Fableによる特別な補足判定工程は新設しない。** 通常の独立レビューの範囲で評価する。

### 6. 実行・改善方針

- R5 v4方式を基本とする。
- 過去Trial結果、既存Prompt、Validator、再生成枠を活用する。
- 問題が発生した場合は原因を分析し、承認Scope内で自律的に修正・再検証する。
- Prompt修正は報告済み範囲の最大1回を基本とする。別の仕様変更が必要になった場合はユーザー判断へ上げる。
- 改善見込みのない同一方向の反復は避ける。
- 品質基準を独断で変更しない。
- 追加予算200円は上限であり、使い切る必要はない。
- 独立した検証は並列化する。ただし、比較条件や実行環境の整合性を損なわないこと。

### 7. 完了報告・PM Gate

検証後、以下を報告すること。

- 記事別のB3切り口・選定した重要数値
- R0→R1/R2→Standard/Advancedの保持状況
- 不要数値の増減と、その数値が記事に必要かどうか
- 文章品質・エンターテインメント性
- Before/After比較
- 各記事の合否とFamily X共通方式としての評価
- 実費、処理時間、量産単価への影響
- Fable独立レビュー
- 未解決事項・残存リスク
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSとの整合、Trial証跡、Git commit・push状況

Trial終了時には、**VALIDATED／REJECTED／USER_DECISION_REQUIRED**のいずれかでCloseoutする。

VALIDATEDであっても、ユーザーの正式承認なしにProductionへ配線しない。

### 8. STOP条件

- 累計580円を超える見込み
- 承認済みの品質基準・仕様の変更が必要
- Trial範囲を超える変更が必要
- 重大な品質・安全上の問題
- 改善見込みがなく、継続の合理性を失った場合

これらを除き、委任範囲内の技術的問題は自律的に解決すること。

**目標はTrial回数を増やすことではなく、Family X共通方式として正式採用できるかを、必要十分な検証で判断できる状態にすること。**