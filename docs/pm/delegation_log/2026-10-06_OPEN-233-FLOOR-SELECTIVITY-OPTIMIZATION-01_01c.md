## 管理ID

OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01(委任_01c: 既存集計から設計分析docとRESULT_PACKET_FLOORを書き出す作業のみ。委任_01/01bは分析・replayまで完了しdoc執筆段階でAPI側中断)。並行タスクなし。**git操作禁止、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/REPORT/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。** 書き込み先: `docs/pm/design_open233_floor_selectivity_01.md`(新規)、`docs/pm/RESULT_PACKET_FLOOR.md`(新規)、`docs/pm/delegation_log/`(委任文保存)のみ。scriptの再実行・修正は不要(既存出力をそのまま使う)。

作業の進め方(出力を小分けにする): docは§ごとに分けてWrite→Edit追記で積み上げる(1回の書き出しを短くする)。思考・説明は最小限にし、既存mdの数値・表を転記・整形することを優先する。新たな長文分析はしない。

**T-0の保存方法**: 受領した本委任文を要約せず「## 管理ID」から末尾まで全見出し込みで `docs/pm/delegation_log/2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01c.md` へそのまま書き出す。

## 性質/到達上限Status/禁止事項

- 性質: 設計分析の文書化(¥0、read-only)。到達上限: **USER_DECISION_REQUIRED または DESIGN_READY_FOR_REVIEW**(VALIDATED不可)。最終Status・案の採否はFable/ユーザー。
- 禁止: コード変更/Prompt変更/Production変更/有料API/gold・Safety-critical定義変更/新Safety原則の「決定」記述/実装・Trial開始。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **条件A該当(決定論/LLMの役割分担変更、実装前)**。レビュー依頼はFableが本docに対して別途行う。
- STOP条件(ユーザー指定): 正当6件を守りながら半分以下へ減らす見込みが立たない/新Safety原則追加が必要/gold定義変更が必要/有料Trialが必要/Production仕様変更が必要 →該当は§9に事実として記す。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> 管理ID：OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01。目的: 後段の機械Safety判定が、現在は精密検査としての選別精度が低すぎる。直近E2Eでは、機械判定が35件を強制的に重大扱いしたが、事後評価では、正当な重大：6件／不要：24件／判断不能：5件だった。
> 今回やること: まず¥0のread-only分析を行う。35件すべてについて、機械判定がなぜ発火したかを分類する。最低限、主体／数字／否定／比較／因果／時期／その他ごとに、発火件数／正当重大だった件数／不要だった件数／判断不能だった件数／後段AIの判定（重大 / 軽微 / 問題なし）／誤爆の典型パターンを整理する。
> 検討してほしいこと: 機械Safetyを完全撤廃する前に、ルールを精密化するだけで大幅に誤爆を減らせるかを検討する。目標感：現在35件の強制重大化を、少なくとも半分以下、できれば1/3程度（約12件以下）まで減らせる見込みがあるか。ただし、単に閾値を緩めるのではなく、正当6件をどこまで維持できるか／どの条件を削る／限定する／追加確認へ回すべきか／「検出したら即重大」ではなく「追加確認トリガー」に変えるべき条件は何か／決定論で残す価値が高い条件は何か、を具体的に設計する。
> 特に確認すること: 「Checkerが多く候補を出したから誤爆した」だけで終わらせず、「後段機械Safety単体として、なぜ24/35が不要判定になったのか」を分析すること。
> 出してほしい設計案: 1. 現行機械Safetyを条件精緻化して維持 2. 一部カテゴリだけ強制重大を維持し、他はAI追加確認へ 3. 機械Safetyは重大判定をせず、追加確認トリガーだけにする 4. その他。各案について、Safety／不要Rewrite削減／コスト／実装複雑性／運用安定性／想定強制重大件数／正当6件の維持見込み、を比較する。
> 判断基準: 半分以下、できれば1/3程度まで減らせる合理的な見込みがあり、正当重大を大きく落とさない案があるなら、次の限定Trial候補とする。そこまで改善できる見込みがないなら、Checker（AI＋機械） → 後段AI → 軽微だけ独立追加確認 の別設計へ進む材料として報告する。
> 到達可能Status: USER_DECISION_REQUIRED または DESIGN_READY_FOR_REVIEW まで。Production変更は禁止。
> Closeout: 35件のカテゴリ別内訳／誤爆の主因／半分以下／1/3まで減らせる見込み／最も有望な設計案／Safetyへの影響／次の限定Trial案と概算費用／unresolved事項／APPROVED_FOR_PRODUCTIONだが未配線の項目への影響有無／Dangling Reference有無、を整理して報告してください。

## KPI provenance欄

- 35件とラベル(不要24/正当6/判断不能5): reuse(RCA §6の【推測】ラベル、Sonnet判定・Fable/ユーザー未確認)。
- floor発火理由・LLM判定・S1: frozen(E2E保存出力、`floor_fire_analysis_01.json/.md`)。
- 案別件数: replay推計(in-sample、¥0)。LLM追加確認の結果は未測定。
- E2E自己確認: No。

## Opus台帳更新

参照のみ: Grep `floor|FLOOR|deterministic` in `docs/pm/OPUS_FINDINGS_LEDGER.md` →関連IDを§3の各案に併記(台帳編集なし)。

## 委任_01bまでの確定事実(転記用)

