## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_03)。並行タスクなし(委任_01b/_01c/_02は完了)。

## 性質/到達上限Status/禁止事項

- 性質: ¥0・調査と文書のみ(コード変更なし)。(a)委任_02のGap棚卸し文書`docs/pm/production_wiring_gap_open233_01.md`と委任_02ログをcommit/push、(b)委任_02が挙げた重要発見のうち配線判断を左右する2点を**事実確認**(Trial Stage 1 Checkerと Production vfl01 Checkerの差分、Trialモデル`gpt-6-luna`とProduction routing `gpt-5.6-luna`の差)、(c)構造的競合K1/K4/K8と関連するユーザー決定のSSOT根拠をGrepで確定、(d)Opus#15(条件A: 新しい処理フローのProduction化、条件C: Production採用提案)向けcontext packet作成、(e)REPORT §63の積み残し2点(Opus#8〜#14各1行、rep29費用の表記統一)。
- 到達上限Status: 文書のみ。対象仕様=`APPROVED_FOR_PRODUCTION`のまま。`PRODUCTION_WIRED`にしない。
- Fableの前提(packetに記載): ユーザー決定のSTOP条件「Trial最終構成とProduction正式経路に構造的な競合がある」「APPROVED仕様をProduction初回pathへ安全に入れられない」「retry/fallbackとの仕様矛盾」に該当しうる候補(K1/K4/K8、Checker・モデル差)があるため、Fableは**Opus#15レビュー→Fable評価の後、Production実装に入らずユーザーへSTOP報告(USER_DECISION_REQUIRED候補)**する方針。Opusには「競合が本物か、設計で吸収できるか、ユーザー判断が必要か」の切り分けを求める。SSOT整備(DRC①: CURRENT_SPECへの正式仕様化)は自律で進めてよい範囲だが、競合の解決方針が決まる前に書くと手戻りになるため、本委任では着手しない。
- **T-0厳守**: 委任文は**全文そのまま保存**(要約・固定ブロックの省略禁止)。長い場合はWrite後にEditで続きを追記して複数回に分ける。委任_01/_01b/_02で要点版保存が続いた(T-0 FAIL)。
- 禁止事項: コード変更禁止(Production・Trial)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。`OPEN_ITEMS.md`は該当1行の進捗欄のみ。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない(委任_02の2ファイルと本委任の成果物のみadd)。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: ¥0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_03.md`。

## ユーザー指示(原文、該当部分。全文はDECISION_LOG 2026-10-05エントリ)

````
Production Wiring必須範囲
Trial runnerだけを移植して完了としてはならない。
…
Trial専用er052_*をProductionから暗黙参照する構造は禁止。
Production正式実装として整理すること。
…
Runtime evidence
静的コード変更やunit testだけではPRODUCTION_WIREDとしない。
最低限、Production正式pathで実際に発火させ、
- actual model_id
- routing
…
受入条件
- Trial最終rep30の採用仕様とProduction挙動が一致
…
STOP条件
以下の場合はSTOPして報告。
- Trial最終構成とProduction正式経路に構造的な競合がある
- APPROVED仕様をProduction初回pathへ安全に入れられない
- retry/fallbackとの仕様矛盾
- 新しいProduct判断が必要
…
通常の実装バグ・テスト修正・SSOT整合はユーザー判断にせず自律的に解決すること。
````

## 作業

1. **commit/push(先に)**: `docs/pm/production_wiring_gap_open233_01.md`、委任_02ログ+check.json。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: rep30有効構成とProduction実装の1対1対応表(Gap棚卸し: A3/B5/C16、構造的競合候補K1〜K13、配線方針案)(委任_02、¥0)`
2. **事実確認(¥0、文書`docs/pm/production_wiring_gap_open233_01.md`に§6「追加確認(委任_03)」として追記)**:
   - (a) Trial Stage 1 Checker(runnerが使う`er051*`のChecker prompt/schema。どの関数・定数か特定)と Production `er003_v1_en_direct_vfl_01_generate.py`のChecker(`build_prior_issues_instruction`周辺のprompt・schema)の**差分**: 同一/コピー後に乖離/別物、を逐語比較(diffコマンドで文字列比較し、差分行数と差分の性質[語句・schemaフィールド・判定規則]を記す)。Trialで「Checker本体Prompt・Schema・判定方法は変更しない」とされてきた前提が、Production vfl01 Checkerに対して成立しているか。
   - (b) モデル: runner `MODEL`定数と、Production `routing.WRITER_MODEL`・Checker/Rewrite/Recheckで実際に使われるmodel id(Grep `model=|MODEL|routing\.`で各経路の該当行)。Model Routing Contractの該当SSOT(Grep `Model Routing Contract|routing contract` in CURRENT_SPEC/PM_GOVERNANCE)。rep30のVALIDATEDが`gpt-6-luna`でのみ成立している事実と、Productionで同一モデルを使う/使わない場合の整理(価格: luna $0.10/0.01/0.50 per 1M; `gpt-5.6-luna`の価格はコード/SSOT上の記載があれば引用、なければ「未確認」)。
   - (c) K8: 「Checker出力形式変更は不採用」のユーザー決定(2026-10-03)をDECISION_LOGからGrepで特定し、該当文を引用(短く)。`STAGE2_SIBLING_LOCATIONS_CYCLE1`がChecker schema変更(`same_fact_id_locations`)を本当に必要とするか、runnerでは`expand_same_fact_id_locations`(L1518付近)が**Checker出力ではなく後段の決定論処理**で兄弟箇所を得ているのではないかをコードで確認(これが後段処理ならK8は競合でない)。
   - (d) K1: Production `MAX_REWRITE_CYCLES=3`(無条件)とTrial `MAX_CYCLES=2`+条件付きcycle 3+判定専用cycleの差。rep30の費用・Human Review 0はTrial定義で得られた点を明記。
   - (e) K4: Family X(P1/P2)の「1回だけ全文再生成→なおMAJORなら`RuntimeError` STOP」とladder④(段落Rewrite)・T(最終手段)の関係。該当コード行を引用。
   - (f) `OPEN-233-A1-PROD`の必須確認項目「解放claimを2-of-2降格の対象から除外」が`STAGE2_NORMAL_TWO_OF_TWO=OFF`で実質無効になる件: 該当行を引用し、読替案(S1で代替)を書く。
