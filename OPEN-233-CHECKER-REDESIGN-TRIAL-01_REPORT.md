# OPEN-233-CHECKER-REDESIGN-TRIAL-01 REPORT (Phase A + Trial 1 + Trial 2)

**Status**: `TRIAL2_DONE_IMPROVEMENT_PROPOSED`(委任_03、2026-09-29)。
Phase A(§1〜8)はTrial計画確定、Trial 1(§9)・Step2診断+Trial 2(§10)は
実行済み(gpt-6-luna累計86 call[Trial1 34+委任_03 52]、¥22.1167/総枠
¥400)。V4-A(Prompt境界明確化)でSafety 100%達成(changed_actor n=5含む)。
Productivity(不要BLOCK率≤25%)・Stability(≥90%)は未達、V5-A(B1限定拡張)
を次委任向けに提案。Production code・共通Checker Prompt・severity・
routing・Production schemaの変更なし。Production配線なし。詳細は§9〜§10
参照。

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

## 9. Trial 1実行(委任_02、2026-09-29)

**Status**: `TRIAL1_DONE_IMPROVEMENT_PROPOSED`。詳細は設計書
`docs/pm/design_open233_checker_redesign_trial_01.md`§2-補/§3-補。

**ユーザー更新判断1〜15**を反映し(逐語`docs/pm/delegation_log/2026-09-29_
OPEN-233-CHECKER-REDESIGN-TRIAL-01_02.md`)、Phase Aの★6件をFable判定で
解決(gold/B2_hormuz/Meta negative control/Guardrail/V2・V3両方実行/実行前
STOP撤回)。実行前STOPは行わず、Phase A→Trial 1実行→分析→V4設計まで
本委任で完了した。

**Trial 1実行(新規harness`er051_open233_checker_trial_01_run.py`、
Production/Model Routing Contract非経由)**: gpt-6-luna、reasoning="high"。

- **Step1(重大群12 fixture、V2/V3各12 call)**: **Safety 100%達成**
  (両variantとも12 fixture全てBLOCKING維持)。
- **Step1(changed_actor n=5、V2/V3各5 call)**: **Safety未達**
  (V2=4/5[80%]、V3=3/5[60%])。3件の未昇格例はいずれもLLMが
  `changed_actor=false`(誤って`unsupported_new_claim`のみtrue)を返した
  ケースで、昇格ルール自体(flagが立った7/7では100%機能)ではなく、その
  手前のLLMカテゴリ判定(Promptのカテゴリ境界曖昧さ)が原因と特定した。
- **Step2/Step3**: 設計書§4のvariant別打ち切りルールに従い、V2・V3とも
  changed_actor Safety未達のため**両方とも未実行**(予算温存目的の拡大
  解釈はせず委任文の明示ルールを厳守)。参考(¥0、V0データreplay): V1を
  B群4件へ適用しても不要BLOCK率は75%→75%で不変(B群は全件severity=MAJOR
  のためfail-closed規則でpost-hoc層だけでは改善不可、Productivity改善は
  V2/V3のPrompt/schemaがLLM一次severityをMAJOR→MINORへ動かすかに懸かる
  未検証事項)。
- **原因分類**: (a) Promptの判定基準(changed_actorとunsupported_new_
  claimのカテゴリ境界がPromptで排他化されていない)。
- **V4設計案**(実装・実行はしない): V4-A(低リスク、主体差し替え時は
  unsupported_new_claimと同時にchanged_actorも立てるようPrompt明記)を
  最優先案とし、V4-B(昇格ルール自体をunsupported_new_claimへ拡張、中
  リスク・Productivity悪化懸念あり要materiality条件)、V4-C(本Trialの
  未昇格3件をregression fixtureとしてfreeze)を提示。
- **Opus L2投入条件**: 明確な該当なし。V4-A/V4-Bの設計判断
  (Safety/Productivityトレードオフ)がFable裁量判断の候補と報告。
- **ユーザー判断11該当**: なし(gold変更・BLOCKING緩和・fail-closed撤廃・
  Production変更のいずれも未実施)。
