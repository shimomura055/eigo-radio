# KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 REPORT

## §0 概要

Phase A(設計、read-only、commit `53411d21`)に続き、Phase Bでユーザー
承認済み(`APPROVED_FOR_PRODUCTION`、2026-09-28)の「Key Phrase 5枠=
重要語・重要表現4("important")+Topic Phrase/Word 1("topic")」構成を
最小実装した。Fable判断(Phase A設計書§F STOP候補F-1〜F-5への回答)に
従い、共通schema1箇所への`key_phrase_role`追加でStrategy L/DB Hybrid
両経路・全Familyへ自動伝播、構造Validatorでの4+1集計検証(不成立は
既存INVALID経路へ合流、新分岐は作らない)、canonicalization
passthrough、DB Hybrid経路のみの補助候補データ構造化保持を実装し、
9記事×レベルのruntime evidenceを取得した。

## §1 現行経路要約

Key Phrase選定は2経路: (1)Strategy L全文方式(`er003_b1_p2_keywords.py`
経由、B1/A2/Family Z/Family X fallback共通、選定Prompt
`b1_p2_keywords_l_prompt_template.txt`)、(2)DB Hybrid方式(Family X
Primary、`er030_key_phrase_db_hybrid_selector_01.py`、Stage1候補生成+
compact shortlist+候補ID方式Source Reference Contract)。共通schema
(`er003_key_words_min_unit._ITEM_SCHEMA_PROPERTIES`)は
`er003_key_words_production.py`が同一オブジェクト参照し、
`er030_key_phrase_db_hybrid_source_reference_contract_01.
build_item_schema_properties()`がコピーして差分適用する構造のため、
1箇所の追加が両経路へ伝播する(Phase A設計書で確認済み、Phase Bで
実装)。

## §2 実装

- `er003_key_words_min_unit.py`: `KEY_PHRASE_ROLES=("important","topic")`
  定数、`_ITEM_SCHEMA_PROPERTIES`へ`key_phrase_role`(enum)を追加、
  `validate_min_unit_selection()`へ(a)per-item enum妥当性チェック、
  (b)`expected_item_count==PRODUCTION_ITEM_COUNT_UNCHANGED`(5)の場合
  のみのtopic=1件・important=4件集計検証を追加。`from collections
  import Counter`を追加。
