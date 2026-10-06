## 管理ID

OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01(委任_01b: 委任_01がAPI側エラーで途中終了したため続きから再開。¥0 read-only分析)。前回までに `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.py` と出力 `floor_fire_analysis_01.json` / `.md` が作成済み(内容の妥当性は本委任で確認)。未作成: 設計分析doc・RESULT_PACKET_FLOOR・委任文保存。並行タスクなし(RECLASSIFY-02は完了)。**ただし本委任はgit操作一切禁止、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/REPORT/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない**(SSOT反映・commitはOpusレビュー後にFableが別委任する)。書き込み先: `docs/pm/design_open233_floor_selectivity_01.md`(新規)、`er052_output/open233_floor_selectivity_offline_01/`(既存、追記・修正可)、`docs/pm/RESULT_PACKET_FLOOR.md`(新規)、`docs/pm/delegation_log/`(委任文保存)。

**T-0の保存方法(重要、過去3回FAIL)**: 受領した本委任文を要約せず、「## 管理ID」から末尾まで全セクション見出しを含む全文をそのまま `docs/pm/delegation_log/2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01b.md` へ書き出すこと。

## 性質/到達上限Status/禁止事項

- 性質: 設計分析(¥0、read-only)。到達上限: **USER_DECISION_REQUIRED または DESIGN_READY_FOR_REVIEW**(VALIDATED不可)。最終Status・設計案の採否はFable/ユーザーが決める。
- 禁止: コード変更(runner・checker・Stage 2・floor実装)/Prompt変更/Production変更/有料Trial・有料API/gold・Safety-critical定義の変更/新しいSafety原則の追加を「決定」として書くこと(提案はユーザー判断事項として明示)/勝手な実装・Trial開始。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **条件A該当(決定論処理とLLM処理の役割分担の変更=例(6)、実装前)**。本委任は分析・設計案作成まで。Opusレビューは本委任成果物に対してFableが別途依頼する。
- STOP条件(ユーザー指定): 正当6件を守りながら半分以下へ減らす見込みが立たない/新しいSafety原則の追加が必要/gold定義変更が必要/有料Trialが必要/Production仕様変更が必要 →該当したら「STOP該当」として事実を記し、比較表は完成させて報告(実装・Trialへ進まない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で(全文)保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> 管理ID：OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01
> 目的: 後段の機械Safety判定が、現在は精密検査としての選別精度が低すぎる。直近E2Eでは、機械判定が35件を強制的に重大扱いしたが、事後評価では、正当な重大：6件／不要：24件／判断不能：5件だった。このままでは不要Rewrite・品質劣化・追加コストを大量に発生させるため、まず機械Safety判定そのものを最適化できる余地があるかを調べる。
> 今回やること: まず¥0のread-only分析を行う。コード変更・Prompt変更・Production変更・有料Trialはまだ禁止。35件すべてについて、機械判定がなぜ発火したかを分類する。最低限、主体／数字／否定／比較／因果／時期／その他ごとに、発火件数／正当重大だった件数／不要だった件数／判断不能だった件数／後段AIの判定（重大 / 軽微 / 問題なし）／誤爆の典型パターンを整理する。
> 検討してほしいこと: 機械Safetyを完全撤廃する前に、ルールを精密化するだけで大幅に誤爆を減らせるかを検討する。目標感：現在35件の強制重大化を、少なくとも半分以下、できれば1/3程度（約12件以下）まで減らせる見込みがあるか。ただし、単に閾値を緩めるのではなく、正当6件をどこまで維持できるか／どの条件を削る／限定する／追加確認へ回すべきか／「検出したら即重大」ではなく「追加確認トリガー」に変えるべき条件は何か／決定論で残す価値が高い条件は何か、を具体的に設計する。
> 特に確認すること: 今回の問題は、Checker側が広く拾うこととは別。後段は精密判定の役割なのに、単語や形式的条件だけで重大へ上書きし、精度が低いこと自体が問題。したがって、「Checkerが多く候補を出したから誤爆した」だけで終わらせず、「後段機械Safety単体として、なぜ24/35が不要判定になったのか」を分析すること。
> 出してほしい設計案: 少なくとも以下を比較する。1. 現行機械Safetyを条件精緻化して維持 2. 一部カテゴリだけ強制重大を維持し、他はAI追加確認へ 3. 機械Safetyは重大判定をせず、追加確認トリガーだけにする 4. その他、より良い案があれば提示。各案について、Safety／不要Rewrite削減／コスト／実装複雑性／運用安定性／想定強制重大件数／正当6件の維持見込み、を比較する。
> 判断基準: 半分以下、できれば1/3程度まで減らせる合理的な見込みがあり、正当重大を大きく落とさない案があるなら、次の限定Trial候補とする。そこまで改善できる見込みがないなら、無理に機械Safetyを延命せず、Checker（AI＋機械） → 後段AI → 軽微だけ独立追加確認 の別設計へ進む材料として報告する。
> 現在Status / 到達可能Status: 現在は設計分析段階。今回到達してよいのは USER_DECISION_REQUIRED または DESIGN_READY_FOR_REVIEW まで。まだ VALIDATED にはしない。Production変更は禁止。
> STOP条件: 正当6件を守りながら半分以下へ減らす見込みが立たない／新しいSafety原則の追加が必要／gold定義変更が必要／有料Trialが必要／Production仕様変更が必要。勝手に実装・Trialへ進まないこと。
> Closeout: 最後に、35件のカテゴリ別内訳／誤爆の主因／半分以下／1/3まで減らせる見込み／最も有望な設計案／Safetyへの影響／次の限定Trial案と概算費用／unresolved事項／APPROVED_FOR_PRODUCTIONだが未配線の項目への影響有無／Dangling Reference有無、を整理して報告してください。

## KPI provenance欄

- 35件の母集団・正当/不要/判断不能ラベル: **reuse**(委任_22 RCA `docs/pm/rca_open233_e2e_neg7_human_review_01.md` §6の【推測】ラベル=Sonnet判定、Fable/ユーザー未確認。所与として用い、再ラベル意見は別欄)。
- floor発火理由・LLM判定・S1結果: **frozen**(E2E保存run json、`e2e_neg7_rca_extract_01.json`、および既存出力`floor_fire_analysis_01.json`)。
- 設計案ごとの想定強制重大件数: **replay推計**(¥0。LLM追加確認が必要な案は「追加確認へ回る件数」として示し、結果は未測定と明記)。
- E2E自己確認: No。

## Opus台帳更新

参照のみ(台帳編集なし): Grep `floor|FLOOR|deterministic` in `docs/pm/OPUS_FINDINGS_LEDGER.md` →floor関連の既存指摘IDを列挙し、各設計案との関係(再利用/矛盾)をRESULT_PACKET_FLOORに記す。

## 事前指定Read一覧

1. `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.md`: 全文(前回の集計結果)。`floor_fire_analysis_01.json`: 構造確認(Grep `"category"|"label"|"floor_reason"` で件数整合を確認)。`floor_fire_analysis_01.py`: Grep `def |CATEGORY|MAP` →カテゴリ対応表とラベル対応表の範囲のみ(35件・正当6/不要24/判断不能5と整合しているか検算。不整合なら修正して再実行)。
2. `docs/pm/rca_open233_e2e_neg7_human_review_01.md`: L6-L12、L27-L31、L43-L57、L61-L73。
3. `er052_open233_self_recovery_flow_runner_01.py`: Grep `deterministic_floor|floor_reason|FLOOR_VERIFY_MODE|changed_actor|changed_number|changed_negation|changed_comparison|changed_causality|changed_time|floor_verify|tier0` →各ヒット±30行(floor発火条件・カテゴリ・verifyモード・S1との関係・BLOCKING上書き実装)。全文Read禁止。
4. `docs/pm/design_open233_kpi_recovery_02.md`: Grep `floor|D\*′|因果|hold-out|誤停止` →該当範囲±20行。
5. `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_04_causal_floor.py`: Grep `def |VOCAB|PATTERN` →構造のみ。
6. `er052_output/open233_floor_alignment_offline_01/replay_01.py`: L1-L60、L280-L300。
7. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `§0|重大誤解原則` →§0。
8. Stage 1の`changed_*`フラグ生成側: Grep `changed_actor|changed_negation` in `er052_output/open233_kpi_recovery_02_offline_01/`配下のcoverage_checker(ファイル名はGrepで特定)→フラグ付与条件の範囲のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Existing Spec / Prior Trial Check(PM_GOVERNANCE 21節、A/B/C分類): Grep `floor` in `OPEN_ITEMS.md`(該当行のみ)、`CURRENT_SPEC.md`(Grep `floor|deterministic floor|FLOOR_VERIFY` →該当行±5行)、`DECISION_LOG.md`(Grep `floor_verify|FLOOR_VERIFY_MODE|因果floor` →該当エントリの見出し行と結論行のみ)。→各設計案をA/B/Cに分類。特に「floor_verifyの時期以外への拡張(RCA案C)」「因果floor語彙hold-out≤2%不達」「線引き(委任_55 APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED未達)」との関係を明記。
- APPROVED_FOR_PRODUCTION未配線項目: Grep `APPROVED_FOR_PRODUCTION` in `OPEN_ITEMS.md` →ID・要約のみ列挙し、floor変更が影響するものを特定。
- Dangling Reference: 設計案が参照する関数名・フラグ名・設定名が実装に実在するかGrepで確認。
- 追記位置: 新規ファイルのみ(SSOTは編集しない)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_01b.md_check.json`
2. 既存集計の検算・不足分の追加(必要時のみscript修正して再実行): `.venv\Scripts\python.exe er052_output\open233_floor_selectivity_offline_01\floor_fire_analysis_01.py --extract er052_output\open233_kpi_recovery_02_offline_01\e2e_neg7_rca_extract_01.json --runs-dir er052_output\open233_e2e_acceptance_01\runs --out-dir er052_output\open233_floor_selectivity_offline_01`
   必須出力: 35件それぞれ(run/cycle/claim_text/fact_id/floor_reason/カテゴリ[主体・数字・否定・比較・因果・時期・その他、対応表明記]/Stage 1 changed_*フラグ/Stage 2 LLM materiality→重大・軽微・問題なし対応/S1有無・結果/floor_verify通過有無/RCAラベル/Rewrite結果)、カテゴリ別集計表(発火/正当/不要/判断不能/LLM判定分布/典型パターン逐語2〜3例)、不要24件の原因割当((i)Stage 1フラグ自体の誤り/(ii)フラグは正しいが重大性判定を欠く/(iii)LLM ACCEPTABLEをverify非経由で上書き/(iv)その他)、設計案1〜4(+5)の¥0 replay(各案で「強制重大のまま/追加確認へ/非重大化」の件数と、正当6件・判断不能5件の行き先)。
3. 設計分析doc `docs/pm/design_open233_floor_selectivity_01.md`: §0前提(provenance・ラベルの性質)、§1 35件内訳表、§2 誤爆主因(「後段機械Safety単体」としての原因、Checker候補過多とは独立の要因)、§3 案1〜4(+5)比較表(Safety/不要Rewrite削減/コスト/実装複雑性/運用安定性/想定強制重大件数/正当6件維持見込み/A-B-C分類/条件A該当)、§4 半減・1/3達成見込みの根拠、§5 最有望案と限定Trial案(対象run・費用概算[¥0 replay/有料の別]・測定項目案[新KPIではない]・STOP条件案)、§6 unresolved、§7 APPROVED未配線項目への影響、§8 Dangling Reference確認結果、§9 STOP条件該当判定(事実)。
4. git操作なし。

## SSOT追記文

SSOTは編集しない。文案のみ`docs/pm/RESULT_PACKET_FLOOR.md`へ: OPEN_ITEMS新規行案(POST_USER_VALIDATION区分、Status=DESIGN_READY_FOR_REVIEW or USER_DECISION_REQUIRED)、REPORT_LEDGER 1行案、DECISION_LOG新エントリ案、REPORT §(番号未定)追加文案。

## Git

git操作なし。SSOT編集権なし。成果物一覧(後続のgit add対象)をRESULT_PACKET_FLOORに列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FLOOR.md`へ: 1. T-0結果。2. 35件カテゴリ別内訳表。3. 誤爆の主因((i)〜(iv)件数と典型パターン)。4. 「後段機械Safety単体」としての精度問題の整理。5. 設計案1〜4(+5)比較表。6. 半分以下/1/3達成見込み(案別の想定強制重大件数と正当6件維持見込み、根拠)。7. 最有望案(Sonnet所見、決定ではない)と限定Trial案・概算費用。8. Safetyへの影響(重大誤解原則との整合、gold・Safety-critical定義への影響なしの確認)。9. Existing Spec / Prior Trial Check(A/B/C)。10. APPROVED_FOR_PRODUCTION未配線項目への影響有無。11. Dangling Reference有無。12. STOP条件該当判定(事実)。13. unresolved。14. 一覧外Read理由。15. SSOT追記文案。16. 成果物一覧(絶対パス)。
