## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_04: 残骸整理・Dangling Reference Check・明示git add・commit・push、¥0)

## 性質/到達上限Status/禁止事項
性質: Closeout作業(¥0)。到達上限: commit/push完了報告(Status=USER_DECISION_REQUIRED、これはSSOT済み)。禁止: SSOT本文の内容変更(参照パス修正のみ可)/有料API/Production変更/`git add -A`/`git add .`/amend・rebase・force push/ACTIVE_TASK・RESULT_PACKET*のcommit。Opus Gate: 実施済み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_04.md` に逐語保存し `python check_delegation_prompt.py <そのパス>` を実行(結果JSONは同名`_check.json`)。FAILでも作業は続行し結果を報告。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「今回は設計とTrial計画まで。Trial実行・Production実装は禁止」「Dangling Reference Checkを実施する」「CURRENT_SPECの正式仕様部分を勝手に更新しない」。

## 事前指定Read一覧
- `docs/pm/ledger_clarity/05_trial_plan.md`(全文、72行)
- `docs/pm/ledger_clarity/04_design.md` の §13 のみ(Grep `^## §13` で位置特定後、その節のみRead)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 残骸削除: `docs/pm/opus_l2_review_lc_part3b.md`、`docs/pm/opus_l2_review_lc_part3c.md` を削除(統合ファイルに同内容が含まれるため)。`docs/pm/opus_l2_review_lc_part*.md` が他に残っていれば一覧して削除。
2. 統合ファイルの存在・行数確認: `docs/pm/opus_l2_review_lc_design_01.md`(本文はReadしない。行数と、`総合判定`/`必須修正`/`Trial計画への修正提案` の語の存在をSelect-Stringで確認するだけ)。
3. Dangling Reference Check(パス実在のみ。内容は読まない):
   - 対象ファイル: `docs/pm/ledger_clarity/01_current_pipeline.md`、`02_cases.md`、`03_trial_eval_design_draft.md`、`04_design.md`、`05_trial_plan.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` の §87 範囲(Grep `^## §87`〜次の`^## §`)、`DECISION_LOG.md` の LEDGER-CLARITY エントリ(Grep `LEDGER-CLARITY-DESIGN-01`)、`OPEN_ITEMS.md` の OPEN-237 行(Grep `OPEN-237`)、`docs/pm/OPUS_FINDINGS_LEDGER.md` の OF-059 行(Grep `OF-059`)。
   - これらの中でバッククォート付きのファイルパス(`docs/...`、`er0XX_output/...`、`*.py`、`*.md`、`*.json`)をGrepで抜き出し、Test-Pathで実在確認。存在しないものを列挙。
   - 特に `docs/pm/opus_l2_review_lc_design_01.md` への参照と、04_design §13 / 05_trial_plan 内の「未作成」注記: 統合ファイルが今は存在するので、「未作成」「作成予定」等の注記があれば「作成済み(2026-10-06、委任_03f、セッション記録から機械抽出・改変なし)」へ**その注記部分のみ**修正する(他の文は変えない)。
   - 不在パスがあれば、タイポ等の明白なものは修正し、それ以外は修正せず報告。
4. `git status --porcelain` を取り、下記対象のみを確認。

## 実行コマンド全文
- `git add OPEN_ITEMS.md DECISION_LOG.md OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md docs/pm/OPUS_FINDINGS_LEDGER.md docs/pm/ledger_clarity/01_current_pipeline.md docs/pm/ledger_clarity/02_cases.md docs/pm/ledger_clarity/03_trial_eval_design_draft.md docs/pm/ledger_clarity/04_design.md docs/pm/ledger_clarity/05_trial_plan.md docs/pm/opus_l2_review_lc_design_01.md`
- `git add docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_*` (globが展開されない場合は個別列挙。`_check.json`も含める)
- `docs/pm/factcheck_s1_second_opinion_01.md`、`docs/pm/factcheck_judgment_inventory_01.md` は**addしない**(別管理ID、ユーザー判断待ち)。`docs/pm/ACTIVE_TASK.md`、`RESULT_PACKET*`、`er0XX_output/`配下、`.json`(root)、その他の未追跡ファイルは**addしない**。
- `git diff --cached --stat` を取り、上記以外が混入していないことを確認(混入があればunstageして報告)。
- commit message(1行目、以下そのまま使用):
  `OPEN-233-LEDGER-CLARITY-DESIGN-01: Fact台帳の明確化設計+Opus条件Aレビュー+Trial計画完了(¥0)【Writer誤読の上流予防、本番推奨経路P'(Researcher/Verification拡張・追加callなし)、案C+Vはoffline Trial用、Trial計画Phase0〜3・上限案¥100、必須修正M1〜M6反映】→USER_DECISION_REQUIRED(Trial承認・経路選択待ち)、Trial未実行・Production変更なし、残11 run待機、REPORT §87/OPEN-237/OF-059`
- `git commit -m "<上記>"` → `git push origin main`
- 失敗(conflict等)時はamend/force禁止、状態を報告して停止。

## SSOT追記文
なし(§87・DECISION_LOG・OPEN-237・OF-059は委任_03eで反映済み。パス注記修正のみ可)。

## Git
上記のとおり。

## 報告(RESULT_PACKET項目、12行以内)
(1)削除した残骸ファイル (2)統合ファイル行数・語存在 (3)Dangling結果(不在パス一覧/修正箇所) (4)staged一覧(`--stat`) (5)commit hash・push結果 (6)T-0結果 (7)05_trial_plan.md の要点: Phase構成・各費用・合計上限・所要時間・合格基準(各1行、数値はファイルどおり) (8)04_design §13 の要点(Opus指摘とFable照合の結論、3行以内)
