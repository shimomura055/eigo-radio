## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_01b = 委任_01の再開、範囲をDECISION_LOGのみに縮小)。並行タスク: 委任_02(Gap棚卸し文書`docs/pm/production_wiring_gap_open233_01.md`のみ作成、git操作なし)。本委任は`DECISION_LOG.md`と委任ログのみ編集。

## 性質/到達上限Status/禁止事項

- 性質: ¥0・SSOT記録のみ。委任_01は長文の逐語出力の途中で出力が止まり、SSOTは未更新・未commit(作業ディレクトリに変更なし、スクラッチ下書き`dl_entry.md`は未完成)。再開にあたりFableは方針を決めた: **長文の逐語記録は「モデルが本文を再出力する」のではなく「既存ファイルから抽出してファイル間でコピーするスクリプト」で行う**(ユーザー要件「逐語」を満たしつつ、生成出力を短く保つ)。モデル自身の出力は、短い見出し・Fable補足・Evidenceパス・スクリプトに限定する。
- 到達上限Status: 対象仕様は`APPROVED_FOR_PRODUCTION`(ユーザー決定済み)。`PRODUCTION_WIRED`にはしない。
- 禁止事項: コード(Production・Trial)変更禁止。`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`PM_GOVERNANCE.md`/REPORT/`REPORT_LEDGER.md`は本委任で編集しない(次の委任_01cで行う)。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。ユーザー決定文の要約・改変禁止。
- 費用上限: ¥0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0/T-2/T-3は標準文面どおり(委任文原文を参照。本ログは要点保存)。T-0: 本ファイルを保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録。

## ユーザー指示(原文、該当部分)

原文全文は`docs/pm/delegation_log/2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01.md`の「## ユーザー指示(原文、全文。DECISION_LOGへ逐語記録すること)」節(L28-218の````ブロック)に保存済み。これを転写元とする。

## 作業(スクリプト転写方式)

1. `docs/pm/tools/append_decision_log_from_sources_01.py`(汎用: 転写元ファイル・開始/終了マーカーを複数受け取り順に`DECISION_LOG.md`末尾へ追記。総文字数・各ブロック先頭/末尾40文字を出力。`--dry-run`あり)。
2. DECISION_LOG末尾エントリ: 見出し`## 2026-10-05 ユーザー決定 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01(Trial Closeout・Production正式採用・Cost KPI更新・改善ループ運用ルール)`／「ユーザー指示原文(逐語)」(委任_01ログ````ブロックをスクリプト転写)／「Fable補足」(短文)／「前管理ID OPEN-233-KPI-RECOVERY-REDESIGN-02 のFable評価・判断(転記)」(設計書§16・§18・§18-C、委任ログ_02〜_10・_12の「Fable判断/前提/評価/照合」ブロック、_13は「Fable判断」ブロックのみをスクリプト転写。各ブロック前に「出典: <パス> L<開始>-<終了>」自動付与)／「Trial Closeout分類」(REJECTED/VALIDATED/USER_DECISION解消/未解決の短い表)。
3. `--dry-run`→本実行→`git diff --stat DECISION_LOG.md`→末尾60行のみ確認。
4. 明示add(`DECISION_LOG.md`、スクリプト、委任ログ_01+_01b+各check.json)→commit→`git push origin main`。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: ユーザー決定(Trial Closeout・APPROVED_FOR_PRODUCTION・+¥3単発Cap撤回・改善ループ3回Cap)をDECISION_LOGへ逐語記録、前管理IDのFable評価を転写(委任_01b、¥0)`

Fable補足(逐語、DECISION_LOGへ入れる文): 「rep30の実測値はユーザー記載のとおり(29ケース・38 run・Human Review 0・重大見逃し0・平均¥0.573/run・rep24比+¥0.13/run・不要Rewrite 3/14で悪化なし)。worst追加は+¥3.135(safety_A4 s1、1/38 run)であり、ユーザー決定により単発Capは撤回、¥3超は報告・記録対象として本決定記録に残す。Status: Trial=VALIDATED、対象仕様=APPROVED_FOR_PRODUCTION、PRODUCTION_WIREDは完了条件1〜12達成後のみ。B′同一箇所昇段・非BLOCKING判定再利用はユーザー承認。F1不採用。追加N増しなし。Productionで問題発生時は個別改善。Opus/Fable改善ループは自律3回Cap、4回目以降は毎回ユーザーGate(PM_GOVERNANCE 11節へ反映、委任_01c)。」

分類表(モデルが書く): REJECTED=確認役(STAGE2_DOWNGRADE_VERIFY)/G_L/N3′(RECHECK_BEFORE_AFTER_PAIRS)/因果floor目録拡張(CAUSAL_FLOOR_VOCAB=inventory)/A1/C/E1/E2/F1/F2/NORMAL群2-of-2(Trial補助、配線しない)。VALIDATED=rep30有効構成(列挙はCURRENT_SPEC側、委任_01c)。USER_DECISION(本決定で解消)=Cap未達の扱い(撤回)/B′§0-4解釈(承認)/非BLOCKING再利用(承認)/次Trial GO(追加N増し不要で解消)。未解決(配線時に扱う)=`blocking_structural_after_ladder`の未検証経路(T無効・T使用済み・cap後T不可・T削除失敗)、`issue_focus_absent_recheck_only`(本文全体判定へ是正済み)、「and」版ACCEPTABLE判断(ユーザー未確認)。

## 報告(RESULT_PACKET)

(1)結論5行以内、(2)追記総文字数・ブロック一覧(出典・行範囲・文字数)、(3)分類表、(4)T-0・commit・push・raw URL・一覧外Read、(5)委任_01cへの引継ぎ(CURRENT_SPEC/OPEN_ITEMS/PM_GOVERNANCE/REPORT§63/REPORT_LEDGER/ACTIVE_TASK/委任_13注記が未実施)。
