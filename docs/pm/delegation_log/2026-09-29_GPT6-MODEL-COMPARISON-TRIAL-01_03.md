## 管理ID

GPT6-MODEL-COMPARISON-TRIAL-01(Phase B 続行=`er009_changed_actor` n=5 限定再実行 → Step 2 → Step 3 を **完走**、委任 _03)。前委任 _02(Step 1 STOP、commit `4c8a24ff`/`3d2c1515`/`f1e583f8`)を引き継ぐ。一時ファイル `docs/pm/ACTIVE_TASK_G6C.md` / `docs/pm/RESULT_PACKET_G6C.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`)。**SSOT 編集は DECISION_LOG のユーザー決定記録 1 エントリのみ**(下記)。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。**Production code・Prompt・Checker・Model Routing Contract・routing の変更禁止**(harness `er050_*` の不具合修正は可、fixture・比較条件の変更は不可)。Opus 起動禁止。

## ユーザー決定(2026-09-29、逐語厳守)

1. `er009_changed_actor` の限定再実行を許可: `gpt-5.6-luna` × 5 回+`gpt-6-luna` × 5 回=10 call。目的=「n=1 の偶然か、モデル差かを切り分けること」。結果はそのまま記録。
2. **Trial は途中で打ち切らない**: 「changed_actor の n=5 結果がどうであっても最後まで完走。GPT-6 Luna が baseline 以上でも未満でも続行。一部 fixture で重大見逃しが出ても、その事実を記録して続行」。目的=「GPT-5.6 Luna vs GPT-6 Luna の全体的な性格差を把握すること」。
3. Step 1(重大: BLOCKING 維持率・false negative・category 検出・severity 判定・post-hoc との関係)/Step 2(境界・過剰品質: Hormuz B 群・changed_causality・bridge 文・`so`・一般化・Meta 境界例・notes_for_writer 関連 → **不要 BLOCK がどの程度減るかを必ず比較**)/Step 3(非決定性 n=5: 判定一致率・category 一致率・severity 一致率・origin 一致率・overall 一致率 → どちらが安定か)を必ず実施。
4. **途中 STOP 条件はモデル品質ではない**: 累計費用が Guardrail ¥300 に達する見込み/API error・timeout が継続して Trial として成立しない/schema 非互換/harness 不具合/fixture integrity 破損/Production code へ影響する異常。
5. `gpt-6-sol` は probe 済み第二候補として保持、本 Phase B では大量比較しない。Astra 対象外。
6. Guardrail ¥300(Phase B 全体、前委任の ¥10.86 を含む累計)。不要な追加 fixture・追加モデル・追加反復は行わない。
7. gold は既存 A/B 暫定、書換禁止。割れた fixture は USER_DECISION_REQUIRED 候補として列挙。
8. Trial 終了 Status は REJECTED / VALIDATED / USER_DECISION_REQUIRED(混在なら USER_DECISION_REQUIRED で可、最終分類は Fable。VALIDATED は Production 採用を意味しない)。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_03.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_03.md --json-out docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_03.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: 累計上限 ¥300(参考換算。GPT-6 単価未確認のため token 数を一次記録、現行単価での参考換算を併記。各 Step 前に「fixture 数・call 数・想定費用・累計見込み」を記録し、累計見込みが ¥300 を超える場合は当該 Step を発火せず STOP)。

## 手順

### 0. 事前(¥0)
`git pull --ff-only`、`git stash list`、fixture sha256 再検証(前委任の fixture 定義 json と一致、不一致なら STOP)、`budget_state.json` の累計(¥10.86)を引き継ぐ。harness に `--fixture <id> --repeat N` の限定実行モードが無ければ追加(fixture 定義・比較条件は不変、mock テスト追加)。

### 1. `er009_changed_actor` n=5(10 call、想定 ≈ ¥9)
両モデル各 5 回。出力: `step1_actor_n5/er009_changed_actor/<model>/run_<k>.json`、集計: 5 回中 MAJOR 回数、`changed_actor` フラグ true 回数、severity 分布、overall 分布、post-hoc 前後(raw severity と post-hoc 後 severity を両方記録し、「フラグ true なのに MINOR」が何回か=post-hoc が昇格しない設計の影響を可視化)。**結果に関わらず Step 2 へ続行**。

### 2. Step 2 境界・過剰品質群(B-1/B-2/B-3/B-4+Meta Standard translation MAJOR、新旧各 1 回、想定 ≈ ¥9〜10)
fixture ごとに新旧の severity/category/origin/overall と gold(B 群=過剰品質候補)を表。**不要 BLOCK 率**(B 群で MAJOR となる率)を新旧で比較。changed_causality の挙動(B-2/B-3)、bridge 文(B-1)、一般化(B-4)、Meta 境界例、notes_for_writer への言及(explanation に notes 文言を引用しているか)を fixture ごとに記述。origin 判定の一致性。判定が大きく割れた fixture を USER_DECISION_REQUIRED 候補として列挙(gold 不変)。