- **費用**: Step1(12 fixture)¥5.8145+Step1(changed_actor n=5)¥1.4737=
  **Trial 1合計¥7.2882**(34 call、error 0)。Step2/Step3¥0。**累計¥7.2882
  / 総枠¥400**。API keyの漏洩なし(保存jsonは`prompt_sha256`のみ、生
  promptは非保存、既存er050方式と同一)。
- **Production/Dangling Reference確認**: `git diff --stat`で
  `er003_v1_en_direct_vfl_01_generate.py`/`er006_*`/`er012_*`/`er019_*`に
  差分なしを確認。mock test 29件全件PASS(再確認)。harness実行時も
  Phase A記録の3定数sha256と毎回突合し(`verify_fixed_constants`相当)、
  不一致は発生しなかった。

Evidence: `er051_open233_checker_trial_01_run.py`(新規)、
`er051_output/open233_checker_trial_01/trial_01/`
(raw response/usage/summary_step1.json/summary_step1_changed_actor_n5.json/
cost.json)、設計書§2-補/§3-補。

## 10. Step2診断+V4-A/V4-C実装+Trial 2実行(委任_03、2026-09-29)

**Status**: `TRIAL2_DONE_IMPROVEMENT_PROPOSED`。詳細は設計書§4-補。

**Fable判定**: (1) Safety未達variantでも診断目的のStep2実行は妨げない
(受入判定ルールは維持)。(2) V4-A(Prompt差分ブロックへのcategory境界
明確化、fixture固有文言なし)を実装・実行。(3) V4-B(昇格ルール拡張)は
本委任では実装・実行しない。(4) V4-C(Trial 1未昇格3件のnegative
regression fixture化)を実装。(5) Guardrail¥50。

**Step2診断(V2/V3、境界群5 fixture、10 call、¥4.1258)**: **最重要発見**
— V2・V3ともB1/B2_hormuz/B3/B4の4件全てでLLM自身の一次severity判定が
MAJORとなり、`classify_deviation_trial()`の優先順位1(severity=="MAJOR"
→BLOCKING、fail-closed維持)が常に先着するため、schema variant由来の
QUALITY/ACCEPTABLE分岐に一度も到達しなかった。不要BLOCK率=V2:4/4
(100%)・V3:4/4(100%)、baseline 75%より**悪化**(B2_hormuz[gold=
QUALITY暫定]が新規にMAJOR検出されたため)。Meta_run03_standard
(negative control)は両variantとも正しくBLOCKING検出(成功)。

**原因分類(1件ずつ確認、詳細は設計書§4-補の表)**: B1=主に(a)Prompt
判定基準(一般常識ブリッジ文の許容規定が不足)。B2/B3/B4=主に(d)context
handling/notes_for_writer(HF-007/HF-009/HF-011/MUSE-HC-006/010の明示
禁止パターンにLLMが正しく従った結果であり、Part B独立評価・v0.2§6-1
機械適用結果と整合)。**構造的根本原因(c)deterministic rule**: schema
variantはLLM一次severity=MINORの場合にしか機能しないという設計上の
制約が実証された(LLM severityはvfl01の既存Prompt判定ルールに従い算出
されるため、Trial Prompt差分ブロックの影響を受けない)。

**V4-A実装**: category境界明確化ブロック(TRIAL_PROMPT_DIFF_BLOCK_V4A、
sha256=`7d8229090910ec1979ac2dbadd2ada8715c14ea441a4acd6edf5279291efe1ad`)
をV2ブロックへ連結。schema/post-hocはV2と同一(mock test検証済み)。