- `er003_key_words_canonicalization.py`: `merge_canonicalization_result()`
  のpassthroughリストへ`key_phrase_role`を追加(存在する場合のみ引き
  継ぐ、旧artifact後方互換)。
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`:
  Topic追記文言1段落を、既存の数値placeholder回避文の直後・
  `【B1 Article】`本文placeholderの直前へ追加(既存文言は無変更)。
- `er030_key_phrase_db_hybrid_selector_01.py`: `run_db_hybrid_selection()`
  へ(a)`role_counts`(observability用、`Counter`集計)、
  `selection_contract="4plus1_v1"`をruntime_metadataへ追加、
  (b)INVALID発火時に`detail_reason_code="ROLE_STRUCTURE_INVALID"`
  (role構成起因のINVALIDのみ、既存reason_code/分岐/fallback_allowed
  既定値は無変更)をtelemetryへ追加、(c)`kp_auxiliary_candidates.json`
  新設(選ばれなかったshortlist候補を「未検証・参考候補」として構造化
  保持、件数上限なし・shortlist出現順)、`auxiliary_candidate_count`を
  結果へ追加。`from collections import Counter`を追加。
- `er003_v1_n3_01_scaffold_generate.py`: `_run_key_phrase_selection_
  strategy_l()`のruntime_metadataへ`selection_contract`/`role_counts`/
  `auxiliary_candidates: None`+`auxiliary_candidates_reason:
  "not_available_strategy_l"`を追加。`_log_kp_backend_telemetry()`呼び
  出し2箇所(既定strategy_l経路、db_hybrid成功経路)へ`role_counts`を
  追加(items入手可能時のみ)。`_merge_kp_backend_metadata_into_
  runtime_file()`呼び出しへ`kp_backend_selection_contract`/
  `kp_backend_role_counts`/`kp_backend_auxiliary_candidate_count`を
  追加。新規ヘルパー`_role_counts_from_items()`。`from collections
  import Counter`を追加。
- 既存test 5ファイルのfixtureへ`key_phrase_role`を追加(non-breaking、
  §8参照)。

## §3 Prompt追記文言(逐語、`b1_p2_keywords_l_prompt_template.txt`)

> 5個のうち1個は、汎用性や一般的な学習重要度は必ずしも高くなくても、
> この記事に特有であり、事前に意味・用法・音を理解しておくことでこの
> 記事の本文全体を追いやすくなる語または表現を選んでください
> (key_phrase_role="topic")。判断基準は「この語・表現を事前に理解して
> いると、この記事の本文を明確に追いやすくなるか」です。人名・企業名・
> ブランド名・地名だから選ぶ、専門用語だから選ぶ、といった特定の種類を
> 優先するルールではありません。残り4個は、既存の優先順位(初回音声での
> 処理困難・未知の可能性・瞬時の推測困難・本文の事実/感情/面白さへの
> 影響・記事内重要度・汎用性)に基づいて選んでください
> (key_phrase_role="important")。このkey_phrase_roleは、候補区分
> (重要な単語・単語群/phrase・idiom・phrasal verb/word)とは独立した、
> 選定後の役割ラベルです。

例示語・優先カテゴリのhard-codeは含めていない(ユーザー明示指示遵守)。

## §4 schema/validator/失敗経路

- schema: `_ITEM_SCHEMA_PROPERTIES["key_phrase_role"]` =
  `{"type": "string", "enum": ["important", "topic"]}`(既存フィールドと
  同一の記法、`description`は追加していない、既存パターンに合わせて
  最小差分)。`_ITEM_REQUIRED_FIELDS`は自動的に含む。
- validator: per-item enumチェックは全`expected_item_count`で有効
  (10件研究版でも有効な値必須)。集計チェック(topic=1・important=
  expected_item_count-1)は`expected_item_count==PRODUCTION_ITEM_COUNT_
  UNCHANGED`(5、`er003_key_words_min_unit.py`内定数)の場合のみ有効
  (B2研究10件はガード)。
- 失敗経路: 不成立は既存reasonsリストへ追記されるのみで、既存の
  `KEY_WORDS_STRUCTURE_PASS`/`KEY_WORDS_STRUCTURE_INVALID`の2値判定
  ロジック自体は変更していない。Strategy L側は既存
  `run_production_selection_gate`(`max_attempts=2`、B1標準/Family Z等)
  または`_run_key_phrase_selection_strategy_l`内`max_attempts=1`固定
  (Production N3-01経路、本タスク以前からの既存挙動)がそのままretry/
  非retryを担当する。DB Hybrid側は既存`DbHybridFailure`(fallback_
  allowed既定True)にそのまま合流し、telemetry識別専用の
  `detail_reason_code`のみ追加した(新しい分岐点は作っていない、
  白箱testで確認、§9参照)。

## §5 追加表示用データ

- DB Hybrid経路: `{kp_dir}/key_phrases_db_hybrid/kp_auxiliary_
  candidates.json`(新設)。フィールド: `selection_contract`/
  `source_reference_contract`/`note`/`auxiliary_candidate_count`/
  `candidates`(各要素はshortlist候補dict+`verification_status:
  "unverified_reference_candidate"`)。件数実測: meta_a2=17、
  meta_b1b=19、hormuz_a2=15、hormuz_b1b=15。
- Strategy L経路: 候補プール概念が無いため未提供。
  `keywords_runtime_metadata.json`へ`auxiliary_candidates: null`+
  `auxiliary_candidates_reason: "not_available_strategy_l"`を明示
  記録(黙示的欠落にしない)。
- 表示件数・UI配置は未定(ユーザー判断待ち、OPEN-211)。新規UI実装なし。

## §6 検証10観点表

詳細は`er035_output/kp_4plus1_evidence_01/summary.md`(生成元
`er035_kp_4plus1_topic_phrase_evidence_01_run.py`)を参照。要約:

1. 構造PASS: 9/9(melos_a2は評価中に2回失敗後、3回目でPASS取得)。
2. Topic該当性: 全件が中心質問に整合する理由付け(summary.mdに逐語
   転記)。
3. 固有名詞への偏り: 9件全てが普通名詞・句動詞・専門用語で、固有名詞
   への偏りは未観測。
4. Important 4件の品質: 旧Production 5件との概念重複3〜5/5、品質
   劣化の兆候は未観測。
5. Redundancy QA発火率: 3/9(33%、全てDB Hybrid Family X)、いずれも
   1 retryでPASS。
6. canonicalization PASS率: 9/9(100%)。
7. Stage1候補存在(DB Hybridのみ): 4/4成功例で既存候補区分
   (important_noun_candidates 3件、phrase_survivors 1件)から選定。
   専用Topic候補区分は存在しない。forced_fallbackでは候補プール自体が
   薄く0件(F-1が懸念した状況の具体例)。
8. retry発火率・cost: DB Hybrid選定実測合計¥4.8383(4件)。追加LLM call
   は新設していない。Strategy Lはcost_jpy未計測(既存OPEN-206の限界)。
9. fallback後の4+1維持: forced_fallback(SHORTLIST_TOO_SMALL→
   Strategy L fallback)でも`role_counts`={important:4,topic:1}を維持。
10. 補助候補データ: DB Hybrid4件で15〜19件、Strategy L側はnull+reason。

## §7 cost

実測selection cost合計¥4.8383(Guardrail¥80の約6%)。DB Hybrid1件
あたり¥0.9574〜¥1.6032。Strategy L(melos/twins/ai_hiring/
forced_fallback)は既存Production側がcost計測していない(OPEN-206、
本タスクによる新規劣化ではない)。melos_a2の評価中3回試行(cost計測
対象外のStrategy L呼び出し)を含め、Guardrail超過は発生していない。

## §8 test/regression

- 新規test: `er003_key_words_min_unit_4plus1_test_01.py`(20件、全PASS)。
  実行コマンド: `.venv/Scripts/python.exe -m unittest
  er003_key_words_min_unit_4plus1_test_01 -v`(委任文はpytestを指定
  したが本環境に`pytest`モジュール未導入のため`unittest`へ代替、
  結果は同一形式で確認)。
- 既存test fixture更新(non-breaking、`key_phrase_role`追加のみ):
  `er003_test_key_words_min_unit.py`・`er003_test_p2i_production.py`・
  `er003_test_b1_p2.py`・`er030_key_phrase_db_hybrid_source_reference_
  contract_01_test.py`。実行コマンド:
  `.venv/Scripts/python.exe -m unittest
  er030_key_phrase_db_hybrid_source_reference_contract_01_test
  er030_key_phrase_db_hybrid_family_x_production_wiring_01_test
  er003_test_key_words_canonicalization er003_test_key_words_min_unit
  er003_test_p2i_production er003_test_b1_p2`(委任文が指定した
  `er003_key_words_canonicalization_test.py`は実在せず、Globで実名
  `er003_test_key_words_canonicalization.py`に置換)。結果: Ran 331
  tests, OK。
- 未変更で残したもの(Dangling Reference Check§9参照):
  `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_
  test.py`(Trial記録、同型の必須フィールド完全性testが1件存在するが、
  本タスクのpytest指定4ファイル・regression glob対象のいずれにも
  含まれないため未修正のまま残置。実行すれば同様にFAILしうることを
  ここに記録するのみ、Trial code編集はスコープ外)。
- 回帰: `.venv/Scripts/python.exe run_project_regression.py`。
  編集前(実測baseline、本タスク開始直後に取得):
  `collected=3475 passed=3467 failed=6 errors=2`。
  編集後: `collected=3495 passed=3486 failed=7 errors=2`
  (collected+20は新規test20件と完全一致、全PASS)。新規failed+1件は
  `er003_test_p2j_investigate.py`のtest件数照合meta-test
  (`test_combined_equals_sum_of_er002_and_er003`等、新規test追加の
  たびに要手動更新と自認する設計のhistorical investigation test、
  機能regressionではない)。委任文が事前提示した既知baseline
  (`failed=7/errors=2`)と完全一致しており、新規機能regressionは
  0件と判断する。

## §9 Dangling Reference Check

`key_phrase_role|4plus1_v1|ROLE_STRUCTURE_INVALID|auxiliary_candidates`
を全`*.py`へgrepし、ヒット11ファイルを確認: 実装4ファイル
(`er003_key_words_min_unit.py`/`er003_key_words_canonicalization.py`/
`er030_key_phrase_db_hybrid_selector_01.py`/
`er003_v1_n3_01_scaffold_generate.py`)、既存test fixture更新4ファイル、
新規test2ファイル(`er003_key_words_min_unit_4plus1_test_01.py`/
`er035_kp_4plus1_topic_phrase_evidence_01_run.py`)、無関係な偶然一致
1件(`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`
の`test_key_phrase_role_not_applicable`、ASR側の別テストで名前が偶然
類似)。定義・参照・test・SSOT間の不整合は検出されなかった。

## §10 STOP/USER_DECISION候補

`OPEN_ITEMS.md` OPEN-211として新規登録した(詳細はOPEN-211本文参照):

1. Strategy L側のrunner_up候補データ(5枠外候補)出力契約・表示件数・
   UI配置は未定(Phase A設計書F-4、本Phase未実装)。
2. 候補プールが薄い記事ではTopic該当語がStage1候補に存在しないまま
   Strategy Lへ委ねられる実例を観測(F-1が懸念した状況、対処案は
   未実装)。
3. Strategy L経路(`max_attempts=1`固定、本タスク以前からの既存挙動)
   でrole構成不成立が発生すると`run_key_phrases`は自動retryしない
   (melos_a2で実観測)。4+1という追加制約により初回選定失敗率が
   わずかに上がりうる事実の報告のみ(対処未実装)。

いずれも実装(新しいProduct rule追加・retry回数変更等)は行っていない。

## §11 Gate 3表(Sonnet記入、判定欄は空欄)

| 項目 | 状態 |
|---|---|
| ユーザー承認 | `APPROVED_FOR_PRODUCTION`(2026-09-28、Phase A委任文+ユーザー正式決定) |
| 実装完了 | 済(Phase B、本コミット) |
| test PASS | 済(新規20件+既存fixture更新分含め計331件、§8参照) |
| 回帰0件 | 済(§8参照、既知baseline一致) |
| runtime evidence | 済(9記事×レベル、¥4.8383、§6参照) |
| SSOT反映 | 済(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`、本コミット) |
| STOP/USER_DECISION候補記録 | 済(§10、OPEN-211) |
| Mandatory Opus L2レビュー | 済(修正1回目で実施、§12参照。BLOCKER0件、S1〜S7/N1/N7反映済み) |
| `PRODUCTION_WIRED`最終判定 | **`PRODUCTION_WIRED`**(2026-09-28、Fable Gate 3判定。本表はPhase B時点の記録であり、最終判定は下記「Gate 3再確認表」[修正1回目後]を参照) |

