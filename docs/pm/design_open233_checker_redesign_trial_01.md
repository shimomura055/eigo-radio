# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Phase A): Trial計画確定

**Status**: PROPOSED / Phase A完了(計画確定のみ)。Production code・共通Checker
Prompt・severity・routing・Production schemaの変更なし。Production配線なし。
**Trial実行(有料fixture実行)は本Phase Aでは行っていない**(API呼び出しなし、
¥0)。本書完成後、Trial実行前にユーザーへ正式報告してSTOPする
(委任文ユーザー決定10)。

本書は`docs/pm/design_checker_redesign_v02_01.md`(v0.2、以下「v0.2」)・
`OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`・
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`(Phase B/Closeout)・
`er050_output/gpt6_checker_comparison_trial_01/`(84 call実測、67件の
deviationレコード)・`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_
REPORT.md`§3・`docs/pm/review_ledger_deviation_redesign_01_part_b.md`
(Hormuz notes_for_writer 12件分類)を出典とする。2026-09-29ユーザー決定
1〜10(逐語は委任記録`docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-
REDESIGN-TRIAL-01_01.md`参照)に基づく。

---

## 1. fixture固定

### 1-1. Safety群(重大fixture、BLOCKING維持率100%対象)

全て`er050_gpt6_checker_comparison_trial_01.py`の`step1_fixtures()`/
`--fixture er009_changed_actor --repeat 5`で使用済みの既存fixtureをそのまま
再利用する(追加fixture作成なし)。sha256は本委任で実測(下表)。

| id | 入力パス | sha256 | 現行判定(V0、gpt-6-luna実測) | gold |
|---|---|---|---|---|
| er009_changed_number | `er009_ledger_deviation_recalibration_02_test.py::FIXTURES["changed_number"]` | `23aa52539d91306b4a36016068de601b790068e1ffd27b6d197115e111a649a0` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_actor(n=1、9種セット内) | 同上`["changed_actor"]` | `ad2864f305a41a19664917cc6cc395167f07a45adfdf964ab6787e42bef16f05` | LEDGER_COMPLIANT(flag=false)、**MISS** | BLOCKING |
| er009_changed_scope | 同上`["changed_scope"]` | `09388af908c4b5bc86ad61bfbd19ec1dfb550fb5d2540b54e98472dbd788527e` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_causality | 同上`["changed_causality"]` | `7cfe5b1a9c85f901972de0169dafc2e5872b210a73638050adaf44993abe97cc` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_certainty | 同上`["changed_certainty"]` | `88e4de364b3395b6535b6ee6ebb3f1a073ef9e063b7494677d2968e81cc7dce3` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_negation | 同上`["changed_negation"]` | `00085fd6c1968e20f03197a44dd61a265e6be151dedbbe79f83dfb1120a9ad4a` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_comparison | 同上`["changed_comparison"]` | `542a56e9294fbe54a4e5f5e90416f1f61b6d943da49c6d3fe63cf13511837e26` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_changed_time | 同上`["changed_time"]` | `f4b44ae6633a12b632bf3e4fd8e4a974b083629dc10e91b3d9350311f4e78297` | MAJOR(flag=true)、PASS | BLOCKING |
| er009_unsupported_new_claim | 同上`["unsupported_new_claim"]` | `98e15aa9dce7c695548eb2adc483c54debdfd0eadccd89e689dadec0c7ca3a3b` | MAJOR(flag=true)、PASS | BLOCKING |
| (共通)LEDGER_TEXT | `er009_output/.../research/verified_fact_ledger.txt`(経由の定数) | `31f6740e97a106e59d6c38a684604be8f4a49d27d541b531666ce26facd17e3e` | — | — |
| A2A3(A-2+A-3統合実行) | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/A3_deviation.json` | `9e664e1ae373f629a58d283a5ad94334bbe76fe3dcf959a2c53f4b0b11d26877` | MAJORx2、PASS(flag構成が一部異なる) | BLOCKING |
| A4 | `er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN2-T1_deviation.json` | `44fed56e96561ad5d5383805e00d3974340912e98bb97512d8a537a004e4f483` | MAJORx2、PASS(検出件数はgpt-6の方が多い) | BLOCKING |
| A5 | `er045_output/family_x_no_heading_segmentation_trial_01/meta/deviation_check_trial.json` | `ee67fba3892448486fd4f4b292fa6a0f4792a3cd39299756b3bb2ec8814a674e` | MAJORx1(+MINORx1)、PASS | BLOCKING |
| er009_changed_actor(n=5反復対象、別委任で追加実行済み) | 同上(er009モジュール、同一fixture、repeat=5) | 同上(`ad2864f3...`) | **3/5 PASS(60%)**、n=1と合わせ3/6(50%) | BLOCKING |

**A-1(category未検出例、別掲・維持率分母から除外提案)**:

| id | 入力パス | sha256 | 現行判定 | gold | 分母への扱い |
|---|---|---|---|---|---|
| A-1 | `er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json`(是正後recheckのみ、`prompt`キーなし) | `f24825e468a9bc0a78f5622a897a300a007487994c8f4fdc97eabc893d5f97b1` | 2回ともCOMPLIANT誤判定(検出漏れ)。既存recheckで人手是正済み | BLOCKING(本来) | **提案: 分母から除外**。理由: このファイルは是正後の結果のみを保存しており、検出漏れを再現するChecker呼び出し用の入力(元記事本文)を含まない(`prompt`キー無し)。V0(GPT6-MODEL-COMPARISON-TRIAL-01)も同じ理由でA-1を実行対象外とした(`A1_NOTE`)。BLOCKING維持率の分母に含めると「実行不可能な項目」が分母に入り測定不能になるため、Safety群の**参考記録**(既知の検出漏れ事例)として別掲に留め、100%判定の分母には含めない。★この提案自体はユーザー/Fable確認が必要(本書独自に確定しない)。 |

Safety群の実行可能fixture数: **12種類(er009 9種+A2A3+A4+A5)+changed_actor
n=5反復**。A-1は参考記録のみ(分母除外提案)。追加fixtureは作成しない
(負例[主体の一般的言い換え等]fixture不足は制約として明記、v0.2§13)。

### 1-2. Productivity群(境界・過剰品質群、不要BLOCK率の分母)

全て`step2_fixtures()`で使用済みの既存fixture。