### 3. Step 3 非決定性(設計書 §3 非決定性群、n=5、新旧両モデル)
対象 fixture を設計書どおり固定(Hormuz run_02/run_03 の JA・Advanced・Standard+Ledger、Advanced/Standard 判定割れケース)。**発火前に call 数と累計見込みを記録**(fixture 数 × 5 × 2)。累計見込みが ¥300 を超える場合は、fixture を削らず「反復回数を 5 → 3 へ下げる」案と「対象を半分にする」案の費用を提示して STOP(ユーザー判断)。実行後: fixture × モデルごとに 完全一致率(5 run の parsed 出力が同一か)、多数決一致率、category 一致率、severity 一致率、origin 一致率、overall 一致率を集計し、現行 vs GPT-6 Luna の安定性を比較。

### 4. 総合集計・REPORT(`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` §Phase B 完走)
- **Quality**: 重大 fixture 検出率(Step 1+actor n=5 反映)、false negative、false positive、不要 BLOCK 率、causality 挙動、origin 判定、notes_for_writer 関連挙動。
- **Stability**: n=5 一致率(overall/category/severity/origin)、fixture 別の揺れ。
- **QCD**: token 使用量(input/output/reasoning、モデル別合計・平均)、latency(中央値・p90・最大)、error 率、retry 率、Cost(token 一次記録+現行単価換算、GPT-6 実単価は未確認と明記)。
- **現行 Checker 設計由来の問題(モデル差と分離)**: post-hoc が降格のみで昇格しない(evidence: フラグ true かつ MINOR の件数)、origin 判定の揺れ、severity 非決定性、changed_actor 等の検出揺れ、を新旧共通の問題として別節に。
- **Trial 終了 Status 候補と根拠**(REJECTED / VALIDATED / USER_DECISION_REQUIRED、最終分類は Fable)。
- **USER_DECISION_REQUIRED 候補 fixture 一覧**(新旧で割れた/gold が明確でない/Product 判断が必要)。
- 設計書 §9 Phase B 完走。RESULT_PACKET へ SSOT 文案(Trial 結果、OPEN-233 追記案[post-hoc 非対称・重大 fixture 側の非決定性]、Routing 判断はユーザー)。

## SSOT(DECISION_LOG 1 エントリのみ)
「2026-09-29 ユーザー判断: changed_actor n=5 限定再実行許可(10 call)/Trial は途中で打ち切らず完走(モデル品質は STOP 条件にしない、STOP 条件=予算・API error 継続・schema 非互換・harness 不具合・fixture 破損・Production 影響)/Step 1〜3 の確認項目/Sol は第二候補保持(本 Phase B で大量比較しない)/最終報告の比較項目(Quality/Stability/QCD/現行設計問題の分離)/終了 Status 分類ルール」。

## 事前指定Read一覧 / 事前指定Grep一覧
- 設計書 §3〜§9、REPORT §Phase B(Step 1)、`er050_gpt6_checker_comparison_trial_01.py`(全文)、`er050_output/gpt6_checker_comparison_trial_01/budget_state.json`・`summary_step1.json`。
- 更新位置: `er050_*`(限定実行モード追加時のみ)、`er050_output/**`、REPORT、設計書、DECISION_LOG、delegation_log。

## 実行コマンド全文
- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er050_gpt6_checker_comparison_trial_01_test_01 -v`
- `.venv\Scripts\python.exe er050_gpt6_checker_comparison_trial_01.py --step 1 --fixture er009_changed_actor --repeat 5 --models gpt-5.6-luna,gpt-6-luna --budget-jpy 300`
- `... --step 2 --models gpt-5.6-luna,gpt-6-luna --budget-jpy 300`
- `... --step 3 --repeat 5 --models gpt-5.6-luna,gpt-6-luna --budget-jpy 300`

## Git
- commit: (1) harness 限定モード+テスト(あれば)+delegation_log、(2) actor n=5 結果、(3) Step 2 結果、(4) Step 3 結果+REPORT+設計書、(5) DECISION_LOG。メッセージ例 `GPT6-MODEL-COMPARISON-TRIAL-01 (Phase B Step 2): 境界・過剰品質fixture 新旧各1回(不要BLOCK率比較)`、trailer `Management-ID: GPT6-MODEL-COMPARISON-TRIAL-01`。path 指定 add、push。

## 報告(RESULT_PACKET_G6C + handback、目安60行)
【changed_actor n=5 再実行結果】(新旧 5 回の MAJOR 回数・フラグ true 回数・post-hoc 前後)【重大 fixture 最終結果】【境界 / 過剰品質 fixture 結果】(fixture 別表、不要 BLOCK 率新旧)【非決定性結果】(一致率表)【総合比較】(Quality/Stability/QCD)【Checker 設計由来の問題】【Cost / Latency】(token・参考換算・累計・Guardrail 遵守)【Trial 終了 Status 候補と根拠】【USER_DECISION_REQUIRED 候補 fixture】/STOP 有無(予算・error 等)/commit hash・raw URL。
