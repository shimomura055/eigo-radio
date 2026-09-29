管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_05: 既存 部分Rewrite/Local Rewrite 機構の棚卸し。**read-only 調査+新規文書1本のみ・API呼び出しなし・¥0・Production非接続**)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質
read-only調査タスク。コード・Prompt・SSOT編集なし、API呼び出しなし、
git add/commit/pushなし(次委任でcommitする前提)。到達上限Status:
INVENTORY_DONE(USER_DECISION_REQUIREDには該当しない、単なる調査報告)。
禁止事項: docs/pm/design_open233_self_recovery_flow_01.md、
OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、DECISION_LOG.md、
OPEN_ITEMS.mdの編集(委任_04が同時編集中のため)。削除・移動・rm・
stash・git add -A禁止。

## 1. 事前指定Read一覧
なし(本委任はSSOT全文読込を行わない設計。既存ファイルはGrepで該当行
±20行のみ参照)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- 対象キーワード: "Local Rewrite"/"局所"/"部分再生成"/"segment再生成"/
  "must-fix"/"tail_fix"/"cooldown"/"prior_issues"/
  "split_family_x_article_text_v2"。
- 対象ファイル(候補): er020系3ファイル、er021系、
  er003_v1_sing01_news_tail_fix.py、er003_v1_n3_01_articles_generate.py、
  er012_b_family_voices_writer_generic_01.py、
  er012_b_family_production_runner_01.py、
  er026_family_z_fiction_production_runner_01.py、
  er019_family_x_audio_production_runner_01.py、
  er019_family_x_audio_plan_01.py、
  er012_e_family_entertainment_two_level_runner_01.py、
  er019_family_x_ja_writer_o_r1_r2_01.py、
  er003_v1_en_direct_vfl_01_generate.py、
  er010_ledger_local_rewrite_09.py、
  er003_v1_n3_01_standard_a2_generate.py、
  er003_v1_n3_01_advanced_adaptation_generate.py、
  er003_v1_n3_01_scaffold_generate.py、CURRENT_SPEC.md。
- 追記位置: 新規ファイル
  `docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`のみ(既存
  ファイルへの追記・更新は行わない)。

## 3. 実行内容
Read/Grep/Globツールで上記ファイルをread-only調査。er010_ledger_
local_rewrite_09.py(Ledger Deviation MAJOR文単位Local Rewrite、
Production稼働中だがFamily B系のみ)、Family X現行must-fix全文retry
(Standard/Advanced各1回のみ)、JA Writer O(Original/R2段単位must-fix、
JA文単位Local Rewrite機構は不在)、TTS発音NGspan Local Rewrite
(er020系、別ドメイン)を確認。詳細は
`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`参照。

## 4. 実行コマンド全文
Bash経由のgit/lsコマンドのみ(API呼び出し・課金コマンドなし):
- `ls docs/pm/ | grep -i "C233"`
- `ls er020_*.py er021_*.py`
本委任はLLM API呼び出しを一切行わない(Read/Grep/Globツールのみで
既存コードとSSOTを調査、有料コマンド実行なし)。

## 5. SSOT追記文
本委任ではCURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdへの追記は
行わない(委任_04が同時編集中のため範囲外。次委任でinventory結果を
踏まえた設計書§5改訂・DECISION_LOG記録を行う想定)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
本委任ではgit add/commit/pushを行わない(index ロック競合回避のため
次の委任へ委ねる)。次委任でのcommit対象(想定): 本ファイル、
本check.json、`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`。
想定コミットメッセージ: "OPEN-233-SELF-RECOVERY-TRIAL-01: 既存Local
Rewrite機構棚卸し文書追加(委任_05)"。trailer:
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。

## 7. 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET_C233I.md参照。
