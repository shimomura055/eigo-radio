# 委任文(保存): FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_02a(2026-10-08)

## 管理ID
FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_02a: Opus条件Aレビュー指摘の反映。API課金なし・git操作なし)。並行タスク `ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01`(別agent実行中)。委任_01と同じ隔離規則を厳守。

## 性質/到達上限Status/禁止事項
- 性質: Trial準備(設計・harness・事前登録の修正)。到達上限Status: READY_FOR_GENERATION(生成は委任_02b)。
- 書込可: er052_output/factlock_writer_trial_01/ 配下、er052_factlock_writer_trial_01_run.py、er052_factlock_writer_trial_01_test_01.py、docs/pm/RESULT_PACKET_FACTLOCK.md、本ファイル(+_check.json)、docs/pm/opus_l2_review_factlock_writer_trial_01.md。
- 編集禁止: RESULT_PACKET.md・ACTIVE_TASK.md・SSOT各種・Production code(er019_*/er003_*/er006_*)・er052_output/all6_writer_redesign_necessity_01/・er052_output/open233_b3_trial_01/runs/。git add/commit/push禁止。有料API禁止(mockのみ)。
- 費用: 0円。Opus独立技術レビューGate: 条件A実施済み(本委任はその反映)。総合判定「修正後に進む」。
- 時間見込み: 45〜60分。並列不要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read基本。G-1: git出力は最小化(本委任は状態確認のみ)。F-1: transcript退避不要。T-0: 本ファイル保存+check_delegation_prompt実行、結果をRESULT_PACKETへ1行。T-2: TTSなし。T-3: 課金なし。

## ユーザー指示(原文)
「CでOK。それ以外も貴殿提案ベースでよいので進めてください。」(2026-10-08)。名称内番号(COSMOS 1408・第4条)は案A(周辺のまま、数字を省いて名称を書く)で進め、所見をユーザーへ報告(ユーザー判断は結果報告時)。

## KPI provenance欄
該当なし(本委任は測定なし)。

## Opus台帳更新
docs/pm/OPUS_FINDINGS_LEDGER.md は編集禁止。RESULT_PACKET_FACTLOCKへ M1〜M9・O1〜O4 の状態表(RAISED→FABLE_DECIDED→IMPLEMENTED)と台帳追記文案を記載。

## 事前指定Read一覧
Opusレビュー全文(docs/pm/opus_l2_review_factlock_writer_trial_01.md へ保存)、harness L50-86/L102-117/L346-381/L472-475、er019_family_x_ja_writer_o_r1_r2_01.py L58/L102-106/L405/L464、DESIGN_01.md §1〜§4/§7/§8、PREREGISTRATION.md、FIXED_SHAS.json。

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep 【F\d|strip_tags|TAG_RE → O1(【事実N】)・M3(広め除去 【\s*[FＦ事実][^】]{0,30}】+残存「【」件数)。注記brief12本はtools/annotate_briefs.py修正で再生成(原本不変・sha再確認)。
- Grep REVISION_INSTRUCTIONS|CONCRETENESS_CONTROL_AN3_BLOCK → R0/R1/R2ブロックをM2/M4/M5/M6で更新。
- Grep 判定|unsupported|neutral → 照合(i)をM1、(ii)をM7へ改修。
- DESIGN_01.md各§更新+末尾に改訂履歴v2(O3/O4不採用の理由: O3=本Trialはパッケージ効果の測定、O4=時間優先)。
- PREREGISTRATION.md: 言えること/言えないこと(M9)、STOP記事の扱い(M8)、同一評価パック必須(M8)、sha再固定(旧sha履歴保存)。

## 実行コマンド全文
cwd=C:\Users\tensh\eigo-radio、python=.venv\Scripts\python.exe。
1. .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_02a.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_02a.md_check.json
2. Opusレビュー全文を docs/pm/opus_l2_review_factlock_writer_trial_01.md へ保存。
3. M1〜M9必須、O1・O2採用、O3・O4不採用(詳細は委任原文のM/O定義、Opusレビュー全文に同じ)。
4. .venv\Scripts\python.exe -X utf8 -m pytest er052_factlock_writer_trial_01_test_01.py -q 全PASS(M1集計/M3除去/O1形式/M7集計/タイトル対象/注記brief12本/Production 5ファイル無変更[git diff HEAD --stat 読取のみ])。
5. FIXED_SHAS.json再固定(旧値は改訂履歴へ)。
6. 委任_02b手順を設計書§10に確定版で記載: smoke 1本(hormuz b4)→「【」残存確認→24本(12 brief×2反復、4並列、--budget-jpy 12/run)→照合→盲検評価(all6記事と同一パック)→集計。費用上限150円(T-3定型文)。開始条件: all6_writer_redesign_necessity_01/MANIFEST.json存在と全48 runのexit記録。

## SSOT追記文
SSOT編集なし。RESULT_PACKET_FACTLOCKへ(1)DECISION_LOGエントリ案、(2)OPUS_FINDINGS_LEDGER追記文案。

## Git(明示add対象・コミットメッセージ・trailer)
本委任ではgit操作禁止。commit候補は委任_01の一覧+opus_l2_review_factlock_writer_trial_01.md+本ファイル(+_check.json)。

## 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET_FACTLOCK.md を上書き: 1.M/O反映状態表 2.R0/R1/R2追記ブロック全文 3.テスト結果 4.新sha一覧 5.委任_02b開始条件・手順・費用・時間 6.問題・残作業 7.check結果1行 8.SSOT追記文案。推奨は書かず事実のみ。

(Opusレビュー全文は docs/pm/opus_l2_review_factlock_writer_trial_01.md に逐語保存)