| id | 入力パス | sha256 | 現行判定(V0、baseline/gpt-6-luna) | gold(暫定) |
|---|---|---|---|---|
| B1 | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json` | `e33d7fb09fdacfcfc931271ad4176f951ada0f1753fe20781ed4124b5faa51b2` | baseline MAJORx1/gpt-6 MAJORx2(いずれもunsupported_new_claim中心) | ACCEPTABLE候補(★要確認) |
| B2_hormuz | `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` | `0594e838284f32c2963d78b85000474451ac741a9cbcd06e03a7f773d04e97b1` | 両モデルともLEDGER_COMPLIANT(0件、検出自体消失、非決定性) | **QUALITY(ユーザー決定4、暫定・Trial評価用ラベル)** |
| B3 | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/B1_deviation.json` | `4bf6f67ce7d18ca1b79a40b28350e89126921e10d4a4cf7ba40c40cb530fe525` | 両モデルともMAJORx1(changed_causality、origin=ja_source、新旧完全一致) | **?(★要確認)**。Part B独立評価は「BLOCKING維持が妥当」(HF-007notes_for_writer抵触)。v0.2§6-1は「causality-onlyでもorigin=ja_sourceのためSTAY BLOCKING」と整合。本書はこの2つの先行評価を踏まえ暫定BLOCKING側に倒すが、Fable/ユーザー最終確認が必要。 |
| B4 | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` | `bb21c160629c725afa3e82b58e8d1d1a32454ddb89a7e7d6e8a05f9dbf82f768` | baseline MAJORx3/gpt-6 MAJORx2(gold4件中一部のみ検出、新旧とも網羅不足) | **?(★要確認、gold4件中3項目の扱い)**。Part B独立評価は「新設計で緩めた場合に現状より品質が下がる可能性」と指摘。 |
| Meta_run03_standard | `er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/standard_attempt1.json` | `4016b8cb25a13dbc1809c0a147e7e992f64808ee0ff396189c0fa342a04e79a0` | baseline LEDGER_COMPLIANT(MISS)/gpt-6 MAJORx1だがgoldと異なるclaim(fact_id=MUSE-HC-012 vs gold MUSE-HC-010、origin=ja_source vs gold translation) | **BLOCKING(real deviation想定)、ただしfact_id 010/012のどちらを正としてBLOCKING判定に使うか★要確認**。この項目は「不要BLOCK」ではなく実際の逸脱を見逃さないかのnegative controlとして扱う(下記1-3参照)。 |

**不要BLOCK率の定義(確定)**:

```
不要BLOCK率 = Checkerが BLOCKING と判定したfixture数
              ÷ gold が QUALITY または ACCEPTABLE のfixture数
```

分母は**B1/B2_hormuz/B3/B4の4件**とする(Meta_run03_standardはgoldが
BLOCKING[実際の逸脱]であり「不要BLOCK」候補ではないため分母から除外、
下記1-3参照)。この定義は`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`
Phase B-7の「不要BLOCK率(B群4件、overall=LEDGER_DEVIATION[MAJOR]維持率):
baseline 3/4(75%)、gpt-6-luna 3/4(75%)」と**同一の算出根拠**(B1〜B4の
4件、うちMAJOR維持3件=75%)であり、baseline 75%という既述の数値と整合する。

### 1-3. Stability群(非決定性群)

全て`step3_fixtures()`で使用済み(V0はn=5実測済み、Phase A本体では
再実行しない。Trial Step3は「最良variantのみ」実行、下記4章)。

| id | 入力パス | sha256 | gold |
|---|---|---|---|
| hormuz_run03_ja_original | `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ja_writer/audit/deviation_checks/ja_original_attempt1.json` | `234dffa0f2bb221c957c2439534e9cef7b2977193920fdcc501aac2d42775263` | 未固定(JA段、origin概念なし、非決定性測定対象) |
| hormuz_run03_ja_r2 | `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ja_writer/audit/deviation_checks/ja_r2_attempt1.json` | `53bc9f1a19791ee1a951507938f9ee998f79218762bee4252a8a2a240cb00a19` | 未固定(同上) |
| hormuz_run03_advanced | `er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/audit/deviation_checks/advanced_attempt1.json` | `ce69cf94890f068dbf421df6914e7eecbfd4f4557f761646d80096443509694a` | COMPLIANT(既存判定) |
| hormuz_run03_standard | `er019_output/family_x_refresh_e2e_01/hormuz/run_03/a2/audit/deviation_checks/standard_attempt1.json` | `88f5ef99a1592c80cfd56372e7db1faa7aebb36308446b6225c106c655af8e38` | MAJOR(changed_scope、origin=ja_source、fact_id=HF-009) → BLOCKING |

追加fixtureは作らない(制約: negative example[通すべきものの正解セット]が
現状B群4件しかなく、Part Bが指摘したとおり統計的判断には不十分。本Trialは
既存資産の範囲で実施する)。

---

## 2. gold確定

BLOCKING/QUALITY/ACCEPTABLEの3値、現行MAJOR/MINORとの対応を併記。
確定できるもの(既存9種fixture+A2A3/A4/A5+changed_actor+
hormuz_run03_standard/advanced)はConfirmedとし、Fable/ユーザー確認が
必要なものは「暫定+要確認」を明記する(Claudeは独自に確定しない)。

| fixture | 現行(MAJOR/MINOR) | gold(3値) | 状態 | 根拠 |
|---|---|---|---|---|
| er009_changed_number/scope/causality/certainty/negation/comparison/time/unsupported_new_claim(8種) | MAJOR(合成fixture) | BLOCKING | **Confirmed** | ER-009-N1 recalibration時からのProduction既定(v0.2§11-1) |
| er009_changed_actor | MAJOR(合成fixture)、baselineはMINORのまま出力 | BLOCKING | **Confirmed**(判定基準)、現行Checker挙動は0/6見逃し | 同上。gpt-6-lunaも3/6のみPASSのため「モデル変更単独では不十分」という前提を維持(v0.2§14★10と同一論点はProduction採用可否、本書はgold自体は動かさない) |
| A2A3(A-2/A-3) | MAJORx2〜3 | BLOCKING | **Confirmed** | 投稿記事の価格方向反転・支払義務者具体化、投資REPORT A候補「明らかに止めるべき」 |
| A4 | MAJORx1〜2 | BLOCKING | **Confirmed** | 対象取り違え(プライバシー文脈)、投資REPORT A候補 |
| A5 | MAJORx1 | BLOCKING | **Confirmed** | ロールバック↔再有効化の意味反転、投資REPORT A候補 |
| A-1 | (検出漏れ、severityの記録なし) | BLOCKING(本来) | **Confirmed(参考記録)** | 検出漏れ自体はseverity設計の対象外(Part B総評、v0.2§1-B) |
| hormuz_run03_advanced | COMPLIANT | (非BLOCKING、QUALITY/ACCEPTABLEいずれかは論点外) | **Confirmed(現状維持)** | 既存判定を維持、本Trialで動かす対象ではない |
| hormuz_run03_standard | MAJOR(changed_scope、HF-009) | BLOCKING | **Confirmed** | V0で新旧とも比較的安定して検出(gpt-6-luna 5/5完全一致) |
| B2_hormuz(Hormuz因果境界) | MAJOR(過去Production記録)、V0 n=1では両モデルとも非検出 | **QUALITY** | **暫定(ユーザー決定4)** | 「Trial評価用ラベル、最終仕様ではない」と明記されたユーザー暫定指定。Part B独立評価(Claude)は「BLOCKING dependent」の立場で反対していた経緯があり、本Trialの中でこの暫定goldに対するCheckerの挙動(V2/V3でBLOCKINGへ戻るか、QUALITY/ACCEPTABLEのままか)自体を観察材料とする |
| B1(原油→ガソリン価格ブリッジ文) | MAJOR(unsupported_new_claim中心) | ACCEPTABLE候補 | **暫定+要確認** | 4回独立発生・JA Writer Prompt自身が要求する構造(v0.2§1-A)、Part B「過剰品質はB-1が最有力候補」。ただし「一般常識」と「新規の具体的主張」の境界基準は依然LLM次第(v0.2§6-2) |
| B3(接続詞"so") | MAJOR(changed_causality、HF-007) | **?(要確認)** | **暫定+要確認** | v0.2§6-1機械適用結果は「STAY BLOCKING」(条件を満たさない)。Part B独立評価も「境界だが緩和には慎重派」。本書はこの2つの先行評価に基づき暫定的にBLOCKING寄りとするが、最終判断はユーザー/Fable |
| B4(Meta一般化3件) | MAJORx2〜3(gold4件中) | **?(要確認)** | **暫定+要確認** | Part B「新設計で緩めた場合に現状より品質が下がる可能性がある」との懸念。既存retry機構で最終的にCOMPLIANTまで解消済みという実績あり(投資REPORT B-4行) |
| Meta_run03_standard | MAJOR(gold fact_id=MUSE-HC-010)、gpt-6検出はfact_id=MUSE-HC-012 | BLOCKING(いずれのfact_idでも実際の逸脱) | **暫定+要確認(fact_id 010/012のどちらを正とするか)** | V0 Phase B-10 USER_DECISION_REQUIRED候補そのもの。「別のclaimを検出しただけ」か「別の理由でMAJORになった」かは本Trialのデータのみでは切り分け不可 |

---

## 3. Family X限定variant(Production非接続、`er051_open233_checker_trial_variant_01.py`新規)

### 3-1. post-hoc v2

既存`_apply_deviation_post_hoc_validation()`(`er003_v1_en_direct_vfl_01_
generate.py:544-561`、MAJOR→MINOR自動降格のみ)の出力を**入力として受け取り**、
新たに`severity_final`/`action`/`basis`/`rule_id`を追加する
`classify_deviation_trial()`関数として実装する(vfl01自体は無変更、import
のみ)。

昇格ルール(ユーザー決定2): `changed_actor`/`changed_number`/
`changed_negation`/`changed_comparison`のいずれかがtrueかつ既存severityが
MINORの場合、`severity_final=BLOCKING`・`rule_id="promote_deterministic_
flag_v1"`とする。

