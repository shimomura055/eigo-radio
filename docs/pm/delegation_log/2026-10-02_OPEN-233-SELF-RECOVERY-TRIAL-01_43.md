## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_43: **日本語側を修正しない場合の実害調査+「英語だけ直す」設計の再検討**[ユーザー指示§4]。read-only調査、¥0)。
**並行タスクあり**: 委任_42(別のsonnet-worker)が`er052_open233_self_recovery_flow_runner_01.py`とそのテスト・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を編集中でcommitも行う。委任_44・45はread-only調査。**本委任はコード・SSOT・ACTIVE_TASK・RESULT_PACKETを一切編集せず、git add/commit/pushもしない**。

## 性質/到達上限Status/禁止事項

- 性質: read-onlyのコード調査と設計案の提示(実装しない)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 調査自体は非該当。ただし本調査の結論に基づく「日本語側の処理構造の見直し」は条件A該当のため、実装前にFableがOpus独立レビューへ回す。報告はOpusがファイル:行を辿って検証できる根拠付きで書く。
- 到達上限Status: 調査結果と設計案の報告まで。
- 費用: ¥0(API・TTS・Trial・LLM呼び出しなし。費用上限[Cap]を伴わないためT-3非該当)。
- 禁止事項:
  - 実装しない。`*.py`・Prompt・テスト・SSOT・設計書を編集しない。runner・Trial・回帰テストを実行しない。Production正式pathを変更しない。
  - git操作は読み取り系のみ(`git grep`/`git show`/`git log`/`git ls-files`)。
  - リポジトリ内に新規作成してよいのはT-0の2ファイルのみ。報告は最終メッセージ本文で返す。
  - runnerは並行タスクが編集中。修正前(現行)の挙動は`git show e0ae8de0:er052_open233_self_recovery_flow_runner_01.py`を一時ディレクトリへ出力したコピーで読む。
  - 「日英整合を保ちたい」という一般論を実害として数えない(ユーザー方針)。実害は具体的な経路を特定できたものだけを挙げる。実害の経路を見つけたのに方針に合わせて小さく見せない。確認できなかった経路は「未確認」と書く。
  - `CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`の全文Read禁止。`er0XX_output/`配下の全文Read禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は最小化。F-1: transcript退避は不要。T-0: 委任文を保存しcheck_delegation_prompt.pyを実行、結果を記録。T-2: 本委任はTTSを伴わない。T-1・T-3は非該当。

## ユーザー指示(原文、抜粋)

> 4. 日本語側は「英語だけ直す」前提で設計を再検討する。ユーザー方針: 日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。英語のDeviation修正のたびに、日本語側の対応箇所を推測して同時Rewriteする前提を見直す。まず「英語だけ修正して終了」する設計を基本案として再検討する。確認すべきこと: 日本語を修正しないことで後続Production処理に実害があるか/古い日本語が後段で再利用され英語へ誤りが再流入する経路があるか/ユーザー表示・音声・解説等で日本語がそのまま正式出力として使われるか/再生成時に日本語から英語を作り直す経路があるか。単に「日英整合を保ちたい」という理由だけなら日本語まで遡って修正する必要はない。実害がなければ日本語側の複雑な推測処理は外す方向で設計する。実害がある場合は経路を具体的に示した上で最小限の対策を提案する。
> 6. Opusレビュー: 日本語側の処理構造見直し等は構造変更に該当する可能性がある。Opus独立技術レビューGateに従う。
> 8. STOP条件: 新しいProduct原則の採用/Safety原則の変更/Production正式仕様の変更判断/¥600予算上限超過/Claude案とOpusレビューが重要点で対立/複数の合理的な設計案に明確なQCDトレードオフがあるときのみUSER_DECISION_REQUIRED。Production正式pathは変更禁止。

## 調査項目

Q1. Production正式pathでの日本語記事の役割(生成元、英語記事の生成元、後続処理への入力を全数列挙: ユーザー表示/音声/派生生成物/QA/regen・retry・fallback/その他。ファイル・関数・行と、原文記事か英語由来かを区別)。
Q2. 英語へ誤りが再流入する経路(日本語原文から英語を作り直す処理、Self-Recovery Flow自体が古い日本語を根拠に英語を元へ戻しうるか)。
Q3. 日本語がそのまま正式出力として使われるか。JA fail-open封鎖の導入理由(設計書§6-7・Opus L2レビュー#4)。
Q4. 再生成時に日本語から英語を作り直す経路(CURRENT_SPECのretry/fallback/regeneration仕様)。
Q5. Self-Recovery Flow側でJA関連処理を外した場合の影響範囲(paired_rewrite、JA対応箇所の推測、JA Recheck、ja_pending_deviation/ja_deviation_unresolved、ja_fail_open_guard、JA/EN等価チェック、JA側指摘の次周回合流)。
Q6. origin=ja_sourceの意味の再確認(英語だけ直してもRecheckが再指摘する構造がないか)。
設計案の提示(実装しない): 基本案「英語だけ修正して終了」の成否、外す処理/残す処理、保証しなくなること、期待効果と根拠の強さ、STOP条件、Existing Spec / Prior Trial Check(A/B/C)。

## 事前指定Read・Grep一覧

CURRENT_SPEC.md(Family体系|en_direct|原文記事|日本語記事|source_article|retry|fallback|regen|Local Rewrite)、er003_v1_n3_01_articles_generate.py・er003_v1_en_direct_vfl_01_generate.py、修正前runnerコピー(1499〜1508/2497〜2536/2920〜3193/3199〜3203/4075〜4131/4496〜4650)、vfl01 502〜601・660〜680、docs/pm/design_open233_self_recovery_flow_01.md(§5-4/§6-7/§6-11)、opus_l2_review_open233_self_recovery_04.md/05.md、design_open233_violation_span_handoff_01.md §4-3、er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv、`git grep -n -I -E "source_article_text|ja_text|article_ja|ja_article|原文記事" -- "*.py" ":!er0*_output/**"`。追記・更新: なし。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`(一時ディレクトリの集計スクリプト用のみ)。
1. `git show e0ae8de0:er052_open233_self_recovery_flow_runner_01.py > <一時ディレクトリ>/runner_e0ae8de0.py`
2. 上記Read/Grep/集計。
3. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md --json-out docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md_check.json`
runner・Trial・回帰テストは実行しない。git add/commit/pushはしない。

## SSOT追記文

なし(編集しない)。

## Git(明示add対象・コミットメッセージ・trailer)

git add/commit/pushは行わない(並行タスクとの衝突回避。T-0の2ファイルは未追跡のまま残す)。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`には書かず、最終メッセージ本文に1.結論 2.Q1表 3.Q2・Q4 4.Q3 5.Q5 6.Q6 7.設計案 8.STOP条件・A/B/C 9.確認済み/未確認・Opus論点 10.読んだ範囲・T-0結果・作成ファイルを記載する。
