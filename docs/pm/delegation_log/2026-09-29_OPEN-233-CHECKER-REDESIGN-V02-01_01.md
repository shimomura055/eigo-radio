## 管理ID

OPEN-233-CHECKER-REDESIGN-V02-01(Ledger / Deviation Checker 根本再設計案 v0.2 の作成=問題構造の再整理・deterministic rule 候補・過剰 BLOCK 低減設計・Trial 案、委任 _01)。**設計のみ(read-only+設計書作成)**。一時ファイル `docs/pm/ACTIVE_TASK_C233.md` / `docs/pm/RESULT_PACKET_C233.md`(commitしない)。並行: 別 Sonnet 1 件(GPT-6 Trial Closeout、SSOT 4 点+REPORT_LEDGER+`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` を編集中)→ **SSOT・REPORT_LEDGER・同 REPORT に触れない(Read は可)**。本タスク出力先: `docs/pm/design_checker_redesign_v02_01.md`(新規)、`OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`(新規、設計書へのポインタ+要約)、delegation_log。**Production code・Checker Prompt・severity・routing・Ledger schema の変更禁止、Production Trial 開始禁止、API 呼び出し禁止(¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。

## 再設計の目的(ユーザー定義、逐語)

「必要なものは確実に止め、不要なものは止めず、しかも安定して判定する Checker へ再設計する。」「過剰品質によって Production の生産性が失われることは許容しない。」eigo-radio は英語学習サービス。ニュースメディア級の過剰 Fact 厳密性で retry 多発・STOP 多発・Human Review 多発・記事完成率低下・latency 増大・cost 増大を招く設計は避ける。逆に、明確な Fact 反転/actor 取り違え/数字・scope の重大変更/否定反転/時系列反転/comparison 方向反転/根拠のない重大 Fact/ニュース理解を実質的に変える因果改変、等の重大事故は確実に止める。**Deviation を検出したことと Production を止めることを分離**。単純に判定を緩くするのではない。**notes_for_writer を丸ごと soft 化する案は採用しない**(Hormuz 12/12 が factual constraint)。必要なら factual_constraint / writer_guidance の分離を検討(schema 変更は Trial 候補、Production 変更しない)。「モデルを強くするだけでは解決しなかった」(GPT-6 Trial で不要 BLOCK 率 75%=75%)。

## 入力(全文 Read 可)

- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(現行仕様・hard/soft・A/B 事例・4 区分・QCD・Hormuz trace・§8 材料)
- `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`+`docs/pm/review_ledger_deviation_redesign_01_part_a.md`/`_part_b.md`(ChatGPT v0.1 素案への Claude レビュー: 実装整合・deterministic 化可能範囲・notes 分類・免罪符化リスク・Trial 設計)
- `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` §Phase B(Step 1/actor n=5/Step 2/Step 3)+`er050_output/gpt6_checker_comparison_trial_01/summary_*.json`(run 単位の flag/severity/origin の揺れを直接読む)
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE|_apply_deviation_post_hoc_validation|DEVIATION_JSON_SCHEMA|FACT_LEDGER_JSON_SCHEMA|notes_for_writer|auto_downgraded|def run_deviation_check`(post-hoc の現行ロジック逐語)
- `er012_e_family_entertainment_two_level_runner_01.py:262-500`、`er019_family_x_ja_writer_o_r1_r2_01.py`(must-fix・案B・STOP 経路)
- `OPEN_ITEMS.md` Grep `OPEN-233`、`CURRENT_SPEC.md` Grep `fail-closed|安全≠成功|Deviation|Human Review Lock`

## 出力: `docs/pm/design_checker_redesign_v02_01.md`(章立て固定)

### 1. 問題構造の再整理(Evidence 付き、各事例に REPORT/json パス)
A. 過剰 BLOCK(Hormuz B-1/B-2/B-3/B-4、changed_causality、context qualifier 無視、Ledger 外だが合理的な一般化)/B. 重大見逃し(`changed_actor=true` なのに MINOR[現行 5/5]、A-1 時制 drift、category 検出そのものの MISS[GPT-6 の actor flag=false 1/6])/C. 非決定性(同一 input が COMPLIANT ↔ MAJOR[JA 段 B-1、B-2 の Production MAJOR → Trial COMPLIANT]、Advanced/Standard で同一 JA の判定差、severity/flag/origin の run 間揺れ、prompt cache の影響有無)/D. Checker 実装上の非対称(MAJOR→MINOR 降格のみ、MINOR→MAJOR 昇格なし、`_apply_deviation_post_hoc_validation` 逐語)/E. origin 判定(ja_source/translation/simplification 由来の誤分類リスク、Meta Standard 例の fact_id 不一致)/F. QCD(call 数 4/記事、retry・STOP 率[Hormuz 3/3 STOP、Family X E2E 完成率]、latency 中央値 33 秒、cost、完成記事率)。各問題を「モデル起因/Prompt 起因/post-hoc 起因/呼び出し側(Action)起因/Ledger 起因」で分類。

### 2. 過剰 BLOCK の原因/3. 重大見逃しの原因/4. 非決定性の原因(それぞれ根本原因を 1 段掘り、GPT-6 Trial で変わったもの・変わらなかったものを分ける)

### 5. deterministic rule 候補(安全側=昇格)
LLM が正しい category flag を立てたのに severity だけ誤った場合の機械的救済: 例 `changed_actor=true`+Ledger actor mismatch → BLOCKING/`changed_number=true`+material numeric mismatch → BLOCKING/`changed_negation=true` → BLOCKING/comparison 方向反転 → BLOCKING/material time inversion → BLOCKING。各 rule について「現行 audit json のフィールドだけで判定可能か」「Ledger 側の構造化値(actor/numeric_value/date)との突合が必要か(schema 拡張要否)」「誤昇格リスク(例: 主体の言い換え・単位換算)」「GPT-6 Trial データに適用した場合の結果(changed_actor 6/6 が BLOCKING になるか、B 群に誤昇格が出るか=既存 run json で机上シミュレーション)」を表に。`changed_causality=true` だけでは自動 BLOCKING にしない等、category ごとの差を設計。

### 6. deterministic rule 候補(生産性側=非 STOP 化)
`changed_causality`(および certainty/scope/unsupported_new_claim の一部)について、「numeric/actor/time/negation 矛盾なし」「Ledger 観測と最終理解が一致」「qualifier あり」「直後に留保文あり」「明示的 factual constraint(notes_for_writer の factual_constraint)に反していない」等の条件で自動 STOP しない設計を検討。**定型 hedge の免罪符化を防ぐ条件**(hedge の有無ではなく、claim が Ledger の観測と矛盾しないことを主条件にする、hedge は補助、等)。B-1/B-2/B-3/B-4 の各 run json に机上適用した結果(BLOCKING/QUALITY/ACCEPTABLE のどれになるか、A 群に誤降格が出ないか)を表に。

### 7. Severity 3 層と Action の分離設計(v0.1 を継承・修正)
BLOCKING(STOP/must-fix)/QUALITY(通過+log)/ACCEPTABLE(通過)。既存 `severity`(MAJOR/MINOR)を残し `severity_final`/`action`/`basis`/`rule_id` を追加する後方互換案。Action 表(origin × severity_final × 段[JA/Advanced/Standard])。fail-closed 原則との整合(BLOCKING は従来どおり fail-closed、QUALITY はログ+通過=**fail-closed の適用範囲を BLOCKING に限定する設計変更である点を明示、ユーザー判断事項**)。QUALITY ログの置き場・閲覧運用。Key Phrase/Comment/In One Line への伝播対策。案B・must-fix・Human Review Lock との関係。

### 8. notes_for_writer の扱い
soft 化しない。factual_constraint / writer_guidance 分離 schema 案(Researcher Prompt 側での分離 or 後段の機械分類)、Checker への渡し方(factual_constraint は hard、guidance は非参照)、過去 Ledger 資産の互換、Trial 候補としての位置づけ(Production 変更なし)。

### 9. 非決定性対策
反復判定(n 回多数決、BLOCKING は 2/2 等)・temperature/seed(Responses API で利用可能か=Phase A probe 結果を参照、推測しない)・prompt cache の影響・Advanced/Standard の重複 Check の統合案(JA canonical で確定後、EN は translation-diff 限定)の費用対効果(GPT-6 Trial の token/latency 実測を根拠に)。

### 10. 実装配置案(Production 変更はしない、案のみ)
単一 `classify_severity()`(vfl01 内 post-hoc の拡張)+呼び出し側 Action 表、drift 回避、Family A/B/C/X/Z への波及範囲、Dangling Reference の可能性、schema 追加の後方互換(既存 481 ファイル・テスト)。

### 11. Trial 案(既存 fixture 使用、追加 fixture は最小)
Safety: 重大 fixture BLOCKING 維持 100%(ER-009-N1 9 種+A 群 5 件+changed_actor n=5)/Productivity: **不要 BLOCK 率を B 群 baseline 75% から明確に下げる**(目標値案と根拠、例 ≤25%)/Stability: 同一 input 一致率(現行 40〜100% → 目標案)/QCD: cost・latency・retry・STOP 率・completion 率。比較構成(現行 Prompt+post-hoc v2 のみ/Prompt 変更あり/反復あり、モデルは `gpt-5.6-luna` と `gpt-6-luna` の両方で)、反復 n、費用概算(GPT-6 Trial の実測 token を根拠、単価は Closeout 委任の確定値を参照できなければ「参照先」と明記)、Guardrail 案、STOP 条件、gold 確定が必要な fixture(changed_actor/Meta Standard/B-4/B-2 等は USER_DECISION_REQUIRED として列挙)。

### 12. 既存仕様との競合/13. リスク・未解決/14. ★ユーザー判断が必要な事項(Safety×Productivity トレードオフ、fail-closed 適用範囲、schema 変更、Family 横断影響、Trial 追加)

## REPORT `OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`
Status 行「PROPOSED / REVIEW(v0.2、Production 変更なし、Trial 未開始)」、設計書へのポインタ、各章の要約(Fable が正式報告へ転記できる粒度)、★項目一覧。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-V02-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-V02-01_01.md --json-out docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-V02-01_01.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧
上記「入力」。更新位置: 設計書(新規)、REPORT(新規)、delegation_log。

## 実行コマンド全文
- `git pull --ff-only origin main`
- 机上シミュレーション: `.venv\Scripts\python.exe <scratchpad>\simulate_rules.py`(自作、repo 外、既存 run json に rule を適用して表を作る。API 呼び出しなし)

## Git
- add 対象(path 指定のみ): 設計書、REPORT、delegation_log+`_check.json`。メッセージ `OPEN-233-CHECKER-REDESIGN-V02-01: 再設計案v0.2(問題構造A〜F・deterministic rule[昇格/非STOP化]・Severity3層とAction分離・notes_for_writer分離案・非決定性対策・Trial案、Production変更なし)`、trailer `Management-ID: OPEN-233-CHECKER-REDESIGN-V02-01`。push。

## 報告(RESULT_PACKET_C233 + handback、目安50行)
【問題構造】【過剰 BLOCK の原因】【重大見逃しの原因】【非決定性の原因】【deterministic rule 候補】(昇格側・非 STOP 化側、机上適用結果の要点)【再設計案 v0.2】【Trial 案】(受入条件・構成・費用概算)【既存仕様との競合】【リスク / 未解決】【★ユーザー判断】/commit hash・raw URL/STOP 有無(新 Product 判断・fail-closed 変更・schema 変更・Family 横断・Dangling Reference の可能性は ★ で列挙し、実装はしない)。
