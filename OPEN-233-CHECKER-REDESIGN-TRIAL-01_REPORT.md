# OPEN-233-CHECKER-REDESIGN-TRIAL-01 REPORT (Phase A)

**Status**: Phase A完了(Trial計画確定のみ)。Production code・共通Checker
Prompt・severity・routing・Production schemaの変更なし。Production配線なし。
**Trial実行(有料fixture実行)は本委任では行っていない**(API呼び出しなし、
¥0)。Trial実行前にユーザーへ正式報告してSTOPする(委任ユーザー決定10)。

本REPORTは設計書`docs/pm/design_open233_checker_redesign_trial_01.md`
(章立て1〜8)の要約であり、詳細根拠(fixture別sha256・gold判定根拠・
variant実装詳細・費用見積の算出過程)は設計書本体を参照。設計書は
`docs/pm/design_checker_redesign_v02_01.md`(v0.2)・`OPEN-233-CHECKER-
REDESIGN-V02-01_REPORT.md`・`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`
(Phase B/Closeout)・`er050_output/gpt6_checker_comparison_trial_01/`
(84 call実測)・`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_
REPORT.md`§3・`docs/pm/review_ledger_deviation_redesign_01_part_b.md`を
統合し、2026-09-29ユーザー決定1〜10(逐語は`DECISION_LOG.md`同日エントリ
参照)に基づく。

## 1. fixture固定(§1)

Safety群(重大fixture、BLOCKING維持率100%対象): ER-009-N1 9種+A2A3
(A-2/A-3統合実行)+A4+A5(合計12実行fixture)+changed_actor n=5反復。
A-1(検出漏れ、`prompt`キーなしで再実行不可)は参考記録のみとし、維持率の
分母から除外する提案(★要確認)。Productivity群(境界・過剰品質群):
B1/B2_hormuz/B3/B4/Meta_run03_standard(5件)。**不要BLOCK率の定義**を
確定: 分母=B1/B2_hormuz/B3/B4の4件(Meta_run03_standardはgoldがBLOCKING
[実際の逸脱]のため分母から除外)、分子=Checkerが BLOCKING と判定した数。
この定義はGPT6-MODEL-COMPARISON-TRIAL-01の「baseline 75%=B群4件中3件
MAJOR」と同一算出根拠。Stability群: hormuz_run03_ja_original/ja_r2/
advanced/standard(4件、V0はn=5実測済み)。追加fixtureは作成しない。
sha256は全fixture実測済み(設計書§1表)。

## 2. gold確定(§2)

Confirmed(8件): ER-009-N1 8種+changed_actor+A2A3+A4+A5+A-1(参考)+
hormuz_run03_advanced/standard=BLOCKING(既存判定を維持)。**暫定+要確認**
(Claudeは独自に確定しない): B1(ACCEPTABLE候補)、B3(暫定BLOCKING寄り、
Part B独立評価とv0.2§6-1機械適用結果に基づく)、B4(gold4件中3項目の扱い)、
Meta_run03_standard(fact_id 010/012のどちらを正とするか)。B2_hormuzは
**ユーザー決定4によりQUALITY(暫定・Trial評価用ラベル)**で確定済み。

## 3. Family X限定variant(§3、`er051_open233_checker_trial_variant_01.py`新規)

**post-hoc v2**: `classify_deviation_trial()`。既存severity=MAJOR→
BLOCKING(fail-closed維持)、4カテゴリ(changed_actor/changed_number/
changed_negation/changed_comparison)いずれかflag=trueかつseverity=MINOR
→BLOCKINGへ昇格、それ以外はvariant別にQUALITY/ACCEPTABLE。origin fieldは
一切参照しない設計(v0.2が確認した「JA段origin=None誤降格の罠」を回避)。

**schema variant**: `qualifier_present`/`qualifier_text`/
`ledger_field_basis`/`observation_consistent`/`matched_notes_id`の5
フィールドを追加(Production schema不変、Trial限定schema)。Hormuz
notes_for_writer 12件(Part B既存分類)+Meta Ledger notes_for_writer 15件
(MUSE-HC-001〜015、本Phase Aで新規分類)は**27件中27件がfactual_
constraint**(writer_guidance 0件)と判明。V2(notes全量)とV3
(factual_constraintのみ)は対象2 Ledgerに限れば実質同一入力になる
可能性が高いことをリスクとして明記(§8-3)。

**Prompt variant**: `vfl01.DEVIATION_PROMPT_TEMPLATE`をimportし差分
ブロック(1017文字、sha256`c7195a19fae043096318bfac3bac88327de1e522ab5
fbddae6de53ea1f4efa80`)を追加する方式(Production側定数は不変)。

**variant一覧**: V0(現行、GPT-6 Trial実測を再利用・再実行しない)/
V1(post-hoc v2のみ、Prompt/Schema不変)/V2(Prompt variant+schema
variant+post-hoc v2、notes全量)/V3(V2+notes factual_constraintのみ)。
**設計上の発見**: V0/V1はPrompt/Schemaが同一のため、既存
`er050_output/gpt6_checker_comparison_trial_01/`の84 call実測raw
データへ`classify_deviation_trial()`を適用するだけで計算可能(**新規API
呼び出し0**)。新規callが必要なのはV2/V3のみ。

**mock test**(`er051_open233_checker_trial_variant_01_test_01.py`、
ネットワーク呼び出しなし): **29 test全件PASS**(実行ログ: 下記6章)。
合成dictでの分類ロジック検証11件、Prompt/schema variant構造検証7件
(Production 3定数のsha256不変=Dangling Reference確認含む)、notes分類
検証4件、既存run json実データreplay検証7件(changed_actorのMINOR→
BLOCKING昇格実例、A群/er009 8種のBLOCKING維持、B群での誤昇格0件、JA段
origin無しレコードでの非降格)。