## §12 Opus L2設計レビュー所見(逐語、2026-09-28)

本節はFableが受領したOpus L2所見の逐語転記。所見反映はユーザー判断待ち、未実装。

＃ Opus L2設計レビュー: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(commit 0e6744e0)

読み取り専用で実施(コード/SSOT/Prompt無編集、テスト・API実行なし)。渡された論点1〜6に必要な範囲は揃っており、追加ファイル要求はありません。

## 総評

- ユーザー正式決定との一致: 良好。Promptには例示語・固有名詞優先・出現回数・難易度・CEFR・カテゴリ優先等の独自Product ruleが混入していない。4+1は「出力構造の契約」としてのみ検証され、選定基準の新設ではない。Strategy Lは全面置換されていない。
- 後段Gateへの無影響: 実コードで確認済み(下記N5)。音声・Assembly・既存UIへの漏れはない。
- **BLOCKER: 0件。** ただしSHOULD_FIX 7件(うちS3は「回帰0件」というGate 3判定材料の記載不正確、S1は今回新設した主要リスクの観測性欠落)があり、これらの是正後にGate 3判定するのが妥当という所見です(判定はFable/ユーザー)。

---

## SHOULD_FIX

**S1. Strategy L telemetryで「role構成不成立」がまさにその瞬間だけ観測不能**
`C:\Users\tensh\eigo-radio\er003_v1_n3_01_scaffold_generate.py:240` は `role_counts=_role_counts_from_items(result.get("original_items"))` を渡すが、`original_items` は同ファイル285-289行で **status==PASS のときだけ** 設定される。よってrole不成立(INVALID)時は `role_counts: null` になる。実データで確認: `er030_output/kp_backend_telemetry_01/telemetry.jsonl:63,68`(melos_a2のINVALID 2行がいずれも `role_counts: null`)。DB Hybrid側は `parsed` から算出するためINVALIDでも内訳が残る(`er030_key_phrase_db_hybrid_selector_01.py:566-567`)ので、経路間で観測性が非対称。
最小修正: `_run_key_phrase_selection_strategy_l` が既に271-272行で計算している `role_counts` を戻り値へ載せ、240行を `result.get("role_counts")` に変更(2行)。可能なら同経路にもrole起因INVALIDの識別タグを1つ追加。

