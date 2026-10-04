# 委任_09 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01(全文保存、分割記録)

## 管理ID・並行タスク

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_09、是正指示CORRECTION-02の§5「後段は準備済みのOpus#15/Fable評価に従い進める」の前倒し作業)。並行タスク: 委任_08(A構成fresh限定確認。`DECISION_LOG.md`/`OPEN_ITEMS.md`/REPORT/`REPORT_LEDGER.md`/provenance文書/`er052_*`スクリプト/`ACTIVE_TASK.md`/`RESULT_PACKET.md`を編集)。本委任はそれらを一切編集しない。編集対象は`CURRENT_SPEC.md`(OPEN-233節への新小節追加のみ)と新規文書`docs/pm/production_wiring_report_open233_01.md`、自分の委任ログのみ。報告はhandback本文(RESULT_PACKETに書かない)。gitはこの3種のみ明示add(index.lockは10秒待ち最大3回再試行)。

## 性質・禁止事項

- 性質: ¥0・SSOT整備(Dangling Reference Check(1)「CURRENT_SPECに正式仕様があるか」の充足)。Opus#15論点10「CURRENT_SPECのOPEN-233節にSelf-Recovery Production Flow仕様を1節新設」を、承認済み内容(DECISION_LOG 2026-10-05ユーザー決定、Gap文書§7 Fable評価、Opus#15)に基づき書く。新仕様の創作は禁止。書くのはrep30有効構成(Gap文書§1 S01〜S23/N01〜N10)とFable評価で採用済みの配線方針のみ。Stage 1 Checker構成は「A構成(gpt-6-luna+rep30 frozen出力を生成したV4A系構成、CORRECTION-02)。詳細定義は委任_08の`docs/pm/rep30_stage1_provenance_01.md` §7で確定後に転記」とプレースホルダで書く。
- 禁止: コード変更、上記以外のファイル編集、`git add -A`/`stash`/`amend`。1回の書き込みは2,500文字以下(小節ごとにEdit追記)。長文逐語引用はせずDECISION_LOG/Gap文書/設計書の該当節を参照。
- T-0: 本ログに全文保存(分割)、check実行、結果をhandback本文に1行。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業1: CURRENT_SPEC.md OPEN-233節に小節新設

小節名「OPEN-233 Self-Recovery Production Flow仕様(APPROVED_FOR_PRODUCTION、PRODUCTION_WIREDは完了条件1〜12達成後)」を、`OPEN-233 Trial Closeout・Production正式採用`小節の直後に追加。項目(根拠として設計書§/Opus#/DECISION_LOG日付を括弧で付す):
1 位置づけ・入口条件(Feature flag、初期OFF、family単位、順序P3/P4→P5→P1/P2、P6は監視専用) / 2 Stage 1 Checker(A構成プレースホルダ、`severity_final`は選別に使わない、MAJORのみStage 2、MINOR渡さない、非検出でもprecheck結果ログ) / 3 Model/Routing(gpt-6-luna、新process、`require_model`、fail-closed `api_failure`、Writer不変) / 4 Stage 2 materiality(V7b正本=`er052_open233_self_recovery_stage2_calibration_01.py` L612、決定論floor、時期のみ追加確認、S1、BLOCKING固定、非BLOCKING 2-of-2再利用、兄弟箇所列挙、「AI1回で重大→問題なし」禁止) / 5 span解決(L0〜L6等) / 6 Rewrite ladder / 7 Recheck / 8 cycle定義(MAX_CYCLES=2+条件付き3、判定専用cycle、T、本文変更計4回) / 9 Human Review出口(許可リスト4種、sub_reason必須、family終端写像) / 10 Family X固有 / 11 retry/fallback/regeneration / 12 Trial依存禁止(`git grep`機械検査) / 13 Cost KPI(+¥2/記事、基準=現行Production 1記事費用[委任_04c: JA側Checker+loop平均¥2.77/中央値¥2.50、n=8、EN側未分離]、¥3超は報告のみ、「正確に半額」訂正[出力$0.50 vs $1.20]) / 14 配線しない(REJECTED/OFF)一覧 / 15 完了条件1〜12とruntime evidence計画(Phase 2: 既存テーマ再生成+STOP実例+P3/P4/P5各1+Safety fixture 3+クリーンPASS>=1+¥0 fixture)。同節内の既存「正確に半額」記述をGrep `半額`で特定し訂正(1行)。

## 作業2: `docs/pm/production_wiring_report_open233_01.md`(新規骨子)

見出し: 1目的・Status / 2 rep30有効構成とProduction対応 / 3 Stage 1 A構成fresh確認(委任_08結果を後で転記) / 4 配線設計 / 5 実装記録 / 6 runtime evidence / 7 Regression・integration / 8 Dangling Reference Check表 / 9 完了条件1〜12チェック表(全て未) / 10 費用記録(¥3超run欄) / 11 未解決・開示事項(K1 T計4回、K4 日本語側誤り残存、A2A3 HF-009 rep30非検出、委任_05 ¥20.10記録)。

## 作業3: commit/push

明示add(`CURRENT_SPEC.md`、新規report、委任ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: CURRENT_SPECに「Self-Recovery Production Flow仕様」節を新設(DRC1充足、Stage 1はA構成プレースホルダ)、Production wiring report骨子(委任_09、¥0)`

## 事前指定Read一覧

CURRENT_SPEC OPEN-233節見出し構造・委任_01c小節、Gap文書§1表・§7、Opus#15論点10、DECISION_LOG 2026-10-05エントリの完了条件。

## 事前指定Grep一覧+追記位置・更新位置の手順

Grep `OPEN-233 Trial Closeout・Production正式採用`→直後に追加、Grep `半額`→訂正。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_09.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_09.md_check.json

Git: git status --porcelain、明示add(3種のみ)、git commit、git push origin main、git log --oneline -1

Git(明示add対象・コミットメッセージ・trailer): 上記作業3のとおり。trailerは`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。

## 報告(handback、短く)

(1)結論5行以内 (2)CURRENT_SPEC追加行範囲・項目数・訂正箇所 (3)report骨子パス (4)T-0・commit・push・raw URL(CURRENT_SPEC)・一覧外Read (5)Fableへの論点(承認済みから外れそうで書かなかった点)。
