# 委任_39 委任文(T-0保存、受領した委任文の全文)

## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_39: **設計再検討のみ**。設計書の新規作成、read-only調査、¥0。実装・Trial・API課金なし)。
**並行タスクあり**: 別のsonnet-workerが `PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02`(運用ルール文書の反映)を実行中で、`docs/pm/PM_GOVERNANCE.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・`docs/pm/REPORT_LEDGER.md`・`docs/pm/PM_BRIEF.md`・`CLAUDE.md`・`docs/pm/templates/*`・`.claude/agents/opus-consultant.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md` を編集し、git commit/pushも行う。**衝突回避のため、本委任ではこれらのファイルを一切編集せず、git add/commit/pushも行わない**(下記)。

## 性質/到達上限Status/禁止事項

- 性質: 設計再検討(設計案の文書化)。ユーザー指示により、本設計案は**実装前にOpusの独立レビューへ回す**(PM_GOVERNANCE 11-3[新設中] 条件A・B該当、かつ今回はユーザーの明示的なレビュー指示)。したがって設計書は、Opusがファイル:行を辿って検証できる自己完結した文書にする。
- 到達上限Status: `USER_DECISION_REQUIRED`のまま(変更しない)。今回の到達範囲は「設計再検討+Opusレビュー+最終推奨案の提示まで」で、本委任はその最初の「設計案作成」部分。
- 費用: ¥0(費用上限[Cap]を伴わないためT-3非該当)。API呼び出し・TTS・Web Search禁止。
- 禁止事項:
  - **実装しない**(`*.py`・Prompt・テストを一切変更しない)。**Trialを回さない**(runner・Trialスクリプトを実行しない、LLMを呼ばない)。**Production正式pathを変更しない**。
  - 既存の記録データ(`er052_output/`配下のJSON)に対する**API呼び出しなしの読み取り集計**(例: 既存claim文字列が記事に逐語で含まれるかの照合)は可。スクリプトはリポジトリ外の一時ディレクトリに作る。これはTrialではなく既存記録の読み取りであることを設計書に明記し、結果は「既存記録の再集計」とラベルを付ける。
  - 並行タスクが編集中の上記ファイル、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`)、既存設計書`docs/pm/design_open233_self_recovery_flow_01.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`を編集しない(SSOT編集権なし)。`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`にも書かない。
  - **git add/commit/pushをしない**(並行タスクのcommitと衝突させないため。commitは後でFableが別途指示する)。読み取り系git(`git log`/`git grep`/`git status --porcelain`)のみ可。
  - リポジトリ内に新規作成してよいのは3ファイルのみ: 設計書`docs/pm/design_open233_violation_span_handoff_01.md`、委任文保存`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39.md`(+T-0の`_check.json`)、結果`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39_result.md`。
  - 「今そうなっているから」を理由に現行処理を残さない。逆に、ユーザーの基本線に合わせるために不都合な事実(逐語保証の限界、解決しない失敗要因等)を伏せない。推測と確認済み事項を書き分ける。実データの引用は実ファイルからの逐語コピーのみ。
  - 文ID・文字オフセット方式へ先に結論を寄せない(ユーザー指示§4・§7: まず「違反範囲そのものを構造化してそのまま渡す」でどこまで解決できるかを優先し、3案を比較した上で最も単純で十分な案を選ぶ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
(本委任はTTSを伴わない。T-1・T-3は非該当。T-0は本委任文の**全文**を保存し、結果は`_39_result.md`へ1行記録する。)

## ユーザー指示(原文)

> OPEN-233 / meta_run03_standard の残存Human Review問題について、現行案をそのまま進めず、以下の考え方を基本線として設計を再検討してください。
>
> 今回は特別に、**Claudeが設計した内容を実装前にOpusへ独立レビューさせてください。**
>
> 通常のOpus利用は先に決めた運用ルールに従えばよく、毎回個別指示は不要ですが、今回はこの設計問題に対する明示的なレビュー指示です。
>
> ## 1. 基本線
>
> Rewrite対象の受け渡しは、原則として以下の4点で再設計してください。
>
> 1. **Checkerは違反箇所を原文逐語で返す**
> 2. **複数文が違反対象なら、複数文のまま範囲として返す**
> 3. **その違反範囲をそのままRewrite側へ渡す**
> 4. **記事へ戻すために必要な後段処理だけ残す**
>
> 重要なのは、
>
> **後段処理がCheckerの判断した違反範囲を勝手に縮小・再解釈しないこと**
>
> です。
>
> 今回のように、
>
> Checker:
> 「この2文が問題」
>
> ↓
>
> 後段処理:
> 「似ている1文だけ選ぶ」
>
> という情報劣化は起こさないでください。
>
> ## 2. まず現行フローとの差分を整理する
>
> 実装前に、現在の処理と上記4点の差を整理してください。
>
> 最低限、
>
> - Checkerが何を返す
> - 後段で何を加工している
> - Rewriteへ何を渡す
> - Rewrite結果をどう記事へ戻す
> - JA側をどう対応付ける
> - 再検査で何を使う
>
> を処理順で示してください。
>
> 特に、
>
> **現在なぜ「Checker出力を一度記事から探し直す」必要があるのか**
>
> を再評価してください。
>
> 「今そうなっているから」ではなく、本当に必要な処理だけ残してください。
>
> ## 3. Checker出力の逐語性を高める
>
> Checkerには、違反箇所について可能な限り、
>
> **記事本文から一字一句そのまま引用する**
>
> ことを明示してください。
>
> 少なくとも、
>
> - 勝手に要約しない
> - 大文字小文字を変えない
> - 句読点を変えない
> - 複数文なら複数文をそのまま返す
> - 離れた2文なら、1つの連続文字列に捏造せず、別々の対象として返す
>
> 方向を検討してください。
>
> もし原文逐語を100%保証できない場合は、その限界を明示してください。
>
> ## 4. 複数文・複数箇所の扱い
>
> 今回の問題は、違反が1文とは限らないことです。
>
> そのため、
>
> - 連続する2文
> - 離れた2文
> - 1文の一部
> - 複数箇所
>
> をどう表現するか設計してください。
>
> ただし、これを理由にすぐ大規模な「文ID・文字オフセット必須」へ飛ばないでください。
>
> まず、
>
> **違反範囲そのものを構造化してそのまま渡す**
>
> ことでどこまで解決できるかを優先してください。
>
> ## 5. 後段処理は「記事へ戻すため」に限定する
>
> 位置情報や対応付けが必要な処理は残して構いません。
>
> 例：
>
> - Rewrite結果を元記事へ戻す
> - JA側の対応範囲を決める
> - Hook / Title / 本文区分を維持する
> - 前後文脈を取得する
> - Rewrite前後を記録する
> - 再検査する
>
> ただし、
>
> **違反対象をもう一度推測し直す処理**
>
> は原則なくしてください。
>
> 位置情報を使う場合も、
>
> 「違反文を後から探すため」
>
> ではなく、
>
> **「すでに特定済みの違反範囲を安全に置換・復元するため」**
>
> に使う設計を優先してください。
>
> ## 6. meta_run03_standard の実例で設計を当てる
>
> 今回問題になった実例、
>
> > It said human staff made inappropriate comments about race during calls.
> > These calls were about trying to lower internet or cable fees.
>
> の2文を使って、
>
> 新設計なら、
>
> - Checkerがどう返すか
> - Rewriteへ何を渡すか
> - どこを直すか
> - どう元記事へ戻すか
> - 1周で2文とも適切に処理できるか
>
> を具体的に示してください。
>
> さらに、もう1件の「離れた2文をまとめて指摘したケース」にも適用できるか確認してください。
>
> ## 7. 文ID・文字オフセット案は代替案として評価する
>
> 文ID・文字オフセット方式を禁止するわけではありません。
>
> ただし、
>
> **本当に必要かを比較した上で採用してください。**
>
> 最低限、
>
> - 原文逐語＋複数範囲をそのまま渡す方式
> - 文IDを併用する方式
> - 文字オフセットまで持つ方式
>
> を比較し、
>
> - 単純さ
> - 堅牢性
> - 非決定性
> - JA/EN対応
> - Rewrite後の戻しやすさ
> - 既存コードへの影響
> - 再発防止
> - コスト
>
> で評価してください。
>
> 最も単純で十分な案を優先してください。
>
> ## 8. Opus独立レビュー
>
> Claudeが設計案を作ったら、**実装前にOpusへ独立レビュー**させてください。
>
> Opusには、Claude案を追認させるのではなく、最低限以下を確認させてください。
>
> 1. Checkerが違反箇所を既に持っているのに、後段で再探索する必要が本当にあるか
> 2. 違反範囲をそのままRewriteへ渡す設計で十分ではないか
> 3. 複数文・離れた複数箇所を安全に扱えるか
> 4. 文ID・文字オフセットは必要か、過剰設計ではないか
> 5. Rewrite結果を記事へ戻す工程だけ位置情報を使う構造にできないか
> 6. JA/EN同時修正に問題が出ないか
> 7. Hook / Title / 本文など既存区分を壊さないか
> 8. retry / fallback / 再検査との整合
> 9. Human Reviewを本当に減らせるか
> 10. 新しいFailure modeを作らないか
> 11. 個別パッチではなく再発防止になっているか
> 12. さらに単純な代替案がないか
>
> ## 9. Opusレビュー後の扱い
>
> Opusの意見をそのまま採用しないでください。
>
> Claude案とOpusレビューを並べて、
>
> - 一致点
> - 相違点
> - 最終推奨案
> - 採用理由
> - 残るリスク
>
> をFableが整理してください。
>
> ## 10. 今回の到達範囲
>
> 今回は、
>
> **設計再検討＋Opusレビュー＋最終推奨案の提示まで**
>
> です。
>
> まだ実装しないでください。
> Trialも回さないでください。
>
> Statusは引き続き`USER_DECISION_REQUIRED`です。
>
> ユーザーが設計案を確認してから、実装・限定Trialへ進みます。
>
> Production正式pathは変更禁止です。

(本委任の担当は§1〜§7の設計案作成。§8のOpusレビュー起動と§9の整理はFableが行う。ただし設計書は、§8の12項目にOpusが答えられるだけの材料[現行コードの該当行・実データ・比較根拠]を含むこと。)

## 事前指定Read一覧

- `docs/pm/explain_open233_checker_to_rewrite_target_01.md`: 全文(275行。委任_38で作成した現行構造の説明。コード行番号・実データの出発点として使う。ただし鵜呑みにせず、設計の根拠にする箇所はコードで再確認する)
- `er052_open233_self_recovery_flow_runner_01.py`: 1105〜1155(Stage 1追記Prompt・`same_fact_id_locations`)、1844〜1875(区分判定)、2241〜2268(`locate_best_sentence`)、2285〜2536(引用断片抽出・`locate_multi_quote_span`・`locate_target`・`locate_paragraph_block`・`locate_ja_counterpart_by_position`)、2555〜2634(Rewrite Prompt雛形)、2731〜3235(`single_text_rewrite`・`paired_rewrite`・`run_stage3_for_claim`・ラダー・guard)。加えて、Recheck(再検査)がStage 1出力をどう受けて次cycleへ渡すか・cycle上限の箇所を `cycle_limit|recheck|max_cycles` でGrepして該当範囲を読む。
- `er003_v1_en_direct_vfl_01_generate.py`: 455〜470(schema)、502〜601(`DEVIATION_PROMPT_TEMPLATE`)。**このPrompt/schemaがProduction正式pathで使われているか、Self-Recovery FlowのStage 1がこれをそのまま呼ぶのか・Trial専用variant(`er051_open233_checker_trial_variant_01.py`)経由なのか**をGrepで確定する(Checker Promptを変える場合に、Production正式pathへ触れずにTrial専用で差し替えられる構造かどうかが設計の前提になる)。
- `er052_open233_self_recovery_stage2_production_01.py`: 40〜79(Stage 2 Prompt、rewrite_hintの指示)、184〜213(`build_local_context`、引用符除去の前例)
- `docs/pm/design_open233_self_recovery_flow_01.md`: §0(219〜290行: 上位原則、特に0-3「Rewriteは品質リスク」・0-4「問題種類→初期Rewrite単位」)、§3-1(444〜531)、§5-2(1725〜1777)、§5-4(1833〜1925)、§5-7(2117〜2161: 最小変更ラダー)、§5-11(2315〜2392)、§6-5(2548〜2627: 局所QA fastpath)、§6-14〜§6-17(3118〜3394)
- 実データ(Pythonで該当キーのみ抽出、全文Read不可):
  - `er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`(deviations全件の`claim_in_article`・`same_fact_id_locations`・`origin`)
  - `er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json`(連続2文の実例、cycle1〜3)
  - `er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json`(離れた2文の実例、JA側hintの食い違い)
- Existing Spec / Prior Trial Check(PM_GOVERNANCE 21節): `docs/pm/design_open233_self_recovery_flow_01.md`・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`・`docs/pm/opus_l2_review_open233_self_recovery_01〜04.md`・`docs/pm/design_open233_checker_redesign_trial_01.md`を `verbatim|逐語|exact substring|quote|span|offset|オフセット|文ID|sentence_id` でGrepし、「Checkerに逐語引用・範囲・位置を返させる」案が過去に検討・試行・却下されていないかを確認して、A(既存仕様あり)/B(過去Trialあり・未採用)/C(本当に新規)に分類する。該当箇所のみ読む。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記Read一覧内のGrep指定のとおり。
- `er052_open233_self_recovery_flow_runner_01.py`: `claim_text|claim_in_article` の全使用箇所(後段でclaim文字列を使っている工程の全数。「違反範囲を再推測している箇所」と「特定済みの範囲を使っているだけの箇所」を分類するため)。
- `er052_open233_self_recovery_flow_runner_01_test_01.py`: `locate_|multi_quote|ladder` (既存テストがどの挙動を固定しているか=設計変更時の影響範囲)。テストは実行しない。
- 追記・更新位置: 既存ファイルへの追記なし。新規ファイル3つのみ。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`(一時ディレクトリの読み取り集計スクリプト実行用のみ)。
1. 上記Read/Grep。
2. (任意・¥0)既存記録の再集計: rep19〜21のmeta_run03_standardおよび同runnerの他記事の出力(`er052_output/open233_self_recovery_flow_runner_01_iter8*/`等、存在する範囲)について、Stage 1/Recheckの`claim_in_article`が (a) そのまま記事に含まれる (b) 両端の引用符を外せば含まれる (c) 引用断片ごとに分割すれば全て含まれる (d) いずれでも含まれない、の件数を数える。「逐語+複数範囲をそのまま渡す方式」が既存データのどれだけをカバーするかの根拠にする。対象run・件数・除外条件を明記。
3. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39.md --json-out docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39.md_check.json`
runner・Trialスクリプト・回帰テストは実行しない。git add/commit/pushはしない。