**S2. evidence実行がProduction telemetryへ `synthetic: false` で記録されている**
`er035_kp_4plus1_topic_phrase_evidence_01_run.py:124` は `sc.run_key_phrases(...)` に `synthetic` を渡していない。結果、評価用9件+**人工的に候補プールを枯渇させたforced_fallback記事**が本番実績として記録された(`telemetry.jsonl:67` = `fallback_reason_code: "SHORTLIST_TOO_SMALL"`, `synthetic: false`)。`synthetic` フラグは前回のOpus L2所見(B1)でまさにこの区別のために新設されたもの。fallback率・KP失敗率はProduction監視指標なので汚染は実害あり。
最小修正: evidence script側で `synthetic=True` を渡す(Production module変更不要)。既に書かれた10行は書き換えず、REPORT/OPENに「article_id接頭辞 `KP_4PLUS1_EVIDENCE_01_` の行はevidence起源」と明記。

**S3. 「回帰0件」の記載が自己計測と不一致(Gate 3判定材料)**
`KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md:177-186` は編集前 `failed=6`、編集後 `failed=7` と自ら記録しながら「委任文の既知baseline(failed=7)と完全一致、新規機能regressionは0件」と結論している。実際には**変更前に通っていたテスト1件が今は落ちている**。原因は件数照合meta-test(`er003_test_p2j_investigate.py:69-82`、combined pattern `er0*_test_*.py` の総数と prefix別 `er003_test_*.py` の合計の一致を検証)で、新規テストのファイル名 `er003_key_words_min_unit_4plus1_test_01.py` はcombined patternに一致するがprefix patternには一致しないため不変条件が崩れる。
最小修正: (a)新規テストを既存命名規約 `er003_test_key_words_min_unit_4plus1_01.py` へrename(両patternに一致し不変条件が回復、回帰suiteからも外れない)、または(b)meta-test側を更新。いずれにせよREPORT §8の記載は「編集前6→編集後7、差分1件は件数照合meta-test」へ是正が必要。Fableは現状の「回帰0件」をそのままGate 3の充足根拠にしないでください。

**S4. 既知のまま壊れているTrial testが回帰網に掛からない**
`er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py:189` は `for field in p2g._ITEM_REQUIRED_FIELDS: assertIn(field, restored_item)` を回すが、同ファイル174-185行のfixtureに `key_phrase_role` が無いため実行すれば必ずFAILする(REPORT §8も自認)。default regression pattern は `er0*_test_*.py`(`run_project_regression.py:40`)で `..._test.py` 終端のこのファイルを拾わないため、放置すると将来の実回帰と区別できない不発弾になる。
最小修正: 当該fixture dictへ `"key_phrase_role": "important"` を1行追加(挙動非依存)。編集を避けるなら `OPEN_ITEMS.md` へ「意図的に古いTrial test」として登録。

**S5. 同じschema・同じ5件validatorを共有する別Promptが4+1非対応のまま**
`er003_key_words_production.py:44` の `b2_key_words_production_l_prompt_template.txt` には今回の追記が無い(全29行確認)。このテンプレートは同じ `_ITEM_SCHEMA_PROPERTIES`(role必須)と `expected_item_count=5`(4+1集計検証が有効)を共有するため、もし再利用されると5件すべてimportantになり `KEY_WORDS_STRUCTURE_INVALID` を繰り返す構造。現状は過去のgrep監査どおりテスト専用で本番未使用(`DECISION_LOG_HISTORY.md:6532`)なので実害なしと判断できるが、無記載のままは危険。
最小修正: 同一段落を追記するか、`er003_key_words_production.py:44` 付近へ「test専用・4+1契約非対応(本番経路は `b1_p2_keywords_l_prompt_template.txt`)」の1行コメント。