## 4. Trial構成・反復回数(§4)

モデル`gpt-6-luna`のみ、reasoning="high"。Step1(重大群12+changed_actor
n=5)→Safety確認、Safety100%未達variantはStep2/3を打ち切り(Trial全体は
続行)。Step2(境界群5件)→不要BLOCK率。Step3(最良variant1つのみn=5)→
V0(GPT-6 Trial既存実測)と比較。**新規call数**: Step1(V2 12+V3 12+
changed_actor n=5×2variant 10)=34、Step2(V2 5+V3 5)=10、Step3
(最良variant1つ×20)=20。**合計最大64 call**(V0/V1は0 call)。

## 5. 正式費用見積(§5)

gpt-6-luna正式単価(Input $0.10/Cached $0.01/Output $0.50 per 1M、
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Closeout C-2)×V0実測token
(fixture別)+Prompt差分ブロック増分(保守的680 token/call)+schema出力
増分(保守的150 token/call)。Step別: Step1(V2+V3)¥5.05、Step1
(changed_actor n=5、V2+V3)¥1.95、Step2(V2+V3)¥4.21、Step3(最良variant
1つ)¥5.35。**合計概算¥16.4**(全variant全step実行時の上限、V0/V1は$0)。
**Guardrail案**: 合計上限¥50(概算の約3倍)、Step別上限Step1¥8/Step2¥6/
Step3¥12(概算の約2倍、ユーザー決定9「想定の2倍でSTOP」に整合)。

## 6. 受入条件・STOP条件(§6〜§7)

Safety: 重大群BLOCKING維持率100%(changed_actorはpost-hoc v2込みでn=5
全件BLOCKING化を要求)。Productivity: 不要BLOCK率≤25%。Stability: gold
既知2fixture一致率がV0(90%)以上。QCD: cost V0の1.5倍以内(案)。受入
目的「過剰品質によってProduction生産性を失わない」を明記。STOP条件:
予算・API error継続・schema非互換・harness不具合・fixture破損・
Production影響・Safety100%未達(当該variantのみ打ち切り)・gold再判断
要USER_DECISION_REQUIRED(B1/B3/B4/Meta_run03_standard)。

## 7. 既存仕様競合・Dangling Reference確認・リスク(§8)

fail-closed設計・案B・JA Fact Check配線決定(2026-09-27 PRODUCTION_WIRED)
との競合点は設計書§8-2に整理(いずれもProduction側は無変更、Trial限定)。
Dangling Reference確認: `er051`はvfl01をimportのみで使用し、mock testで
Production 3定数のsha256不変を実測検証済み。リスク: V2/V3の差が対象
Ledgerでは観測されない可能性(§3参照)、token見積の概算性、gold未確定
fixtureが多い点。

## 8. 実行ログ(証跡)

- `git pull --ff-only origin main`: 実行済み(HEAD `8be7d639`のまま、
  競合なし)。
- `.venv\Scripts\python.exe -m unittest er051_open233_checker_trial_
  variant_01_test_01 -v`: **Ran 29 tests in 0.049s, OK**(全件PASS、
  ネットワーク呼び出しなし)。
- `.venv\Scripts\python.exe run_project_regression.py --pattern
  "er003*_test_*.py"`: **collected=1557 passed=1553 failed=3 errors=1**。
  4件はいずれも本タスク無関係のpre-existing失敗(P2J履歴監査テストの
  ハードコード済み過去件数[1925/1032/660]と現在のリポジトリ全体ファイル
  数の乖離によるもの、および`er015_standard_a2_6000_generation_first_
  trial_01.py`のProduction Prompt検証エラー[本タスクの変更範囲外]。
  いずれも`er051_*`ファイルの追加[2ファイル]では説明できない規模の
  既存乖離であり、リポジトリ全体で他タスクの未commit差分・過去からの
  蓄積ドリフトに起因する)。

## ★ユーザー判断が必要な事項(§8-4)

1. A-1をBLOCKING維持率の分母から除外する提案の承認。
2. B1/B3/B4/Meta_run03_standardのgold最終値(暫定+要確認の解消)。
3. B2_hormuz暫定QUALITYラベルの最終化タイミング(Trial実行後か別途か)。
4. 費用見積・Guardrail案(合計¥50、Step別上限)の妥当性。
5. V2/V3の差が観測されない可能性を踏まえたTrial実行の優先度
   (両方実行するか片方に絞るか)。
6. Trial実行の正式開始可否(本Phase A完了後、実行前STOP)。

## Evidence

- 設計書: `docs/pm/design_open233_checker_redesign_trial_01.md`
- 新規実装: `er051_open233_checker_trial_variant_01.py`、
  `er051_open233_checker_trial_variant_01_test_01.py`
- 入力: `docs/pm/design_checker_redesign_v02_01.md`、
  `OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`、
  `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`、
  `er050_output/gpt6_checker_comparison_trial_01/`、
  `er050_gpt6_checker_comparison_trial_01.py`、
  `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`、
  `docs/pm/review_ledger_deviation_redesign_01_part_b.md`
- delegation記録: `docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-
  REDESIGN-TRIAL-01_01.md`(T-0 check結果: `status: FAIL`、必須セクション
  「範囲」見出し文言不一致+実行コマンド一部のplaceholder誤検知、他の
  delegation記録でも同型のFAILが多数存在する機械的誤検知、ブロッキング
  ではない記録用ツール)