判定ロジック(優先順位):
1. 既存`severity=="MAJOR"` → `severity_final="BLOCKING"`、
   `rule_id="existing_major_v2"`、`action="STOP"`(fail-closed維持、
   ユーザー決定1「BLOCKING=従来どおりfail-closed」)。
2. 上記に該当せず、4カテゴリいずれかのflag=trueで既存severityがMINOR
   → `severity_final="BLOCKING"`(昇格)、`rule_id="promote_deterministic_
   flag_v1"`、`action="STOP"`。
3. 上記いずれにも該当しない(=MINORかつ4カテゴリ非該当) →
   variant別のQUALITY/ACCEPTABLE判定(下記3-2〜3-3)。**「causality-only
   & origin!=ja_source→demote」というorigin基準の非STOP化ルールは
   実装しない**(v0.2§1-E/§6-1が実データで確認した「JA段origin=None
   誤降格の罠」を踏襲、origin fieldは分類ロジックの入力に使わない)。

`basis`フィールド: BLOCKING時は`"ledger_fact"`(既存10カテゴリ判定)または
`"deterministic_flag"`(昇格ルール由来)、QUALITY/ACCEPTABLE時は
下記3-2の`ledger_field_basis`をそのまま転記(schema variant未使用のV1では
`"model_minor_no_schema_signal"`固定)。

### 3-2. schema variant(Trial出力schema、Production schema不変)

`deviation`項目へ以下4フィールドを追加する拡張schema
(`_extended_deviation_item_schema()`を模した`_trial_deviation_item_schema()`
として`er051`内に新設、`DEVIATION_JSON_SCHEMA`自体は変更しない):

| フィールド | 型 | 内容 |
|---|---|---|
| `qualifier_present` | boolean | claim自体またはその前後1〜2文に限定語・留保文が存在するか |
| `qualifier_text` | string | 該当箇所(存在しない場合は空文字列) |
| `ledger_field_basis` | enum("ledger_fact","notes_factual_constraint","notes_writer_guidance","none") | 判定根拠がFact本体フィールドか、notesのfactual_constraintか、writer_guidanceか |
| `observation_consistent` | boolean | 記事の最終理解がLedgerの観測と矛盾しないか |
| `matched_notes_id` | string | 根拠にした notes に対応するfact_id(該当なしは空文字列) |

Ledger入力側の分離: Researcher出力の`notes_for_writer`を、Trial内で
**手動分類**する(委任文どおり、Hormuz 12件はPart B分類[全件factual_
constraint]を使用、Meta Ledger 15件[MUSE-HC-001〜015]は本Phase Aで
新規分類、下表)。「factual_constraintのみ渡す」variant(V3)と「現行どおり
全量渡す」variant(V2)を用意する。

**Meta Ledger notes_for_writer 15件分類(本Phase Aで新規実施)**:

| fact_id | notes_for_writer要旨 | 分類 |
|---|---|---|
| MUSE-HC-001 | Meta公式発表に基づく仕様、独立検証ではない | factual_constraint(確実性の境界) |
| MUSE-HC-002 | 機能の存在≠実際の性能・成功率 | factual_constraint(scope/確実性) |
| MUSE-HC-003 | Meta自身の設計説明、請負業者への情報共有範囲の直接資料ではない | factual_constraint(scope) |
| MUSE-HC-004 | Reuters報道の転載、Meta公式ページでは詳細確認不可 | factual_constraint(出典/確実性) |
| MUSE-HC-005 | 8月開始は社内投稿由来の報道、公式発表日と混同しない | factual_constraint(時系列) |
| MUSE-HC-006 | 「全ての電話」と書かない、「一部」「テスト」と限定 | factual_constraint(scope) |
| MUSE-HC-007 | 50%を全従業員比率として断定しない | factual_constraint(numeric_scope) |
| MUSE-HC-008 | 「人間の方が95〜98%成功」と一般化しない、因果・有意性は未確認 | factual_constraint(numeric_scope+causality) |
| MUSE-HC-009 | 「AI電話は一般に切られる」と拡張しない | factual_constraint(scope) |
| MUSE-HC-010 | 懸念の存在≠大規模な情報漏えいの断定 | factual_constraint(確実性、B4/A4に直結) |
| MUSE-HC-011 | 契約スタッフ全体・実験全体へ一般化しない | factual_constraint(scope) |
| MUSE-HC-012 | 「サービス全体を停止」と書かない、対象は人間コンシェルジュ機能 | factual_constraint(scope/fact、A5に直結) |
| MUSE-HC-013 | 広報担当者の説明として記録、客観的満足度measureと扱わない | factual_constraint(確実性/出典) |
| MUSE-HC-014 | 公開済み一般機能とロールバック済み実験を区別 | factual_constraint(scope) |
| MUSE-HC-015 | 公式設計説明と実験時の実際運用を混同しない | factual_constraint(scope) |

