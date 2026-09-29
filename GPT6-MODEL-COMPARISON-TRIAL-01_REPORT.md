# GPT6-MODEL-COMPARISON-TRIAL-01 REPORT (Phase A / Phase B)

**Status(Phase A)**: Trial計画確定のみ。**Status(Phase B、委任_02)**:
Step 1(重大fixture群)を実行し、`gpt-6-luna`に重大見逃し1件を検出したため
ユーザー決定どおり**STOPし、Step 2/Step 3は実行していない**。Trial終了Status候補
=`USER_DECISION_REQUIRED`(詳細は§Phase B-5)。**Status(Phase B、委任_03、完走)**:
ユーザー決定(2026-09-29「Trialは途中で打ち切らない」)に基づき、
`er009_changed_actor` n=5限定再実行 → Step 2(境界・過剰品質群) → Step 3
(非決定性n=5)を**すべて実行完了**した(STOPなし、累計参考換算¥41.26/¥300
[13.75%]、error率0%、全84 call成功)。詳細は§Phase B-6〜B-12。Trial終了
Status候補=`USER_DECISION_REQUIRED`(詳細§Phase B-12、最終分類はFable/ユーザー)。
Production code・Prompt・Checker・Model Routing Contractの変更は一切
行っていない。Opus起動なし。

本REPORTはPhase A/Phase Bの要約であり、詳細は設計書`docs/pm/design_gpt6_model_
comparison_trial_01.md`(§9にPhase B追記あり)を正とする。

---

# Phase B(委任_02、2026-09-29)

## Phase B-1. `gpt-6-sol`互換性probe結果

1 call実行(`er050_output/gpt6_sol_probe_result.json`)。**SUCCESS**。

| 項目 | 結果 |
|---|---|
| status | SUCCESS(エラーなし・timeoutなし) |
| model_returned | `gpt-6-sol` |
| response_id | `resp_004c44a5ce42091a006abb79fcebfc87d0ab7947c4cacc6fff` |
| reasoning="high" | 受理(reasoning_tokens=17、Phase Aのluna/astra probeでは0だったが今回は非ゼロを観測) |
| text.format.type=json_schema + strict:true | 受理、schemaどおりのJSONを返却 |
| elapsed_seconds | 3.716 |
| input/output tokens | 67 / 40 |

**比較対象には追加していない**(ユーザー決定どおり、Luna/Solで不足時の第二候補としての
位置づけを維持)。参考換算費用: ¥0.0098(無視できる額)。

## Phase B-2. Trial実行条件(sha256固定の証明)

`er050_gpt6_checker_comparison_trial_01.py::verify_fixed_constants()`が起動時に
以下3点をPhase A記録済みsha256と突合し、不一致ならRuntimeErrorでSTOPする設計
(実行時に例外なく通過、固定性確認済み):