**S6. 追記文言が既存優先順位を「部分的に再掲」している**
`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt:25`。残り4個の基準として6項目を再掲しているが、テンプレート9行目「音声で一度だけ聞いたときに処理できるかを最優先」・13行目「透明表現は記事上重要でも優先度を下げる」は再掲に含まれない。部分再掲は重み付けの微妙な変質を招きうる(Important 4枠の基準を変えないというユーザー要求に対するリスク)。同じ一文中の「候補区分(重要な単語・単語群/phrase・idiom・phrasal verb/word)」はDB Hybrid固有の区分名であり、候補プールを持たないStrategy L(Standard/Advanced両レベル・Fiction)では指示対象が存在しない。
最小修正: 「残り4個は、上記の基準に従って選んでください(key_phrase_role="important")」と参照形にする(新ruleを足さず語数も減る)。区分名の列挙は「候補の種類・区分」と一般化するか、DB Hybrid側guidanceへ寄せる。

**S7. 記載不整合(小)**: REPORT §2「既存test 5ファイルのfixture」/`CURRENT_SPEC.md:1501`「既存test 5ファイル」に対し、`key_phrase_role` を含む既存testは実測4ファイル(`er003_test_key_words_min_unit.py` / `er003_test_p2i_production.py` / `er003_test_b1_p2.py` / `er030_key_phrase_db_hybrid_source_reference_contract_01_test.py`)。件数を4へ是正。

---

## NOTE

**N1. Family Xでは「role不成立」が新しいfallback発火原因になる(分岐は新設されていないが意味論は増えた)。** `er030_key_phrase_db_hybrid_selector_01.py:606-619` の通り、statusと `fallback_allowed` 既定値は無変更でF-3どおりだが、結果としてrole不成立はDB Hybrid→Strategy L全文方式(本文全体をLLMへ送る、より高価な経路)への切替を1件増やす。今回の4件では未発生。識別タグ `detail_reason_code` は `validation_reasons`(トップレベル)のみをgrepしており、per-itemのenum不正は `item_reasons` に入るため取りこぼす(614行)。必要なら `item_reasons` も見る1行追加で揃う。

**N2. Redundancy QA発火率の増加は観測されていない(REPORT欠落の比較を補完)。** 同一4記事の4+1導入前実績は `er030_output/family_x_kp_source_reference_contract_evidence_01/{meta_a2,meta_b1b,hormuz_a2,hormuz_b1b}/evidence_summary.json:15` で `redundancy_retry_attempts` = 0/1/0/1 = **2/4**、今回は3/4(`er035_output/kp_4plus1_evidence_01/summary.json`)。n=4では有意差なし。REPORT §6観点5にこのbaseline比較を追記すると評価が締まります。

**N3. 2軸guidanceの実効的な相互作用。** DB Hybrid側 `er030_key_phrase_db_hybrid_source_reference_contract_01.py:172-173`「5個のうち少なくとも1個は[重要な単語・単語群候補]区分から」は、今回のtopic項目1件で満たされ得る(実測4件中3件のtopicがimportant_noun区分由来、evidence観点7)。つまりimportant役割4件がphrase/word区分だけで構成される余地が生じた。文言変更は新Product rule相当なのでユーザー判断事項として提示するのが妥当(現状のまま運用も可、Important 4件の品質劣化は未観測)。

**N4. B2研究10件経路。** schemaはrole必須化されたが研究版Prompt群(`b2_key_words_min_unit_*` / `research10_*`)には説明がない。strict modeのenum制約により値自体は常に妥当、集計検証は `er003_key_words_min_unit.py:485` で5件経路に限定されガード済み(設計どおり)。ただし研究版のroleは無意味なラベルなので、将来の集計で4+1データとして混ぜないこと。

**N5. 後段Gate無影響性は実コードで確認済み(論点4)。** canonicalization prompt(`er003_key_words_canonicalization.py:206-214`)とRedundancy QA prompt(`er011_key_phrase_set_redundancy_qa_01.py:114-118`)はいずれもフィールドwhitelistで組むため `key_phrase_role` はどのLLM入力にも入らない。TTS読み上げ原稿は `er003_b2_key_words.py:419-430` が `order`/`display_phrase`/`ja_gloss` のみ参照。source gateは `rank`/`used_form`/`source_span`/`source_sentence` のみ。canonicalization passthroughは存在時のみ引き継ぐ条件付き(`er003_key_words_canonicalization.py:624-627`)で旧artifact後方互換。`kp_auxiliary_candidates.json` は `key_phrases/key_phrases_db_hybrid/` 配下(`er030_key_phrase_db_hybrid_selector_01.py:650`)でAssembly/TTSの参照集合外。

**N6. 補助候補データの性格づけは妥当だが配信面は未決。** 各要素に `verification_status: "unverified_reference_candidate"`、ファイル先頭に「validator/canonicalization/source gate未通過の未検証参考候補」noteがあり、品質保証済み5件と構造的に区別可能(良い設計)。一方で中身はStage1候補dictそのままで本文由来の語・文ID等を含むため、将来クライアントへ配る場合は「記事の一部を外部へ出す」ことになる点をUI決定時に併せて判断する必要あり。

**N7. 定数の二重管理(低リスク)。** 判定は `expected_item_count == p2g.PRODUCTION_ITEM_COUNT_UNCHANGED`(5)、呼び出し側は `prod.PRODUCTION_ITEM_COUNT`(5)。将来枠数が片方だけ変わると4+1検証が**黙って無効化**される(失敗ではなく不検査)。両者は既存testで5に固定されているため現状の実害なし。等価性testを1件足すと安全。

