# 委任_45 受領文(T-0保存)

## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_45: **Checker引用の特定不能35件の原因分類+対策設計+逐語Prompt変更の効果評価**[ユーザー指示§3]。既存記録の読み取り分析、¥0)。
並行タスクあり: 委任_42が`er052_open233_self_recovery_flow_runner_01.py`・テスト・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を編集中でcommitも行う。委任_43・44はread-only調査。本委任はコード・SSOT・ACTIVE_TASK・RESULT_PACKETを一切編集せず、git add/commit/pushもしない。

## 性質/到達上限Status/禁止事項

- 性質: read-onlyの既存記録分析と対策設計案の提示(今回は実装・Promptの試行をしない)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 分析自体は非該当。ただし「Checkerの出力契約変更」は条件A該当のため、実装前にFableがOpus独立レビューへ回す。Opusレビュー#5(`docs/pm/opus_l2_review_open233_self_recovery_05.md`)の`violation_spans`保留の指摘(`claim_in_article`との二重化を避け、1つの欄から対象決定・Stage 2表示・prior_issues・同一判定を作る)を踏まえる。
- 到達上限Status: 原因分類・対策設計案・Prompt変更の効果見積もりの報告まで。
- 費用: ¥0(API・TTS・Trial・LLM呼び出しなし。T-3非該当)。
- 禁止事項: 実装しない。`*.py`・Prompt・テスト・SSOT・設計書を編集しない。LLMを呼ばない。runner・Trial・回帰テストを実行しない。Production正式pathを変更しない。git操作は読み取り系のみ。新規作成してよいのはT-0の2ファイルと、`er052_output/open233_handoff_log_aggregation_01/unverified35_classification_01.csv`・`classify_unverified_01.py`のみ。報告は最終メッセージ本文で返す。
- 修正前runnerは`git show e0ae8de0:...`のコピーで読む。
- 35件すべて(ユニーク13種類)について、Checkerの文字列と記事本文の該当箇所を並べて目視し原因を判定する。
- Prompt変更の効果を楽観的に書かない(見積もりであり実測ではない。`same_fact_id_locations`の前例を踏まえる)。判定基準は変えず違反範囲の出力形式だけを変える案に限る。
- `CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`の全文Read禁止。`er0XX_output/`配下の全文Read禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0/T-2は常時有効。本委任はTTSを伴わない。T-1・T-3は非該当。

## ユーザー指示(原文、抜粋)

> ## 3. Checker引用13.4%特定不能について、原因調査＋対策まで行う
> 重大指摘261件中35件、13.4%で、Checkerが返した違反箇所の文字列を記事本文へそのまま対応付けられませんでした。35件を原因別に分類してください。最低限、原文を少し言い換えて返している/大文字小文字・句読点等の差/「〜で始まる段落」など説明文を混ぜている/複数箇所を1つの文字列に結合している/その他、に分けてください。原因ごとに対策を設計してください。特に「違反箇所は記事本文から一字一句そのまま引用すること。要約・言い換え・勝手な結合は禁止。複数箇所なら別々の原文範囲として返すこと」と明示するPrompt変更で、どこまで解消できるかを評価してください。必要性が高いと判断した場合は、Trial/検証用Promptで限定的に実装して確認して構いません。ただし判定基準そのものは変えず、違反範囲の出力形式だけを変えること。対策後、特定不能率/検出漏れ/false PASS/出力失敗/Human Reviewへの影響を確認してください。
> ## 6. Opusレビュー(抜粋): Checkerの出力契約変更等、構造変更に該当する場合は実装前にOpusレビューが必要。
> ## 8. STOP条件(抜粋): 新しいProduct原則の採用/Safety原則の変更/Production正式仕様の変更判断/¥600予算上限超過/Claude案とOpusレビューが重要点で対立しFableで解消できない/複数の合理的な設計案に明確なQCDトレードオフがありユーザー判断が必要、の場合のみUSER_DECISION_REQUIREDとしてSTOP。

## 分析の内容

A. 原因分類(C1言い換え/C2大小文字・句読点/C3説明文混在/C4複数箇所結合/C5その他、13種類すべて表化、非BLOCKING7行・K2の14件は件数のみ)。
B. 影響の実態(32 runの最終結果、現行の対象が意図と一致していたかの目視、人間確認へ回るrun数22の再確認、記事別・時期別)。
C. 原因ごとの対策設計案((i)機械的照合の追加[同値変換と再推測の線引き]、(ii)Prompt出力形式変更、(iii)Checker返し直し、(iv)人間確認)の比較表。
D. 逐語Prompt変更の効果見積もりと設計案(D-1/D-2/D-3、Trial専用追記のみ、Prompt文案、必要性判定)。
E. 限定確認の設計(実行しない。5項目の測り方、対象、回数、費用概算)。

## 事前指定Grep一覧+追記位置・更新位置の手順

各instance JSONから該当周回の記事本文・指摘フィールドをスクリプトで抽出。追記・更新: なし(既存ファイルは編集しない)。

## 事前指定Read一覧

aggregate_01.py、claims_detail_01.csv(Pythonで該当35行抽出)、修正前runner(1105〜1188、1468〜1510)、er003 vfl01(454〜470、502〜601)、er051(175〜250)、design_open233_violation_span_handoff_01.md(§2・§3・§8・付録A)、opus_l2_review_open233_self_recovery_05.md、design_open233_self_recovery_flow_01.md §7。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは `.venv\Scripts\python.exe`。(1)修正前runnerの一時ディレクトリへのコピー、(2)抽出・分類スクリプト`classify_unverified_01.py`→`unverified35_classification_01.csv`、(3)検算(35行・13種類)、(4)T-0チェック。runner・Trial・回帰テストは実行しない。LLMを呼ばない。git add/commit/pushはしない。

## SSOT追記文

なし(編集しない)。

## Git(明示add対象・コミットメッセージ・trailer)

git add/commit/pushは行わない(並行タスクとの衝突回避)。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

RESULT_PACKETには書かず最終メッセージ本文に: 1結論/2表A/3影響B/4対策比較C/5Prompt設計D/6限定確認E/7STOP条件とOpus論点/8検算・限界/9読んだファイル・T-0結果・作成ファイル。