| 定数 | sha256(Phase A記録=今回実測、完全一致) |
|---|---|
| `DEVIATION_PROMPT_TEMPLATE` | `d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9` |
| `DEVIATION_DEVELOPER_MESSAGE` | `28d7efc6d289a246ddcf71da118ca175af86dd2001fe1ca4725a5c534c299b2b` |
| `DEVIATION_JSON_SCHEMA`(sort_keys） | `bf6858126fc5888b43d84f06e0c9f6f550415516d2c9ca6ef6269f7229ed407f` |

A/B/Meta群fixture(A2A3/A4/A5/B1/B2/B3/B4/Meta run_03 Standard)は、既存audit json
保存済みの`prompt`文字列からテンプレート逆展開方式(`extract_inputs_from_prompt()`)で
`verified_ledger_text`/`article_text`/`source_article_text`を復元し、
`verify_reconstruction()`で再度テンプレートへ通した結果が保存済み`prompt`と
**byte単位で完全一致**することを全8件で検証済み(mock test
`test_reconstruction_matches_for_all_audit_fixtures`、および実行時`load_audit_fixture()`
内で例外なく通過)。A2A3/A4/B1/B2/B3/B4/Metaのsha256は設計書§3の実測値と完全一致
(mock test `test_audit_fixture_sha256_matches_design_doc`でも固定)。

model引数のみが2モデル間で異なり、他の`client.responses.create()`引数
(`input`/`reasoning`/`text`)が完全一致することもmock test
`test_model_is_only_varying_argument`で検証済み。

**A-1は実行対象外**(design書自身が「検出漏れ自体を再現したfixtureではない」と明記
済みの是正後recheckファイルのみで、promptキーを持たず再実行不可。ハーネス内
`A1_NOTE`に理由を記録)。**A5は設計書記載パス(`must_fix_retry_result.json`、retry後
COMPLIANT結果)ではなく、同一run内の是正前ファイル(`meta/deviation_check_trial.json`、
MAJOR検出時点の原本、fact_id=MUSE-HC-012が完全一致)を実際のfixture inputとして採用**
(新規fixtureの捏造ではなく、既存実データの中から再現可能な原本を採用しただけ、
REPORT内に理由明記)。

## Phase B-3. Step 1: 重大fixture群結果(ER-009-N1 9種 + A2A3 + A4 + A5、新旧各1回)

| fixture | gold(期待) | gpt-5.6-luna(baseline) | gpt-6-luna | 判定 |
|---|---|---|---|---|
| er009_changed_number | MAJOR, changed_number=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| **er009_changed_actor** | **MAJOR, changed_actor=true** | **MINOR(changed_actor=true だがseverity=MINOR)** | **LEDGER_COMPLIANT(0 MAJOR)** | **両者MISS(baselineもMISS)** |
| er009_changed_scope | MAJOR, changed_scope=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_causality | MAJOR, changed_causality=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_certainty | MAJOR, changed_certainty=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_negation | MAJOR, changed_negation=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_comparison | MAJOR, changed_comparison=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_time | MAJOR, changed_time=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_unsupported_new_claim | MAJOR, unsupported_new_claim=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| A2A3 | LEDGER_DEVIATION(MAJORx3件相当) | MAJORx2 | MAJORx2(flag構成が一部異なる) | 両者PASS(MAJOR維持) |
| A4 | LEDGER_DEVIATION | MAJORx1(changed_scope) | MAJORx2(unsupported_new_claim+changed_certainty) | 両者PASS(MAJOR維持、gpt-6は検出件数増) |
| A5 | LEDGER_DEVIATION、changed_fact | MAJORx1(changed_fact) | MAJORx1(changed_fact+changed_negation) | 両者PASS(MAJOR維持) |

**BLOCKING維持率(ER-009-N1、9件中)**: baseline 8/9(88.9%)、gpt-6-luna 8/9(88.9%)。
**新たな重大見逃し**: `er009_changed_actor`で発生。ただし**baselineも同一n=1実行で
同時に見逃した**(baselineはseverity=MINORと判定、Ledger Deviation Checkerの
prompt上のルール「10種のいずれかが明確にtrueならMAJORにする」に本来従えば
changed_actor=trueでMAJORになるはずだが、モデルがMINORのまま返した。post-hoc
validationはMAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの補正は行わない設計
のため、この非対称性がそのまま出力に反映されている)。gpt-6-luna側はそもそも
`changed_actor`フラグ自体をfalseと判定し、deviation自体を報告しなかった
(baselineより検出力が低い可能性、または単なる非決定性の可能性のいずれも否定できない
=n=1のみでは切り分け不可)。

**ユーザー決定「gpt-6-luna に重大見逃しがあれば STOP」に該当するため、Step 2/Step 3は
実行せず本委任をここでSTOPした**(Step2/3の追加実行はしていない)。

## Phase B-4. Cost / Latency(Step 1のみ)

| model | n | 参考換算合計(¥) | latency中央値(秒) | latency最大(秒) | input tok平均 | output tok平均 | reasoning tok平均 |
|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | 12 | 5.72 | 7.85 | 42.06 | 5113.8 | 1628.7 | 1361.6 |
| gpt-6-luna | 12 | 5.13(同一参考レート換算、実単価未確認) | 9.24 | 33.94 | 5113.8 | 1375.2 | 1107.9 |

累計参考換算(Step1のみ): ¥10.85(`er050_output/gpt6_checker_comparison_trial_01/
summary_step1.json`の`cumulative_ref_jpy`)。Sol probe(¥0.0098)を含めても
**累計¥10.86**で、Guardrail上限¥300の3.6%程度。error率0%(24/24 call成功)。
retry機構は本harnessでは使用していない(must-fix retry等はProduction側の機構、
Trial harnessは単発run_deviation_check()呼び出しのみ)。

gpt-6-lunaはreasoning tokens平均が baseline比 約-18.6%(1361.6→1107.9)、
output tokens平均も約-15.6%少ない。latency中央値はgpt-6-lunaの方がやや遅い
(7.85秒→9.24秒)が、最大値はgpt-6-lunaの方が短い(42.06秒→33.94秒)。n=12のみで
統計的な結論は出せない。

**GPT-6単価は未確認のため、上記参考換算はgpt-5.6-luna単価をそのままGPT-6にも
適用した仮の値であり、実費ではない**。token数(input/output/reasoning)を一次記録
として`er050_output/gpt6_checker_comparison_trial_01/step1/**/run_1.json`へ保存済み。

## Phase B-5. リスク / 未解決問題 / Trial終了Status候補

- **最大のリスク**: `er009_changed_actor`のMISSが「gpt-6-luna固有の検出力低下」なのか
  「Checker自体(prompt+モデル)の単純な非決定性」なのかを、本Trialのn=1実行では
  切り分けられない。baselineも同一n=1で同時にMISSしたことは、後者(非決定性)の
  可能性を示唆するが、断定はできない(Step3で計画していた非決定性測定[n=5反復]は
  STOPにより未実行のため、この切り分けに必要なデータが取得できていない)。
- 発見事項: post-hoc validationがMAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの
  補正を行わない設計上の非対称性が、今回のchanged_actor MISSで可視化された
  (baseline側: changed_actor=trueなのにseverity=MINORのまま出力された)。これは
  Production Checkerの既存設計そのものであり、本Trialで新たに変更・提案するもの
  ではない。設計判断が必要と考えられる場合はユーザー/Fable判断へ回す
  (Production code変更はしていない)。
- Step 2(境界・過剰品質群)・Step 3(非決定性)は未実行のため、Over-blocking改善・
  Stability改善の実測データは**本委任では取得できていない**。
- Sol probeはSUCCESSしたが、比較対象への追加はユーザー決定どおり見送り。

**Trial終了Status候補**: `USER_DECISION_REQUIRED`。根拠: (1)ユーザー事前決定の
STOP条件(gpt-6-lunaの重大見逃し)に文字どおり該当したため機械的にSTOPしたが、
(2)同一fixtureをbaselineも同時に見逃しており、これがgpt-6-luna固有の後退か
既存Checkerの非決定性かの区別ができていない。続行(Step3非決定性測定の先行実行、
または当該fixtureのみ追加反復)するか、ここで`REJECTED`として打ち切るかは
Product判断が必要(**Claudeが独自に続行判断はしない**)。

**USER_DECISION_REQUIRED候補fixture**: `er009_changed_actor`
(baseline/gpt-6-luna両方が同一n=1実行でMISSした事実、post-hoc validationの
非対称設計、n=1のみでの評価の限界、の3点をあわせて判断材料とする)。

---

---

# Phase B 完走(委任_03、2026-09-29)

ユーザー決定(2026-09-29「changed_actor n=5限定再実行許可/Trialは途中で
打ち切らず完走/モデル品質はSTOP条件にしない」)に基づき、前委任_02でSTOPした
地点から再開し、`er009_changed_actor` n=5 → Step 2 → Step 3を完走した。
harness `er050_gpt6_checker_comparison_trial_01.py`に`--fixture`/`--repeat`
限定実行モードを追加(fixture定義・比較条件・Prompt/Schema/Validatorは無変更、
mock test 3件追加、14/14 PASS)。STOP条件(予算超過見込み・API error継続・
schema非互換・harness不具合・fixture破損・Production影響)はいずれも
発生しなかった。

## Phase B-6. `er009_changed_actor` n=5限定再実行結果

両モデル各5回(計10 call)。出力:
`er050_output/gpt6_checker_comparison_trial_01/step1_er009_changed_actor_n5/`
(harness側の自動命名により実際のディレクトリ名は
`step1_er009_changed_actor_n5`、委任文中の例示パスと同義)。

| model | run | raw severity | changed_actor flag | overall_status | auto_downgraded |
|---|---|---|---|---|---|
| gpt-5.6-luna | 1〜5(全5回) | **MINOR(5/5)** | true(5/5) | LEDGER_COMPLIANT(5/5) | false(5/5) |
| gpt-6-luna | 1 | MAJOR | true | LEDGER_DEVIATION | false |
| gpt-6-luna | 2 | MAJOR | true | LEDGER_DEVIATION | false |
| gpt-6-luna | 3 | MAJOR | true | LEDGER_DEVIATION | false |
| gpt-6-luna | 4 | MINOR | true | LEDGER_COMPLIANT | false |
| gpt-6-luna | 5 | MINOR | **false** | LEDGER_COMPLIANT | false |

**baseline(gpt-5.6-luna)**: 5/5ともraw severity=MINORのまま出力(post-hocの
MAJOR→MINOR自動降格ではない、モデル自身がMINORと判定している。全5回で
`changed_actor=true`のフラグは正しく立つが、severityがMAJORへ上がらない)。
**5/5 MISS(0%)**。前委任_02のn=1結果(同じくMINOR)と合わせ、baselineの
このfixtureに対する挙動は**非決定性のノイズではなく再現性のある系統的な
検出弱点**であることが確認できた(n=1+n=5=計6回で0/6=0%)。

**gpt-6-luna**: 5回中3回はMAJOR判定(PASS)、2回はMINOR(うち1回はflag=true
のまま severityのみ低い、1回はflagごとfalseになる完全見逃し)。**3/5(60%)
PASS**。前委任_02のn=1結果(LEDGER_COMPLIANT、完全見逃し)と合わせ、
計6回中3回PASS(**3/6=50%**)。

**結論**: baselineは本fixtureを一貫して見逃す(0/6)のに対し、gpt-6-lunaは
半数は正しく検出する(3/6)。n=1のみでは「両者とも同程度に弱い」と見えたが、
n=5で切り分けた結果、**gpt-6-lunaの方が本カテゴリの検出力が明確に高い**
ことが分かった。ただしgpt-6-lunaも完全ではなく、残り50%は見逃す。

post-hoc前後: 全11回(baseline 5+gpt-6 6[n=1含む])を通じ`auto_downgraded=true`
(MAJOR→MINOR降格)の発生は0件。つまり今回観測された全てのMINOR出力は
**モデル自身の生severityであり、post-hoc処理由来ではない**。一方
post-hoc validationはMINOR→MAJORへの補正を一切行わない設計のため、
モデルがflag=trueとしながらseverity=MINORと出力した場合(baseline 5/5、
gpt-6 1/6)、その非対称設計がそのまま見逃しとして表出する(§Phase B-11で
新旧共通の設計問題として整理)。

累計参考換算: このステップのみ¥2.54(10 call、error 0)。

## Phase B-7. Step 2: 境界・過剰品質群結果(B1/B2_hormuz/B3/B4/Meta_run03_standard、新旧各1回)

| fixture | gold概要 | gpt-5.6-luna | gpt-6-luna |
|---|---|---|---|
| B1 | MAJOR、changed_scope+unsupported_new_claim、origin無し(JA側) | MAJOR×1(unsupported_new_claimのみ、fact_id=HF-011) | MAJOR×2(unsupported_new_claim×2、fact_id=HF-002/HF-006) |
| B2_hormuz | MAJOR、changed_causality、origin=ja_source | **LEDGER_COMPLIANT(0件)** | **LEDGER_COMPLIANT(0件)** |
| B3 | MAJOR、changed_causality、origin=ja_source | MAJOR×1(changed_causality、origin=ja_source、fact_id=HF-007) | MAJOR×1(**新旧で完全一致**: changed_causality、origin=ja_source、fact_id=HF-007) |
| B4 | MAJOR×4(ja_source×3+translation×1) | MAJOR×3(全てorigin=ja_source、fact_id=MUSE-HC-006/010/004、translation由来の1件は未検出) | MAJOR×2(origin=translation×1[fact_id=006]+origin=ja_source×1[fact_id=006、重複]、baselineより検出件数減) |
| Meta_run03_standard | MAJOR、changed_fact+changed_certainty、origin=translation、fact_id=MUSE-HC-010 | **LEDGER_COMPLIANT(0件、MISS)** | MAJOR×1(changed_fact+changed_scope+changed_certainty+unsupported_new_claim、**origin=ja_source**、**fact_id=MUSE-HC-012**、goldと異なるclaimを検出) |

**不要BLOCK率(B群4件、overall=LEDGER_DEVIATION[MAJOR]維持率)**: baseline
3/4(75%)、gpt-6-luna 3/4(75%)。**両モデルとも同一(B2_hormuzのみ両者とも
LEDGER_COMPLIANTへ変化)**。今回のn=1再実行ではOver-blocking改善(不要BLOCK
削減)は**新旧いずれにも確認できなかった**(B2の変化はモデル差ではなく
非決定性の可能性が高い、両モデルが同じfixtureで同じ方向に変化したため)。

**changed_causality挙動(B2/B3)**: B3は新旧で severity/flag/origin/fact_id
が完全一致(安定した検出)。B2はそもそも両モデルとも今回は検出しなかった
(非決定性、Step3のhormuz非決定性群と整合する現象)。

**bridge文(B1)/一般化(B4)**: B1はgold flagのchanged_scopeを両モデルとも
再現できず(unsupported_new_claimのみ検出)。B4は両モデルともgoldの4件中
一部しか検出できず、gpt-6-lunaはbaselineよりさらに検出件数が少ない
(2件、うち1件はfact_id重複で実質1.5件相当)。

**origin判定**: B3・B4のja_source判定は両モデルで概ね一致するが、B4の
translation-origin項目はbaseline側で完全に検出漏れ、gpt-6-luna側では
検出したがfact_idが他のja_source項目と重複しておりgoldとの厳密対応が
不明瞭。Meta_run03_standardはbaselineが完全MISS、gpt-6-lunaはMAJOR検出
したがorigin=ja_source(gold=translation)・fact_id=MUSE-HC-012(gold=
MUSE-HC-010)と、**検出はしたが別のclaimを指している可能性が高い**
(§Phase B-10のUSER_DECISION_REQUIRED候補)。

**notes_for_writer言及**: Step2全11件のdeviations(baseline 5件+gpt-6 6件)
のexplanationテキストを検索した結果、"note"/"notes_for_writer"等への
明示的言及は**0/11件**(両モデルとも無し)。

累計参考換算: このステップのみ¥7.55(10 call、error 0)。

## Phase B-8. Step 3: 非決定性群結果(n=5、Hormuz run_03、新旧両モデル)

事前記録(発火前): fixture数4×repeat5×モデル2=**40 call**。Step1
actor n=5・Step2実行後の累計¥21.86に対し、既存step1/step2の平均call単価
(約¥0.25〜1.6)から想定追加費用は概算¥15〜30程度と見積り、累計見込みは
¥40〜55程度で上限¥300を大幅に下回ると判断し、反復回数・対象を削減せずに
そのまま発火した(実績: 40 call・追加¥19.4、累計¥41.26)。

overall_status系列(5 run):

| fixture | gold(既知) | gpt-5.6-luna 系列 | gpt-6-luna 系列 |
|---|---|---|---|
| hormuz_run03_ja_original | (非決定性測定対象、gold未固定) | C,D,D,D,C | D,D,C,D,D |
| hormuz_run03_ja_r2 | (非決定性測定対象、gold未固定) | C,D,C,C,C | C,C,D,C,D |
| hormuz_run03_advanced | **COMPLIANT**(既存判定) | C,C,C,C,C | C,C,D,C,C |
| hormuz_run03_standard | **MAJOR**(changed_scope、origin=ja_source、fact_id=HF-009) | C,C,D,D,C | D,D,D,D,D |

(C=LEDGER_COMPLIANT、D=LEDGER_DEVIATION)

**一致率集計**:

| fixture | model | 完全一致率(5/5同一) | 多数決一致率 | gold一致率(gold既知の場合) |
|---|---|---|---|---|
| ja_original | gpt-5.6-luna | 0% | 60%(D) | — |
| ja_original | gpt-6-luna | 0% | 80%(D) | — |
| ja_r2 | gpt-5.6-luna | 0% | 80%(C) | — |
| ja_r2 | gpt-6-luna | 0% | 60%(C) | — |
| advanced | gpt-5.6-luna | **100%**(C×5) | 100%(C) | **100%** |
| advanced | gpt-6-luna | 0% | 80%(C) | 80% |
| standard | gpt-5.6-luna | 0% | 60%(C) | **40%** |
| standard | gpt-6-luna | **100%**(D×5) | 100%(D) | **100%** |

**category/severity/origin一致率(positiveと判定されたrunのみ、標準化した
flagタプルで比較)**: ja_originalはbaseline 3件中2件が同一flag組合せ
(unsupported_new_claimのみ)、gpt-6は4件中2件が同一(changed_fact+
unsupported_new_claim)。ja_r2のgpt-6正例2件は完全一致(changed_causality
のみ、fact_id=HF-009)。standardはgpt-6が5/5全run**完全一致**
(changed_scope、origin=ja_source、fact_id=HF-009、goldと完全一致)、
baselineの正例2件も同一組合せ(changed_scope、origin=ja_source、
fact_id=HF-009)だが出現頻度自体が5回中2回(40%)に留まる。severityは
検出時は両モデルとも常にMAJOR(MINORは0件)。origin判定はja_original/
ja_r2(source_article_text無し)では両モデルともNone(想定どおり)、
advanced/standardの正例では両モデルとも一貫してja_source(goldと一致)。

**総合**: 4fixture平均の完全一致率はbaseline 25%(1/4)・gpt-6-luna 25%
(1/4)で同値だが、**中身が逆**(baselineはadvancedで完全一致、gpt-6は
standardで完全一致)。gold既知の2fixture(advanced/standard)の平均
gold一致率はbaseline 70%((100+40)/2)、gpt-6-luna 90%((80+100)/2)で
**gpt-6-lunaの方が高い**(standardでの圧倒的な安定性・正確性が寄与)。
ja_original/ja_r2(gold未固定)は両モデルとも高い非決定性を示し、
Checker自体の非決定性がモデルに依らず存在することを確認した。

累計参考換算: このステップのみ¥19.40(40 call、error 0)。

## Phase B-9. QCD総合集計(全84 call、Step1原本12 fixture含む委任_02分+委任_03分)

| model | n(call) | 参考換算合計(¥) | input tok平均 | output tok平均 | reasoning tok平均 | latency中央値(秒) | p90(秒) | 最大(秒) |
|---|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | 42 | 21.04 | 5105.5 | 2120.2 | 1949.1 | 11.93 | 25.39 | 53.64 |
| gpt-6-luna | 42 | 20.22(同一参考レート換算、実単価未確認) | 5105.5 | 2018.5 | 1808.5 | 16.00 | 33.34 | 53.46 |

累計参考換算(Phase B全体、Sol probe¥0.0098含む): **¥41.27**(Guardrail¥300の
**13.76%**)。error率**0%**(84/84 call成功)。retry機構は本harnessでは
未使用(単発run_deviation_check()呼び出しのみ、Production側must-fix retry
等とは独立)。

gpt-6-lunaはoutput/reasoning tokensが平均で若干少ない(reasoning
-7.2%、output -4.8%)一方、latency中央値は+34%程度長い(11.93秒→16.00秒)。
最大値はほぼ同等。**GPT-6単価は依然未確認のため、上記参考換算は
gpt-5.6-luna単価をそのまま流用した仮の値であり実費ではない**。

## Phase B-10. USER_DECISION_REQUIRED候補fixture一覧

1. **er009_changed_actor**: baseline系統的0/6見逃し vs gpt-6-luna 3/6
   PASS。gpt-6-lunaは明確に改善しているが50%はなお見逃す。Production
   採用可否の判断材料(Checker側の設計改善[post-hoc非対称の是正]と
   モデル変更のどちらで対処すべきかは別途判断要)。
2. **Meta_run03_standard**: baselineは完全MISS(LEDGER_COMPLIANT)、
   gpt-6-lunaはMAJORを検出したがgoldと異なるfact_id/origin(MUSE-HC-012
   vs MUSE-HC-010、origin=ja_source vs translation)。「別のclaimを
   検出しただけ」なのか「たまたま別の理由でMAJORになった」のか、
   本Trialのデータのみでは切り分けられない。
3. **B4**: gold4件中、baseline3件・gpt-6-luna2件(うち1件fact_id重複)
   しか検出できず、新旧とも検出網羅性に課題。gpt-6-lunaはbaselineより
   さらに検出件数が少ない。
4. **B2_hormuz**: 既存Production記録はMAJORだったはずだが、本Trialの
   n=1再実行では新旧ともLEDGER_COMPLIANT。過剰品質是正の実例なのか
   単なる非決定性なのか未確定(n=1のみのため)。
5. **hormuz_run03_advanced/standard(判定割れケース)**: gpt-6-lunaは
   standardで圧倒的に安定(100%)、advancedではbaselineの方が安定
   (100% vs 80%)。「どちらのfixtureの安定性をより重視するか」は
   Product判断が必要(standardはgold=MAJORでgpt-6が完全一致、advancedは
   gold=COMPLIANTでbaselineが完全一致)。

gold自体(既存A/B群の暫定ラベル)は本Trialでは書き換えていない。

## Phase B-11. 現行Checker設計由来の問題(モデル差と分離)

以下はgpt-5.6-luna/gpt-6-lunaの**両方**で観測された、Checker設計
(prompt/post-hoc validation/schema)自体に起因すると考えられる問題であり、
本Trialで新たに変更・提案するものではない(既存設計の観測事実の記録)。

- **post-hocの非対称性**: `_apply_deviation_post_hoc_validation()`は
  MAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの補正を行わない。
  今回、flag=true(明確な逸脱シグナル)なのにseverity=MINORのまま出力
  される事例が baseline 6/11件・gpt-6-luna 1/11件(Step1 actor
  n=5+n=1、B1のflag未再現分は除く)観測された。この非対称設計により、
  モデルが「flagは立てるがseverityを上げない」判断をした場合、
  post-hocでは救済されず、そのままMINOR(=BLOCKされない)として出力
  される。
- **origin判定の揺れ**: Meta_run03_standardでgpt-6-lunaがgoldと異なる
  origin(ja_source vs translation)・異なるfact_id(MUSE-HC-012 vs
  MUSE-HC-010)を報告した事例、B4でbaseline/gpt-6-lunaの検出origin構成
  が異なる事例など、origin判定は同一Checker設計内でもモデル・run間で
  揺れる。
- **severity/overallの非決定性**: Step3のja_original/ja_r2/advancedで、
  同一input・同一model・同一Promptにもかかわらず5 run中で判定が割れる
  事例が多数観測された(§Phase B-8)。これは特定モデルに限った問題では
  なく、Checker全体(reasoning effort="high"のLLM判定+post-hoc処理)の
  設計特性である。
- **changed_actor検出の弱さ**: baselineは本カテゴリを構造的に見逃す
  傾向がある(§Phase B-6)。10category中「fixture不足」と分類していた
  4category(changed_number/actor/negation/time、設計書§3-5)のうち
  changed_actorについて、実データではなく合成fixtureのみでの評価
  ではあるが、実際に系統的な検出弱点が確認できたことは、他の
  fixture不足categoryについても同様のリスクがある可能性を示唆する
  (本Trialでは追加fixture作成は行っていない)。

## Phase B-12. Trial終了Status候補と根拠

**Trial終了Status候補**: `USER_DECISION_REQUIRED`。

**根拠**:
1. **Quality(Safety)**: gpt-6-lunaはchanged_actorカテゴリでbaselineより
   明確に優れる(3/6 vs 0/6)。ER-009-N1の他8categoryは新旧とも維持
   (n=1のみ)。A2A3/A4/A5(重大群)は両者ともMAJOR維持。**Safety面では
   gpt-6-lunaがbaseline以上**と言える材料がある一方、changed_actorでも
   50%は見逃しが残り「完全に安全」ではない。
2. **Over-blocking改善(OPEN-233の主目的)**: B群不要BLOCK率は新旧同値
   (75%=75%)で、**改善は確認できなかった**。この点だけを見れば
   gpt-6-lunaへの切替に積極的な理由は乏しい。
3. **Stability**: gold既知の2fixture平均でgpt-6-lunaがやや高い
   (90% vs 70%)が、fixtureごとに勝敗が逆転しており(standardは
   gpt-6-luna圧勝、advancedはbaseline勝ち)、一様な優位ではない。
4. **QCD**: token使用量はgpt-6-lunaがやや少ない、latencyはgpt-6-lunaが
   やや長い、costは参考換算では同程度(実単価未確認)。決定的な差では
   ない。
5. **未解決の疑問**: Meta_run03_standardでgpt-6-lunaが「gold通りの
   claimを検出したのか別のclaimを検出したのか」判別できておらず、
   B4の検出網羅性の低さ(新旧とも)、B2_hormuzの非決定性による
   MAJOR消失など、Product判断が必要な論点が複数残る(§Phase B-10)。

以上より、**REJECTED(明確に劣る)でもVALIDATED(明確に優れる、
Production採用可)でもなく**、changed_actor検出力の改善という
明確なプラス材料とOver-blocking未改善という明確なマイナス材料が
併存するため`USER_DECISION_REQUIRED`とする(最終分類はFable/ユーザー)。
**VALIDATEDであってもProduction採用を意味しない**(GPT-6単価未確認、
Routing判断は別途ユーザー判断)。

詳細な実行データは`er050_output/gpt6_checker_comparison_trial_01/`配下
(`step1_er009_changed_actor_n5/`・`step2/`・`step3/`・
`summary_step1_er009_changed_actor_n5.json`・`summary_step2.json`・
`summary_step3.json`・`budget_state.json`)に保存済み。

---

## 1. 対象モデル実確認結果(要約)

- 現行baseline: `gpt-5.6-luna`(reasoning effort実測値`"high"`)。
- `GET https://api.openai.com/v1/models`実行(2026-09-29、環境変数key使用・keyは
  一切出力に含めていない)。全132モデル中、`gpt-6`を含むidが**3件実在**:
  `gpt-6-luna` / `gpt-6-sol` / `gpt-6-astra`。推測ではなくAPI実測。
- endpoint/API互換性probe(scratchpad上の自作スクリプト、現行`vfl01.run_deviation_
  check()`と同一のResponses API呼び出し形式[`reasoning={"effort":"high"}`+
  `text.format.type="json_schema"`+`strict:true`]を使用): `gpt-6-luna`・
  `gpt-6-astra`の計2 callとも**SUCCESS**(エラーなし、`reasoning_tokens=0`)。
  `gpt-6-sol`は費用上限(¥5、probe 1〜2 callまで)の都合上probe未実施(未確認)。
- 単価: `curl`で公式価格ページ取得を試みたがHTTP 403、**未確認(ユーザー提示待ち)**。
  推測値・旧モデル単価の流用はしていない。

## 2. Fixture構成(要約)

- 重大事故群: ER-009-N1危険fixture 9種(存在確認OK、sha256実測)+調査REPORT A群5件
  (存在確認OK、sha256実測、うちA-1は「検出漏れ事例」の是正後recheckのみ記録)。
- 過剰品質/境界群: B群4件+Meta run_03 Standard translation MAJOR 1件(全件存在確認
  OK、sha256実測)。
- 非決定性群: Hormuz run_01〜03(存在確認OK)、run_02/run_03のLedgerがsha256完全一致
  (同一入力での非決定性測定に使用可能)、run_03内でAdvanced(COMPLIANT)/Standard
  (MAJOR)の判定不一致を実データで確認。
- category被覆: 10category中6種(changed_fact/scope/causality/certainty/comparison/
  unsupported_new_claim)は実運用incidentデータあり。**4種(changed_number/actor/
  negation/time)はER-009-N1合成fixtureのみでfixture不足**(実データなし、新規作成は
  未実施)。

## 3. 比較条件・受入条件案・費用/Guardrail案・リスク

設計書§4〜§8を参照(Prompt/Schema/Validatorのsha256固定・model引数のみ差替え、
重大fixture維持率100%等の受入条件案とその根拠、GPT-6単価未確認のため現行単価仮置きの
概算費用[Checkerのみ約¥162〜180程度、確定額ではない]、Guardrail段階発火案、API非互換・
単価未確定・goldラベル再現性・fixture数の少なさ等のリスク)。

## 4. 未解決・未確認事項

- GPT-6候補3件のうちどれを比較対象とするか(ユーザー判断待ち)。
- GPT-6単価(未取得)。
- `gpt-6-sol`のendpoint互換性(probe未実施)。
- Trial harnessがModel Routing Contractを経由するか直接指定するかの方式(Phase B設計時に確定)。

## 5. Phase A終了時点のStatus

`USER_DECISION_REQUIRED`(候補選定・単価確認がユーザー判断待ちのため)。
**Phase B(大量実行)は本タスクでは開始していない**。

## 6. Evidence

- 設計書: `docs/pm/design_gpt6_model_comparison_trial_01.md`
- delegation記録: `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md`
  (T-0 check結果: `status: FAIL`、理由は委任文中のplaceholder表記2箇所、必須項目8件は
  全てOK。詳細は設計書冒頭を参照)
- probe実行ログ(要約、詳細は上記1節): `gpt-6-luna`/`gpt-6-astra`各1 call SUCCESS