**N8. evidenceの読み方(論点5)。** 9件でTopic選定は全件が中心質問に整合し固有名詞偏りゼロ、Important 4件は旧Production 5件と概念重複3〜5/5で劣化兆候なし、という結論は資料から妥当に読める。ただし(a)Topic該当性判定はモデルの自己申告理由の転記+Sonnetの主観であり独立評価ではない(1〜2記事はユーザー目で確認する価値あり)、(b)F-1が本来懸念した「1回だけ出現する一般語だが理解の前提」ケースは**観測されておらず、反証もされていない**(観測されたのは人工的に候補を枯渇させたforced_fallback、すなわち別事象)。F-1は「evidenceにより解消」ではなく「未観測のまま継続」と扱うのが正確です。

---

## ユーザー判断が必要な項目(整理)

1. **Strategy L経路のretry緩和**(最重要)。現状 `er003_v1_n3_01_scaffold_generate.py:262-265` が `max_attempts=1` 固定(4+1導入前からの既存挙動)で、role不成立は即失敗・`run_key_phrases` も再試行しない(melos_a2で実観測)。4+1は制約を1つ増やすため初回失敗率は上がる方向。影響はFiction/legacy/Family X fallback経路で、失敗時は当該レベルのKPが生成されずAssembly前でSTOP(不正データの混入ではなく手動再実行コスト)。選択肢: (a)現状維持、(b)この経路のみ `max_attempts=2` へ(worst case 選定call +1回、¥1前後/記事)、(c)role不成立に限り再試行。※既存Production既定値は元々2(`MAX_PRODUCTION_RETRY_ATTEMPTS`)で、1固定はこの経路の独自指定。
2. **F-1対処**: 候補プールが薄い記事でTopic該当語がStage1に存在しない場合の扱い(現状=Strategy Lへ委ねる/無対処)。新候補生成ロジックは未実装のままが設計方針と整合。
3. **F-4 runner-up契約**: Strategy L側の5枠外候補を出す新出力契約の要否(OPEN-211に登録済み)。
4. **UI件数・配置**: 未定のまま(新規UIなし)。
5. (任意)N3の「重要語区分から最低1件」をimportant役割4件側の条件に読み替えるか。

## Gate 3への所見(判定はFable/ユーザー)

仕様一致・共通schema伝播・失敗経路の合流・後段Gate無影響・cost(¥4.84、Guardrail比6%)は確認できました。一方で「回帰0件」の記載は実測と不一致(S3)、新設リスクの観測性に欠落(S1)、Production telemetryにevidence混入(S2)、既知FAILテスト残置(S4)があります。いずれも小修正(合計十数行、API支出ゼロ、Production挙動不変)で解消できる範囲なので、S1〜S5を反映した上でGate 3判定に進むのが安全だと考えます。Production採用可否の宣言は行いません。

---

## 修正1回目(2026-09-28、ユーザー既決事項の実装+Opus L2 SHOULD_FIX反映)

### T-0結果

委任文を`docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_04.md`へ保存、
`check_delegation_prompt.py`実行結果は`FAIL`(理由: 「事前指定Grep一覧+追記位置・更新位置の手順」セクション欠落、
実行コマンドの一部[`.venv\Scripts\python.exe -m pytest ...`/`run_project_regression.py`行]が「値/絶対パスを含む」
判定基準に対しfalse positiveで引っかかったもの)。委任文自体はFableから受領した原文のまま保存しており、
本タスクはその内容(既決事項+Opus所見反映)を実装した。必須セクション8項目中7項目`[OK]`(`[MISSING]`は
「事前指定Grep一覧+追記位置・更新位置の手順」のみ)、fixed block(E-1/D-1/G-1/F-1)は全て`[OK]`。

### 既決事項→実装の照合表

| ユーザー既決事項 | 実装 |
|---|---|
| Strategy L retry最大2回 | `er003_v1_n3_01_scaffold_generate.py::_run_key_phrase_selection_strategy_l`の`max_attempts`を`1`固定から`prod.MAX_PRODUCTION_RETRY_ATTEMPTS`(=2)へ変更 |
| 2回目到達時は報告必須 | `strategy_l_attempts`/`retry_reached_second_attempt`を戻り値・`keywords_runtime_metadata.json`・telemetryへ記録、print出力あり |
| Topic欠損時はDB側backup(4件+backup1件)で補完 | DB Hybrid schemaへ`backup_item`(important役割の予備候補、常に1件返す)追加。topic欠損/単独無効時のみPython側で5件目として機械的に置換(`topic_slot_filled_by_backup`/`backup_substitution_reason`記録) |
| Topic slotが重要語区分該当なら充足扱い | 機械検証コード自体が元々存在しないことを確認、guidance文言は無変更のままSSOTへ記録のみ(実装変更なし) |
| Strategy L runner-up/5-slot外候補は現時点不要、将来UI設計時に再検討、Open Item defer | 実装せず、`OPEN_ITEMS.md`OPEN-211を`DEFERRED`(runner_up契約のみ)へ更新 |

### Opus L2所見(§12)→対応の照合表

