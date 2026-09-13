# PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01

**性質**: 設計文書のみ($0、API呼び出しなし)。本タスクではTrialを**実行しない**
(実際の委任・計測実施はFableが別タスクとして行う)。Production/QA/Prompt
(記事生成仕様・生成コード)には一切関与しない。

**ユーザー承認(2026-09-13、原文)**:
> 施策1は推奨案(a)でTrial設計に進めてください。施策2も推奨案(a)とし、
> まず既存ルールの委任文明記率を100%に是正して観察してください。施策1では
> tool_usesとusageに加え、見落とし・手戻りも確認してください。

**前提数値(根拠: `PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01_REPORT.md`)**:
- Before母集団357件(sonnet-worker委任、7日分)、After33件(約18時間)、
  いずれもtranscript取得率100%。
- 全体中央値(Before→After): tool_uses 50→68(+36%)、累積usage
  4,296,480→5,324,655(+23.9%)、最終ターンcontext 135,747→154,148(+13.6%)、
  tool_result総文字数 127,294→152,716(+20.0%)。tool_uses⇔累積usage相関
  +0.93。全文Read率⇔usage相関−0.047。
- (a)Consolidation/SSOT反映+commit種別のみ(Before比率25.8%≈92件、
  After比率39.4%≈13件): 累積usage中央値 404.8万→575.6万、same-file
  reread率中央値 44.8%→51.7%、全文Read率中央値 46.6%→61.3%
  (いずれも改善方向は確認できていない=施策1のTrial対象として「効果を
  確認すべき」種別)。
- After委任文へのE-1/D-1/G-1明記率55%(18/33)。明記あり群は
  cumulative_usage中央値271.3万(Beforeの429.6万より低い)、明記なし群は
  1,031.5万(Beforeより高い)が、タスク種別構成の交絡でN小・分離不能。

---

## 1. 対象タスク種別

**今回のTrial対象**: (a)Consolidation/SSOT反映+commit
(`PM-CLOSEOUT-CONSOLIDATION-*`系、REPORT編纂→DECISION_LOG/OPEN_ITEMS等への
反映→git commit/push)。理由: (i)定型性が高く手順を委任文で完全に事前指定
できる、(ii)Before/After比較の母集団が最大(357件中92件相当)、(iii)
Production/記事生成に直接触れないためリスクが最小、(iv)現状Before→Afterで
tool_uses・usageとも改善方向が確認できておらず、施策の効果検証対象として
適切。

**将来拡張候補の順序(本Trialが有効/評価不足/効果なしと判定された後に
検討、いずれも今回は着手しない)**:
1. (f)計測/監査タスク(TOKEN-EFFICIENCY/AUDIT系) — (a)に次いで定型性が高い。
2. (d)Wiring/Production-fix — 定型化しにくいが、E-1/D-1明記群で改善方向の
   兆候がある種別(全文Read率54.1%→36.7%)。ただしProduction変更を伴うため
   リスクは(a)より高い。
3. (b)Trial/Production-run(記事生成本体) — 種別内消費が最大でリスクも
   最大のため最後。Trial arm導入は記事生成品質(Gate 1〜7)への影響評価を
   別途要する。

## 2. Trial arm(委任文形式の変更のみ、手順・品質要件は不変)

Trial armは**委任文の書き方のみ**を変更する。Fable/Sonnetの作業手順・
Gate要件・受入条件は一切変更しない。

1. **事前指定Read/Grep一覧**: Fableが委任文中に、必要なRead/Grepを
   「ファイル:行範囲」または「Grepパターン:対象パス」の形式で列挙する
   (例: `DECISION_LOG.md:末尾50行`、`Grep "PM-CLOSEOUT-CONSOLIDATION-10[5-9]" DECISION_LOG.md`)。
   Sonnetは列挙外の追加Readが必要な場合、理由をRESULT_PACKETに1行記録する
   (`docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`のT-1行)。
2. **小さな確認の一括化**: 複数の存在確認・件数確認は1回のBash/Grepへ
   まとめる(例: `ls a.md b.md c.md`を1コマンドに、複数grepを`grep -n
   "A|B|C" file`にまとめる等)。
3. **回帰**: `run_project_regression.py --pattern`で変更module関連へ
   絞った反復実行を基本とし、Production wiring前の**最終1回のみ**default
   パターン(全件)を実行する(既存運用[2026-09-10 Token効率運用(3)]を
   踏襲、新規ルールではない)。
4. **Git手順**: `git status --porcelain`→対象ファイルのみ明示`git add`→
   commit→pushを1連続の手順として委任文に明記し、途中の状態確認コマンドを
   増やさない。
5. **RESULT_PACKET**: 固定テンプレ(既存`docs/pm/RESULT_PACKET.md`相当の
   構造)をそのまま使い、Sonnetが構成を都度考えない。
6. **SSOT追記文案**: DECISION_LOG/OPEN_ITEMS等への追記文案はFableが委任文に
   含める(Sonnetは文案作成のために既存REPORTを再読しない。追記先ファイルの
   該当挿入位置[末尾/索引行]のみ確認する)。

**削らないもの(明記)**: 受入条件照合、Dangling Reference確認、対象ファイル
の明示`git add`(`-A`禁止は不変)、Production wiring前の回帰全件1回実行、
Gate 1〜7・PM Closeout Mandatory Check・1記事ずつ完結原則・安全≠成功原則
(いずれも`PM_GOVERNANCE.md`SSOT、変更なし)。

## 3. 計測指標