**分類結果: Meta Ledgerも15件中15件がfactual_constraint、0件が
writer_guidance**。Hormuz(12/12)と合わせ、本Trial対象2 Ledger合計
27件中27件がfactual_constraintであり、v0.2§8が指摘した「Ledgerの
notes_for_writerは実質的にscope/causality/certaintyという既存10カテゴリの
境界情報そのものである」という観察が、Meta Ledgerでも再現された
(観察、断定はしない。他Family・他記事は本Phase A未確認)。この結果、
**V3(factual_constraintのみ渡す)とV2(全量渡す)は、対象2 Ledgerに限れば
実質的に同じ入力になる**(writer_guidanceが0件のため差が出ない)。
V2/V3の差はTrial実行時にこの2 Ledger限定では観測されない可能性が高い
ことをリスクとして明記する(下記8章)。

### 3-3. Prompt variant(Family X限定、共通Prompt不変)

`vfl01.DEVIATION_PROMPT_TEMPLATE`を**importしてそのまま使用**し、Trial側で
文字列連結により差分ブロックを追加する(`vfl01`のグローバル定数自体は
書き換えない)。差分ブロック本文(`TRIAL_PROMPT_DIFF_BLOCK_V01`、
`er051_open233_checker_trial_variant_01.py`内定数):

```
(改行)
【Family X限定 Trial追加指示(OPEN-233-CHECKER-REDESIGN-TRIAL-01、Production非適用)】
- claim単体だけでなく、その前後1〜2文の限定語・留保文(qualifier/hedge)を踏まえて、
  記事の最終的な理解がVerified Fact Ledgerの観測と矛盾しないかをobservation_consistentとして
  判定してください。
- 限定語・留保文(例: "may", "some", "temporarily", "briefly"等およびその訳語)がclaim自体
  またはその前後1〜2文に存在する場合、qualifier_presentをtrueとし、該当箇所をqualifier_text
  に記録してください。存在しない場合はfalseとし、qualifier_textは空文字列にしてください。
  留保文が存在するだけで機械的にobservation_consistent=trueにはしないでください
  (定型ヘッジによる免罪符化を禁止します)。
- Verified Fact Ledgerのnotesには、判定根拠として使用すべき禁止・限定事項
  (factual_constraint)が含まれる場合があります。判定の根拠がfactual_constraintの記述と
  一致・矛盾する場合はledger_field_basisを"notes_factual_constraint"とし、一致する
  fact_idをmatched_notes_idに記録してください。Factの本体フィールド
  (claim/scope/numeric_value/causal_strength等)のみを根拠にした場合はledger_field_basis
  を"ledger_fact"としてください。
- writer_guidance(トーン・文体等の執筆助言であり、factual_constraintではないもの)は
  判定根拠として使用しないでください。
- 各deviationについて、qualifier_present/qualifier_text/ledger_field_basis/
  observation_consistent/matched_notes_idを必ず出力してください。
```

sha256(この差分ブロック文字列そのもの、`\n\n`込み):
`c7195a19fae043096318bfac3bac88327de1e522ab5fbddae6de53ea1f4efa80`
(文字数1017、概算token数は§5参照)。この差分ブロックは`DEVIATION_PROMPT_
TEMPLATE`の末尾(【判定ルール】節の後)に追加する形で連結する。
`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`と同じ「import + 文字列連結」方式
であり、v0.2§10-4が指摘した「Family横断で同時波及する」リスクを回避する
(Production側`vfl01.DEVIATION_PROMPT_TEMPLATE`自体は一切書き換えない)。

### 3-4. variant一覧

| 構成ID | Prompt | Schema | post-hoc | notes入力 | 新規API呼び出し要否 |
|---|---|---|---|---|---|
| V0 | 現行(vfl01) | 現行(vfl01) | 現行(vfl01のまま) | 全量(現行どおり) | **不要**(GPT-6 Trial実測結果[84 call]を再利用、再実行しない) |
| V1 | 現行(vfl01) | 現行(vfl01) | post-hoc v2(昇格のみ、schema変更なし) | 全量(現行どおり) | **不要**(V0と同一Prompt/Schemaのため、V0で保存済みの`raw_parsed`を`classify_deviation_trial()`へ再適用するだけで計算可能。新規API呼び出しゼロ) |
| V2 | Prompt variant(差分ブロック追加) | schema variant(4フィールド追加) | post-hoc v2(QUALITY/ACCEPTABLE分岐込み) | 全量 | **必要**(Prompt/Schemaが変わるため) |
| V3 | V2と同じ | V2と同じ | V2と同じ | factual_constraintのみ(Hormuz/Metaとも実質全量と同じ、上記3-2参照) | **必要**(V2と別呼び出し。ただし3-2の理由で挙動差が出ない可能性が高い) |

### 3-5. mock test(`er051_open233_checker_trial_variant_01_test_01.py`)

Production(vfl01)を一切変更せずimportのみで動作することをテストで証明する
(実行結果は下記6章、実際のテスト結果は本委任の実行ログに記載)。

- 既存run json(V0で保存済みの`er050_output/.../step1/**/gpt-6-luna/run_1.json`
  等、67件のdeviationレコードの母集団と同じ実データ)へ`classify_deviation_
  trial()`を適用し、以下を検証:
  - 誤昇格0件(既にBLOCKINGでないもの[MINOR]が、4カテゴリ非該当なのに
    BLOCKINGへ誤って上がらないこと)
  - A群(er009 9種+A2A3+A4+A5)がすべて`severity_final=="BLOCKING"`を維持
    すること
  - JA段(`hormuz_run03_ja_original`/`hormuz_run03_ja_r2`、origin概念なし)
    のcausality-onlyレコードが、origin=Noneであることを理由に誤って
    ACCEPTABLE/QUALITYへ降格しないこと(=分類ロジックがorigin fieldを
    一切参照しないことをコードレビュー的にも構造的にも保証)
  - changed_actorのflag=true・severity=MINORの12件(v0.2§5「8件」+
    n=5反復5件相当)が全て`severity_final=="BLOCKING"`へ昇格すること