3. **Opus#15 packet** `docs/pm/opus_packet_open233_production_wiring_01.md`(雛形(a)〜(g)): (a)管理ID・性質・到達上限・禁止事項・ユーザー決定要旨、(b)ユーザー指示原文(上記+完了条件1〜12、DECISION_LOG参照)、(c)Gap文書の要点(§1正本、§2 P1〜P6、§3対応表の集計、§4推奨方針・K1〜K13、§6追加確認)とパス・行番号、(d)Fableの前提(上記)と、Fableが特に判定を求める論点: ①K1/K4/K8・Checker差・モデル差のそれぞれが「本物の構造的競合(ユーザー判断必要)」「設計で吸収可能(自律)」「競合でない」のどれか ②新module+薄いアダプタ構成と`er010`置換/併存の妥当性、6経路(P1〜P6)・Local Rewriteループ3重複への配線で「初回path・retry・fallback・regenerationの整合」を保つ最も単純な構造 ③Production Gate(MAJOR→STOP)からmateriality降格(V7b+S1+floor)へ替えることのSafety(「AI1回で重大→問題なし」禁止の維持) ④許可リスト4理由への出口集約と既存6出口の対応 ⑤Trial Checker/モデルで検証された結果がProduction Checker/モデルへ移る際の妥当性担保(runtime evidenceで何を見れば「一致」と言えるか、差がある場合の最小の追加検証) ⑥配線順序と部分配線の扱い(rep30は構成全体で検証、部分配線は`PRODUCTION_WIRED`にしない) ⑦runtime evidence最小セット(既存記事+fixture、8〜10 run、¥10〜20)の十分性 ⑧SSOT整備(DRC①で0件)の最小範囲、(e)配線しない項目一覧、(f)Opus出力形式(結論→論点別判定[競合/吸収/非競合、採用/不採用/修正採用]→Safety hole→ユーザー判断が必要な点→STOP条件該当有無)、(g)`docs/pm/OPUS_INDEPENDENT_REVIEW_BLOCK.md`逐語貼付。
4. REPORT §63: Opus#8〜#14の指摘と対応を各1行(出典: `docs/pm/opus_l2_review_open233_*_{08..14}.md`の結論部と設計書の採否小節をGrepし、1行ずつ)、rep29費用「run合計¥24.43/予算state¥24.667(Phase累計は予算state基準)」に統一注記。
5. `OPEN_ITEMS.md`該当行進捗「委任_03: Gap文書commit、Checker/モデル差・K1/K4/K8事実確認、Opus#15 packet。次: Opus#15→Fable評価→ユーザーへSTOP報告(構造的競合候補)」。`docs/pm/REPORT_LEDGER.md`1行。`docs/pm/ACTIVE_TASK.md`(addしない)。
6. 2回目commit/push(明示add: Gap文書、packet、REPORT、OPEN_ITEMS、REPORT_LEDGER、委任_03ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: Trial/Production Checker差・モデル差・K1/K4/K8の事実確認、Opus#15向けpacket、REPORT §63追補(委任_03、¥0)`

## 事前指定Read一覧

- `docs/pm/production_wiring_gap_open233_01.md` §1・§2・§4-3(K1〜K13)・§5(範囲Read)。
- runner: Grep `^MODEL|import er05|from er05|expand_same_fact_id_locations|same_fact_id_locations` → 該当範囲。
- `er051*`: Grep `CHECKER|checker|schema|prompt` → Checker prompt定数/関数の範囲。`er003_v1_en_direct_vfl_01_generate.py`: Grep `build_prior_issues_instruction|CHECKER|schema|WRITER_MODEL|routing` → 範囲。
- Production P1/P2: Gap文書§2が示すファイル・行(RuntimeError STOP箇所、MAX_REWRITE_CYCLES)。
- `DECISION_LOG.md`: Grep `出力形式|Checker出力|schema` の2026-10-03付近のみ(全文Read禁止)。
- `docs/pm/opus_l2_review_open233_*_{08..14}.md`: 各ファイルの「## 結論」節のみ。
- `docs/pm/opus_packet_open233_kpi_recovery_02_04.md`(雛形)、`docs/pm/OPUS_INDEPENDENT_REVIEW_BLOCK.md`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Gap文書: 末尾に§6追加。REPORT: Grep `^## §63` → 節内の「Opus#8〜#14」「rep29」該当行を更新。`OPEN_ITEMS.md`: Grep `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01` → 該当行の進捗欄のみ。`REPORT_LEDGER.md`: 末尾1行。

## 実行コマンド全文

T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_03.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_03.md_check.json
差分比較: Checker prompt文字列を一時ファイル(スクラッチ)に書き出して`diff`または`difflib`で比較(スクリプトはスクラッチに置く)。
Git: `git status --porcelain` → 明示`git add` → commit → `git push origin main` → `git log --oneline -1`。

## 報告(RESULT_PACKET項目)

(1)結論10行以内(Checker差の性質、モデル差、K8が競合か否か、K1/K4の整理、packet準備完了か)、(2)§6の要点(確認/推測の区別)、(3)packetパス、(4)REPORT §63追補内容、(5)T-0(全文保存したか・PASS/FAIL)・commit×2・push・raw URL(Gap文書・packet)、一覧外Read、(6)Fableへの論点。