## 設計書の要件(`docs/pm/design_open233_violation_span_handoff_01.md`)

冒頭に: 管理ID、Status(USER_DECISION_REQUIRED据え置き・設計案でありユーザー未承認・未実装)、「実装前にOpus独立レビュー対象」、結論の要約(10行以内)。読み手はプロジェクト責任者とOpus(レビュー役)。日本語、平易に、技術用語は初出時に短い説明。根拠にはファイル:行を付ける。

1. **現行フローと基本線4点の差分**(ユーザー§2): 処理順(Checkerが返すもの→後段での加工→Rewriteへ渡すもの→記事への戻し方→JA側の対応付け→再検査で使うもの)で表にする。各工程を「(R)違反対象を再推測している処理」「(P)特定済みの範囲を記事へ戻す・記録する・文脈を取るための処理」「(?)どちらとも言えない」に分類し、根拠(コード行)を付ける。**「なぜCheckerの出力を一度記事から探し直しているのか」の再評価**: 探し直しが本当に必要な理由と、現行実装の都合・経緯に過ぎないものを分ける。Stage 2(判定役)のrewrite hint内の引用を対象決定の第一手に使っている点(Checkerの指摘範囲と別の箇所を指しうる)、最小変更ラダー(単語→1文→段落)が対象範囲を1文へ絞る点、書き換え後guard(`claim_text not in candidate`)が引用符付き文字列では常に成立しうる点も、この分類に含めて評価する。
2. **Checker出力の逐語性**(ユーザー§3): Promptへ加える指示の文案(実装はしない、文案のみ)と出力形式の案。ユーザーが挙げた5点(要約しない/大文字小文字を変えない/句読点を変えない/複数文は複数文のまま/離れた2文は別々の対象として返す)への対応。**逐語を100%保証できない限界を明示**(LLM出力である以上Promptだけでは保証できない。既存の前例: `same_fact_id_locations`は逐語指示があるのに`"Paragraph 7"`等を返した)。そのうえで、受け取り側での機械的な逐語確認(完全一致照合)と、**逐語でなかった場合の扱いの選択肢**(例: その対象だけ安全側へ倒す/Checkerへ1回だけ返し直させる/正規化[引用符・空白のみ]して再照合、等)を、追加LLM呼び出しの有無・非決定性・Human Reviewへの影響とともに比較し、推奨を示す。「正規化」と「再推測」の境界(どこまでが機械的で、どこからが推測か)を明確に定義する。
3. **複数文・複数箇所の表現**(ユーザー§4): 連続する2文/離れた2文/1文の一部/複数箇所、それぞれを出力形式でどう表すか。まず「違反範囲そのものを構造化して(例: 範囲の配列として)そのまま渡す」方式でどこまで解決できるかを示す。同一文字列が記事中に複数回出現する場合の扱い、範囲同士が重なる場合の扱いも定義する。
4. **後段処理の限定**(ユーザー§5): 残す処理(記事へ戻す/JA側の対応範囲/Hook・Title・本文区分の維持/前後文脈の取得/Rewrite前後の記録/再検査)と、なくす処理(違反対象の再推測)の一覧。各「残す処理」が、特定済みの範囲を入力としてどう動くか。**JA側の対応範囲の決定は、Checkerが返さない情報を必要とする**ので、ここは再推測を完全にはなくせない可能性がある — その場合は正直に「残る推測」として書き、選択肢(CheckerにJA側の対応箇所も逐語で返させる/origin別に扱う/現行の位置比近似を残す等)を比較する。最小変更ラダー・設計書§0-3「Rewriteは品質リスク」(不要な書き換えを増やさない)との両立(範囲全体をRewriteへ渡しつつ、範囲内の変更は最小にする、書き戻しは範囲全体の置換、等)も示す。
5. **実例への適用**(ユーザー§6): (i) rep21 sample1の連続2文、(ii) rep20 sample2の離れた2文、それぞれについて、新設計での「Checkerの返し方(具体的な出力例)→Rewriteへ渡すもの→直す箇所→記事への戻し方→JA側→再検査」を処理順で具体的に示す。**「1周で2文とも適切に処理できるか」**は、設計が保証する部分(2文とも対象としてRewriteへ渡り、2文とも書き戻し対象になる)と、保証できない部分(Rewrite役のLLMが実際に適切に直すか、再検査が別の指摘を出すか)を分けて答える。rep21 sample1のcycle3で出た別事実(MUSE-HC-010)の新規指摘のように、**受け渡しの是正では解決しない要因**も明示する。
6. **3案比較**(ユーザー§7): (案1)原文逐語+複数範囲をそのまま渡す、(案2)文IDを併用、(案3)文字オフセットまで持つ。評価軸は 単純さ/堅牢性/非決定性/JA・EN対応/Rewrite後の戻しやすさ/既存コードへの影響/再発防止/コスト の8つ(表)。各案で「LLMに何を出力させるか」「LLMが間違えたときに何が起きるか・機械的に検出できるか」を必ず書く(例: LLMは文字数を数えるのが不得意、文IDは記事を文に分割して番号を振って渡す前処理が要る、等。根拠のない一般論は「一般的な傾向であり本プロジェクトでは未検証」と明記)。最も単純で十分な案を推奨し、**推奨案で足りない場合にのみ次の案へ進む条件**を書く。
7. **影響範囲と整合**: 変更が必要になるコード・Prompt・テストの一覧(実装はしない)、Trial専用で実現できる範囲とProduction正式pathに触れる範囲の区別、retry/fallback/再検査・cycle上限・fail-closed(迷ったら人間確認へ)との整合、Hook/Title/本文区分への影響、既存の是正(委任_35の原因(d)・委任_36の`locate_multi_quote_span`等)のうち新設計で不要になるもの/残すもの。
8. **新しく生まれうるFailure modeと残るリスク**: 例: 逐語でない出力が増えてHuman Reviewが増える可能性、範囲全体を渡すことで書き換え量が増える可能性、Checkerの出力形式変更が検出精度(見逃し・誤検出)に与える影響、固定fixtureが新形式と合わなくなる点、等。Human Reviewを本当に減らせるかの見込みを、根拠のある範囲と不明な範囲に分けて書く(数値目標を根拠なく書かない)。
9. **Existing Spec / Prior Trial Check結果**(A/B/C分類と根拠)。
10. **検証するなら何を確認すべきか**(限定Trialの骨子のみ。実行しない。費用は概算の根拠が示せる場合のみ、示せなければ「未算定」)。
11. **確認済み/未確認の区別**、Opusに特に見てほしい論点(設計者として自信がない点・判断が割れうる点を率直に列挙)。