**基本指標(`docs/pm/tools/measure_delegation_task.py --task-id <taskId>`で
taskId指定・JSON出力、動作確認済み・4節参照)**:
tool_uses、cumulative_usage(全ターンusage合計)、final_context_size
(最終ターンのcontext相当)、tool_result_total_chars、same_file_reread_rate
(文字ベース)、full_read_rate_by_chars/by_calls、duration_seconds。

**見落とし・手戻り指標(定義固定、Fableが`docs/pm/tool_uses_trial_log.md`
[新規テンプレ、本タスクで作成]へ委任ごとに1行記録)**:
- `gate_reject`: gate-checkでの差し戻し回数
- `accept_criteria_miss`: 受入条件未達で発覚した件数
- `fixup_commit`: commit後に必要になった修正commit件数
- `scope_leak`: 対象外ファイル混入件数
- `ssot_error`: SSOT記載誤り件数

## 4. 比較方法

**Before**: `PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01_REPORT.md`の
(a)Consolidation種別母集団(約92件、中央値・IQRは同REPORTの種別別集計を
そのまま引用、本タスクでは再計算しない)。
**After(Trial arm)**: `docs/pm/tool_uses_trial_log.md`に記録されたN件。

**目標N=6**: (a)種別のBefore母集団(約92件)に対し、統計的な方向性
(中央値の変化)を見るための最小限としてN=6を設定する(E-1/D-1/G-1
再測定でのN=13〜18でも「評価不足」判定だったため、N=6でも確定判定は
できない可能性が高いが、Fableの運用負荷とのバランス上、まず6件で
「明確な悪化シグナルの有無」を確認する第一段階とする)。

**N=3時点の中間判断基準**: 3件のうち2件以上でgate_reject/
accept_criteria_miss/fixup_commit/scope_leak/ssot_errorのいずれかが
1件以上発生した場合、N=6完了を待たずSTOP条件(6節)に従い一旦停止し
Fableへ報告する。悪化シグナルがなければN=6まで継続する。

**ペアリング方法**: 各Trial arm委任について、同時期(直近30日以内)の
Before母集団から「対象SSOTファイル数・追記文字数が近い」Consolidation
タスクを1件、Fableが目視で選び`pairing_before_task`列(管理ID)に記録する
(自動抽出は行わない、規模の近さは主観判断で可、目的は外れ値比較の回避)。

## 5. 判定基準(Fableが確定)

- tool_uses中央値▲20%以上 **かつ** 見落とし・手戻り(5指標合計)が
  Before相当より増加しない → **VALIDATED候補**
- tool_uses中央値の減少なし(▲20%未満) → **効果なし**
- 見落とし・手戻りが増加(5指標のいずれかが複数件発生等、Fableが
  過大と判断) → **REJECTED候補**
- 上記いずれにも該当しない(N不足・方向性が読めない等) → **評価不足**

## 6. STOP条件

- 見落とし・手戻り(5指標)の増加が観測された場合。
- Gate要件(受入条件照合・Dangling Reference確認・明示add・回帰全件1回等)
  の省略がTrial arm遂行のために必要になった場合(=Trial arm設計の欠陥)。
- Sonnetが事前指定一覧に含まれない大量Read/Grepを必要とした場合
  (=委任文の事前指定が不十分、設計不備として設計修正が先)。
- 上記いずれかに該当した場合、Trialを一旦停止し
  `USER_DECISION_REQUIRED`ではなくまずFableへ報告する(Trial設計内の
  問題であり、Production採用可否の判断ではないため)。

## 7. 計測手段

`docs/pm/tools/measure_delegation_task.py`(新規)を作成した。
`er011_pm_agent_read_audit_01.py`(無変更)の`classify_path`/
`bash_command_read_targets`/`tool_result_text_len`/`extract_mgmt_id`を
importして再利用し、分析ロジックは
`PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01`のscratchpad
`remeasure_e1_d1_01.py`の`analyze_task()`と同一定義を踏襲した(独自の
再定義はしていない)。

**taskId解決順序**(F-1恒久手順に準拠、`docs/pm/PM_GOVERNANCE.md`F-1節):
(1) `<PROJECTS_BASE>/*/subagents/agent-<taskId>.jsonl`(非0バイト)、
(2) `docs/pm/transcripts/<taskId>_recovered.jsonl`(F-1退避済み代替)。
両方とも見つからない場合はエラーを返す(推測・代替値の生成はしない)。

**動作確認(既存の復元transcript、$0)**:
- `python docs/pm/tools/measure_delegation_task.py --task-id a13715a15827192a6`
  → 正常終了(exit 0)。`tool_uses=3, cumulative_usage=97165,
  final_context_size=27685, duration_seconds=15.737`等を出力。
- `python docs/pm/tools/measure_delegation_task.py --task-id a804ec4e76562ba24`
  → 正常終了(exit 0)。`tool_uses=45, cumulative_usage=3092285,
  same_file_reread_rate=0.1057, full_read_rate_by_chars=0.4794`等を出力。
- 存在しないtaskId(`nonexistent_task_id_test`)を指定 → エラーJSONを
  出力しexit 1(推測値を出さないことを確認)。

## 参照ファイル

- `PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01_REPORT.md`(前提数値の根拠)
- `docs/pm/PM_GOVERNANCE.md`(11節E-1/D-1/G-1、F-1節、10〜13節)
- `docs/pm/tools/measure_delegation_task.py`(新規、計測手段)
- `docs/pm/tool_uses_trial_log.md`(新規、Fable記録用テンプレ)
- `docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`(新規、施策2)

## 状態

設計完了。**実行(実際の委任・Trial arm適用)はFableが別途行う**(本タスクの
スコープ外)。Production/QA/Prompt変更なし。
