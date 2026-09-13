## 管理ID
PM-CLOSEOUT-CONSOLIDATION-123

## 範囲
性質: SSOT反映+Git+read-only Closeout棚卸し。¥0、API呼び出しなし。Productionコード無編集。並行タスクなし。禁止: `git add -A`/`stash`/`amend`、既存行削除、判断語の新規付与(Fable確定済み文言を転記)。`git index.lock`があれば10秒待ち最大3回。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-123.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-123.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-123_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文)
> Closeout時には必ず、未処理USER_DECISION_REQUIRED/APPROVED_FOR_PRODUCTION未配線/未報告Trial/SSOT・DECISION_LOG・OPEN_ITEMS反映漏れを棚卸ししてください。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_FC4.md`(全文、1回)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. `OPEN_ITEMS.md`: Grep `-n` `^\| OPEN-147 \|`(範囲=次の`^\| OPEN-`行の直前または末尾)。範囲最終行の実際の末尾へ追記(閉じ`|`があればその直前、なければ行末。巨大行はPythonで安全に末尾追記可)。
2. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-122|^## 参照元`(本文追記位置=`## 参照元`直前)。索引行は`CONSOLIDATION-122`索引行の直後に同形式で1行。該当行のみRead(前後3行)。
3. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: 末尾10行のみ(`Get-Content -Tail 10`)。
4. 棚卸し(read-only、編集しない): (a) `OPEN_ITEMS.md` Grep `-n -o` `^\| OPEN-1[3-4][0-9] \|.{0,80}` と各行末尾300字(`-o` `.{0,300}$`)で、Status語が`USER_DECISION_REQUIRED`かつReconciliation注記なしのIDを列挙。(b) 同様に`APPROVED_FOR_PRODUCTION`を含み末尾300字に`PRODUCTION_WIRED`を含まない行のID(全番号帯、`^\| OPEN-[0-9]+ \|`)。(c) `Glob *_REPORT.md`で更新日2026-09-13のファイルを列挙し、各管理IDの`DECISION_LOG.md`Grep一致件数(`-c`)を確認、0件を「未記録候補」に。(d) `git status --porcelain`で`er013_*`/`FAMILY-A-*`/`EDITORIAL-*`の未追跡があれば列挙(反映漏れ候補)。

## SSOT追記文(そのまま使用、日付2026-09-13)
### OPEN_ITEMS.md OPEN-147 末尾追記
「**追記(2026-09-13、EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04、Fable Gate 1判定=`USER_DECISION_REQUIRED`、Production採用の承認ではない、別テーマ未着手)**: ユーザー判断(別テーマ不採用、同一テーマ・同一記事で長文化の仕様原因を構造診断→再設計→最小再Trial)に基づき実施。実測訂正: Trial-03のA2 550語は当時の目安450-600内、B1 744語は目安700を44語(6.3%)超過(「大幅超過」ではない)。診断(¥0): 主因はWriter Promptではなく**Layer 2/3が事前に3つの想像場面を台本として生成していたこと**(Writerが全場面を使用)、副因は場面ごとに[[IMAGINED]]枠+枠外示唆+期待/不安対比の3点セットが反復し「場面数×3点セット」が総語数をほぼ説明。対処(v4契約、新規`er013_family_c_future_writer_04.py`/`_trial_04_run.py`、既存`_01/_02/_03`無編集): 場面数を決定的に2へ削減、統合示唆段落を記事全体で1回、Scaffold入力25→14件、A2/B1別length budget(380-520/450-620)を編集Gate閾値と一致。offline: er013 67/67、全件2557/2554(失敗3は既知無関係)。再Trial(同一Ledger・Scaffold再利用、実費¥20.53、Family C枠累計¥195.03/¥300): **語数 A2 550→405(-26%)/B1 744→484(-35%)、両方目安内**。研究解説スキャン0・製品名0・枠内hedge密度0・Ledger COMPLIANT維持(Fact Safety未緩和)。新規課題: B1でFuture Framing QA v2がREVIEW_REQUIRED(統合示唆段落が2場面の間に置かれ"will"等の未hedge断定が枠外に出た、respecの副作用)。既存未解決: Fact Checker A' advisory REVIEW_REQUIRED(A2/B1、Trial-03から不変)。**Fable編集Gate所見**: 語数構造は解消したが、A2場面1が行動の列挙("It recognizes a shoe, a cable, and a bag…")に寄り、Trial-03にあった感情の起伏(thrill/irritation、"Am I being helped…")が薄れ、希望/不安の対比も末尾1文のみ→感情強度はTrial-03の2から1相当へ後退。原因仮説: 場面budget縮小時に「出来事」を優先し「感情の起伏1つ+選択1つ」の必須要素が守られていない(v4契約の必須/任意切り分けが不十分)。残る構造問題: (1)場面内の必須要素を「感情の起伏1+選択1」に固定し出来事列挙を上限化、(2)統合示唆段落の位置(場面の後)と枠外hedgingの契約化、(3)Fact Checker advisoryの扱い方針。比較artifact: `er013_output/family_c_future_trial_04/index.html`。根拠: `EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_REPORT.md`。次段階(v5契約での同一テーマ再Trial可否、費用目安¥20〜25)はユーザー判断。」
### DECISION_LOG.md 新規エントリ(`## 参照元`直前)
「## PM-CLOSEOUT-CONSOLIDATION-123(2026-09-13)
EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04: ユーザー判断「前回のFable推奨『別テーマでもう1本Trial』は採用しません。次の記事・次テーマには進まないでください。(中略)まず費用ゼロで、なぜFamily Cが長くなるのかを構造的に診断してください。(中略)『少し長いが許容』とする前提では進めません。(中略)別テーマTrialには進まないでください。」に基づき実施。結果とFable所見は上記OPEN-147追記のとおり。Gate 1: `USER_DECISION_REQUIRED`(語数は解消、感情強度の後退とB1 Framing QA新規課題により完全PASS未達)。Production配線・CURRENT_SPEC正式化・APPROVED変更なし。実費¥20.53。」
索引行: CONSOLIDATION-122索引行と同形式で1行。
### docs/pm/MODEL_ROUTING_TRIAL_LOG.md 追記
「2026-09-13 EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04: gpt-5.6-luna、¥20.53(Ledger/Scaffold再利用、A2/B1+QA)。」

## 実行コマンド全文
- `.venv\Scripts\python.exe docs/pm/tools/collect_subagent_transcripts.py --help`→表示引数で退避: taskId `ae54f53cd7a48f655 a9da50e40eb5e7128`(tasks dir=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks`、subagents dir=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents`)
- `git status --porcelain`

## Git
明示`git add`: `EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_REPORT.md`、`er013_family_c_future_writer_04.py`、`er013_family_c_future_trial_04_run.py`、(存在すれば)`er013_family_c_future_qa_04.py`・`er013_family_c_future_qa_test_04.py`、`er013_output/family_c_future_trial_04/`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-123*`、`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04*`、`docs/pm/transcripts/`追加分。コミットメッセージ`PM-CLOSEOUT-CONSOLIDATION-123: Family C長文化診断+v4再Trial(USER_DECISION_REQUIRED、¥20.53)のGit記録+OPEN-147更新+Closeout棚卸し`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。commit hash(full)を報告。

## 報告
`docs/pm/RESULT_PACKET.md`へ20行以内: commit hash(full)/push結果、SSOT追記位置、T-0検証結果、退避結果、棚卸し表(a〜d)、一覧外操作の有無。最終メッセージ6行以内。