## SSOT追記文

なし(SSOTは編集しない。ユーザー承認前の設計案のため、既存設計書・REPORT・OPEN_ITEMSへの反映は行わない)。

## Git(明示add対象・コミットメッセージ・trailer)

**git add/commit/pushは行わない**(並行タスクとの衝突回避)。SSOT編集権なし。`-A`/`stash`/`amend`禁止。新規3ファイルは未追跡のまま残す。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`には書かず、`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_39_result.md`と最終メッセージに次を記載:
1. 管理ID・委任番号・Status(USER_DECISION_REQUIREDのまま)・費用¥0・実装/Trial/commitなしの確認。
2. 設計案の結論(推奨案、3案比較の要約表、現行から「なくす処理」「残す処理」)。
3. 実例2件への適用結果の要約と、「1周で2文とも処理できるか」への答え(保証できる部分/できない部分)。
4. 逐語保証の限界と、逐語でなかった場合の扱いの推奨。
5. 受け渡しの是正では解決しない要因、新しいFailure mode、残るリスク。
6. Existing Spec / Prior Trial CheckのA/B/C分類。
7. 既存記録の再集計を行った場合はその結果(対象・件数・ラベル)。
8. Opusに特に見てほしい論点。
9. 読んだファイルと行範囲、一覧外の追加Readの理由、T-0結果1行。
10. 作成した3ファイルのパスと、他ファイルを変更していないことの確認(`git status --porcelain=v1`で自分の新規ファイル以外に自分起因の変更がないこと。並行タスクによる変更は区別して記載)。
