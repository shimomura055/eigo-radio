## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_42: **受け渡し修正の実装+限定Trial**[ユーザー指示§1・§2]、ユーザー決定の記録)。
**並行タスクあり(3件、いずれもread-only・git操作なし・SSOT/コードを編集しない)**: 委任_43(日本語側の実害調査)、委任_44(2周目・3周目の新規指摘の原因分析)、委任_45(Checker引用の特定不能35件の原因分類)。これらは`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43*`〜`_45*`だけを新規作成する。**本委任はそれらのファイルに触れない・addしない**。コード・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を編集するのは本委任だけ。

## 性質/到達上限Status/禁止事項

- 性質: Trial/検証用の範囲での実装+課金ありの限定Trial。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: **条件A・B該当、ただしレビュー済み**(`docs/pm/opus_l2_review_open233_self_recovery_05.md`、2026-10-02)。本委任の実装範囲は、レビュー済み設計(`docs/pm/design_open233_violation_span_handoff_01.md`)からユーザー決定で項目を減らしたもの(Checker Prompt変更なし・別AI引用救済なし・文単位スナップなし)+Opusが指摘しFableが採用した修正のみであり、新しい構造は含まないため再レビューしない。**本委任の範囲を超える構造変更(Checkerの出力契約変更、日本語側の処理構造の見直し[英語だけ直す化]、Checker見逃し対策、cycle構造の変更)は実装しない**(別途Opusレビュー後に委任する)。
- 到達上限Status: Trial要素としての測定結果の報告まで。`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の分類はFableが行う(本委任では成功条件ごとの実測値と所見を示す)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`は対象外。
- 費用: Phase累計¥485.9275/総枠¥600/残¥114.0725。**本委任の上限¥15(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。** 総枠¥600を超える見込みになった場合は必ずSTOP(ユーザーSTOP条件)。
- 禁止事項:
  - **Production正式pathを変更しない**(`er003_v1_n3_01_articles_generate.py`、`er003_v1_en_direct_vfl_01_generate.py`[Checker Prompt/schema本体]等。変更はTrial専用の`er052_open233_self_recovery_flow_runner_01.py`とそのテスト・Trial実行スクリプトの範囲に限る)。**Checker(Stage 1/Recheck)のPrompt・schemaを変更しない**。Stage 2(判定役)のPrompt・rubric・floorを変更しない。cycle上限(`MAX_CYCLES`/`HARD_MAX_CYCLES`)・ラダー⑥(既定OFF)を変更しない。
  - ユーザー基本線に反する処理を残さない・足さない: Checkerが示した違反範囲を後段で再推測しない/別AI(判定役)の引用でRewrite対象を決めない/類似度・単語重なりで1文へ縮小しない/文ID・文字オフセットを導入しない/文の一部の指摘を最初から文全体へ広げない(最小修正優先: 語句→文全体→必要最小範囲の順でのみ拡張)。
  - 1回TrialがFAILした・新しい変種が1つ出た、だけではSTOPしない(ユーザー§8)。原因特定→本委任の範囲内の修正→限定再確認まで進める。ただし修正が本委任の範囲を超える構造変更になる場合は、実装せず、原因と必要な変更を報告する。
  - 推測を事実として書かない。成功条件の判定は実測値で示す。false PASS・Safety対照の結果を省略しない。
  - `git add -A`/`stash`/`amend`/force push禁止。既存の未commit変更(`er0XX_output/`配下の既存ファイル)・並行タスクのファイル・無関係の未追跡ファイルに触れない・addしない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-
WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久
運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を
`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/
check_delegation_prompt.py --file <path> --json-out <path>_check.json`
を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する
(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、
既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルール
ではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り
`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外
条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`
等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは
別ラベルであり、ラベルの意味を混同しない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、
費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のための
Guardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限
記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済み
scope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な
範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時
(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の
原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らか
にQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を
報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続
条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の
全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に
該当する条件として維持する(置き換えではない)。
(本委任はTTSを伴わない。T-1は非該当。T-0の保存先は`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_42.md`、見出しを省略せず保存。)

## ユーザー指示(原文)

(2026-10-02、全文。`DECISION_LOG.md`へ**逐語で**収録すること。本委任の担当は§1・§2。§3〜§5は並行タスク[委任_43〜45]が調査中で、その対策実装は別委任。)

> OPEN-233について、ここまでのユーザー判断を反映して次工程へ進んでください。
>
> 今回は「調査だけ」ではなく、**調査結果に基づいて必要な対策まで入れる**ことを前提とします。
>
> ただしProduction正式pathは変更禁止です。Trial/検証用の範囲で進めてください。
>
> ## 1. まず受け渡し修正を実装する
>
> 今回の直接原因だった、
>
> **Checkerが複数文を違反として出しているのに、後段処理が1文だけ選んでRewriteへ渡す**
>
> という問題を修正してください。
>
> 基本線は以下です。
>
> - Checkerが示した違反範囲を後段で再推測しない
> - 複数文なら複数文のままRewriteへ渡す
> - 離れた複数箇所なら複数範囲として渡す
> - 別AIの引用でRewrite対象を決めない
> - 類似度や単語重なりで勝手に1文へ縮小しない
> - 文ID・文字オフセット方式は現時点では採用しない
> - 最小修正優先ルールを維持する
>
> Rewrite範囲は既存ルールどおり、
>
> **語句単位で修正**
> ↓
> 語句だけでは違反が解消しない、または文が不自然になる
> ↓
> **文全体へ拡張**
> ↓
> それでも不足する場合のみ、さらに必要最小範囲へ拡張
>
> としてください。
>
> 文の一部が違反だからといって、最初から文全体Rewriteへ広げないでください。
>
> `oil prices → Brent futures`
>
> のように語句だけで済むものは、語句だけを修正します。
>
> ## 2. 受け渡し修正後、限定Trialを実施する
>
> 対象はまず`meta_run03_standard`中心で構いません。
>
> 最低限、
>
> - 2文取りこぼし型
> - 離れた複数箇所型
> - Safety確認用の対照
>
> を確認してください。
>
> 成功条件：
>
> - 2文取りこぼしによるHuman Review 0
> - Checkerが示した違反範囲を勝手に縮小しない
> - 誤って危険な記事をPASSしない
> - Rewrite範囲は最小修正優先
> - 不要な段落・全文Rewriteを増やさない
>
> 費用は既存予算内で最小限にしてください。
>
> ## 3. Checker引用13.4%特定不能について、原因調査＋対策まで行う
>
> 過去ログ集計では、
>
> **重大指摘261件中35件、13.4%**
>
> で、Checkerが返した違反箇所の文字列を記事本文へそのまま対応付けられませんでした。
>
> これは今回のMetaでは0件でしたが、全体として潜在課題です。
>
> 単に件数を再報告するのではなく、35件を原因別に分類してください。
>
> 最低限、
>
> - 原文を少し言い換えて返している
> - 大文字小文字・句読点等の差
> - 「〜で始まる段落」など説明文を混ぜている
> - 複数箇所を1つの文字列に結合している
> - その他
>
> に分けてください。
>
> その上で、原因ごとに対策を設計してください。
>
> 特に、
>
> **Checkerに「違反箇所は記事本文から一字一句そのまま引用すること。要約・言い換え・勝手な結合は禁止。複数箇所なら別々の原文範囲として返すこと」と明示するPrompt変更で、どこまで解消できるか**
>
> を評価してください。
>
> 必要性が高いと判断した場合は、Trial/検証用Promptで限定的に実装して確認して構いません。
>
> ただし、判定基準そのものは変えず、**違反範囲の出力形式だけを変える**こと。
>
> 対策後、
>
> - 特定不能率
> - 検出漏れ
> - false PASS
> - 出力失敗
> - Human Reviewへの影響
>
> を確認してください。
>
> ## 4. 日本語側は「英語だけ直す」前提で設計を再検討する
>
> ユーザー方針は明確です。
>
> **日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。**
>
> したがって、
>
> 英語のDeviation修正のたびに、日本語側の対応箇所を推測して同時Rewriteする前提を見直してください。
>
> まず、
>
> **英語だけ修正して終了**
>
> する設計を基本案として再検討してください。
>
> 確認すべきなのは、
>
> - 日本語を修正しないことで後続Production処理に実害があるか
> - 古い日本語が後段で再利用され、英語へ誤りが再流入する経路があるか
> - ユーザー表示・音声・解説等で日本語がそのまま正式出力として使われるか
> - 再生成時に日本語から英語を作り直す経路があるか
>
> です。
>
> 単に「日英整合を保ちたい」という理由だけなら、日本語まで遡って修正する必要はありません。
>
> 実害がなければ、日本語側の複雑な推測処理は外す方向で設計してください。
>
> 実害がある場合は、その経路を具体的に示した上で最小限の対策を提案してください。
>
> ## 5. 2周目・3周目で新しい問題が見つかる件は、原因調査だけでなく対策まで行う
>
> これは受け渡し問題とは独立した課題です。
>
> 同じ元記事でも、
>
> - 1周目では問題Aだけ検出
> - 2周目で別問題Bを初めて検出
> - 3周目でさらに別問題Cを検出
> - あるrunではB/C自体が出ない
>
> という揺れがあります。
>
> 各ケースについて、具体文付きで切り分けてください。
>
> 最低限、
>
> - 1周目で何を検出したか
> - 2周目で何を検出したか
> - 3周目で何を検出したか
> - 各指摘はMinor / Majorどちらだったか
> - 元記事に最初から存在していた問題か
> - Rewriteによって新しく発生した問題か
> - 同じ問題がMinor→Majorへ変化したのか
> - 1周目では完全に見逃していたMajorなのか
>
> を明確にしてください。
>
> その上で、原因ごとに対策まで入れてください。
>
> 例：
>
> ### 重大問題の見逃しが原因
> Checker Prompt・チェック順序・全件走査方法を見直し、
>
> **1回目で重大問題をまとめて検出できる構造**
>
> を優先してください。
>
> ### Minor / Major判定の揺れが原因
> 重大度判定基準を明確化し、必要なら決定論的なSafetyルールへ寄せてください。
>
> ### Rewriteが新しい問題を作っている場合
> Rewrite Prompt・最小修正ルール・Rewrite後QAを是正してください。
>
> ### 周回構造そのものが原因
> cycle上限を安易に増やすのではなく、
>
> **なぜ複数周必要になるのかを減らす設計**
>
> を優先してください。
>
> 原因分析だけでSTOPせず、Guardrail内で対策実装＋限定再確認まで行ってください。
>
> ## 6. Opusレビュー
>
> 今回の作業には、
>
> - Checkerの出力契約変更
> - 日本語側の処理構造見直し
> - Checker見逃し対策
>
> など、構造変更に該当する可能性があります。
>
> 先に正式採用したOpus独立技術レビューGateに従ってください。
>
> 新しい構造案を実装する前にOpusレビューが必要な条件に該当する場合は、必ず実施してください。
>
> ただし、今回すでにOpusレビュー済みの受け渡し修正そのものを、内容が変わっていなければ重複レビューする必要はありません。
>
> ## 7. 今回の到達目標
>
> 見えている残課題は以下です。
>
> 1. 受け渡し問題
> 2. Checker引用13.4%特定不能
> 3. 日本語側を同時修正する必要性
> 4. 2周目・3周目で重大問題が新たに出る揺れ
>
> 今回、可能なものは**調査だけでなく対策＋限定確認まで**進めてください。
>
> その後、
>
> **最新版で29件横断再確認**
> ↓
> 重大な新問題がなければ
> **実記事N増し**
>
> へ進む想定です。
>
> ## 8. STOP条件
>
> 以下の場合のみUSER_DECISION_REQUIREDとしてSTOPしてください。
>
> - 新しいProduct原則の採用が必要
> - Safety原則の変更が必要
> - Production正式仕様の変更判断が必要
> - ¥600予算上限超過が必要
> - Claude案とOpusレビューが重要点で対立し、Fableで解消できない
> - 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要
>
> 単に1回TrialがFAILした、1つ新しい変種が出た、という理由だけでは戻さず、Guardrail内で原因特定→対策→限定再確認まで進めてください。
>
> Production正式pathは変更禁止です。
>
> Trial終了時には、
>
> - REJECTED
> - VALIDATED
> - USER_DECISION_REQUIRED
>
> のいずれかへ分類してください。
>
> VALIDATEDでもProduction採用ではありません。

## 実装仕様(Fable確定。この範囲で実装する)

対象: `er052_open233_self_recovery_flow_runner_01.py`(Trial専用runner)とそのテスト`er052_open233_self_recovery_flow_runner_01_test_01.py`、および新しいTrial実行スクリプト(既存の`…_rep21_representative_01.py`と同じ形式の`…_rep22_…`)。

**(1) 範囲の確定(新規関数。再推測ではなく照合)**: Checkerの`claim_in_article`(runner内では`claim_text`)だけを入力に、次の文字単位の照合のみで、記事中の範囲(記事側の文字列)を確定する。定義は無料集計(`er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`、委任_41)と同一にする(同スクリプトの照合ロジックを参照し、runnerへ移植する。importはしない)。
- L0 そのまま含まれる/L1 文字列全体を囲む1組の引用符・括弧を外す/L2 空白・改行の連続、曲線/直線の引用符・アポストロフィの同一視/L3 大文字小文字の同一視/L4 引用断片が2つ以上あり、断片以外の残りがつなぎ語・句読点・空白だけ(and / or / , / ; / / / 、 / と / および / & 等)の場合に限り、各断片を別々の範囲にして各々L0〜L3で照合。残りに説明文がある場合(断片1つ+説明文も含む)は分解せず確定不能。
- 確定の条件: 対象本文に**ちょうど1箇所**。0箇所・2箇所以上は確定不能。L4は全断片が確定した場合のみ。照合はEN本文・JA本文の両方に対して行い、どちらで確定したかを保持する。
- 複数範囲の整理: 重なる、または間が空白だけで隣接する範囲は1つに結合(段落区切り`\n\n`はまたがない)。一方が他方を含む場合は大きい方へ吸収。
- 確定不能の指摘: 類似度・単語重なり・判定役の引用・位置比へ**落とさない**。その指摘は新しい理由`violation_span_unverified`でStage 4(人間確認、fail-closed)とし、他の指摘は通常どおり処理する。確定不能の件数・原因(不一致/複数箇所一致/説明文混在)を記録する。
**(2) 対象決定の置換**: `locate_target`(runner 2449〜2473付近)の4段(判定役hint引用→`locate_multi_quote_span`→`locate_best_sentence`[類似度]→er010単語重なり)を、対象決定から外す。Stage 2のrewrite hintは**書き換え指示文としてのみ**Rewrite Promptへ渡す(対象決定には使わない)。区分判定`detect_claim_section_type`(1844〜1872付近)も、確定範囲が各区分ブロックに含まれるかの包含判定へ置き換える(複数区分にまたがる場合は最も保護の強い区分: title>in_one_line>hook>body。hook保持等の制約は範囲ごとに適用)。旧関数は削除せず残してよいが、対象決定の経路から呼ばれないこと(呼び出し元をGrepで確認)。新旧を切り替える定数(例: `HANDOFF_MODE`、既定=新方式)を設け、旧方式も実行可能にしておく(比較・切り戻し用)。
**(3) Rewriteへ渡すもの・呼び出し単位**: **1指摘=1回の呼び出し**。確定した全範囲を配列で渡し、範囲ごとの書き換え結果を同じ個数・同じ順序の配列で返させる(個数・順序が合わなければその水準は失敗扱い)。範囲を含む段落を**読み取り専用の文脈**として付ける。Promptには「範囲の中で直す必要のない部分は一字一句そのまま返す」「範囲の外は書き換えない」を明記する。
**(4) 最小修正優先(既存ラダーの維持、ユーザー§1)**: 水準①(語句・接続詞の最小編集)は**確定範囲そのもの**(文の一部ならその断片、複数文ならその複数文)を対象にする。①で不成立の場合のみ水準③へ進み、**その時点で初めて**、範囲を含む文全体(複数範囲ならそれぞれを含む文)へ拡張して書き直す。それでも不成立の場合のみ水準④(範囲を含む段落)。⑥は既定OFFのまま。既存の`filter_levels_by_problem_kind`・`escalate_to_paragraph`等の水準選択ロジックの意味は変えない(対象範囲の与え方だけ変える)。水準ごとの対象範囲・結果を記録する。
**(5) 書き戻し**: 範囲ごとに、書き戻し直前に現在の本文で「ちょうど1箇所」を再確認して`.replace(範囲, 書き換え結果, 1)`。再確認に失敗したらその水準は失敗扱い(推測で置換しない)。
**(6) 書き換え後guard**: 現行の`claim_text.strip() not in candidate`(引用符付き文字列では常に成立し、取りこぼしを検出できない)を、「Checkerが指した**各範囲**が実際に変化したこと」(①は範囲、③④は拡張後の対象)へ置き換える。主体置換ガード(`actor_rewrite_guard_ok`)等の既存ガードは維持。delete型の再出現確認(2769付近の類似度)は、「確定範囲の文字列(正規化後)が本文に残っていないこと」の完全一致確認へ置き換える(確認自体はなくさない)。意味上の解消判定は従来どおり全文Recheckが担う。
**(7) 周回間の同一判定・prior_issues**: `find_matching_prior_record`/`normalize_claim_text`(4255付近)と、Recheckへ渡す`prior_issues`(4500付近)は、正規化後の確定範囲(複数なら順に連結した表現)を使うよう揃える(生の引用符付き文字列のままだと同一判定が揺れる)。Stage 2へ渡す`claim_text`表示(4081付近)は**変更しない**(判定役の入力を変えると判定が変わりうるため。変更が必要と判断した場合は実装せず報告)。
**(8) 日本語側(暫定。構造見直しは別委任)**: 日本語側の処理構造の見直し(英語だけ直す化)は並行調査+Opusレビュー後の別委任で行うため、本委任では次の最小対応に留める。
- originが`ja_source`で確定範囲が**1つ**の場合: 既存の`paired_rewrite`経路を使い、EN側の対象だけ新方式の確定範囲に差し替える。JA側の対応決定の既存処理は**変更しない**(本委任では触らない)。
- originが`ja_source`で確定範囲が**複数**の場合、または指摘の文字列がJA本文でのみ確定した場合: 暫定として、確定できた言語側だけを新方式で直す既存の片側経路(3081〜3106付近)に入れ、もう一方は既存の再検査に任せる。`locate_multi_quote_span`+位置比優先の分岐(2958〜2959付近)は使わない。
- 上記が暫定である旨をコードコメントと設計書追記に明記し、該当した指摘の件数を記録する。
**(9) 記録**: 指摘ごとに、Checker文字列/確定範囲(配列)/照合レベル/確定不能理由/水準別の対象と結果/before・after(範囲ごと)/guard結果を、instance JSONへ記録する(次回以降の集計が再現値ではなく記録値でできるように)。
**(10) テスト**: 旧`locate_target`の優先順位(hint引用が第一手、包含スパン優先)を固定している既存テスト(`TestLocateTarget`、`TestLocateTargetMultiQuoteIntegration`等)は、新方式の仕様に合わせて意図的に書き換える(旧方式の関数単体テストは、旧関数を残す限り維持)。新規テストに必ず含める実例: (a) rep21 s1の2文claim(引用符付き)→2文が1つの範囲、水準①で範囲全体がRewrite対象になる。(b) rep20 s2 cycle2の`“They could not tell if it was AI or a person” and “They did not realize it.”`→2範囲、間の文は対象外。(c) `Paragraph beginning “People asking Muse to call”`→確定不能(`violation_span_unverified`)。(d) `“Some calls needed user information to continue.”`(記事は「Also, some calls needed…」)→L3で文の一部として確定し、水準①の対象は断片、水準③で初めて文全体。(e) 同じ文字列が2箇所にある→確定不能。(f) 配列の個数不一致→失敗扱い。(g) 書き戻し直前の再確認失敗→推測で置換しない。(h) guard: 2範囲のうち1つしか変化していない→不成立。

## 限定Trial(実装・テスト通過後。課金あり)

**開始前チェック(PM_GOVERNANCE 22節、必須)**: ユーザー指示§1・§2・§8の各項目を全件列挙し、実装・Trial設計のどこに反映したかの対応表を作る。**未反映が1件でもあれば課金Trialを開始しない**(STOPして報告)。対応表はRESULT_PACKETと設計書追記に載せる。
**構成(最小限)**:
- (T1) 2文取りこぼし型: `meta_run03_standard`、固定Stage 1(`er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、rep20/21と同じ方式)で**n=4**。
- (T2) 離れた複数箇所型: rep20 sample2 cycle2の状態(記録されたcycle1後のEN/JA本文+記録されたcycle2のStage 1/Stage 2出力)を固定入力にしてStage 3以降だけを実行する再現(**n=2**)。記録から再現入力を組めない要素があれば、何が不足かを示したうえで、最も近い実行可能な形(例: 単体のStage 3呼び出し)で確認する。組み方と限界を明記。
- (T3) Safety対照: rep21と同じ`changed_number`対照 **n=1**(既存の決定論的floorが発火し、誤ってPASSしないこと)。
- TTSなし。追加のretry・再実行は、失敗原因を特定してからに限る(同じ失敗の無意味な再実行をしない)。
**確認項目(成功条件ごとの実測)**:
1. 2文取りこぼしによるHuman Review: T1のn=4で、2文claimが1周目に2文とも対象になったか(記録値)、Stage 4件数とstage4_reason。取りこぼし起因のStage 4が0か。
2. Checkerの範囲を縮小していないか: 全BLOCKING指摘について「水準①の対象==確定範囲」を機械的に照合(不一致0件か)。
3. 誤PASSなし: T3でfloor発火・false PASS 0件。T1/T2でも、未解消のBLOCKINGが残ったまま合格になった例が0件か。
4. 最小修正優先: 水準別の成立件数(①/③/④)、①から開始していること。
5. 不要な段落・全文Rewriteを増やしていないか: 段落水準(④)・全文(⑥)の実行件数を、rep20・rep21(同じ固定入力、旧方式)の記録と比較。
6. その他: 確定不能(`violation_span_unverified`)件数、cycle数、call数、費用(今回/Phase累計/残)、JA暫定経路に入った件数、Stage 4の全内訳(受け渡し以外の理由[再検査の新規指摘等]で人間確認になった場合は、周回ごとの指摘を具体文付きで記録)。
**FAIL時**: 原因を特定し、本委任の実装範囲内で直せるものは直して該当ケースだけ再確認する(上限内)。範囲外の原因(再検査の揺れ、判定役の重大度の揺れ、日本語側の構造等)は、直さずに事実として報告する。

## 事前指定Read一覧

- `docs/pm/design_open233_violation_span_handoff_01.md`: §1-1(39〜64行)、§2-4(156〜180行)、§3(184〜201行)、§4-1〜4-5(205〜273行)、§7(387〜430行)
- `docs/pm/opus_l2_review_open233_self_recovery_05.md`: 「## 3.」「## 5.」「## 6.」(Grepで位置特定)
- `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`: 照合ロジック(L0〜L4、ちょうど1箇所判定)の関数部分(Grep `def ` で位置特定)
- `er052_open233_self_recovery_flow_runner_01.py`: 275〜279、1844〜1875、2241〜2536、2551〜2640、2731〜3235、4075〜4339、4490〜4650(改変対象。構造変更のため関数単位で読む)
- `er052_open233_self_recovery_flow_runner_01_test_01.py`: `class Test`でGrepし、書き換え対象のテストクラスのみ
- `er052_open233_self_recovery_flow_runner_01_rep21_representative_01.py`: 全体(Trial実行スクリプトの雛形、固定fixtureの使い方、Safety対照、予算state)
- `er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json`・`…_rep21/instances_s1/meta_run03_standard.json`: T2の再現入力とテスト実例に必要なキーのみ(Pythonで抽出)
- `docs/pm/delegation_log/2026-10-01_OPEN-233-SELF-RECOVERY-TRIAL-01_36.md`: 全体(直近の実装委任での記録・回帰の実施方法・SSOT更新パターンの前例)
- `docs/pm/design_open233_self_recovery_flow_01.md`: §6-17(3293〜3394行)と末尾(追記位置・書式)。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: 末尾の§34(書式・追記位置)
- `docs/pm/PM_GOVERNANCE.md`: 22節(`^## 22\.`でGrep、Trial開始前/終了前チェックの定義部のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `locate_target|locate_best_sentence|locate_multi_quote_span|extract_quoted_fragment|locate_ja_counterpart_by_position|detect_claim_section_type|claim_text.strip\(\) not in`(runner内の全呼び出し元)
- Production側がrunnerをimportしていないことの確認: `git grep -n "er052_open233" -- "er003*.py" "er0[0-4]*.py"`(0件であること)
- 追記・更新位置:
  1. `docs/pm/design_open233_self_recovery_flow_01.md`: §6-17の後へ新節(§6-18)「受け渡し修正(違反範囲をそのまま渡す)の実装と限定Trial(委任_42)」。実装内容、ユーザー決定との対応表(22節)、Trial結果、暫定事項(JA側)。
  2. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: 末尾へ§35(同内容の詳細証跡)。
  3. `DECISION_LOG.md`末尾: 新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し修正の実装・限定Trialほか次工程の承認(2026-10-02ユーザー決定、委任_42)」。(1)ユーザー原文の逐語全文、(2)本委任の実装範囲と結果、(3)§3〜§5は並行調査中(委任_43〜45)で対策実装はOpusレビュー後の別委任、(4)STOP条件(原文§8)、(5)Opusレビューの扱い(受け渡し修正はレビュー#5済みで再レビューなし)。
  4. `OPEN_ITEMS.md` OPEN-233行: 既存パターンに従い、Statusセルを本委任の結果を表す値へ更新(旧値は「旧Status参考(委任_37): …」として行内に保持する既存方式)。次Actionセル末尾に追記。
  5. `docs/pm/REPORT_LEDGER.md`: OPEN-233行の備考へ委任_42を追記。Opus発火=無(本委任。レビュー#5を再利用)。
  6. `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(`.gitignore`対象、addしない): ACTIVE_TASK固定ヘッダを本委任の結果で更新(管理ID=OPEN-233 委任_42/Status=結果を表す一言/UDR-blocking=該当があれば/UDR-deferred=修正後の29件横断再確認、実記事N増し/APPROVED未配線=なし/STOP条件=ユーザー§8の6条件/次アクション=Fableが結果を照合、並行調査[委任_43〜45]の結果と合わせて次の対策を設計・Opusレビュー/未回答報告=なし/報告単位Status)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。Pythonは必ず `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`。
1. `git status --porcelain=v1 | grep -v '^??'`(作業前確認)
2. 実装→単体テスト: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01 -v 2>&1 | tail -n 30`
3. 関連テスト・回帰: 委任_36の記録にある実施方法に従う(runner関連の全unittest、および`run_project_regression.py`を`--pattern`に`_test`を含む形で全件1回。例: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe run_project_regression.py --pattern "er052*_test_*.py"` と、委任_36で実施したproject-wideの指定)。新規failureが0であること。既存の既知failureがある場合は委任_36時点との差分で判定。
4. Trial開始前チェック(22節の対応表)→未反映0を確認。
5. Trial実行: 新規作成する`er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`を、rep21スクリプトと同じ引数体系で実行(出力先`er052_output/open233_self_recovery_flow_runner_01_rep22/`、予算stateは本委任の上限¥15を明示。`--budget`/`--budget-jpy`等の引数が雛形にあれば実値で指定)。実行したコマンドは引数の実値を含めて全文をRESULT_PACKETへ記録する。
6. T-0: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_42.md --json-out docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_42.md_check.json`
7. `git diff --stat`(変更が指定範囲内であること、Production正式pathのファイルに差分がないこと)→Git。

## SSOT追記文

上記「追記位置」1〜5のとおり(文案は実測結果に基づき作成。結果を良く見せる表現にしない。未達の成功条件は未達と書く)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **あり**(`DECISION_LOG.md`・`OPEN_ITEMS.md`[OPEN-233行のみ]・`docs/pm/REPORT_LEDGER.md`・`docs/pm/design_open233_self_recovery_flow_01.md`・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`)。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`は編集しない。並行タスクはSSOTを編集しない。
- 明示`git add`対象(1ファイルずつ、実際に変更・作成したもののみ): `er052_open233_self_recovery_flow_runner_01.py` / `er052_open233_self_recovery_flow_runner_01_test_01.py` / `er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py` / `er052_output/open233_self_recovery_flow_runner_01_rep22/`配下の本Trialの出力(rep21で追跡しているのと同じ種類のファイルのみ、個別指定) / `docs/pm/design_open233_self_recovery_flow_01.md` / `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md` / `docs/pm/REPORT_LEDGER.md` / `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_42.md` / 同`_42.md_check.json`。既存の共有telemetry等(`er011_output/attempt_history.jsonl`等)がTrial実行で更新された場合の扱いは委任_36の前例に従う。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し修正(Checkerの違反範囲をそのままRewriteへ、再推測の廃止)を実装、限定Trial rep22で確認(委任_42)`(結果に応じて「確認」の語を実態に合わせる)
- trailer: `git log -1 --format=%B e0ae8de0`の形式に合わせる。commit後`git push origin main`。エラー・競合が出たらSTOPして報告。テスト・回帰に新規failureがある状態ではcommitせず報告(CLAUDE.md「動作確認に失敗した場合」)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに次を記載(数値を省略しない。長い報告書の.mdファイルを別途新規作成する必要はない):
1. 管理ID・委任番号、費用(今回/Phase累計/残)、Production正式path未変更の確認(`git show --stat HEAD`の対象一覧、Production側のimport確認結果)。
2. 実装内容(仕様(1)〜(10)それぞれの実装箇所[関数名・行範囲]と、仕様どおりにできなかった点・判断した点)。対象決定の経路から旧4段が外れていることの確認(呼び出し元Grep)。
3. テスト・回帰の結果(件数、新規failure、意図的に書き換えたテストの一覧)。
4. Trial開始前チェックの対応表(ユーザー指示の各項目→反映先)。
5. Trial結果: T1/T2/T3ごとの最終状態・stage4_reason・cycle数・call数・費用。成功条件1〜5の実測値と達成/未達。T2の再現入力の組み方と限界。
6. Stage 4になったrunがあれば、周回ごとの指摘(具体文、fact_id、重大度)と原因の切り分け(受け渡し起因か、それ以外か)。
7. FAIL→修正→再確認を行った場合は、その経緯(何が原因で、何を直し、再確認でどうなったか)。
8. 暫定事項(JA側)に該当した件数と挙動。
9. 残る問題・未確認事項・次工程(29件横断再確認)へ進む前に必要なこと。
10. T-0結果、実行コマンド全文、commitハッシュ・push結果、変更ファイルのraw.githubusercontent.com URL。
11. 指示どおりにできなかった点・迷った点・一覧外の追加Read。
