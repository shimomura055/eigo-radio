管理ID: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_01(日本語→英語化で生じる軽微・重大NGの発生パターン解析と対策案。API支出¥0、既存artifactのみ)。日付 2026-10-08。ユーザー指示「日本語＞英語で軽微・重大が一部発生していますが、今までの発生パターンを解析してください。傾向があるのか。確認の上、対策を考えてください。Opusレビューも入れてください。」(Opusレビューは本委任の後に Fable が別途依頼する。本委任は解析と対策案の作成まで)。

## 禁止事項
- API支出 ¥0(LLM呼び出し禁止)。既存ファイルの読み取り・集計のみ。
- SSOT・Production コードを変更しない。git 操作をしない。
- `docs/pm/RESULT_PACKET.md` と `docs/pm/ACTIVE_TASK.md` には書かない(別Agentが並列実行中)。結果は `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_01_result.md` に書く。
- 推測で数値を書かない。件数は全て出典ファイルを示す。分類が判断を伴う場合は「判定: 手動」と明記し、根拠文を引用。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_01.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。

## 背景
- OPEN-243(`OPEN_ITEMS.md`、本日起票): 翻訳段(EN化)で生じる事実NGと EN deviation check / Checker の見逃し。実例: Trial B 評価パックの重大候補1 `er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/b1b/article.md`「in one case in which Meta was asked to negotiate internet and cable bills」(台帳 MUSE-HC-011: 依頼者はMeta従業員 → 主体反転、ユーザー判定 重大)。EN deviation check は MINOR(changed_number のみ、changed_actor=false、origin=translation)、Checker は別事実(HC-010)理由で候補化→Stage 2 second opinion で ACCEPTABLE に格下げ、出力に残存。
- Fact Lock 残存NG分析 `er052_output/factlock_writer_trial_01/eval/residual_analysis/RESIDUAL_NG_VS_CHECK.md`: factlock セルの EN 軽微6件中3件+保留1件が翻訳段由来(「幹部」→「executives」複数形化 ×2、EN末尾「In one line」要約文の付け足し、タイトル訳語「AI Phone-Answering Service」)。
- EN化の実装: `er003_v1_en_direct_vfl_01_generate.py`(Advanced/Standard adaptation、`run_deviation_check`、origin 判定)。Checker: OPEN-233 Self-Recovery(`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`)。

## 作業
1. **EN段NGの全件収集**(出典付き):
   a. Trial A(`er052_output/all6_writer_redesign_necessity_01/eval/`、盲検 judgments・HUMAN_CHECK_TA・SUMMARY_TA)と Trial B(`er052_output/factlock_writer_trial_01/eval/`、judgments・HUMAN_CHECK_FL・residual_analysis)の全NG項目のうち、所在が EN(EN_ONLY / JA+EN)のもの。各件について JA R2 の対応文を突合し「JA由来 / 翻訳段由来 / 翻訳で増幅」を判定(手動判定は引用付き)。
   b. EN deviation check の出力(`**/b1b/audit/deviation_check.json`、`**/a2/audit/deviation_check.json`、`**/audit/deviation_checks/advanced_*.json`、`standard_*.json`)を `er052_output/all6_writer_redesign_necessity_01`、`er052_output/factlock_writer_trial_01`、`er052_output/gpt6_wiring_e2e_01`、`er019_output`(直近の refresh E2E・production wiring run)から収集し、`origin == "translation"` の指摘を全件列挙(severity、changed_* フラグ、related_fact_id、文)。
   c. Checker ゴールドセット(`er052_output/all6_writer_redesign_necessity_01/T-B/TB_SUMMARY.md` の PAST-* 項目)と OPEN-233 REPORT の過去の EN 重大事例のうち、JA に無く EN で生じたものがあれば列挙。
   d. O3観測(本日 Production E2E run_01/run_02 の EN STOP 1/2本)の STOP 内容(`er052_output/gpt6_wiring_e2e_01/**/deviation_check*.json`)。
2. **パターン解析**: 収集した全件を次の軸で集計表にする。
   - 型: 主体(入替/受動化)、数(単複・人数)、範囲(限定/拡大)、因果、否定・断定の強さ、付け足し(要約文・一般化)、訳語選択(固有名詞・サービス名)、時制、その他
   - 発生箇所: 本文 / タイトル / 末尾要約(「In one line」等) / Standard(A2) vs Advanced(B1b)
   - 言語構造の要因(手動判定): 日本語の主語省略・受動/能動の曖昧さ・単複無標・敬称/役職の集合名詞化 など
   - 重大度(盲検判定 / ユーザー判定があれば併記)
   - 検出状況: EN deviation check(指摘有無・severity・origin)、Checker(候補化・Stage 2 判定・最終)
   - モデル世代(5.6-luna / 6-luna)
   傾向の有無を、件数の偏り(型別・箇所別・検出率)として記述。件数が少ない軸は「n不足」と明記。
3. **EN化プロンプト・検査の現状確認**(Grep、変更しない): `er003_v1_en_direct_vfl_01_generate.py` の Advanced/Standard adaptation プロンプトが JA 本文のほかに台帳を受け取るか、「In one line」等の要約文を生成する指示があるか、`run_deviation_check` の分類項目(changed_actor 等)の定義と origin 判定ロジック、Checker Stage 2 の second opinion 格下げ条件(`er052_*open233*` 実装の該当箇所)。
4. **対策案**(実装しない。各案に: 狙う型、変更箇所、実装規模(S/M/L)、追加費用の見込み方(トークン増の有無、確認済み単価のみ使用、未測定なら「未測定」)、副作用、検証方法):
   例として検討する範囲: (a) EN adaptation 入力に台帳を同梱/主体・数の保持指示、(b) 「In one line」要約の生成停止または台帳照合対象化、(c) JA↔EN 文対応の決定論チェック(固有名詞・数・主体の一致)、(d) EN deviation check の分類器改修(主体入替の専用質問、単複の扱い)、(e) Checker Stage 2 の second-opinion 格下げを主体・否定・因果型では不可にする、(f) タイトル・固有名詞の訳語を台帳/用語表で固定、(g) その他解析から導かれる案。優先順位は付けず、根拠と trade-off を並べる(判断は Fable/Opus/ユーザー)。
5. 成果物: `er052_output/open243_translation_ng_analysis_01/ANALYSIS_01.md`(全件表・集計表・傾向)、同 `COUNTERMEASURES_01.md`(対策案)、同 `items.jsonl`(全件の機械可読)。result には要約(件数・主要傾向・対策案一覧・未確認事項・check_delegation_prompt 結果・所要時間)。