| # | 所見概要 | 対応 |
|---|---|---|
| S1 | Strategy L telemetryがINVALID時`role_counts: null`(観測性欠落) | `_run_key_phrase_selection_strategy_l`の戻り値へ`role_counts`を常時格納、呼び出し側`role_counts=result.get("role_counts")`へ変更 |
| S2 | evidence実行がProduction telemetryへ`synthetic=false`混入 | `er035_kp_4plus1_topic_phrase_evidence_01_run.py`の`run_key_phrases`呼び出しへ`synthetic=True`追加、OPEN-211へevidence起源のarticle_id接頭辞注記 |
| S3 | 「回帰0件」記載が自己計測と不一致(rename未対応) | `git mv`で`er003_test_key_words_min_unit_4plus1_01.py`へrename、実測で件数照合meta-testの自ファイル起因分が解消したことを確認(§8参照) |
| S4 | Trial testが既知FAILのまま回帰網外に残置 | `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py`fixtureへ`"key_phrase_role": "important"`追加 |
| S5 | 別Promptが4+1非対応のまま無記載 | `er003_key_words_production.py`の`PRODUCTION_PROMPT_TEMPLATE_PATH`直前へ1行コメント追加 |
| S6 | 追記文言が既存優先順位を部分的に再掲 | 「残り4個は上記の基準に従って選んでください」への参照形へ縮約、候補区分列挙を「候補の種類・区分」へ一般化 |
| S7 | 既存testファイル数の記載不整合(5→実測4) | REPORT/CURRENT_SPEC双方を4へ是正 |
| N1 | `detail_reason_code`判定が`item_reasons`を取りこぼす | `er030_key_phrase_db_hybrid_selector_01.py`の`role_structure_invalid`判定へ`item_reasons`参照を追加 |
| N7 | 定数二重管理(`PRODUCTION_ITEM_COUNT_UNCHANGED`/`PRODUCTION_ITEM_COUNT`)の黙示的無効化リスク | 等価性test1件追加(`ProductionItemCountEquivalenceTests`) |

(N2〜N6/N8は所見記録のみで実装不要と既に判断済みのため本修正の対象外)

### Prompt最終文言(逐語)

`b1_p2_keywords_l_prompt_template.txt`(Strategy L/DB Hybrid共有、修正差分は下線部相当の2箇所):

> 5個のうち1個は、汎用性や一般的な学習重要度は必ずしも高くなくても、この記事に特有であり、事前に意味・用法・音を理解しておくことでこの記事の本文全体を追いやすくなる語または表現を選んでください(key_phrase_role="topic")。判断基準は「この語・表現を事前に理解していると、この記事の本文を明確に追いやすくなるか」です。人名・企業名・ブランド名・地名だから選ぶ、専門用語だから選ぶ、といった特定の種類を優先するルールではありません。**該当する語・表現が見当たらない場合でも、topicの項目を空にせず、その記事の中で最も近いと考えられる候補を選んでください。**残り4個は、**上記の基準に従って選んでください**(key_phrase_role="important")。このkey_phrase_roleは、**候補の種類・区分**とは独立した、選定後の役割ラベルです。

`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`(DB Hybrid固有、末尾へ追加):

> - 上記5件とは別に、backup_itemとして、重要語・重要表現(key_phrase_role="important")の予備候補を1件、上記5件とは異なるcandidate IDで選んでください。topicの候補が正しく選べた場合でも、backup_itemは必ず1件返してください(その場合は採用されません)。

例示語・優先カテゴリ・DB Hybrid固有区分名のhard-codeは追加していない(ユーザー明示指示遵守、既存指示を踏襲)。

### schema差分

DB Hybrid `build_json_schema()`(`er030_key_phrase_db_hybrid_source_reference_contract_01.py`):

```
properties: {
  "items": {type: array, minItems=maxItems=5, items: <既存item schema>},
  "backup_item": <items[]と同形のitem schema(候補ID方式のprops、必須)>,  # 新規
}
required: ["items", "backup_item"]  # backup_itemを追加
```

`er003_key_words_min_unit.validate_min_unit_selection()`へ新引数`topic_requirement_satisfied_via_backup: bool = False`
を追加(既定False、既存呼び出し元は全て無変更のまま影響を受けない)。Trueの場合のみtopic=1件・important=
{expected_item_count-1}件の集計検証を1箇所skipする(他の判定は無変更)。呼び出し元はDB Hybrid経路の
`run_source_reference_contract_gate`のみ。

### 検証結果

- **単体test**: `er003_test_key_words_min_unit_4plus1_01.py`(rename後、27件、旧20件+新規7件[retry2回到達
  報告2件・S1 role_counts観測性1件・DB Hybrid backup_item補完3件[missing→PASS/invalid item→PASS/backup重複→
  INVALID]・N7等価性1件])単体で全PASS。関連既存test(`er030_key_phrase_db_hybrid_source_reference_contract_01_test`/
  `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test`/`er003_test_key_words_canonicalization`/
  `er003_test_key_words_min_unit`/`er003_test_p2i_production`/`er003_test_b1_p2`、計331件)全PASS(実行時間
  約139秒、実API呼び出しなし)。
- **回帰**: `run_project_regression.py`実測`collected=3551 passed=3542 failed=7 errors=2`。委任文が事前提示した
  既知baseline(`failed=7/errors=2`)と完全一致、機能regression0件。S3是正の直接確認として、rename後のファイル名
  `er003_test_key_words_min_unit_4plus1_01.py`が`fnmatch`で`er0*_test_*.py`(combined)・`er003_test_*.py`
  (prefix)の両patternへ一致することを直接確認した。ただし`er003_test_p2j_investigate.py::test_combined_equals_
  sum_of_er002_and_er003`は依然として失敗する。原因を追加調査した結果、`unittest.TestLoader().discover(".", ...)`
  が repository全体を再帰的に走査するため、本タスクと無関係な並行実行中の他管理ID(`FAMILY-XY-*`/`TTS-ALL-*`
  Trial)が追加した新規testファイル群にも同種のprefix/combined不一致が存在し、combined側とsum_by_prefix側の
  差分が(diff 1600件超)と極めて大きいことを確認した(自ファイル1件のrenameでは到底説明できない規模)。これは
  既存`OPEN-209`(discovery pattern gap+test infra mock-drift構造リスク)と同根の、本タスク管掌外の既存/並行
  ドリフトであり、本タスクでは追加の是正を行っていない(並行タスクのファイルには一切触れていない)。