- Production関数(`vfl01._apply_deviation_post_hoc_validation`/
  `vfl01.DEVIATION_PROMPT_TEMPLATE`/`vfl01.DEVIATION_JSON_SCHEMA`)の
  sha256が本委任実行前後で不変であることを検証(Dangling Reference確認、
  下記8章)。

---

## 4. Trial構成・反復回数

モデルは`gpt-6-luna`のみ(ユーザー決定7)、reasoning="high"(現行と同一)。

**重要な設計上の発見**: V0とV1はPrompt/Schemaが完全に同一であるため、
V1はAPI呼び出しを新たに必要とせず、V0で既に保存済みの84 call分の
`raw_parsed`(`er050_output/gpt6_checker_comparison_trial_01/**/run_*.json`)
へ`classify_deviation_trial()`を後から適用するだけで計算できる
(call数0、費用$0)。新規API呼び出しが必要なのはV2/V3のみ。

| Step | 対象fixture | V0 | V1 | V2 | V3 |
|---|---|---|---|---|---|
| Step1(重大群) | er009 9種+A2A3+A4+A5(12) | 再利用(0 call) | 再利用(0 call) | 12 call | 12 call |
| Step1(changed_actor n=5) | er009_changed_actor(5反復) | 再利用(0 call) | 再利用(0 call) | 5 call | 5 call |
| Step2(境界群) | B1/B2/B3/B4/Meta_run03_standard(5) | 再利用(0 call) | 再利用(0 call) | 5 call | 5 call |
| Step3(非決定性群、最良variantのみ) | hormuz_run03_ja_original/ja_r2/advanced/standard×n=5(20) | 再利用(0 call、V0比較用) | (Step1/2でSafety/Productivity要件を満たせばV1のみ再利用でも可、満たさなければV2/V3のいずれか1つを新規実行) | 条件付き20 call | 条件付き20 call |

**実行順序(条件分岐)**:
1. Step1をV1(0 call)で計算し、Safety(BLOCKING維持率)を確認。V1で
   Safety 100%未達なら、V2/V3を実行してSafety改善を確認する
   (昇格ルールだけでは不十分な場合、schema/Prompt variantの寄与を見る)。
2. Step1でSafety 100%未達のvariantは、そのvariantに限りStep2/Step3を
   実行しない(委任文の受入条件、下記6章)。V0/V1がSTOP対象になっても
   Trial全体は続行する(V2/V3を評価対象として残す)。
3. Step2をSafety合格variant(複数可)についてV2/V3のみ新規実行
   (V0/V1は既存データ再利用)。不要BLOCK率を算出。
4. Step3は、Step1+Step2で最もSafety+Productivityの評価が良い「最良
   variant」1つのみをn=5で新規実行し、V0(GPT-6 Trial既存実測)と比較する。

**call数合計(新規API呼び出しのみ)**: Step1(V2 12+V3 12+changed_actor
n=5×2variant=10)=34 call、Step2(V2 5+V3 5)=10 call、Step3(最良variant
1つ×20)=20 call。**合計最大64 call**(V0/V1は0 call)。全variant全stepを
実行した場合の上限であり、Safety未達variantの打ち切りで実際にはこれより
少なくなる可能性が高い。

---

## 5. 正式費用見積

