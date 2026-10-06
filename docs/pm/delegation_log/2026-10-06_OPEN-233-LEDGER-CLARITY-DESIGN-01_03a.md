## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_03a: Opus必須修正M1〜M6の設計doc反映+Trial計画の確定)。並列委任_03b〜d(Opus逐語保存)、_03e(SSOT)が同時進行(`docs/pm/opus_l2_review_lc_part*.md`、SSOTには触れない)。**書込先: `docs/pm/ledger_clarity/04_design.md`(追記・訂正)、`docs/pm/ledger_clarity/05_trial_plan.md`(新規、120行以内)、`docs/pm/delegation_log/`。コード・SSOT・CURRENT_SPEC・git変更なし。API呼出なし。**
作業方式: §ごとにEdit(1回30行以内)、Bash heredoc不使用、説明最小。既存文は削除せず「Opus反映(訂正)」で追記。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: 設計修正・Trial計画(¥0)。到達上限: USER_DECISION_REQUIRED(Trial計画承認待ち)。禁止: 有料API/Trial実行/Production実装/CURRENT_SPEC更新/新Product仕様の「決定」記載/S1等採否変更。Opus Gate: 条件Aレビュー実施済み(本委任は反映)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_03a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> レビューで重要な問題が見つかった場合は設計を修正する。大きな設計変更や新たなProduct仕様が必要になった場合は、勝手に採用せず、選択肢として報告する。Trial計画: 品質①②③、各評価の測定方法・合格基準・検証件数・揺れ対策を事前定義、費用上限案と所要時間。