- 35件=不要24/正当6/判断不能5。LLM判定: ACCEPTABLE 25/QUALITY 6/BLOCKING 4。
- 不要24件の原因: (i)Stage 1フラグ不整合17、(ii)重大性判定欠如6、(iv)Tier0語彙1、(iii)0。
- 案別replay(強制重大件数/正当6の行き先): 案0現行 35/6件強制重大。案1条件精緻化 14/6件強制重大。案2確定のみ強制+他は追加確認 8/追加確認2・強制重大4。案3トリガーのみ 0/追加確認6。案4 floor撤廃+既存S1 4/追加確認(S1)2・強制重大4。案5段階化 14/6件強制重大。
- 実装: `apply_floor`(runner L2432)は5つの`changed_*`フラグのいずれかtrueでLLM判定に関係なくBLOCKING上書き、重大性判定なし。`FLOOR_VERIFY_MODE=time_only`では`changed_time`のみ追加確認、他4フラグは`FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS`で決定論。これは委任_58〜61でユーザーが決めた`APPROVED_FOR_PRODUCTION`の線引き(PRODUCTION_WIRED未達)。委任_58のF1「CLEARED自動解放」は廃止済み。因果floor語彙の目録拡張(`CAUSAL_FLOOR_VOCAB=inventory`)はREJECTED、known6のみ有効(`CAUSAL_FLOOR`既定False)。`FLOOR_FLAGS`定義はrunner L779。

## 事前指定Read一覧

1. `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.md`: 全文(カテゴリ別表・35件一覧・案別replay・典型例。docへ転記する正本)。
2. `docs/pm/rca_open233_e2e_neg7_human_review_01.md`: L61-L73(是正案C/D/Gの既存記述、A/B/C分類用)。
3. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `重大誤解原則` →§0の原則文(1段落のみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- A/B/C分類: Grep `floor_verify|FLOOR_VERIFY_MODE|因果floor|CAUSAL_FLOOR` in `DECISION_LOG.md` →見出し行のみ(エントリIDと結論の1行)。Grep `floor` in `OPEN_ITEMS.md` →該当行の行頭ID・Statusのみ。
- APPROVED未配線: Grep `APPROVED_FOR_PRODUCTION` in `OPEN_ITEMS.md` →行頭ID・要約のみ列挙。floor線引き(委任_55/58〜61)を特定。
- Dangling Reference: 各案が参照する名前(`apply_floor`/`FLOOR_VERIFY_MODE`/`FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS`/`FLOOR_FLAGS`/`CAUSAL_FLOOR`/S1関数名)をrunnerでGrepし実在を確認(行番号を§8に記す)。
- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01c.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01c.md_check.json`
2. `docs/pm/design_open233_floor_selectivity_01.md` を§単位で書く: §0前提(provenance・ラベルの性質)/§1 35件カテゴリ別内訳表(主体・数字・否定・比較・因果・時期・その他×発火・正当・不要・判断不能・LLM判定分布)+典型パターン逐語例/§2 誤爆主因((i)〜(iv)件数、「後段機械Safety単体」としての原因=重大性判定の不在・フラグ無検証上書き、Checker候補過多とは独立である根拠)/§3 案0〜5比較表(Safety・不要Rewrite削減・コスト・実装複雑性・運用安定性・想定強制重大件数・正当6件維持見込み・A/B/C分類・条件A該当・関連Opus台帳ID)+各案の条件の具体(どのフラグを削る/限定/追加確認へ、決定論で残す価値が高い条件)/§4 半減・1/3達成見込み(案別、in-sample注意)/§5 最有望案(Sonnet所見)と限定Trial案(対象: E2E保存9 run+段階A保存データでの¥0 replay→必要なら有料fresh、費用概算、測定項目案[新KPIではない]、STOP条件案)/§6 unresolved(判断不能5件の扱い、ラベルのFable/ユーザー確認、out-of-sample未検証)/§7 APPROVED未配線項目への影響(floor線引きAPPROVED_FOR_PRODUCTIONとの関係=案2〜4は線引き変更に当たりユーザー承認要)/§8 Dangling Reference確認(名前と行番号)/§9 STOP条件該当判定(事実のみ)。
3. `docs/pm/RESULT_PACKET_FLOOR.md`: 報告16項目(1 T-0/2 内訳表/3 主因/4 単体精度問題/5 比較表/6 達成見込み/7 最有望案・Trial案・費用/8 Safety影響/9 A-B-C/10 APPROVED未配線影響/11 Dangling/12 STOP判定/13 unresolved/14 一覧外Read/15 SSOT追記文案[OPEN_ITEMS新規行案(POST_USER_VALIDATION)・REPORT_LEDGER 1行案・DECISION_LOG新エントリ案・REPORT §案]/16 成果物一覧)。docの要約で可(重複記述は最小)。
4. git操作なし。

## SSOT追記文

SSOTは編集しない。文案のみRESULT_PACKET_FLOORの15へ。

## Git

git操作なし。SSOT編集権なし。成果物一覧(後続のgit add対象: design doc、RESULT_PACKET_FLOORは対象外、offline_01配下3ファイル、delegation_log 01/01b/01c)をRESULT_PACKET_FLOORに列挙。

## 報告(RESULT_PACKET項目)

上記3.の16項目。所見は【確認】/【推測】ラベル付き。最終分類(USER_DECISION_REQUIRED/DESIGN_READY_FOR_REVIEW)はしない。
