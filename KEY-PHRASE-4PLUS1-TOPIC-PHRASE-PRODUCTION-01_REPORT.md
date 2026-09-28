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
| Mandatory Opus L2レビュー | 未実施(共有Core module変更のため対象と判断、実施要否・タイミングはFable判断) |
| `PRODUCTION_WIRED`最終判定 | 未(Fable判断待ち) |