- **実データ**(`er035_output/kp_4plus1_evidence_02/`、`synthetic=True`、Guardrail¥20内):
  - DB Hybrid `meta_a2`(実API、backup_item付き新schema): `status=KEY_WORDS_STRUCTURE_PASS`、
    `role_counts={topic:1, important:4}`、`cost_jpy=1.1945`、`topic_slot_filled_by_backup=false`
    (topicが正常に選ばれたためbackup未使用、schema自体はAPIへ受理されbackup_itemも返却された[strict mode
    のrequired制約により応答が成功した時点で構造的に保証される])。
  - Strategy L `melos_a2`(実API): `status=KEY_WORDS_STRUCTURE_PASS`、`strategy_l_attempts=1`、
    `retry_reached_second_attempt=false`(今回は1回目でPASS、2回目は発火せず)。
  - retry 2回目到達・DB Hybrid backup補完のいずれも実APIでは今回発火しなかった(現実のモデル挙動は
    概ね指示に従うため、稀な失敗ケースを実APIで再現するのは確率的に不安定)。両機構の正しさは上記の
    決定的単体test6件(fakeなselector応答を用いたgate/wrapper関数の直接呼び出し、API呼び出しなし)で
    確認した。

### cost実測

DB Hybrid `meta_a2`のみ計測対象(selection cost¥1.1945)。canonicalization/Redundancy QA/Strategy L選定は
既存OPEN-206の限界により本タスクでも未計測(新規劣化ではない)。Guardrail¥20に対し、計測対象分は6%程度。

### Dangling Reference Check

`backup_item|topic_slot_filled_by_backup|retry_reached_second_attempt|strategy_l_attempts`を全`*.py`へgrepし、
ヒット5ファイル: 実装4ファイル(`er003_key_words_min_unit.py`/`er003_v1_n3_01_scaffold_generate.py`/
`er030_key_phrase_db_hybrid_selector_01.py`/`er030_key_phrase_db_hybrid_source_reference_contract_01.py`、
`er003_key_words_min_unit.py`は新設引数のdocstring内言及のみ)+新規test1ファイル。無関係な参照・取りこぼしは
検出されなかった。`topic_requirement_satisfied_via_backup|backup_substitution_reason|_identify_topic_backup_
substitution_target`も同様に同じ5ファイルのみでDangling無し。

### Gate 3再確認表(Sonnet記入、判定欄は空欄)

| 項目 | 状態 |
|---|---|
| Production正式path | DB Hybrid/Strategy L両経路とも既存Production正式pathのみを変更(Trial/DEV経路は無変更、`er034_..._trial_06_*`はfixture1行のみ) |
| retry/fallback/regeneration機構との整合 | Strategy L retryはProduction既定`MAX_PRODUCTION_RETRY_ATTEMPTS`(=2)に揃えただけ(独自上限追加なし)。DB Hybrid backup補完は既存`DbHybridFailure`/`fallback_allowed`既定値を一切変更せず、曖昧ケースは全て既存経路へ委譲(新しい分岐点を作らない、Fable既存判断[F-3]を踏襲) |
| runtime evidence | 済(実API2件、§実データ参照。retry/backup機構自体は決定的単体testで補完) |
| regression/negative test | 済(regression failed=7/errors=2既知baseline一致。negative testはDB Hybrid backup重複→INVALID維持testを含む) |
| telemetry | 済(`strategy_l_attempts`/`retry_reached_second_attempt`/`topic_slot_filled_by_backup`/`backup_substitution_reason`をtelemetry.jsonl・runtime_metadata.json双方へ記録) |
| SSOT | 済(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`、本コミット) |
| PM_GOVERNANCE | 該当なし(通常のProduction配線修正、Gate 1〜7の枠組み内) |
| Git | 所有ファイル+testのみadd予定(`git add -A`不使用)、他Agent差分は一切addしない |
| Dangling | 済(上記参照) |
| `PRODUCTION_WIRED`最終判定 | **`PRODUCTION_WIRED`**(2026-09-28、Fable Gate 3判定。スコープ: 共通Key Phrase経路[Strategy L/DB Hybrid両経路・全Family]の4+1構成、DB Hybrid backup補完、Strategy L retry2回+2回目報告、runner-upはOPEN-211で`DEFERRED`。根拠: commit`0e6744e0`/`0cb59383`、Opus L2[BLOCKER0件、S1〜S7/N1/N7反映]、evidence9記事+差分evidence_02、test27件+regression baseline一致、SSOT反映済み) |

### STOP・新規USER_DECISION候補

なし(本修正はユーザー既決事項の実装+Opus所見反映の範囲内で完結し、新たな仕様判断は発生しなかった)。

### commit hash・raw URL

本コミットのhash・raw URLはRESULT_PACKETおよびcommit後の報告を参照。
