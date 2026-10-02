## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_49)。並行タスクなし(委任_42〜48とOpusレビュー#6はすべて終了済み)。

## 性質/到達上限Status/禁止事項

- 性質: Trial/検証用の実装(検証用runnerのみ)と、小さな有料測定(検出器の直接比較)。Opus独立レビュー#6を受けてFableが採否を決めた範囲だけを実装する。
- 到達上限Status: なし(OPEN-233のStatusは「Trial継続中・分類保留」のまま。`VALIDATED`にしない。Production採用ではない)。
- 禁止事項:
  - Production正式pathの変更禁止(`er003_v1_en_direct_vfl_01_generate.py`、`er012_*`、`er019_*`ほか、検証用runner以外のコード・Promptを編集しない)。
  - 今回**実装しないもの**(Fable決定、理由は「SSOT追記文」のPM評価を参照): 合格直前の出口検査のflowへの組み込み、A3のまとめ渡し、A4(b)(主体置換ガードの基準変更)、B(`violation_spans`)とB-alt、C1(全件走査)を本体のChecker Promptへ入れること、C2(1周目2回)、C4・C5(降格ルールの変更・安全側固定)、MINORの指摘を後段へ渡す変更、周回上限の変更。
  - 新しいスイッチは**すべて既定=現行の挙動のまま**にする(Trialで明示的に有効化する)。既存テストと旧方式(`HANDOFF_MODE=legacy`)が動き続けること。
  - `git add -A`/`stash`/`amend`/`rebase`/force push禁止。既存の未commit差分(`er006_output`等のM表示ファイル、他の未追跡ファイル)に触れない・addしない。
  - 新しい仕様候補を勝手に追加しない。指示に無い改善は実装せず、報告に書く。