`gpt-6-luna`正式単価(`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Closeout
C-2、Standard/Short context): Input $0.10/1M・Cached input $0.01/1M・
Output $0.50/1M(reasoning tokenはoutput側に含む、二重計上なし)。為替
¥156.88/USD(Frankfurter API、2026-09-28付)。

**トークン見積方法**: V2/V3は新規callのためトークン実測が存在しない。
V0(gpt-6-luna)で同一fixtureに対して実測済みのinput/output token数を
ベースラインとし、(a) Prompt variant差分ブロック(1017文字)による
input token増分、(b) schema variant追加5フィールドによるoutput token増分
を保守的に上乗せする概算を用いる。tiktoken未導入のため、既存3 fixture
(B1/A2A3/B4)の実測`prompt`文字列長とinput_tokensの比(1.523〜2.009
文字/token)から、**保守的(高コスト側)な1.5文字/token**を採用し、
差分ブロック(1017文字)の増分を**約680 token/call**と見積る。schema
variant出力増分は各deviationあたり5新規フィールド分、fixtureあたり
平均1〜3 deviationsと仮定し**約150 token/call**(保守的)と見積る。

| Step | variant | 対象call数 | input token計(V0実測+680/call) | output token計(V0実測+150/call) | 費用(USD) | 費用(JPY) |
|---|---|---|---|---|---|---|
| Step1(12 fixture) | V2 | 12 | 61,365+8,160=69,525 | 16,502+1,800=18,302 | $0.006953+$0.009151=$0.016104 | ¥2.526 |
| Step1(12 fixture) | V3 | 12 | 同上(保守的に同一と仮定、notes削減効果は見込まない) | 同上 | $0.016104 | ¥2.526 |
| Step1(changed_actor n=5) | V2 | 5 | 25,125+3,400=28,525 | 5,992+750=6,742 | $0.002853+$0.003371=$0.006224 | ¥0.976 |
| Step1(changed_actor n=5) | V3 | 5 | 同上 | 同上 | $0.006224 | ¥0.976 |
| Step2(5 fixture) | V2 | 5 | 26,197+3,400=29,597 | 20,161+750=20,911 | $0.002960+$0.010456=$0.013415 | ¥2.105 |
| Step2(5 fixture) | V3 | 5 | 同上 | 同上 | $0.013415 | ¥2.105 |
| Step3(最良variant、20 call) | V2またはV3のいずれか1つ | 20 | 101,745+13,600=115,345 | 42,123+3,000=45,123 | $0.011535+$0.022562=$0.034096 | ¥5.350 |

**合計(全variant全step実行時の上限、Step3は1variantのみ)**:
USD = $0.016104×2+$0.006224×2+$0.013415×2+$0.034096 = **$0.104578**、
JPY ≈ **¥16.406**。V0/V1は$0(再利用)。

**Guardrail案**:
- 合計上限: **¥50**(概算¥16.4の約3倍、余裕を持たせる)。
- Step別上限: Step1(V2+V3+actor n=5)¥8、Step2(V2+V3)¥6、Step3¥12
  (各段の概算の約2倍、ユーザー決定9「想定の2倍でSTOP」に整合)。
- 段階発火: 各API呼び出し後に累計を`budget_state.json`(既存er050
  harnessと同形式)へ記録し、Step別上限到達で当該Step以降のcallを中止
  (既実行分は保存)。
- 合計¥50到達で即STOP(Trial全体中止、既実行分は保存)。
- この見積は**推定**であり、実際のtoken数(特にschema variant出力の
  実際の増分)は未実測のため保守率を含む。2倍を超過した時点でSTOPし、
  ユーザーへ報告する。

---

## 6. 受入条件(確定案)

- **Safety**: 重大fixture群(ER-009-N1 9種+A2A3+A4+A5、changed_actor
  n=5は別枠)のBLOCKING維持率**100%**(1件でも`severity_final!=
  "BLOCKING"`なら不採用)。changed_actorは**post-hoc v2の昇格ルール込みで**
  n=5全件が`severity_final=="BLOCKING"`となることを要求する(V0で
  MISSしていた3/6→本Trialでは昇格ルールにより理論上5/5全件BLOCKING化
  されるはず、V1段階[0 call]で事前確認可能)。A-1は分母から除外
  (1-1節の提案どおり、★要確認)。
- **Productivity**: 不要BLOCK率(1-2節の定義)**≤25%**(baseline 75%から
  明確な改善)。
- **Stability**: Step3非決定性群の一致率(gold既知2fixture[advanced/
  standard]のgold一致率平均)が**V0(gpt-6-luna実測、90%)以上**。
- **QCD**: 記事換算(4 call相当)cost・latency中央値・retry・STOP率を
  V0と比較。costは**V0の1.5倍以内**(案、根拠: V0のgpt-6-luna記事換算
  コストは¥0.8173[C-3実測]。Prompt/schema拡張による増分を見込んでも
  1.5倍[¥1.226]以内に収まる想定[本書§5概算のtoken増分率は約13〜27%
  程度]であり、実測が1.5倍を超えた場合は「新schemaのoutput token増分が
  想定より大きい」ことを示すシグナルとして扱う)。
- **受入目的の明記**: 「過剰品質によって Production 生産性を失わない」
  (ユーザー決定9)。Safety(重大見逃しを増やさない)を絶対条件とした上で、
  Productivity改善(不要BLOCK率低下)とStability/QCDの許容範囲内の変化を
  もって採用候補とする。**本Phase Aでの受入条件確定はTrial実行後の
  評価基準であり、Trial結果自体を先取りしない**。

---

## 7. STOP条件

- 予算超過見込み(Step別上限またはGuardrail合計¥50到達)。
- API error継続(既存er050 harnessと同じ、累計5 call以上でerror率
  20%超過)。
- schema非互換(`text.format.type=json_schema`+`strict:true`で
  拡張schemaが受理されない等)。
- harness不具合(fixture読み込み失敗、Prompt再構成の不一致等)。
- fixture破損(sha256不一致、本書§1記載値との差分検出)。
- Production影響(vfl01のグローバル定数sha256が実行前後で変化、
  Dangling Reference検出)。
- **Safety 100%未達**: 当該variantのみ打ち切り、Trial全体は続行する
  (委任文の設計どおり、V2がSafety未達でもV3の評価は続ける)。
- **goldの再判断が必要な判定割れ**(下記USER_DECISION_REQUIRED候補):
  B3/B4/Meta_run03_standardのgold未確定、A-1の分母除外提案、B2_hormuz
  暫定QUALITYラベルの最終化。Claudeはこれらのgoldを独自に書き換えない。

---

## 8. 既存仕様との競合・Dangling Reference確認・リスク・★ユーザー判断

### 8-1. Dangling Reference確認(設計)

`er051_open233_checker_trial_variant_01.py`は`er003_v1_en_direct_vfl_01_
generate.py`を**importのみ**で使用し(`DEVIATION_PROMPT_TEMPLATE`/
`DEVIATION_JSON_SCHEMA`/`run_deviation_check`等を読み取り専用で参照)、
vfl01のモジュールレベル定数・関数を一切上書き・monkeypatchしない設計とする
(`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`が`DEVIATION_PROMPT_TEMPLATE`を
`.replace()`で新しい文字列を作る既存パターンと同じ手法)。mock testで
vfl01側3定数のsha256が実行前後で不変であることを検証する(§3-5)。

### 8-2. 既存仕様との競合

| 既存決定 | 競合点 | 本Phase Aでの扱い |
|---|---|---|
| fail-closed設計(origin=ja_source即STOP) | QUALITY層導入はfail-closed適用範囲をBLOCKINGに限定する実質緩和(v0.2§7-4) | Trial variantのみに限定、Production側の`vfl01.run_deviation_check()`・呼び出し元(`er012_e...py`/`er019...py`)は無変更。Production配線は本Trialのスコープ外 |
| 案B(ja_source MAJOR時のJA差し戻し1回retry、APPROVED_FOR_PRODUCTION・Gate3待ち) | 3層化導入時、案Bが発動する条件が変わる可能性(v0.2§7-7) | 本Trialは案Bのコード(`build_must_fix_block()`)を呼ばない(er051はvfl01の`run_deviation_check()`のみ呼び出す独立harness) |
| JA Fact Check配線決定(2026-09-27、PRODUCTION_WIRED) | Action判定部分の事実上の再設計になりうる | Production側の当該配線は無変更、Trialは別スクリプト(er051)・別出力先(`er051_output/`)で完結 |
| OPEN-233自体(2026-09-29 REOPENED (ACTIVE)) | Trial結果がOPEN-233の再評価材料になる | 本Phase AはTrial計画確定のみで再評価判断はしない(委任文ユーザー決定10) |

### 8-3. リスク

- V2/V3の差(notes全量 vs factual_constraintのみ)が、対象2 Ledger
  (Hormuz/Meta)ではいずれも27/27件がfactual_constraintのため**観測されない
  可能性が高い**(§3-2)。差を検証するにはwriter_guidance比率が高い別
  Ledger/別記事が必要だが、本Phase Aでは追加fixtureを作らない方針
  (委任文の制約)のため、この論点は「制約」として明記するに留める。
- token見積(§5)はtiktoken未導入のため文字数比率による概算であり、
  実測との乖離リスクがある(Guardrail 2倍で対応)。
- gold未確定のfixture(B3/B4/Meta_run03_standard)が多く、Step2の
  Productivity評価(不要BLOCK率)の「正解」自体が本書時点では確定して
  いない。Trial実行結果を見てもgoldが確定しなければ、受入条件の判定が
  保留になるリスクがある。
- Safety群のうち`changed_number`/`changed_negation`/`changed_comparison`
  は実運用データではなく合成fixtureのみでの評価(v0.2§13既述の制約を
  継承)。

### 8-4. ★ユーザー判断が必要な事項

1. A-1をBLOCKING維持率の分母から除外する提案(§1-1)の承認。
2. B3/B4/Meta_run03_standardのgold最終値(§2「暫定+要確認」の解消)。
3. B2_hormuzの暫定QUALITYラベル(ユーザー決定4)を、本Trial結果を踏まえて
   最終化するタイミング(Trial実行後か、別途か)。
4. §5の費用見積・Guardrail案(合計¥50、Step別上限)の妥当性。
5. V2/V3の差が対象Ledgerでは観測されない可能性が高いという§8-3の
   リスクを踏まえ、Trial実行の優先度(V2/V3両方実行するか、片方に
   絞るか)。
6. Trial実行の正式開始可否(本Phase A完了後、実行前STOP)。

---

## 2-補. Phase A要確認事項の解決(Fable判定、委任_02)

2026-09-29ユーザー更新判断1〜15(逐語は`docs/pm/delegation_log/2026-09-29_
OPEN-233-CHECKER-REDESIGN-TRIAL-01_02.md`参照)を受け、Fableが§8-4の★6件を
以下のとおり判定した(Claude/Sonnetは独自にgoldを確定しない原則を維持)。

1. **A-1(§1-1)**: 再実行不可のため参考記録のまま維持し、BLOCKING維持率の
   分母から除外する(REPORTに明示開示)。
2. **gold(B1/B3/B4/Meta_run03_standard)**: 既存暫定goldを変更しない。
   不要BLOCK率の定義は本書§1-2の既存定義(B1/B2_hormuz/B3/B4の4件のうち
   BLOCKING維持数/4、baseline 75%・目標≤25%と同一根拠)を維持する。B3/B4への
   Part B「BLOCKING妥当」異見はgold変更ではなく**リスク欄**に記録し、Trial結果で
   「≤25%達成にB3/B4の通過が不可欠」かつ「その通過がSafety上不当」と分析される
   場合のみ、終了時にgold再判断(ユーザー判断11)として報告する。B1=ACCEPTABLE
   候補(暫定)。
3. **B2_hormuz**: QUALITY暫定のまま維持。最終化はTrial後(ユーザー判断6)。
4. **Meta_run03_standard**: negative control。fact_id 010/012いずれでも
   「実逸脱をBLOCKINGと判定」すれば検出成功とし、fact_id差異は観測として
   記録する(gold変更なし)。
5. **Guardrail**: Trial 1(委任_02)単体¥50、Step別上限はPhase A案
   (Step1¥8/Step2¥6/Step3¥12)をそのまま採用。総枠¥400(累計管理)。
6. **V2/V3**: 両方実行する(差が出ない可能性は承知の上で観測データを取る)。
7. **実行前STOP**: 撤回。承認済み範囲内でPhase A→Trial→分析→改善→再Trialまで
   進めてよい(ユーザー判断8)。

## 3-補. Trial 1実行結果(委任_02、2026-09-29)

**実行**: `er051_open233_checker_trial_01_run.py`(新規、Trial専用harness、
Production/Model Routing Contract非経由)。モデル`gpt-6-luna`、
reasoning="high"。

### Step1(重大群12 fixture、V2/V3各12 call)

**結果: Safety 100%達成(V2/V3とも)**。12 fixture全てで`overall_action_
trial=="STOP"`、全deviationが`severity_final=="BLOCKING"`(MAJORは
`existing_major_v2`、changed_actor 1件がMINORで`promote_deterministic_
flag_v1`により昇格)。費用¥5.8145(24 call)。

### Step1(changed_actor n=5、V2/V3各5 call)

**結果: Safety未達(V2/V3とも)**。

| variant | attempt1 | attempt2 | attempt3 | attempt4 | attempt5 | BLOCKING率 |
|---|---|---|---|---|---|---|
| V2 | MAJOR→BLOCKING | MINOR→BLOCKING(昇格) | **MINOR→ACCEPTABLE(未昇格)** | MINOR→BLOCKING(昇格) | MAJOR→BLOCKING | **4/5(80%)** |
| V3 | MAJOR→BLOCKING | MAJOR→BLOCKING | **MINOR→ACCEPTABLE(未昇格)** | MAJOR→BLOCKING | **MINOR→QUALITY(未昇格)** | **3/5(60%)** |

受入条件(§6)「changed_actorはpost-hoc v2の昇格ルール込みでn=5全件が
`severity_final=="BLOCKING"`」を**V2・V3とも未達**。費用¥1.4737(10 call)。
Step1合計費用: ¥7.2882(34 call、0 error)。

### 原因切り分け(未昇格3件の実データ、V2#3/V3#3/V3#5)

3件とも共通パターン: LLMが返した`changed_actor`フラグが**false**(fixtureの
真の逸脱カテゴリはchanged_actorだが、LLMは`unsupported_new_claim=true`
[+一部`changed_fact=true`]として分類し、severityもMAJORではなくMINORと
判定)。

```
V2#3: severity=MINOR changed_actor=False changed_fact=False unsupported_new_claim=True -> ACCEPTABLE
V3#3: severity=MINOR changed_actor=False changed_fact=True  unsupported_new_claim=True -> ACCEPTABLE
V3#5: severity=MINOR changed_actor=False changed_fact=True  unsupported_new_claim=True -> QUALITY
```

対照的に、成功した7件(V2#1,2,4,5/V3#1,2,4)は全て`changed_actor=True`が
正しく返っており、昇格ルール(`promote_deterministic_flag_v1`)またはMAJOR
(`existing_major_v2`)によって確実にBLOCKINGへ到達している。

**原因分類: (a) Promptの判定基準**。決定論的昇格ルール自体は「flagが立てば
確実にBLOCKING化する」という設計どおり100%機能している(7/7)。問題は
昇格ルールの**手前**、LLMが実在しない機関名(fixtureでは実在の研究者名
"Kareem Haggag and Giovanni Paci"をLedgerが保持するのに対し、記事側は
"A team at Harvard Business School"と主体を差し替えている)を「主体の
変更(changed_actor)」ではなく「Ledgerに無い新規主張(unsupported_new_
claim)」として分類する、カテゴリ境界の曖昧さにある。現行
`DEVIATION_PROMPT_TEMPLATE`の10カテゴリ定義は、changed_actorと
unsupported_new_claimの重複(「Ledgerに存在しない主体」は両方の定義に
該当しうる)を明示的に排他化していない。schema自体([10フラグ]は
Boolean配列として両方trueにできる構造)は情報不足ではなく、Promptが
「主体の差し替えは常にchanged_actor=trueを立てる(unsupported_new_claim
と同時にtrueにしてよい)」という優先順位を指示していない点が根本原因。

**(b) 昇格ルールの射程**: 4カテゴリ(changed_actor/changed_number/
changed_negation/changed_comparison)ベースの昇格ルールは、対象カテゴリの
flagが正しく立った場合のみ機能する「必要条件は満たすが十分条件ではない」
設計であることが実データで確認された。flag自体の精度に依存するため、
flag精度が100%でない限りSafety 100%は保証されない。

### Step2/Step3: 未実行(本委任、理由明記)

設計書§4「Step1でSafety 100%未達のvariantは、そのvariantに限りStep2/
Step3を実行しない」に従い、V2・V3とも**changed_actor n=5でSafety未達**の
ため、Step2(境界群5 fixture)・Step3(非決定性群20 call)は**両variantとも
実行しなかった**(委任文の明示ルールを厳守、予算温存目的の拡大解釈はしない)。
このため、Trial 1では境界群(B1-B4/Meta_run03_standard)へのV2/V3適用に
よる不要BLOCK率の実測データは得られていない。

参考(¥0、既存V0データreplay): V1(post-hoc v2のみ、schema/Prompt不変)を
B1-B4へ適用すると、不要BLOCK率は**75%→75%で変化なし**(B1/B3/B4は全て
既存severity=MAJORのため、fail-closed規則[ユーザー決定1]によりpost-hoc
層のどのvariantでもBLOCKING固定であり、post-hoc層だけでは改善不可能。
Productivity改善の全てはV2/V3のPrompt/schema変化が**LLM自身の一次severity
判定**をMAJOR→MINORへ動かすかどうかに懸かっている)。この一次severity
依存性は、Step2実行なしでは検証できない重要な未検証事項として明記する。

### V4設計案(実装・実行はしない、次委任向け)

**V4-A(最優先、低リスク)**: Trial Prompt差分ブロック(`TRIAL_PROMPT_DIFF_
BLOCK_V01`)へ以下を追加する案:「記事内の主張が、Verified Fact Ledgerの
`subject`と異なる人物・団体・機関に行為や発見を帰属させている場合は、
それが新規情報([unsupported_new_claim])に見えても必ず`changed_actor`も
trueにしてください(両方trueで構いません、主体の差し替えを
unsupported_new_claimだけに分類しないでください)」。狙い: カテゴリ境界の
曖昧さを直接解消し、昇格ルールの「射程」問題(上記(b))を、昇格ルール自体を
変えずにflag精度側で解決する。B群(境界・過剰品質群)は主体差し替え事例を
含まないため、Productivityへの悪影響は低リスクと想定(ただし未検証、
Trial 2でB群への副作用有無を確認要)。

**V4-B(要追加検証、中リスク)**: 昇格ルールを
`unsupported_new_claim==true and severity==MINOR`にも拡張する案。
V0のB群実データでは`unsupported_new_claim=true`はB1/B4/Meta_run03_standard
に頻出するが**いずれもseverity=MAJOR**(既にBLOCKING、fail-closedで昇格
不要)であり、MINORでの出現は本Trialの母集団(V0 B群4件+今回のSafety群)
では未観測。ただしB群はn=1実測のみで非決定性が高いことが既知(§1-3)の
ため、`unsupported_new_claim`単独昇格はB群のBLOCKING率をさらに押し上げ
(既に75%)、Productivity目標(≤25%)の達成を一段と困難にするリスクが
高い。**materiality条件**(Ledgerのsubjectフィールドと明確に異なる固有
名詞が含まれる場合のみ昇格、単なる補足情報の追加は対象外とする等)を
併用しない限り採用しない。

**V4-C(regression fixture案)**: 本Trialで得た3件の未昇格実データ
(V2#3/V3#3/V3#5、`er051_output/open233_checker_trial_01/trial_01/
step1_changed_actor_n5/er009_changed_actor/{V2,V3}/run_{3,5}.json`)を
「既知の未昇格例」としてfreeze保存し、V4-A適用後の再TrialでこれらのLLM
出力パターン(changed_actor=false+unsupported_new_claim=true+severity=
MINOR)が実際に解消されたか照合するnegative regression fixtureとして
再利用する(新規API呼び出しなしで、Prompt改訂の効果を過去の実失敗例に
対して机上検証できる)。

### Opus L2投入条件(該当有無、投入はしない)

ユーザー決定9の8条件のうち、明確に該当するものはない(deterministic false
positiveは0件、fail-closed自体は7/7で正しく機能、Family横断影響は未検証
[Family X限定Trialのため対象外]、同一改善の2回不達には該当しない[今回が
初回])。**候補として報告するもの**: 「結果解釈が非一意」に近い論点として、
「昇格ルールを維持したままPrompt側でカテゴリ境界を修正する(V4-A)」か
「昇格ルールの射程自体をより広いカテゴリ・条件へ拡張する(V4-B)」かの
設計判断は、Safety(見逃しをゼロにする)とProductivity(過剰BLOCKを増やさ
ない)のトレードオフに直結し、Fableの裁量判断が必要と考えられる。ただし
本委任1回のデータのみでは断定できず、Opus L2の必須発火条件(i)〜(iv)に
機械的に一致するとは判定しない(Fableの最終判断に委ねる)。

### ユーザー判断11該当の有無

**なし**。本委任はgold変更・BLOCKING対象緩和・fail-closed撤廃・Production
Prompt/schema/Validator変更・GPT-6 Luna routing変更・OPEN-233のProduction
正式採用のいずれも行っていない(V4はいずれも設計提案のみ、未実装・未実行)。

### 費用(Trial 1、委任_02)

Step1(12 fixture、V2+V3、24 call): ¥5.8145。Step1(changed_actor n=5、
V2+V3、10 call): ¥1.4737。**Trial 1合計: ¥7.2882(34 call、error 0)**。
Step2/Step3は未実行のため¥0。Phase A(委任_01)は¥0。**累計: ¥7.2882 /
総枠¥400**。詳細: `er051_output/open233_checker_trial_01/trial_01/
cost.json`。

### Status

**TRIAL1_DONE_IMPROVEMENT_PROPOSED**。Safety目標(重大fixture群100%)は
12-fixture本体では達成したが、changed_actor n=5別枠(V2 80%/V3 60%)で
未達のため、Step2(Productivity)・Step3(Stability)は実行していない
(全体のSafety/Productivity/Stability/QCD目標達成には至っていない)。
原因(LLMのカテゴリ境界曖昧さ)を特定し、低リスクなPrompt修正案(V4-A)を
設計した。次委任でV4-A実装+Trial 2(Step1 changed_actor n=5再検証、
成功すればStep2/Step3実行)を提案する。

---

## 出典一覧

- `docs/pm/design_checker_redesign_v02_01.md`(v0.2、全章)
- `OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`
- `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`(Phase B/Closeout全体)
- `er050_output/gpt6_checker_comparison_trial_01/`(84 call実測、
  `summary_step1.json`/`summary_step1_er009_changed_actor_n5.json`/
  `summary_step2.json`/`summary_step3.json`/`cost_recalc_01.json`)
- `er050_gpt6_checker_comparison_trial_01.py`(harness、fixture定義)
- `er003_v1_en_direct_vfl_01_generate.py`(`DEVIATION_PROMPT_TEMPLATE`/
  `DEVIATION_JSON_SCHEMA`/`_apply_deviation_post_hoc_validation`/
  `FACT_LEDGER_JSON_SCHEMA`/`run_deviation_check`)
- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`§3
- `docs/pm/review_ledger_deviation_redesign_01_part_b.md`
  (Hormuz notes_for_writer 12件分類)
- Meta Ledger notes_for_writer 15件分類(本Phase A新規実施、出典
  `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/
  deviation_checks/advanced_attempt1.json`のprompt埋め込みLedgerテキスト)
- delegation記録: `docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-
  REDESIGN-TRIAL-01_01.md`
