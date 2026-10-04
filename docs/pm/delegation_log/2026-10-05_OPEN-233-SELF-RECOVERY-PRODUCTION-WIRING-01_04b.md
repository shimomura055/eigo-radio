## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_04b = 委任_04の再開)。並行タスクなし。

## 出力方法(最重要、先に読む)

委任_04は長文を1回のWriteで書き出す途中で応答が停止した。本委任では**1回のWrite/Editで書く本文を3,500文字以下に分割**する(Writeで先頭部分→Editで末尾へ順に追記)。長文(本委任文の保存、Opus#15全文、Fable評価)はすべてこの分割方式で保存する。同じ内容を一括で再出力しない。既存の部分ファイル`docs/pm/delegation_log/2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_04.md`(2,790バイト、途中まで)は削除し、本委任のログは`..._04b.md`に保存する。

## 性質/到達上限Status/禁止事項

- 性質: (a)Opus#15レビュー全文の保存(末尾「添付」節を分割転写)、(b)Fable評価の記録、(c)¥0の数値確定(rep30 call_logの両単価再計算、現行Production 1記事あたり費用の基準算出)、(d)P6経路の¥0棚卸し、(e)**K14 Phase 1実測(有料≈¥3〜6、`gpt-6-luna`)**。**Production実装は行わない**。
- 到達上限Status: 対象仕様=`APPROVED_FOR_PRODUCTION`のまま。`PRODUCTION_WIRED`にしない。本委任後、FableはユーザーへSTOP報告(K7モデルrouting=ユーザー判断、K14はPhase 1結果次第)。
- 禁止事項: Production・Trial本体コード変更禁止(Phase 1は新規スクリプト`er052_open233_*`で実施し、runner・er051本体は変更しない)。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`は編集しない。`DECISION_LOG.md`は短いエントリのみ追記。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない(委任_04の部分ファイル削除は可)。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: ¥8(Guardrail。Phase 1≈¥3〜6)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥720.20、上限¥900、残¥179.80。有料実行前に概算を出し実測と並記。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、ユーザー正式採用に伴う恒久運用、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。記録用)。
T-2(2026-09-25、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を明示する。(本委任はTTSを伴わない。)
T-3(2026-09-26、費用上限を伴う全委任で常時有効): 費用上限は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_04b.md`。(注: 固定ブロックの一部は保存時に要約。)
