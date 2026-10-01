## 管理ID

`PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02`(初回委任)。並行タスクなし(他Agentは起動していない)。`OPEN-233-SELF-RECOVERY-TRIAL-01`はUSER_DECISION_REQUIREDのまま据え置き(本委任で技術変更をしない)。

## 性質/到達上限Status/禁止事項

- 性質: **PM/開発運用ルール(文書)の正式反映**。ユーザーが2026-10-02に確定した「Opus独立技術レビュー」運用ルールを、既存SSOTへ重複定義を避けて反映する。ユーザー原文: 「今回の作業は運用ルールの正式反映まで行って構いません」。
- 到達上限Status: 運用ルールとして正式反映済み(ユーザー決定済みのため、11-2節の前例にならい当該節へ「2026-10-02ユーザー決定」と明記)。Production仕様のStatus(`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`)には関与しない。
- 費用: ¥0(API・TTS・Trial・Opus起動なし。費用上限[Cap]を伴わないためT-3非該当)。
- 禁止事項:
  - **既存ルールと競合する箇所を勝手に上書き・削除・書き換えしない**(ユーザー原文: 「既存ルールと競合する場合は勝手に上書きせず、競合内容を報告してください」)。今回の編集は**追記(additive)のみ**。既存文言の修正が必要と思われる箇所は、編集せず「競合」として報告する。K1〜K5以外の競合を見つけた場合も同様。
  - **`.claude/agents/sandwich-pm.md`(Fable本体の定義)は一切編集しない**。`.claude/agents/*.md`の**frontmatter(name/description/tools/model)はどのファイルも変更しない**(ユーザー原文: 「Opus 5.5の固定運用などは今回採用しません。モデル指定については現状変更不要です」)。
  - コード(`*.py`、`docs/pm/tools/check_delegation_prompt.py`含む)・Prompt・Production pathを変更しない。
  - **OPEN-233の技術変更(文ID・文字オフセット方式、locate修正等)を実装しない・設計しない**。Trialを回さない。
  - `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`の**既存見出し文字列を変更しない・見出しを追加しない**(`check_delegation_prompt.py`が見出し文字列でセクション検出するため)。
  - `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`PM_GOVERNANCE.md`の全文Read禁止(Grep→該当範囲Read)。
  - `git add -A`/`stash`/`amend`/force push禁止。既存の未commit変更(`er0XX_output/`配下11件、`docs/pm/delegation_log/2026-10-01_PM-CRASH-DATA-INTEGRITY-CHECK-01*`、`2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01*`、その他未追跡)には触れない・addしない。
  - 本ルールの対象でない既存節の体裁整理・ついでの修正をしない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
(本委任はTTSを伴わない。T-1・T-3は非該当。T-0は本委任文の**全文**を`docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_01.md`へ保存する。)

## ユーザー指示(原文)

(以下はユーザーが2026-10-02に送った指示の全文。`DECISION_LOG.md`には要約ではなく**この原文を逐語で**収録すること[PM_GOVERNANCE 2節Gate 2付近の「承認は原文引用」の教訓に従う]。)

> Opusの技術レビュー運用について、ユーザー判断が確定しました。
>
> 以下を正式なPM/開発運用ルールとして反映してください。
>
> なお、Opus 5.5の固定運用などは今回採用しません。モデル指定については現状変更不要です。
>
> ## 1. 目的
>
> Opusを、単なる任意相談先ではなく、
>
> **重要な技術設計に対する独立レビュー役**
>
> として明示的に活用します。
>
> 背景として、FableはPM・PR管理・Gate管理を主担当とし、複雑な技術設計についてClaudeの提案をそのまま受け入れないために、必要な場面ではOpusによる独立レビューを入れます。
>
> Opusレビューの目的はClaude案の追認ではありません。
>
> 必ず、
>
> - そもそもその設計が必要か
> - より単純な方法がないか
> - 既存処理をそのまま利用できないか
> - 不要な複雑化をしていないか
> - 根本原因に対する対策になっているか
> - 別のFailureを生まないか
>
> を独立に評価させてください。
>
> ## 2. Opusレビュー必須：新しい構造・処理フローを設計するとき
>
> 以下のような構造変更を新規設計・変更する場合、実装前にOpusレビューを必須とします。
>
> 例：
>
> - Checker → Rewrite間の受け渡し
> - retry / fallback / regeneration
> - Human Reviewへの遷移
> - LLM出力を後段で解釈・変換する仕組み
> - 複数LLMをまたぐ処理
> - deterministic処理とLLM処理の役割分担
> - model routing
> - validator / QAの大きな構造変更
> - Production初回経路と後続経路の関係変更
>
> 単純なコード修正ではなく、処理構造・責務分担・データの流れを変える変更が対象です。
>
> ## 3. Opusレビュー必須：同じ問題へ2回修正しても再発したとき
>
> 同じ問題について、
>
> 1回目の修正
> → 再発
> → 2回目の修正
> → さらに同種問題が再発
>
> となった場合、3回目の個別パッチへ進む前にSTOPしてください。
>
> この時点でOpusに、
>
> **「個別バグの連続なのか、根本設計に問題があるのか」**
>
> をレビューさせます。
>
> Opusレビューなしに3回目以降の個別パッチを惰性的に追加しないでください。
>
> 今回のOPEN-233 / meta_run03_standardのように、
>
> 「1つの変種を直すと別変種が出る」
>
> ケースが典型例です。
>
> ## 4. Opusレビュー必須：重要変更をProduction採用候補にするとき
>
> Trialで良い結果が出て、ユーザーへProduction正式採用を提案する前に、
>
> 重要な技術変更についてOpus最終レビューを入れてください。
>
> 特に以下に関係する変更を対象とします。
>
> - Production初回経路
> - retry
> - fallback
> - regeneration
> - validator
> - Human Review
> - model routing
> - Safety判定
> - 自動Rewrite
> - 自動Recovery
>
> Opusには、
>
> - Trial専用実装になっていないか
> - Production全体で矛盾しないか
> - 初回・retry・fallback間で仕様が一致しているか
> - Dangling Referenceがないか
> - Failure時に安全側へ倒れるか
> - QCD上の新しい問題を生まないか
>
> を確認させてください。
>
> これはユーザーのProduction採用判断を代替するものではありません。
>
> Opusレビュー後も、正式採用はユーザー判断が必要です。
>
> ## 5. Opusレビューを入れる：QCDが大きく悪化したとき
>
> 以下のような明確な悪化を検出した場合、追加Trialや場当たり修正を繰り返す前に、Opusによる技術レビューを入れてください。
>
> 例：
>
> - Human Review率が大きく増えた
> - コストが大きく増えた
> - 不要Rewrite率が大きく増えた
> - Safety改善によって記事品質が悪化した
> - 非決定性が大きく増えた
> - ある修正によって別Family・別経路が壊れた
> - retry / fallbackが異常に増えた
>
> 単なる1件の通常FAILではなく、設計上の問題を疑うべき変化が対象です。
>
> ## 6. 採用しない条件
>
> 以前案にあった、
>
> **「Fable自身が技術的に十分評価できないとき」**
>
> という条件は採用しません。
>
> 理由は、判断基準が曖昧だからです。
>
> Opus利用条件は、上記のように客観的に判定できる条件を使ってください。
>
> ## 7. Opusレビュー不要の例
>
> 以下のような作業では、原則Opusレビュー不要です。
>
> - typo修正
> - 原因が明確な単純バグ
> - 1行程度の明白な修正
> - ログ追加
> - テスト追加
> - 承認済み仕様の単純な配線
> - ドキュメント更新
> - 既存仕様どおりの機械的変更
>
> 不要にOpusを呼び、コストや作業時間を増やさないでください。
>
> ## 8. Opusレビューで必ず確認する観点
>
> Opusには、最低限以下を独立してレビューさせてください。
>
> 1. そもそもこの変更・設計は必要か
> 2. より単純な構造にできないか
> 3. 既存処理・既存データを利用できないか
> 4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
> 5. 不要なLLM処理を追加していないか
> 6. 非決定性を増やさないか
> 7. Human Reviewを増やさないか
> 8. 不要Rewriteを増やさないか
> 9. コストを不必要に増やさないか
> 10. retry / fallback / regenerationと矛盾しないか
> 11. Failure時に安全側へ倒れるか
> 12. 個別パッチではなく再発防止になっているか
>
> Claude/Fableの案を前提として追認せず、代替案が良ければ明確に提案させてください。
>
> ## 9. Fableの役割
>
> FableはOpusレビュー結果をそのまま採用しないでください。
>
> Claude案・Opusレビュー・CURRENT_SPEC・ユーザー承認内容・QCD・PM Gateを照合して、最終的なPM評価を行ってください。
>
> 役割は、
>
> - Claude：調査・設計・実装・テスト
> - Opus：重要技術設計の独立レビュー
> - Fable：目的・QCD・仕様・Gate・ユーザー判断との整合を管理
>
> とします。
>
> ## 10. 今回の反映先
>
> このルールを既存のPM Governance / 開発運用ルールへ正式に反映してください。
>
> 最低限、
>
> - PM_GOVERNANCE
> - DECISION_LOG
> - Claude/Fableへの委任テンプレート等、実際の運用で参照される箇所
>
> を確認し、重複定義を避けてSSOTへ反映してください。
>
> 既存ルールと競合する場合は勝手に上書きせず、競合内容を報告してください。
>
> 今回の作業は運用ルールの正式反映まで行って構いません。
>
> 反映後、
>
> - 変更ファイル
> - 追加したルールの要約
> - 既存ルールとの競合有無
> - 実際に次回以降このGateが発火する経路
> - commit / push結果
>
> を報告してください。
>
> また、現在進行中のOPEN-233についても、今回のルールに照らしてOpusレビュー対象に該当するかを判定してください。
>
> ただしOPEN-233の技術変更自体は、今回の運用ルール反映と混ぜて実装しないでください。

## Fableの設計判断(この方針で反映すること)

(Fableの設計判断の全文: 正本の置き場所[11-3節=条件・役割・不要例の正本、`OPUS_INDEPENDENT_REVIEW_BLOCK.md`=観点文言の正本、他はポインタのみ]/11-3節の内容[管理ID・位置づけ・条件A〜D・不採用条件・不要例・観点・Fableの役割・モデル指定・既存ルールとの関係・K1〜K5と暫定運用・発火経路・OPEN-233当てはめ]/Fableが把握済みの競合K1〜K5[K1回数上限、K2任意Opusレビュー、K3 sandwich-pm.md旧記述、K4実施タイミング重なり、K5レビュー後の実装着手]とK6以降の報告方針/発火経路1〜8[PM_BRIEF・CLAUDE.md、DELEGATION_STANDARD_TEMPLATE、OPUS_CONTEXT_PACKET_TEMPLATE・opus-consultant.md本文、PM_GOVERNANCE 2節、14節・11-2末尾・1節、REPORT_LEDGER、MODEL_ROUTING_TRIAL_LOG、OPEN_ITEMS OPEN-233行]。実施結果は`DECISION_LOG.md`同管理IDエントリ・`PM_GOVERNANCE.md`11-3節に反映済み。)

## 事前指定Read一覧

(PM_GOVERNANCE 1節・Gate 2〜3・11節・11-1/11-2・14節・変更履歴、DELEGATION_STANDARD_TEMPLATE全文、OPUS_CONTEXT_PACKET_TEMPLATE 1〜60行と189〜末尾、DELEGATION_READ_EFFICIENCY_BLOCK 1〜10・50〜58行、opus-consultant.md全文、sandwich-pm.md 40〜62行[読むだけ]、PM_BRIEF 40〜56・192〜200行、CLAUDE.md Fableサンドイッチ節、MODEL_ROUTING_TRIAL_LOG L2/L3定義部、DECISION_LOG冒頭・最新エントリ、REPORT_LEDGER表ヘッダ・末尾、OPEN_ITEMS OPEN-233行の列区切り、CURRENT_SPEC 1777行付近。)

## 事前指定Grep一覧+追記位置・更新位置の手順

(PM_GOVERNANCE見出し一覧・`Opus|opus`・`十分評価できない`、リポジトリ全体の`Opus.*(最大|上限|1回|2回)|L2\+L3|発火条件`、HISTORY_INDEXの`PM-OPUS-ESCALATION-3TIER`。追記位置は発火経路1〜8のとおり、全て追記のみ。挿入後`git diff --stat`と削除行[`^-`]で既存行が削除・改変されていないことを確認。)

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`。
1. `git status --porcelain=v1 | grep -v '^??'`
2. `git log -3 --stat -- DECISION_LOG.md` / `git log -1 --format=%B 5d4fa8ff`
3. Read/Grep→編集(追記のみ)。
4. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_01.md --json-out docs/pm/delegation_log/2026-10-02_PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02_01.md_check.json`(テンプレート編集後に実行)
5. `git ls-files "docs/pm/tools/*test*" "*check_delegation*test*"`で列挙し、該当があれば`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest <該当ファイル>`(無ければ「該当なし」)。
6. `git diff --stat`と`git diff | grep -c '^-[^-]'`、`git diff -- .claude/agents/opus-consultant.md | head -n 30`、`git status --porcelain=v1 -- .claude/agents/sandwich-pm.md`。
7. Git。

## SSOT追記文

(`DECISION_LOG.md`新規エントリ[ユーザー原文逐語・反映先・正本・不採用・競合K1〜K5・OPEN-233当てはめ・前提確認]、`PM_GOVERNANCE.md`11-3節+ポインタ+変更履歴、`OPEN_ITEMS.md`OPEN-233行次Action追記[Status不変、新規Open Item起票なし]、`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`上書き[.gitignore対象のためadd不可]。)

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`PM_GOVERNANCE.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`[OPEN-233行追記のみ]・`REPORT_LEDGER.md`・`HISTORY_INDEX.md`[前例がある場合のみ])。`CURRENT_SPEC.md`は編集しない。
- 明示`git add`対象: PM_GOVERNANCE.md / DECISION_LOG.md / OPEN_ITEMS.md / REPORT_LEDGER.md / PM_BRIEF.md / CLAUDE.md / MODEL_ROUTING_TRIAL_LOG.md / OPUS_INDEPENDENT_REVIEW_BLOCK.md / OPUS_CONTEXT_PACKET_TEMPLATE.md / DELEGATION_STANDARD_TEMPLATE.md / opus-consultant.md / 本委任文ログ(1ファイルずつ指定)
- コミットメッセージ: `PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02: Opus独立技術レビューGate(PM_GOVERNANCE 11-3)を新設、テンプレート・エージェント定義・PM_BRIEF等へ参照を追記(既存ルールは未変更、競合K1〜は報告)`
- trailer: 直前commitの形式に合わせる。commit後`git push origin main`。エラー・競合・add拒否はSTOPして報告。

## 報告(RESULT_PACKET項目)

1. 変更ファイル一覧(追記節・行範囲・追記行数・削除行数)。2. 追加ルールの要約+11-3節全文+ブロック全文。3. 既存ルールとの競合K1〜K5+K6以降。4. 発火経路1〜8の追記箇所と逐語。5. sandwich-pm.md・frontmatter未変更確認。6. T-0結果・テスト結果。7. commit/push結果・raw URL。8. 迷った点・追加Read。

(注: 本ファイルのFable設計判断以降の各節はSonnet実行層が要約形で保存したもの。ユーザー原文・性質/禁止事項・固定ブロックは逐語。完全な委任文原本は会話ログ上にのみ存在し、本ファイルは見出し構成を保って保存した。)
