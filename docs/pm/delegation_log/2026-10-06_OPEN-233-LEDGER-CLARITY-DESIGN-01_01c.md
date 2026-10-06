## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_01c: Trial評価設計のドラフト—品質①Writer誤認、②Checker精度、③記事Quality の測定方法・合格基準・件数・揺れ対策・費用式。¥0)。並列委任_01a(仕様調査)、_01b(事例収集)、_01d(SSOT)が同時進行。**書込先: `docs/pm/ledger_clarity/03_trial_eval_design_draft.md`(新規、150行以内)、`docs/pm/delegation_log/`のみ。コード・SSOT・git変更なし。API呼出なし。Trial実行禁止。**
作業方式: 説明最小、Bash heredoc不使用、Write/Edit 1回40行以内。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0 Trial計画ドラフト(設計案確定後にFableが統合)。禁止: 有料API/Trial実行/gold・KPI変更/新しい重大基準の提案(既存の重大Fact誤り基準で評価)。Opus Gate: 設計案と併せて条件Aレビュー対象。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01c.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外(¥0)。

## ユーザー指示(原文、要点)
> Trial計画: 品質①Writerの重大Fact誤認を減らせるか(HC-012、HF-009を含む複数事例で従来台帳と明確化台帳を比較。未使用の検証例も含める)。品質②Checkerの検出精度が改善するか(重大見逃しと正常文の不要重大判定の両方。Checker構成は原則固定)。品質③記事の自然さ・面白さを損なわないか(Writer出力を比較し読みやすさ・自然さ・ストーリー性・多様性)。各評価について測定方法・合格基準・検証件数・モデルの揺れへの対策を事前に定義。Trial費用上限案と所要時間を提示。

## 既存の再利用資産(費用式の根拠。Grep/範囲Readで確認)
- 自己回復フローrunner `er052_open233_self_recovery_flow_runner_01.py`: 1 run(Writer生成+Checker+後段+Rewrite)の実費≈¥3.5/run(新9 run E2E実績、`er052_output/open233_prod_e2e_02/report_final/report_abcde.md` Grep `¥|cost`)。fixture切替(`--fixture`/Ledgerパス指定)の引数があるかGrep `add_argument|fixture|ledger_path`。
- ラベル付け基準 `er052_output/open233_prod_e2e_01/labeling_guide_01.md`(重大/軽微/問題なしの定義、Grep `重大|軽微`)、集計`aggregate_report_abcde_01.py`(A〜E指標)。
- 記事Quality評価の既存手段: Grep `quality|naturalness|readability|多様性|diversity|rubric` in `docs/pm/` と `er0*.py`(既存のQuality判定prompt/scoreがあれば流用候補として記す。なければ「新規に簡易rubricが必要」)。
- Writer揺れ: 同一台帳で複数run(新9 runは同fixtureを複数seedで実行)の実績。

## 設計内容(各評価: 目的/比較条件/測定方法/指標/合格基準案/件数/揺れ対策/費用式/時間)
①Writer誤認: 条件=従来台帳 vs 明確化台帳(同fixture、Checker構成固定、同seed数)。測定=Writer出力(Rewrite前の初稿)に対し、重大Fact誤りの有無を(a)既存Checker+後段(現行承認構成)と(b)Fable/Sonnetのoffline読解ラベル(labeling_guide準拠)の両方で計数。指標=重大誤り件数/run、HC-012型・HF-009型の発生率(従来台帳の実績: HC-012系誤読は新9 runでmeta 5 run中1件【要確認】)。合格基準案=明確化台帳で重大誤り件数が従来以下かつHC-012/HF-009型0件、held-out事例でも悪化なし。件数=fixture 2(meta/hormuz)×台帳2条件×seed n(nは費用から逆算、3〜5)。揺れ対策=同条件複数seed、差は件数でなく率と区間で示す。
②Checker精度: 同じrunのChecker出力で、重大見逃し(ラベル重大だが非BLOCKING)と不要重大判定(ラベル問題なしだがBLOCKING/Rewrite)を従来/明確化で比較。Checker構成=承認構成固定(変更しない)。合格基準案=見逃し減少または同等、不要重大判定増加なし、Rewrite件数/run非増。
③記事Quality: 同条件のWriter出力を対で比較(従来台帳版 vs 明確化台帳版)。測定=(a)決定論指標(文数・語彙多様性・文長分布・Ledger逐語コピー率)(b)LLM pairwise判定(別prompt、読みやすさ/自然さ/ストーリー性/多様性の4軸、どちらが良いか+理由、順序入替で2回)(c)Fable抜粋確認。合格基準案=pairwiseで明確化版が「劣る」判定の割合≤25%かつ4軸いずれも有意に劣化なし、逐語コピー率の上昇≤+5pt。揺れ対策=順序入替・複数判定。
費用式: run数×¥3.5+Quality判定call数×単価(Stage 2単価¥0.06/call基準)+台帳明確化call(fact数×1、¥0.1〜0.3/fixture)。low/mid/highと上限案(例: 2 fixture×2条件×3 seed=12 run≈¥42+判定≈¥3→上限¥50案、および縮小案 2×2×2=8 run≈¥30)。所要時間(3並列で run≈8分/run → 12 run≈35分+評価30分+SSOT20分)。
STOP条件案・過学習防止(held-out fixture/factを事前固定、明確化promptはHC-012/HF-009の文言を直接埋め込まない)。
出力: `docs/pm/ledger_clarity/03_trial_eval_design_draft.md`。

## 事前指定Read一覧
Grep結果の範囲Readのみ(各40行以内)。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記「既存の再利用資産」のGrep。新規ファイルのため追記位置なし。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01c.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01c.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
最終報告8行以内(①②③の合格基準案、件数案、費用low/mid/high、時間、既存Quality評価手段の有無、T-0)。