## Opus必須修正(反映内容)
M1: §2のHF-009「Writer誤読例」は合成文(G-03=testset_01 L1204「合成(委任_60)」)と訂正。本番hormuz/run_03のR0・R2・ENは途中/最終を正しく記述("did not fall across the board"まで)。HF-009はChecker側の課題(1状態しか持たない)と整理。HC-012の誤り発生段: 台帳「ロールバック」→B3 brief逐語(`storyline_b3/selected_brief.md` L11)→JA R0「以前の状態に戻しました」(`ja_writer/original.md` L13)→R1/R2維持→EN "restored…"(`b1b/article.md` L17)。既存Meta R0 4系統すべて曖昧訳(基準発生率高)。
M2: §6を訂正: WriterはB3の要約briefを読む(`er019_family_x_storyline_b3_fact_selection_01.py` L78)、台帳を直接読まない。B3 briefには台帳にない因果が加わる例あり(brief L4)。R1/R2は台帳非参照。評価は台帳→B3 brief→R0→R1/R2→ENの各段で対象factの意味保持を測る。
M3: Vに決定論検査を必須追加: fact_id集合・fact数・数値・日付・固有名・否定語・因果語の集合が元と新で一致(否定語・因果語はChecker正規表現 `er052_open233_stage1_coverage_checker_01.py` L437-526 を再利用)。LLM Vは補強。
M4: txt書式制約: claim行(1行目)に新しい否定語・因果語・番号・括弧を入れない。否定ガイドはnotes_for_writerに一本化。途中/最終は英字キーの字下げタグ行(例`phase_interim:`/`phase_final:`、空行なし。`parse_ledger_text`は英字キーのみ解釈、日本語キー行は捨てられる: precheck `TAG_LINE` L60/L92-96、ブロック区切りは空行 L3012/L177)。uncertaintyもタグ行。
M5: 多義語の意味確定と主体・因果の補完は原資料を参照できる工程でのみ許可。本番推奨経路=**P'**(Researcherスキーマ・prompt拡張+既存Verification 9観点に「多義語の意味確定/途中と最終の区別が原資料と一致」を追加、追加callなし、費用≈出力token分<¥1)。案C+Vは既存台帳のoffline適用(Trial用)に限定。C+Vを本番に採る場合は多義語factにWeb再Verification(選択肢B、+≈¥14/run)必須。比較表をP'/C+V/C+V+B/Sで再掲。
M6: phase定義を台帳側に一本化(同一主体・同一指標の時系列変化のみINTERIM/FINAL、別事象は別event SINGLE。設計§4のHC-012「両方SINGLE」とTRIAL-03の「テスト=INTERIM/機能=FINAL」の食い違いを記載)。凍結した台帳eventsをCheckerの比較基準として共有し、Checker側のLedger event抽出(TRIAL-03で揺れた)を廃止する方針をF1として記載(実装は台帳Trial合格後、ユーザー判断)。
推奨修正R1〜R3(任意): `ambiguity`をVERIFIEDでもtxtに出す(¥0)/明確化対象を曖昧度高・中に限定/30 fact以上は分割処理。
F2: 「限定語なし方向表現→最終状態と比較」はChecker側のlabeling_guide比較手順として扱える(新Product原則にしない)。
§13(新設)「Opus条件Aレビュー要約とFable照合」: 総合判定、M1〜M6反映状況、Fable照合(Sonnet案との対立ではなく訂正・精緻化。本番経路P' vs C+Vと台帳スキーマ拡張は新Product仕様候補→ユーザー判断)、逐語は`docs/pm/opus_l2_review_lc_design_01.md`。

## Trial計画(`05_trial_plan.md`、Opus修正提案を基に確定案として整理。すべて「案」、承認待ち)
Phase 0(¥0): 既存の全R0/R2/ENからHC-012・HF-009・HF-012・HC-014の言い換え方の基準発生率を集計(Meta R0は4系統中4で曖昧)。
Phase 1(約¥3〜6): meta・hormuz・small_bagの3台帳に案Cをoffline適用→M3決定論diff→変更fact全件をFable/Sonnetがoffline照合。合格基準: 追加情報0件/意味確定の誤り0件(原文未確認の多義語は「判定保留」)/Checker決定論検査の誤爆増0件(既存SUPPORTED unitを新ブロックで再判定、¥0)。
Phase 2(上限¥60): B3+JA R0〜R2+ENのみ(全フローChecker runは使わない)を台帳A(従来)/B(明確化)×3テーマ×各8 seed。評価=対象factの決定論語彙判定+二重ラベル(各段)。合格基準: HC-012型曖昧訳がAで6/8以上に対しBで1/8以下/held-out(HF-012・HC-014・small_bag方向語fact)で悪化なし/Quality(03 draft §4基準、逐語コピー率+5pt以内、pairwise「劣る」≤25%)。C_wは最初の1 chainで実測し上限超過見込みならSTOP。
Phase 3(必要時、上限¥30): 承認済みChecker構成でA/B各2 run、誤爆・見逃し確認。
合計上限案¥100。過学習防止(prompt規則に固有名を入れない、合格基準・held-outの事前固定・sha256凍結)。所要時間見込み(Phase 0 ¥0 20分/1 30分/2 60分/3 30分+評価・SSOT)。揺れ対策(seed 8、二重ラベル、順序入替)。必要なDEV経路(B3/Writerへの台帳パス差替え引数、Production既定は従来)。STOP条件。Status分類(VALIDATED/REJECTED/USER_DECISION_REQUIRED、VALIDATEDでもProduction採用ではない)。
Dangling Reference: 参照ファイル・行の実在をGlob/Grepで確認し末尾に記載。

## 事前指定Read一覧
`docs/pm/ledger_clarity/04_design.md`: 全文(116行)。`03_trial_eval_design_draft.md`: §4〜§7(Grep `^## `→範囲)。

## 事前指定Grep一覧+追記位置・更新位置の手順
設計doc: Grep `^## §` で各§末尾を特定→「Opus反映」追記。Dangling: Grep/Glob `selected_brief.md|original.md|b1b/article.md|TAG_LINE|parse_ledger_text|facts_have_causal|numbers_not_in_facts`。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_03a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_03a.md_check.json`

## SSOT追記文
なし(委任_03eが担当)。

## Git
なし。

## 報告(RESULT_PACKET項目)
最終報告8行以内(反映した§、本番推奨経路、Trial計画の費用上限・時間、Dangling結果、T-0)。
