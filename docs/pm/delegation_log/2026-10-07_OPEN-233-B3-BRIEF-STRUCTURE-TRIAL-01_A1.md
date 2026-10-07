## 管理ID
OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_A1: 6条件のB3指示文設計+Trial専用の差し替え実装+テスト+固定ブロック準備。¥0・API呼び出しなし)

## 性質/禁止事項
性質: 設計+DEV実装(Trial専用)。禁止: Production変更(`er019_family_x_storyline_b3_fact_selection_01.py`・他Production runner・CURRENT_SPEC)/有料実行/SSOT編集/`git add -A`/`er052_output/open238_precheck_fix_trial_01/`に触れない(別委任が使用中)。

## 固定ブロック
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力は必要行のみ。F-1: 退避不要。T-0: 本ファイル(委任文の簡略保存、2026-10-07、Sonnet実行層が要旨保存)。

## 背景(要旨、逐語ではなく簡略保存)
仮説doc `docs/pm/b3_brief_structure_hypothesis_01.md`(H1主体・対象省略、H2Storyline連結、H3fact基盤薄・未提示不記載)。現行B3は「簡潔にまとめた文章」のみ。既存DEV runner `er052_open233_polysemy_nb_dev_01.py`(patched_b3、--brief-md、--phase、--no-checker)。承認済み6条件: V0現行/V1主体・対象保持/V2Storyline単純化/V3=V1+V2/V5最大忠実(fact_id・逐語・役割・5件以上・未提示明記)/V6最大簡潔(逆方向対照)。テーマ meta/hormuz/space_weapons、台帳 `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`。標本: 条件×テーマ×B3 2回×Writer 2本=72記事、Checkerなし。

## 事前指定Read一覧
`er019_family_x_storyline_b3_fact_selection_01.py`、`er052_open233_polysemy_nb_dev_01.py`、`docs/pm/b3_brief_structure_hypothesis_01.md`、`er052_output/open233_note_transfer_matrix_01/cost.json`。

## 事前指定Grep一覧+追記位置・更新位置の手順
patched_b3 / add_argument / storyline_b3 / brief_md をDEV runnerとer019 runnerでGrep。新規ファイルのみ作成し既存追記なし。

## 実行コマンド全文
1. 設計doc `docs/pm/b3_trial_01/design_01.md`(各条件の指示文・差し込み位置・「簡潔に」の扱い・読み方事前固定・Opus条件A論点5点以内・費用見積・Dangling Check)。
2. 実装 `er052_open233_b3_variant_dev_01.py`(VARIANTS・patched_b3_variant・provenance)+ `er052_output/open233_b3_trial_01/tools/run_b3_variant.py`。
3. テスト `er052_output/open233_b3_trial_01/tests/test_b3_variant_dev_01.py` 全PASS+dry-runで `er052_output/open233_b3_trial_01/prompts/<variant>_<slug>.txt` 出力。
4. 実行計画 `er052_output/open233_b3_trial_01/PLAN.md`(予算guard、停止時規則各枠1回再実行・合計8回、¥500超見込みでSTOP)。
5. 本T-0保存+`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-07_OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01_A1.md --json-out docs\pm\delegation_log\2026-10-07_OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01_A1.md_check.json`
6. Production無変更確認 `git status --porcelain -- er019_family_x_storyline_b3_fact_selection_01.py er003_v1_en_direct_vfl_01_generate.py er019_family_x_ja_writer_o_r1_r2_01.py CURRENT_SPEC.md` が空。

## SSOT追記文
SSOT編集禁止(追記なし)。

## Git
個別addのみ。message: `OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 Phase A: 6条件(V0/V1/V2/V3/V5/V6)のB3指示設計+Trial専用差し替え(patched_b3_variant)+テストX件PASS+dry-run prompt出力、Production変更なし・¥0`。push。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>

## 報告
12行以内: (1)各条件の指示文要旨 (2)差し込み位置と「簡潔に」の扱い (3)テスト件数・PASS (4)dry-run prompt出力パス (5)費用見積(工程別) (6)Opus論点 (7)commit hash (8)Production無変更 (9)T-0