**V4-C実装**: Trial 1未昇格3件(V2#3/V3#3/V3#5)をnegative regression
fixtureとしてfreeze、mock test 3件追加(`V4CRegressionFixtureTest`)。

**Trial 2(V4-A)**: Step1(重大群12+changed_actor n5、17 call、¥3.8175)
**Safety 100%達成**(Trial 1のSafety gap解消、changed_actor n=5全件で
LLM一次severityが直接MAJORへ到達)。Step2(境界群5 fixture、5 call、
¥1.9884)不要BLOCK率=2/4(50%、V2/V3診断100%より改善だがn=1のため
non-determinismと区別不可、副作用なし)。Step3(非決定性群4 fixture×n=5、
20 call、¥4.8968)gold既知2fixture平均一致率=**80%**(advanced100%改善/
standard60%悪化)、受入条件(V0実測90%以上)**未達**。QCD: 記事換算概算
¥1.019(V0の1.5倍¥1.226以内、概ね達成)。

**variant別総括表**:

| variant | Safety(重大群) | changed_actor n5 | 不要BLOCK率(B群) | Stability(gold2fixture) | 備考 |
|---|---|---|---|---|---|
| V0(実測) | 100% | 50%(3/6見逃し) | 75% | 90% | baseline |
| V1(post-hoc昇格のみ) | 100%(理論) | 100%(理論、post-hoc) | 75%(不変、replay) | 未測定 | API call不要 |
| V2(Prompt+schema) | 100% | 80% | **100%**(診断) | 未測定 | Trial 1でchanged_actor未達 |
| V3(V2+notes絞込) | 100% | 60% | **100%**(診断) | 未測定 | 同上 |
| V4-A(V2+境界明確化) | **100%** | **100%** | 50%(n=1) | **80%** | Safety達成、Productivity/Stability未達 |

**V5案(設計のみ)**: V5-A(B1限定、一般的経済波及ブリッジ文の許容規定を
Trial Prompt差分ブロックへ追加、B2/B3/B4は現状維持で不要BLOCK率理論値
1/4=25%を狙う、最有力・低リスク)。V5-B(B2/B3/B4はgold再確認のみ、
本診断結果がB3のgold=BLOCKING寄りを補強)。V5-C(severity=MAJORでも
schema信号次第で降格を許す構造変更、fail-closed部分緩和の可能性があり
**ユーザー判断11抵触の可能性**、実装・実行しない)。

**Opus L2論点案(5件)**: (1)V5-Aの「一般常識」境界基準文言設計、
(2)B2_hormuz gold最終化の進め方(非決定性データを踏まえて)、
(3)B3 goldをBLOCKINGへ確定してよいか、(4)Stability低下(90%→80%)が
Prompt分量増加の影響か既知の非決定性かの追加検証優先度、(5)V5-Cを検討
対象に含めるかfail-closed原則維持でV5-A限定に留めるか。

**ユーザー判断11該当**: なし(V5-Cはfail-closed緩和に抵触する可能性がある
提案として明記のみ、実装・実行せず)。

**費用**: 委任_03合計¥14.8285(52 call、error 0、内訳: 診断¥4.1258+
Trial2 Step1[12+5]¥3.8175+Step2¥1.9884+Step3¥4.8968)。累計(Trial 1
¥7.2882+委任_03¥14.8285)=**¥22.1167 / 総枠¥400**。残¥377.8833。
Guardrail¥50中29.7%使用。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(er003/er006/er012/er019)に差分なし。mock test 37件全件PASS
(既存29件+新規8件)。harness実行時にPhase A記録の3定数sha256と毎回
突合し不一致なし。API key漏洩なし。

Evidence: 設計書§4-補、`er051_open233_checker_trial_02_run.py`(新規)、
`er051_output/open233_checker_trial_01/trial_01_step2_diag/`、
`er051_output/open233_checker_trial_01/trial_02/`。

## 11. Opus L2レビュー#1(委任_04で逐語保存)

**Status**: `USER_DECISION_REQUIRED`(指標定義・gold再判断)。詳細は
Opus L2レビュー#1全文(read-only、診断のみ、実装・実行なし)。

**保存先**: `docs/pm/opus_l2_review_open233_checker_trial_01.md`(委任文に
含まれていた論点1〜5+総合の全文を一字も変えず保存)。

**Fable判定(委任文§1に基づく)**:
- 指標定義(不要BLOCK率)・gold(B1のclaim分割、B3のBLOCKING確定)の
  再判断は**USER_DECISION_REQUIRED**該当。現行fixture単位定義(分母
  B1〜B4の4件)は、B3・B4がgold=BLOCKING妥当という独立評価(Opus論点2)を
  前提とすると、正しいCheckerでも不要BLOCK率2/4=50%が下限であり、
  ≤25%達成には実逸脱の見逃しが必要になるため。
- C1(materiality軸V6追加)は**事前了承要**(fail-closed撤廃には該当しない
  というOpus見解だが、「何をBLOCKINGと呼ぶか」の一次基準変更に触れるため
  Trial 3実行前にFamily X限定・Production非接続の範囲での明示開示・可否
  取得を推奨)。
- V5-C(observation_consistent==True かつ ledger_field_basis=="ledger_fact"
  での降格)は実データで既知のBLOCKINGを複数見逃すことが実証されており、
  **不採用を推奨**(設計案から削除)。
- notes_for_writerのschema分離(v0.2案)は、B群deviation 22件中
  notes_factual_constraint由来はわずか2件(9.1%)という実測と矛盾するため
  **不採用を推奨**(効果が見込めず、Ledger生成側への波及リスクのみ残る)。
- HOOK_CLAUSEとV4-Aの文言はchanged_comparisonで正面衝突することが
  特定された。Family X限定variantの間は無害(hook_aware=Falseのため)だが、
  **共通Prompt/Family横断展開時は必須確認事項**(Family N3の危険Hook
  fixture 3種でregressionを回すこと)。

## 12. Stability n=20実測(委任_04)

**Status**: 実測完了(80 call、error 0、¥23.5636)。Opus L2レビュー#1論点4
推奨1に基づく測定追加。**設計変更・variant実装は行っていない**
(V0=現行Production Prompt/schemaそのまま、V4A=既存実装済みTrial variant、
いずれも無変更で流用)。

**実行条件**: `hormuz_run03_standard`(gold=BLOCKING、HF-009 changed_scope)
と`Meta_run03_standard`(gold=BLOCKING、negative control)の2 fixture ×
V0/V4A 2variant × n=20 = 80 call。モデルgpt-6-luna、reasoning=high、
Contract非経由。実行中にシステムのメモリ不足でbackgroundプロセスが1回
kill されたため(66/80完了時点)、既存成功run(error無し)を再課金せずに
残り14 callのみ再実行する`--resume`機能を追加して完走した(課金の重複
なし、既存run_N.jsonの再利用のみ)。harness:
`er051_open233_checker_trial_03_stability_run.py`(新規)。実測データ:
`er051_output/open233_checker_trial_01/trial_03_stability_n20/`。

**検出率(gold claim捕捉率、n=20)・95%信頼区間(Wilson)**:

| fixture | variant | 検出 | 検出率 | 95%CI(Wilson) | category/fact_id一致 |
|---|---|---|---|---|---|
| hormuz_run03_standard | V0 | 20/20 | **100%** | [83.9%, 100%] | 20/20(changed_scope=true・HF-009、全件一致) |
| hormuz_run03_standard | V4A | 17/20 | **85%** | [64.0%, 94.8%] | 17/17(検出時は全件changed_scope=true・HF-009で一致) |
| Meta_run03_standard | V0 | 18/20 | **90%** | [69.9%, 97.2%] | 17/18(1件はrelated_fact_id=MUSE-HC-011で010/012いずれとも不一致) |
| Meta_run03_standard | V4A | 20/20 | **100%** | [83.9%, 100%] | 20/20(全件010/012のいずれかで一致) |

**V0 vs V4Aの差の検定(Fisher正確検定、両側p値)**:
- hormuz_run03_standard: V0 20/20 vs V4A 17/20 → **p=0.2308(有意差なし)**。
  方向としては悪化(100%→85%)だが、n=20でも統計的有意差には至らない。
- Meta_run03_standard: V0 18/20 vs V4A 20/20 → **p=0.4872(有意差なし)**。
  方向は改善(90%→100%)。
- 2fixture併合(V0 38/40 vs V4A 37/40): **p=1.0(有意差なし)**。
- **結論**: Trial 2(n=5)で観測された「90%→80%」の低下は、n=20でも**統計的
  有意差を持って再現しなかった**(hormuzのみ悪化方向、Metaは改善方向で
  相殺)。Opus論点4(C)の「測定不足」という診断が正しかったことを裏付ける。

**非検出回のreasoning_tokens(思考量不足では説明できないというOpus所見の
再検証)**:

| fixture | variant | 検出時平均reasoning_tokens | 非検出時平均reasoning_tokens |
|---|---|---|---|
| hormuz_run03_standard | V0 | 2353.4(n=20、非検出0件) | — |
| hormuz_run03_standard | V4A | 3072.5(n=17) | **3830.3(n=3)** |
| Meta_run03_standard | V0 | 3275.9(n=18) | **4116.5(n=2)** |
| Meta_run03_standard | V4A | 4263.7(n=20、非検出0件) | — |

非検出回のreasoning_tokensは、検出回の平均よりむしろ**高い**(hormuz
V4A: 3830 vs 3072、Meta V0: 4117 vs 3276)。Opus論点4(B)「思考量不足では
説明できない」という所見を本実測でも再確認した。

**cost/latency平均(n=20、call単位)**:

| fixture | variant | 平均cost(¥) | 平均elapsed(秒) |
|---|---|---|---|
| hormuz_run03_standard | V0 | ¥0.2143 | 24.7秒 |
| hormuz_run03_standard | V4A | ¥0.2818 | 40.5秒 |
| Meta_run03_standard | V0 | ¥0.2978 | 35.3秒 |
| Meta_run03_standard | V4A | ¥0.3843 | 56.3秒 |

**Opus論点4推定(単発recall 60〜85%)との照合**: 実測4セルは85%/90%/100%/
100%であり、**Opus推定レンジの上限寄り〜上限超**だった。最悪値は
hormuz_run03_standard/V4Aの85%(Opus推定レンジの上端と一致)で、
「実運用での見逃し確率が約40%」という論点4のSafetyリスク記述(n=5、
3/5=60%検出のみに基づく暫定推定)は、n=20実測では**過大評価だったことが
判明**した(実際は17/20=85%検出、見逃しは15%)。ただし85%はSafety観点で
依然0%ではなく、実データfixtureでの非ゼロの見逃しリスクは残る
(V0・V4Aともに100%ではない実測があった)。

## 13. negative claim候補表・claim単位gold候補表(ユーザー確認待ち、委任_04)

**negative claim候補**: 既存Production実行(`er019_output/`配下、retryを
経て最終的にLEDGER_COMPLIANTになった記事本文、API費用¥0)から16件を
claim単位で抽出した。詳細・出典・sha256は
`docs/pm/negative_claim_candidates_open233_01.md`参照。gold確定は行って
いない(候補表のみ)。特筆事項: 候補1〜3(`family_x_b3_production_wiring_
01/run_01/a2`のStandard版、LEDGER_COMPLIANT)は、同一runのAdvanced版
(design書B4 fixture、LEDGER_DEVIATION MAJORx4)とほぼ同内容のclaimを含む
が、Standard版はヘッジ表現(may/would seem等)のため通過し、Advanced版は
断定表現のためBLOCKINGされている(表現の断定度による判定差の実例)。

**claim単位gold候補表**: Opus L2レビュー#1論点2のB1-a/b/c・B2・B3・
B4-a/b/c/d評価表を、設計書§2のgold表の下に別表(§2-補)として追加した
(既存fixture単位gold表は変更していない)。「現行fixture単位定義での
下限50%」の算術も設計書§2-補へ再掲した。詳細:
`docs/pm/design_open233_checker_redesign_trial_01.md`§2-補。

## Evidence

- 設計書: `docs/pm/design_open233_checker_redesign_trial_01.md`
- 新規実装: `er051_open233_checker_trial_variant_01.py`、
  `er051_open233_checker_trial_variant_01_test_01.py`、
  `er051_open233_checker_trial_02_run.py`(委任_03新規、Step2診断+Trial 2)
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