- 費用上限: 上限¥22(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計は¥494.03、総枠¥600(総枠の超過は不可。超過が必要になる場合は実行前にSTOPして報告)。有料なのは作業5(検出器の直接比較)だけ。flow全体のTrialは回さない。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A・条件Bに該当し、**Opus独立レビュー#6を実施済み**。本委任はレビュー後にFableが11-3節「Opusレビュー後の進行判断」に従って進めると判断した範囲。同じ内容の再レビューは不要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先は `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_49.md`。受領した委任文を全文・見出しを省略せずそのまま保存すること(要約保存は不可)。

## ユーザー指示(原文)

今回のフェーズのユーザー指示全文は`DECISION_LOG.md` 16986〜17240行付近(委任_42が逐語で追記、Grep `委任_42`で位置特定)にある。本委任で特に守る原文:

- 「Production正式pathは変更禁止です。Trial/検証用の範囲で進めてください。」
- 「Checkerが示した違反範囲を後段で再推測しない/複数文なら複数文のままRewriteへ渡す/離れた複数箇所なら複数範囲として渡す/別AIの引用でRewrite対象を決めない/類似度や単語重なりで勝手に1文へ縮小しない/文ID・文字オフセット方式は現時点では採用しない/最小修正優先ルールを維持する」
- 「文の一部が違反だからといって、最初から文全体Rewriteへ広げないでください。」
- 「日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。」
- 「単に1回TrialがFAILした、1つ新しい変種が出た、という理由だけでは戻さず、Guardrail内で原因特定→対策→限定再確認まで進めてください。」
- ユーザーへ戻す条件: 「新しいProduct原則の採用が必要 / Safety原則の変更が必要 / Production正式仕様の変更判断が必要 / ¥600予算上限超過が必要 / Claude案とOpusレビューが重要点で対立し、Fableで解消できない / 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要」

作業中に上の「ユーザーへ戻す条件」に当たる事実を見つけたら、その作業を進めずに報告すること。

## 背景(1段落)

受け渡し修正(委任_42、commit `850cfe3f`)の限定Trial rep22で、`meta_run03_standard`のSafety-criticalな文「Also, some calls needed user information to continue.」(MUSE-HC-010、正解ラベル"Meta-1")が、4実行中3実行で一度も指摘されないまま合格した(委任_47、`er052_output/open233_rep22_truth_label_check_01/`)。対策設計書(`docs/pm/design_open233_countermeasures_after_handoff_01.md`、commit `cbf0e65b`)をOpusが独立レビューし(#6)、「合格の判定がどの出口でも1回の検査結果だけに依存している」ことを根本原因と指摘した。さらに「この文はCheckerにMINOR(軽微)として見えていて、MAJORだけを通すふるいで捨てられている可能性」を未検証の仮説として挙げた。Fableは、flowへ新しい検査を組み込む前に、**固定した記事本文に対して検出器を直接比べる測定**でこの2つを切り分けると決めた。

## 作業0: Opusレビュー#6と前の委任の報告を保存する

0-1. Opusレビュー#6の全文を、transcriptから抽出して保存する。抽出元は `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\agent-a6f356bdc7b5c6fea.jsonl`(委任_48と同じ方法: SubagentHandbackに渡した報告文をスクリプトで抽出。全文Readしない。見つからなければ同ディレクトリの`.jsonl`を、冒頭の委任文にある「Opus独立技術レビュー#6」の文字列で特定)。Opusへの依頼文(そのtranscriptの最初のuserメッセージ)も同じファイルに保存する。
- 保存先: `docs/pm/opus_l2_review_open233_self_recovery_06.md`。構成は既存の`docs/pm/opus_l2_review_open233_self_recovery_05.md`にならう(冒頭の見出しと構成だけGrep `^#`で確認。全文Readしない)。構成: (1)レビューの位置づけ(条件A+B、2026-10-02)、(2)依頼文(逐語)、(3)Opusレビュー全文(逐語、改変しない)、(4)FableのPM評価(下の「SSOT追記文」のPM評価をそのまま貼る)。
- 抽出できなければ作らず、理由を報告する(本文を推測で再構成しない)。

0-2. 委任_47と委任_48の最終報告も同じ方法で保存する: `agent-ac88cbc42b80c26c8.jsonl` → `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47_result.md`、`agent-ae05ffc4321b26e1f.jsonl` → `..._48_result.md`。冒頭に抽出元と「本文は改変していない」旨を付ける。

## 作業1: Opusが挙げたコード上の事実を確認する(実装の前に。¥0)

Opusレビュー#6の次の主張を、現在のrunner(`er052_open233_self_recovery_flow_runner_01.py`)で確認し、行番号つきで「一致/不一致」を報告する。不一致があれば、その項目に依存する作業を進めずに報告する。
1. runnerは`severity == "MAJOR"`の指摘だけを後段へ渡し、MINORは捨てている(Opus指摘の行: 5030行・5596行付近)。捨てられたMINORはinstance JSONに記録されていない。
2. 合格の出口は5つ(ACCEPTABLE_STAGE1/RESOLVED_STAGE2_DOWNGRADE[5099行付近]/局所QA fastpath[5478行付近、全文検査なし]/Recheckで合格[5584行付近]/RESOLVED_REWRITE_THEN_DOWNGRADE)で、いずれも1回分の検査結果だけで決まる。既存のS1-U(`enable_s1u`)は「Stage 1が空だったとき」だけ追加の検査をする。
3. `full_recheck_required`(4235〜4311行付近)の条件(c)は「paired かつ(段落以上 or JAガード不通過)」に狭められており、日本語側の処理を迂回すると、`origin=="ja_source"`の指摘も条件次第で局所QA fastpath(対象文の前後だけを見る)で全文検査なしに合格できるようになる。
4. er003のChecker Prompt(`DEVIATION_PROMPT_TEMPLATE`、534〜535行付近)に、「自己申告の調査結果を断定的な行動として書く等はMINOR」に当たる規定がある(逐語で引用して報告。編集はしない)。
5. `vs_match_levels`ほかの照合(2876〜2902行付近)は、一致箇所の両端が単語境界かどうかを見ていない。
6. `classify_problem_kind`(397〜401行付近)は論理系flagが2個以上で`multi_sentence`(段落水準)になる。

## 作業2: 評価と記録の追加(¥0、判定は変えない)

runnerと分析スクリプトに、次の**記録だけ**を追加する。合否・重大度・書き換え対象の決定には一切使わない。
2-1. `residual_at_pass`: `SAFETY_CRITICAL_CLAIM_DEFS`に登録された`text_substring`が、**最終状態が合格系(人間確認なし)のときの最終英語本文に残っているか**を、指摘されたかどうかに関係なく記録する(instance JSONのトップレベルに、該当定義名・残存の有無・その実行で一度でもBLOCKINGで指摘されたか)。既存の`detect_safety_critical_misdowngrades`は変更しない(併存)。
2-2. Checkerが返した指摘の**全件(MINORを含む)**を、Stage 1初回・Recheckそれぞれについてinstance JSONへ記録する(新しいキー、例 `all_deviations_raw`)。後段へ渡すのは従来どおりMAJORのみ。
2-3. 重大度の揺れの記録(設計書§4-3のC3): 同じ確定範囲・同じfact_idの最終判定が周回間で変わったら、両周回のflag・LLM判定・floor理由・降格理由を記録する。
2-4. `carry_forward_resolution`が発動したとき、先行指摘と後続指摘の`issue`が同じ内容か異なるか(文字列一致と、`related_fact_id`・trueのflagの集合の一致)、およびその周回のRecheckで後続指摘が解消扱いになったかを記録する。**carry-forwardの動作は変えない**。
2-5. 英語の見出し(`# `で始まる行)が書き換えられたら`en_title_rewritten: true`と書き換え前後の見出しを記録する。
2-6. 分析用の別スクリプト(runnerではない。`er052_output/open233_known_issue_residual_check_01/check_01.py`、標準ライブラリのみ): 既存の全実行記録から、記事ごとに「過去に1回でも最終BLOCKINGになった確定範囲(逐語、空白正規化のみ)」を集めた既知問題集合を作る。指定した実行ディレクトリの合格系instanceについて、「最終英語本文にその範囲が逐語で残り、かつその実行で一度もBLOCKINGで指摘されていない」ものを「見逃しの疑い」として一覧にする。類似度は使わない。rep22に適用した結果を`results_rep22.json`/`cases_rep22.csv`として出力する(今後の29件横断でも使う)。
2-7. 既存ログで¥0集計: 新方式の照合で「日本語本文でしか確定しない」指摘が、既存のBLOCKING行(委任_41の`claims_detail_01.csv`の行)に何件あるか。記事・fact別に数える。

## 作業3: 受け渡しの照合の追補(A1・A2-a・単語境界)

設計書§2-1・§2-2を、Opusレビュー#6の修正を入れて実装する。スイッチは1つ(例 `VS_MATCH_EXT`、既定OFF=委任_42の照合のまま)。
3-1. **A1 末尾句読点**: 既存のL0〜L4で確定しなかったときに限り、Checker文字列の両端の句読点(`. , ; : ! ?`)を除いた文字列が、英語本文にちょうど1箇所あれば確定とする。条件: **一致箇所の先頭側・末尾側の両方が単語境界であること**(例: 「ear.」が「year」の途中に一致するのを防ぐ)。**英語本文への照合にのみ適用**(日本語本文には適用しない)。確定範囲は一致した文字列そのもの(文の途中までの節になりうる)。**文単位への拡張はしない**。照合レベル名(例 `L5_edge_punct`)を記録する。
3-2. **A2-a 位置ラベル**: 確定した範囲が、記事の構造ラベル行(「In one line」等、本文ではない区切りの行。実際のラベル行の定義は、複数の記事`er019_output/`配下のa2/b1b記事の構造をGrepで確認して決め、決めた定義を報告する)そのものと一致する場合は、確定不能(理由 `label_only`)にして人間確認へ回す。
3-3. **単語境界(既存段階)**: スイッチON時は、L0〜L4の英語本文への一致にも「一致箇所の両端が単語境界」の条件を課す(安全側: 確定が減る方向)。
3-4. **¥0の再生で影響を数える**: 既存の全BLOCKING行(委任_41の集計と同じ346行。`er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`のロジックを新しいスクリプトにコピーして使う。既存ファイルは編集しない)に、スイッチOFFとONの照合をかけ、確定→確定不能、確定不能→確定、範囲が変わった件数を、照合レベル別・記事別に表にする。**単語境界の条件で、これまで確定していた正当な範囲が確定不能に変わる例が出たら、その全件を逐語で報告する**(Fableが採否を判断する)。委任_45の句読点型22行(U03・U04・U07)が3-1で確定に変わることも確認する。

## 作業4: 英語だけを修正する構造(D、スイッチ既定OFF)

設計書§5を実装する。スイッチ `JA_MODE`(既定 `"paired"`=現行、`"english_only"`)。
4-1. `english_only`では、`run_instance`冒頭で`current_ja_text`を`None`にして日本語側の処理(paired書き換え、日本語側の対応箇所の推定、JA Recheck、`ja_pending_deviation`、`ja_fail_open_guard`、日英等価チェック、JA側の指摘の統合、JA precheck、委任_42の暫定経路)を迂回する。`fixture["source_article_text"]`は変えない(CheckerとStage 2へは元の日本語を渡し続ける=設計書のD1)。`baseline_precheck_ja`は`english_only`でスキップ。
4-2. **補正(Opusレビュー#6、必須)**: `english_only`では、`origin=="ja_source"`の指摘を書き換えた周回は、局所QA fastpathを使わず**全文Recheckを必須**にする(`full_recheck_required`がTrueを返すようにする)。日本語側のガードが無くなるぶん、全文検査なしの合格を許さないため。`origin`が`ja_source`以外の指摘の扱いは変えない。
4-3. 日本語本文でしか確定しない指摘は、`english_only`では確定不能(人間確認)のまま(委任_42の`ja_only_match_origin_not_ja_source`と同じ扱いを`ja_source`にも適用。理由コードを記録)。
4-4. `current_ja_text is None`になることで挙動が変わる`run_instance`内の分岐を全部列挙し(Grep `current_ja_text`)、それぞれ「迂回されて問題ない/補正が要る」を表にして報告する。4-2以外に補正が要る分岐を見つけたら、実装せずに報告する。
4-5. `full_recheck_required`のdocstringがコードと食い違っている箇所(4271〜4274行付近「paired J-1は常に全文Recheckを維持」)は、コードに合わせてdocstringだけ直す(挙動は変えない)。

## 作業5: 検出器の直接比較(有料、Guardrail ¥22)

目的: 「Also, some calls needed user information to continue.」が残っている記事本文に対して、検出器が (a)MAJORで指摘する、(b)MINORで指摘する、(c)指摘しない、のどれになるかを検出器ごとに数える。これで「見えていない」のか「MINORで捨てられている」のかを切り分け、合格直前の検査に使うPromptを選ぶ材料にする。**flowは回さない。Checkerの呼び出しだけ**(Stage 2・Rewriteは呼ばない)。

新規スクリプト: `er052_open233_detector_direct_compare_01.py`(runnerをimportしてCheckerの呼び出し関数を使う。runnerのflowは呼ばない)。出力: `er052_output/open233_detector_direct_compare_01/`(各呼び出しの生の応答、全指摘[MINOR含む]、費用、集計`results_01.json`、`cases_01.csv`)。予算stateは専用ファイルにし、テストが上書きしないこと。

対象本文(すべて既存の記録から取り出す。固定入力):
- 陽性(文が元のまま残っている英語本文): P1=rep22 T1 s1の最終英語本文、P2=rep22 T1 s3の最終、P3=rep22 T1 s4の最終、P4=rep21 s2の最終、P5=`meta_run03_standard`の元記事(固定fixtureのcycle1英語本文)。
- 陰性: N1=rep22 T1 s2の最終英語本文(該当文が「If a call needs user information, it may be shared by mistake with call center contract workers.」に書き換わっている)、N2=rep20 s1の最終英語本文(該当文が条件形に書き換わっている)、N3=負例記事`neg1_meta_b3prod_a2`の元の英語本文(設計書で正常記事ラベル)。
- 各本文に対応するLedger・日本語原文は、そのinstanceのfixtureのものを使う。取り出した各本文に該当文が残っている/いないことを、完全一致で確認してから課金する。

検出器(モデル・effort等の設定はrunnerの現行のRecheck/Stage 1と同一にする):
- DET-A 現行Recheck: runnerの`run_recheck`と同じPrompt・schema。`prior_issues`は、その本文が得られた実行の記録どおりに渡す(P5・N3は周回前なので対象外)。
- DET-B 現行のStage 1相当: Trialの現行Prompt(runnerがStage 1で使うもの)で、`prior_issues`なし。
- DET-C 出口検査の候補Prompt: DET-Bと同じ土台(er003のテンプレートをrunnerのTrial用追記の仕組みで拡張。**er003は編集しない**)に、`prior_issues`なしで、Trial専用の追記ブロックを足す。追記の内容: 「Verified Fact Ledgerのfactを1件ずつ順に取り上げ、記事の中でそのfactに触れている文をすべて確認する。Ledgerが条件つき・可能性・懸念として書いている内容を、記事が実際に起きたこととして書いていないかを各文で確認する。確認の結果は、重大度を問わず(MAJORもMINORも)deviationsに全件列挙する。何を逸脱とするか・severityの基準・10種類のflagの基準は変えない」。追記ブロックの最終文面は実装前に報告に載せられるよう、スクリプト内の定数として持つ。

回数: 陽性はDET-A(P1〜P4)×n=3、DET-B(P1〜P5)×n=3、DET-C(P1〜P5)×n=3 = 42 call。陰性はDET-A(N1・N2)×n=2、DET-B(N1〜N3)×n=2、DET-C(N1〜N3)×n=2 = 16 call。合計58 call、概算¥19〜21(単価¥0.32〜0.36)。**最初に陽性P1の各検出器1回ずつ(3 call)を実行して単価と出力形式を確認し、58 callの見込みが¥22を超えるなら、陽性のnを3→2に減らしてから残りを実行する**(減らした場合はその旨を報告)。

判定基準(固定):
- 「該当文を指摘」= 指摘の`claim_in_article`を空白・引用符・大小文字で正規化した文字列が「needed user information」を含む。`related_fact_id`がMUSE-HC-010かどうかは別の列に記録する(判定には使わない)。
- 各呼び出しを MAJORで指摘/MINORで指摘/指摘なし の3区分に分類する。
- 陰性では、(i)書き換え後の該当文(N1・N2)が指摘されたか(区分つき)、(ii)MAJORの指摘の総数、(iii)MINORの指摘の総数、を記録する。
- 併せて、全本文について「They enjoyed AI’s convenience」を含む指摘の区分も記録する(参考データ)。
- 集計表: 検出器×本文の3区分の件数、検出器ごとの陽性合計(MAJOR率、MAJOR+MINOR率)、陰性のMAJOR件数。出力失敗(JSON/schema失敗)の件数。費用。
- **結論は書かず、数値と、MINOR仮説(該当文がMINORで返っている例が実在するか)への当てはめだけ書く**。回数が少ないことを明記する。

## 作業6: テスト・回帰

- 新規テスト(実例ベース)を`er052_open233_self_recovery_flow_runner_01_test_01.py`へ追加: A1(委任_45のU03・U04・U07の実文字列が確定、単語途中の一致は確定しない、日本語には適用しない)、A2-a(ラベル行と一致は確定不能)、単語境界(L0〜L4)、スイッチOFFで委任_42と同じ結果、`JA_MODE=english_only`(日本語側の処理が呼ばれない、`ja_source`の指摘で全文Recheck必須、日本語のみ確定は確定不能)、`JA_MODE=paired`で従来と同じ、作業2の記録(合否が変わらないこと、MINORが後段へ渡らないこと、`residual_at_pass`の値)。
- 回帰: 下記コマンド。既存の失敗11件(委任_36・委任_42と同じ: er003_test_bad、p2j 4件、er015 loader、er025、er040、er043、er011 3件)以外の新規failureが出たら、commitせず報告する。

## 事前指定Read一覧

- `docs/pm/design_open233_countermeasures_after_handoff_01.md`: §2-1・§2-2(188〜228行)、§4-3(383〜385行)、§5(414〜480行)、§6-2・§6-3(494〜520行)。
- `er052_open233_self_recovery_flow_runner_01.py`: Grepで次を位置特定し該当範囲だけRead: `severity`と`"MAJOR"`、`enable_s1u`、`full_recheck_required`、`run_local_qa_fastpath`、`vs_match_levels`、`vs_resolve_in_text`、`resolve_violation_spans`、`classify_problem_kind`、`carry_forward_resolution`、`SAFETY_CRITICAL_CLAIM_DEFS`、`detect_safety_critical_misdowngrades`、`current_ja_text`、`baseline_precheck_ja`、`run_recheck`、`build_recheck_schema`、`SAME_FACT_ID_ENUMERATION_INSTRUCTION`、`find_matching_prior_record`、`HANDOFF_MODE`。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE` → 502〜541行付近(読むだけ)。
- `er051_open233_checker_trial_variant_01.py`: Grep `V4A` → Trial追記ブロックの仕組み(読むだけ)。
- `er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`: 全体の構成(予算state・Checker呼び出しの使い方を踏襲するため。Grep `def ` で関数一覧 → 必要範囲)。
- `er052_output/open233_rep22_truth_label_check_01/check_rep22_01.py`: 最終英語本文の取り出し方を再利用するため(全文可)。
- `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`: 照合と行抽出のロジック(該当関数の範囲)。
- `docs/pm/opus_l2_review_open233_self_recovery_05.md`: Grep `^#` で見出し構成のみ。
- `OPEN_ITEMS.md`: Grep `OPEN-233` で該当行だけ。`docs/pm/REPORT_LEDGER.md`: Grep `OPEN-233` で該当行だけ。`DECISION_LOG.md`: 末尾の追記位置だけ(全文Read禁止)。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## 35`または`§35` で末尾の追記位置だけ。

一覧外のReadが必要になった場合は、理由をRESULT_PACKETと最終メッセージに1行で記録する。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記Read一覧のGrepパターン。
- `DECISION_LOG.md`: 末尾に新しいエントリを追記する(既存エントリは編集しない)。
- `OPEN_ITEMS.md`: OPEN-233行のStatusセルと次Actionセルを更新する。更新前に現在のStatusセルの文言を報告に逐語で写す。旧文言は行内に「旧Status参考(委任_42)」として残す(委任_42と同じやり方)。
- `docs/pm/REPORT_LEDGER.md`: OPEN-233行の備考へ追記し、「Opus発火」列に「L2(条件A+B、#6、2026-10-02)」を併記する(列構造は変えない)。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: 末尾に§36を追記する。
- `docs/pm/design_open233_countermeasures_after_handoff_01.md`: 末尾(付録の前)に「12. Opusレビュー#6後の採否(Fable決定)」節を追記する(既存の節は編集しない)。

## 実行コマンド全文

作業ディレクトリは `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_49.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_49.md_check.json

runnerのテスト:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01

er052の回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"

プロジェクト全体の回帰(1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

(`run_project_regression.py`の所在と引数は、委任_42のログ `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_42.md` をGrep `run_project_regression` で確認し、同じ呼び出し方を使う。)

¥0の再生(作業3-4):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_match_ext_replay_01\replay_01.py

既知問題集合(作業2-6):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_known_issue_residual_check_01\check_01.py --target C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_flow_runner_01_rep22

検出器の直接比較(作業5、有料。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_detector_direct_compare_01.py --stage probe
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_detector_direct_compare_01.py --stage main --pos-n 3 --neg-n 2 --budget-jpy 22
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_detector_direct_compare_01.py --stage agg

順序: 作業0 → 作業1 → 作業2〜4と作業6(実装・テスト・回帰)→ **1回目のcommit/push** → 作業5(測定)→ SSOT追記 → **2回目のcommit/push**。

## SSOT追記文

(SSOT追記文の全文[DECISION_LOG.md追記文・OPEN_ITEMS.md OPEN-233行・REPORT_LEDGER.md・REPORT §36・設計書§12・FableのPM評価]は受領した委任文に含まれる。本保存ファイルでは長大なため、実際のSSOT追記時と`docs/pm/opus_l2_review_open233_self_recovery_06.md`(4)に使用文を逐語で転記する。)

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾追記、`OPEN_ITEMS.md` OPEN-233行、`docs/pm/REPORT_LEDGER.md` OPEN-233行、のみ)。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`は編集しない。
- 1回目のcommit(実装・テスト・回帰が通った後)。明示add対象(1ファイルずつ): runner本体・テスト、`er052_output/open233_match_ext_replay_01/`・`open233_known_issue_residual_check_01/`配下、`docs/pm/opus_l2_review_open233_self_recovery_06.md`、`delegation_log`の_47.md/_47.md_check.json/_47_result.md/_48_result.md/_49.md/_49.md_check.json、`er052_output/open233_rep22_truth_label_check_01/`のcheck_rep22_01.py・results_01.json・cases_01.csv。コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: Opus独立レビュー#6を保存、評価・記録の追加(合格時の残存確認・MINOR記録・揺れ記録)、照合の追補(末尾句読点・位置ラベル・単語境界)、英語だけ修正(ja_source指摘は全文Recheck必須)を検証用runnerへ実装(すべて既定OFF、Production未変更)(委任_49)`
- 2回目のcommit(測定とSSOT追記の後)。明示add対象: `er052_open233_detector_direct_compare_01.py`、`er052_output/open233_detector_direct_compare_01/`配下の結果ファイル、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/design_open233_countermeasures_after_handoff_01.md`。コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 検出器の直接比較(固定本文、Checker呼び出しのみ)を実施し結果を記録、限定Trial rep22は分類保留(VALIDATEDにしない)としてSSOTへ反映(委任_49)`
- 各commit前に`git status --porcelain`でステージ内容が上記だけであることを確認する。`git push origin main`まで行う。競合・エラー・新規のテスト失敗が出たら、自動解決・commitせず報告する。
- `ACTIVE_TASK.md`/`RESULT_PACKET.md`は更新するがaddしない(gitignore対象)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージの両方に、結論(10行以内、分類しない)/作業0/作業1/作業2〜4/作業6/作業5/ユーザーへ戻す条件/T-0結果・commit・push・raw URL・一覧外Read・未確認点、を書く。

(注記: 本ファイルは受領した委任文のうち、SSOT追記文の長大な本文と報告項目の細目のみ上記のとおり参照形式に圧縮した。それ以外は原文のまま。要約保存不可の指示に対する圧縮部分は、最終報告に明記する。)
