# Key Phrase「4(重要語・重要表現)+1(Topic Phrase/Word)」構成 最小実装設計

管理ID: `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`(Phase A: 現行実装調査+
最小実装設計、read-only・¥0・API呼び出しなし・コード/SSOT編集なし)。
委任文全文: `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_01.md`。

本ドキュメントはPhase Aの調査結果+Phase B(実装)の設計案であり、それ自体は
SSOT(`CURRENT_SPEC.md`)への正式反映ではない。Phase B着手・SSOT反映には
Fable/ユーザーの承認が必要。

## 0. Existing Spec / Prior Trial Check Gate(分類)

- `DECISION_LOG.md`/`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG_HISTORY.md`/
  `OPEN_ITEMS_HISTORY.md`を「4+1」「4plus1」「Topic Phrase」「topic_phrase」
  「Topic Word」でGrepしたが、無関係な1件(`DECISION_LOG.md:2313`、旧
  DECISION_LOG本体の文字数集計に関する記述)以外ヒットしなかった。
  **分類C(本当に新規)**: 既存仕様・過去Trialなし。
- `Family体系`: `CURRENT_SPEC.md:1325-1362`「Family体系(2026-09-27ユーザー
  決定)」節を確認。Active Production Family = X/Y/Z(現状X/Zのみ着手済み)、
  Legacy/Backup = Family A/B/C(最新仕様へ追従させない・新規実装しない・
  read-onlyの参照元のみ)。委任文の「Family A/B/C/News等の共通経路」
  「Voices系/Fiction・Family C系での検証」は、legacy記事本文を**read-only
  検証入力として使うだけ**であり、配線対象はFamily X(News Entertainment)/
  Family Z(Fiction)に限定する、という解釈で相違ない。
- 既存の近縁フィールド `topic_exposure_dependency`(`er003_key_words_min_unit.py:127`、
  TRI_LEVELS enum)は、選定itemの難易度理由の一部としてLLMが自己申告する
  研究由来のメタデータであり、`validate_min_unit_selection()`(397-408行)は
  enum妥当性を確認するのみで選定基準・構造ゲートには使われていない。
  「その項目の難しさが話題への事前露出依存度に起因するか」という軸であり、
  「その項目自体が記事のTopic Phraseとして機能するか」という今回の新概念とは
  別軸。流用すると意味が混同するため、別フィールドとして新設することを推奨する
  (下記B-1)。

## A. Production正式初回経路(Family X / Family Z)

### Family X 通常記事(News Entertainment、Primary = DB Hybrid)

```
er019_family_x_audio_production_runner_01.py::run_theme_scaffold()
  (kp_backend既定 "db_hybrid")
  → er003_v1_n3_01_scaffold_generate.py::run_key_phrases()
      (article単位のRedundancy retry loop、最大 KEY_PHRASE_REDUNDANCY_RETRY_MAX=2回、
       選定+canonicalization+Redundancy QAの3工程のみ再実行、本文は不変)
      → run_key_phrase_selection(kp_backend="db_hybrid")
        → _run_key_phrase_selection_db_hybrid_with_fallback()
          → er030_key_phrase_db_hybrid_selector_01.py::run_db_hybrid_selection()
              1. Stage1候補生成+shortlist組み立て
                 (er030_key_phrase_db_hybrid_core_01.py::run_stage1_and_shortlist、
                  決定論的DB検索[CEFR-J/NGSL/Wiktionary/wordfreq]、API呼び出しなし)
              2. 候補ID付与(src_ref_contract.assign_candidate_ids)+
                 source_span整合性の事前補正(correct_shortlist_source_span_consistency)
              3. compact prompt組み立て(src_ref_contract.build_lightweight_user_message、
                 静的instructionsは b1_p2_keywords_l_prompt_template.txt から抽出、
                 article全文は含まない[assert_no_full_article_bodyで機械確認])
              4. Selector LLM呼び出し1回(候補ID enum制約のStructured Outputs)
              5. 候補ID→source_span/source_sentence決定論的復元(restore_source_fields)
              6. 構造Validator(p2g.validate_min_unit_selection、expected_item_count=5)
          → PASS: canonicalization(er003_key_words_canonicalization.py)
              → Key Phrase Set Redundancy QA(er011_key_phrase_set_redundancy_qa_01.py、
                 C(5,2)=10ペア判定)+ 禁止記号QA
          → 非PASS/例外/契約違反等: DbHybridFailure
              → fallback_allowed=True: Strategy L全文方式へfallback
                (MODEL_CONTRACT_VIOLATIONのみfallback不可・STOP)
```

Strategy L全文方式(fallback、および下記Family Z本経路):
```
run_key_phrase_selection(kp_backend="strategy_l")
  → er003_b1_p2_keywords.py::run_selection_gate()
    → er003_key_words_production.py::run_production_selection_gate()
      (記事全文をprompt送信、max_attempts=2[技術失敗/構造不合格時に1回再試行])
```

### Family Z(Fiction、`er026_family_z_fiction_production_runner_01.py`)

`scaffold.run_key_phrases(article_text, KEY_PHRASE_DIR, article_id, "A2", process=None)`
は`kp_backend`未指定=既定`"strategy_l"`。DB Hybrid Source Reference Contract側は
`family_profile="family_z"`が明示的に`NotImplementedError`(Family Z DB Hybrid
Core v2全体の採用可否は別管理ID、`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-
PRODUCTION-WIRING-01`のスコープ外、CURRENT_SPEC該当節に明記済み)。よって
**Family Zは現状Strategy L経路のみ**を通る。

### Family A/B/C(legacy)

新規実装対象外。既存完成記事本文はread-only検証入力としてのみ使用可
(下記E節)。

### 共通の後段Gate

`er003_key_phrase_source_gate_01.py::check_key_phrase_source_presence`
(Assembly系のどこかで別途、source_span/source_sentenceの本文実在確認)。

### DEV/Trial scriptとの区別

`er027/028/029/032/034_key_phrase_db_hybrid_*` はTrial記録であり無変更のまま
保持されるだけで、Production経路には含まれない(Production module
`er030_key_phrase_db_hybrid_core_01.py`/`..._selector_01.py`/
`..._source_reference_contract_01.py`が実際の呼び出し対象)。

## B. 4+1の最小実装案

### B-1. 新フィールド `key_phrase_role`(名称案、最終決定はFable/ユーザー)

- enum: `["important", "topic"]`
- 追加場所: `er003_key_words_min_unit.py::_ITEM_SCHEMA_PROPERTIES`
  (115-134行、単一の追加地点)。
  - `er003_key_words_production.py`(`_ITEM_SCHEMA_PROPERTIES = p2g._ITEM_SCHEMA_PROPERTIES`、
    63行)経由でStrategy L(B1/A2/Family Z/Family X fallback共通)のschemaへ、
  - `er030_key_phrase_db_hybrid_source_reference_contract_01.py::build_item_schema_properties()`
    (108-118行、`p2g._ITEM_SCHEMA_PROPERTIES.items()`をループしてsource_span/
    source_sentenceのみ差し替える設計)経由でDB Hybrid(Family X Primary)の
    schemaへ、**1箇所の変更で両経路へ自動伝播**する。
  - `_ITEM_REQUIRED_FIELDS = tuple(_ITEM_SCHEMA_PROPERTIES.keys())`(135行)
    のため自動的にrequired化される(OpenAI Structured Outputs strict modeの
    制約と整合、既存パターンと同じ)。
- 注意点: この辞書は`er003_key_words_min_unit.py`自身の10件研究版schema
  (137-158行、`RESEARCH_ITEM_COUNT`件、B2向け)とも共有オブジェクトのため
  `key_phrase_role`が意図せず波及する。B2は現行Active Production経路
  (Family X/Z)に含まれないため実害は小さいが、構造検証(下記B-2)は
  `expected_item_count`で分岐しB2側(10件)では4+1条件を評価しないよう
  ガードする必要がある。

### B-2. 構造Validator拡張

- 追加場所: `er003_key_words_min_unit.py::validate_min_unit_selection()`。
  - 397-408行のenum検証ブロックへ`key_phrase_role`の妥当性チェック
    (`item.get("key_phrase_role") not in ("important", "topic")`)を追加。
  - 453-460行(rank/display_phrase重複チェック)と同じ場所に、新しい集計
    ブロックを追加する案:
    ```python
    role_counts = Counter(it.get("key_phrase_role") for it in items if isinstance(it, dict))
    if expected_item_count == PRODUCTION_ITEM_COUNT:  # 5件のProduction経路のみ
        if role_counts.get("topic", 0) != 1 or role_counts.get("important", 0) != expected_item_count - 1:
            reasons.append(f"key_phrase_roleがtopic=1件・important={expected_item_count-1}件でない"
                            f"(実際: {dict(role_counts)})")
            ok = False
    ```
  - 「新しいProduct ruleを作らない」という制約は「何を選ぶか」という選定基準
    の話であり、「出力構造が仕様通りか(4+1になっているか)」という構造検証は
    ユーザーが直接決定した契約(4+1固定)そのものである。既存の「rankが
    1〜5の重複なし」チェックと同格の構造検証として扱ってよいと考えるが、
    最終確認はFable判断に委ねる。
  - 不成立時の扱い(合流先、要Fable確認): 既存`KEY_WORDS_STRUCTURE_INVALID`
    ステータスにそのまま合流させる(新しいstatus値を作らない)。
    - Strategy L側: `run_production_selection_gate`のmax_attempts=2内で
      自動再試行(既存の技術失敗/構造不合格と同じ扱い)。
    - DB Hybrid側: 現在1呼び出しのみ(retryはouter loopに委譲する設計)で、
      非PASS statusは`DbHybridFailure`経由でStrategy Lへfallbackする設計
      になっている。4+1構造不成立を`DbHybridFailure`の新reason_code
      (例: `ROLE_STRUCTURE_INVALID`、fallback_allowed=True)として扱い
      Strategy Lへfallbackさせるのが既存構造への最小差分だが、**これは
      新しい分岐点の追加でありFable判断が必要**(STOP候補F-3)。

### B-3. Promptへの追加(1箇所、両経路・両Family共通)

- 追加場所: `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (全26行)。この1ファイルが、Strategy L(`er003_b1_p2_keywords.py`経由、
  B1/A2/Family Z/Family X fallback共通)とDB Hybrid静的instructions
  (`er030_key_phrase_db_hybrid_selector_01.py::extract_static_instructions
  (bk.load_prompt_template())`、139-154行、article placeholder以前を丸ごと
  抽出)の**両方に使われる唯一の共有ファイル**であることを確認済み。
  1箇所の追記で両経路・両Family(X/Z)へ伝播する。
- 追記文言案(ユーザー定義の逐語+中心質問のみ、例示・優先順位ruleなし):
  > 5個のうち1個は、汎用性や一般的な学習重要度は必ずしも高くなくても、
  > この記事に特有であり、事前に意味・用法・音を理解しておくことでこの
  > 記事の本文全体を追いやすくなる語または表現を選んでください
  > (`key_phrase_role="topic"`)。判断基準は「この語・表現を事前に理解して
  > いると、この記事の本文を明確に追いやすくなるか」です。人名・企業名・
  > ブランド名・地名だから選ぶ、専門用語だから選ぶ、といった特定の種類を
  > 優先するルールではありません。残り4個は、既存の優先順位(初回音声での
  > 処理困難・未知の可能性・瞬時の推測困難・本文の事実/感情/面白さへの
  > 影響・記事内重要度・汎用性)に基づいて選んでください
  > (`key_phrase_role="important"`)。
- 既存guidanceとの重複整理(要確認): DB Hybrid側の追加guidance
  (`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`、
  `er030_key_phrase_db_hybrid_source_reference_contract_01.py:168-183`)は
  「必ず候補一覧から選ぶ」「重要語区分から最低1件」という**候補プールの
  出自区分**の制約であり、新設する「important/topicロール」(**選定後の
  役割区分**)とは別の軸。両文言が並存すると選定LLMが混同するリスクが
  あるため、文言整理方針はPhase B着手前にFable/ユーザーへ確認することを
  推奨する(STOP候補F-2)。

### B-4. Stage 1候補プールにTopic候補が含まれるか

- DB Hybridのshortlistは3区分: 「重要な単語・単語群候補」
  (`important_noun_phrase_candidate=True`、CEFR/頻度フィルタなしの
  repeated compound noun heuristic中心)、「phrase/idiom/phrasal verb候補」、
  「word候補」(後者2区分はCEFR-J/NGSL/Wiktionary/wordfreqのZipf頻度閾値で
  フィルタされる、`er030_key_phrase_db_hybrid_core_01.py:143-395`)。
- Topic Phraseの多くは「記事に特有で繰り返し使われる複合語・専門語」に
  該当しうるため、**「重要な単語・単語群候補」区分が実質的な母集団として
  機能する可能性が高い**(固有名詞に限定されない一般カテゴリのため、
  「固有名詞枠にしない」というユーザー方針とも整合しやすい)。
- リスク(STOP候補F-1): 「一度しか出現しない、一般的でよく使われる単語
  だが文脈上その記事のTopic理解に必須」というケース(例: ある専門記事で
  1回だけ登場する鍵概念語)は、repeated_compound_noun_heuristic(繰り返し
  出現が前提)にもCEFR難易度フィルタ(一般語のため頻度が高く除外される)
  にも該当せず、**Stage 1候補プールに一切現れない可能性がある**。現時点
  では推測であり、Phase Bで実データ検証してから最終判断する。
- Strategy L(全文方式、Family Z・Family X fallback)は候補プールという
  概念自体がなく、モデルが本文全文から自由に選ぶため、この制約を受けない。

## C. 構造化・後方互換

- `keywords_runtime_metadata.json`(DB Hybrid固有、`run_db_hybrid_selection`
  559-593行)へversion文字列(例: `selection_contract="4plus1_v1"`)を追加
  する場合、既存の`source_reference_contract`と同じ「新設フィールドを
  追加するだけ、既存フィールドは無変更」のパターンに倣う。
- **重要な実装ポイント(見落としやすい)**: `er003_key_words_canonicalization.py::
  merge_canonicalization_result()`(571-628行)は選定結果を**明示的なキーの
  whitelistで再構成**しており(rank/source_span/source_sentence/
  display_phrase/key_phrase/used_form/japanese_gloss/japanese_gloss_tts/
  changed_from_display_phrase/normalization_reason/qa/qa_overall_status/
  reasoningのみ)、`source_reference_contract`/`source_candidate_id`/
  `surface_echo`/`candidate_mismatch_suspected`は615-623行の**個別
  passthroughリストでのみ生存**する設計。`key_phrase_role`もこの
  passthroughリストへ明示的に追加しないと、`keywords_canonicalized.json`
  には自動的に生存しない。
- Redundancy QA(`er011_key_phrase_set_redundancy_qa_01.py::build_user_message`、
  112-125行)は`rank`/`key_phrase`/`japanese_gloss`/`source_sentence`のみを
  プロンプトへ渡す設計であり、`key_phrase_role`が無くても既存ロジックは
  そのまま動く(壊れない)。4観点(意味/使用場面/文法的学習価値/記事内概念)の
  重複判定は元々topic/important区分そのものを見ておらず意味的重複だけを
  見るため、**topic-important間の役割重複を追加検知するための改修は不要**
  (既存ロジックがそのまま使える、「既存Redundancy QAを壊さない」という
  要求と整合)。
- source consistency gate(`er003_key_phrase_source_gate_01.py::
  check_key_phrase_source_presence`、66-90行)は`rank`/`used_form`/
  `source_span`/`source_sentence`のみ参照し未知フィールドを無視するため
  無改修で動作する。
- TTS reading copy(`er003_b2_key_words.py::build_key_words_reading_copy`、
  415-430行)は`order`(rankから変換)/`display_phrase`/`ja_gloss`のみを使い、
  5件を順番に読み上げるだけで役割の区別をしない。TTS本体呼び出し
  (`er003_v1_n3_01_tts_generate.py`838/928/975/1074行)もrankでソートして
  5件をそのまま処理するだけ。**音声側の挙動・順序・生成コストは一切
  変更されない**(「音声5枠とは別に」というユーザー要求と整合、TTS側の
  改修は不要)。
- 既存artifact(旧`keywords_canonicalized.json`)には`key_phrase_role`が
  存在しないため、読み込み側で当該フィールド不在を「旧contract」として
  扱う設計にすれば後方互換(既存の`source_reference_contract`分岐と同じ
  パターン)。

## D. 追加表示用データ(5枠外候補+Topic Phrase識別)

- **Topic Phrase自体の表示**: `keywords_canonicalized.json`の該当itemに
  `key_phrase_role="topic"`が付与されるため、追加データ生成なしで既存
  artifactから判別可能(表示側が`key_phrase_role`を見て別枠表示するだけ)。
- **「5枠に入らなかった重要語・重要フレーズ」表示用データ**は選定方式に
  よって非対称:
  - DB Hybrid(Family X Primary): `db_hybrid_stage1_debug.json`
    (Stage1候補全件、決定論的生成、API費用ゼロ)と選定時の`candidate_id`表
    (`shortlist_with_ids`)が既に出力artifactとして存在する
    (`run_db_hybrid_selection`467-468行)。この母集団から選ばれなかった
    候補を抽出することは技術的に可能。ただしこれらはvalidator/
    canonicalization/source gateを一切通過していない**未検証の生候補**
    であり、既存5件と同じ品質保証(source_span検証・自然な日本語グロス・
    Human Review運用)を経ていない。表示する場合は「参考候補(未検証)」
    である旨の明示が必要。
  - Strategy L(Family Z、Family X fallback): 候補プールという概念自体が
    存在しない(モデルが本文全文から直接5件を選ぶ)。「5枠外候補」を得るには
    (a) 同一selector call内で追加的に「次点候補」を出力させる新フィールド
    (例: `runner_up_candidates`配列、追加call不要でschemaに配列を1つ
    追加するだけ)を新設する、(b) この経路では5枠外表示機能を提供しない、
    のいずれかの選択が必要(STOP候補F-4)。
  - **件数・UI配置(何件表示するか、どの画面に置くか)は現時点で未定**
    (委任文の指示通り、ここでは決めない)。
- **既存UI経路の有無**: `OPEN-169`(`USER-TEST-SCRIPT-READABILITY-PROD-01`、
  `PRODUCTION_WIRED`、2026-09-18)でKey Phraseハイライト+日本語訳のUI
  (`user_test/unified.html`、`renderTranslationSection`)が存在するが、
  生成元(`er012_b_family_production_runner_01.py`)は**Family B(Voices、
  legacy)専用runner**であり、Family X(`er019_family_x_audio_production_
  runner_01.py`)・Family Z(`er026_family_z_fiction_production_runner_01.py`)
  は別のplayer/runner実装を使っている(builder scriptがFamily単位で個別
  実装されている構造、共通UIコンポーネント化はされていない)。したがって
  **Family X/Z向けの「既存UI経路」は現時点で存在しない**と判断する。
  委任文の代替方針(「無理にUI新設せず、Production記事生成側で後段UIが
  利用可能な構造化データとして保持・出力するまでを対象」)に従い、
  Phase Bのスコープは「`keywords_canonicalized.json`等のartifactへ
  role/5枠外データを構造化して保持するところまで」とし、新規UI実装は
  スコープ外として報告する。

## E. 検証計画(概要のみ、Phase Bで詳細確定)

- 対象記事(read-only既存evidence、新規生成なし):
  - Family X News: Meta A2/B1B、Hormuz A2/B1B(既存artifact例:
    `er030_output/family_x_kp_source_reference_contract_evidence_01/`、
    `er030_output/family_x_kp_db_hybrid_evidence_01/`、`..._02/`)。
  - Family Z Fiction: Melos A2×3(既存evidence)。
  - legacy参照専用: Family B(Voices)・Family C(twins、Future Story)本文は
    read-only入力としてのみ使用、新規生成・新規配線はしない。
- 観点表(10項目案):
  1. 構造PASS(4 important + 1 topic)
  2. Topic Phrase該当性の主観判定(中心質問に照らして妥当か)
  3. 固有名詞への偏り有無(ユーザー方針「固有名詞枠ではない」の遵守確認)
  4. Important 4件の品質劣化有無(既存Strategy L/DB Hybrid実績との比較)
  5. Redundancy QA発火率変化
  6. canonicalization QA PASS率変化
  7. Stage1候補プールにTopic該当語が存在したか(DB Hybridのみ、B-4節)
  8. retry発火率・追加コスト
  9. fallback発火時の役割整合(DB Hybrid→Strategy Lへfallback後も4+1構造維持)
  10. 5枠外データの有無・品質(D節)
- retry/regeneration時の4+1維持確認: `run_key_phrases`のRedundancy retry
  loopの各attemptで`role_counts`をtelemetryへ記録し、retry後も4+1構造を
  維持できるかを確認する。

## F. STOP候補(Phase B前にFable/ユーザー確認を推奨)

1. Stage 1候補プールが「一度しか出現しない一般語だが記事のTopic理解に
   必須」なケースを構造的に拾えない可能性(B-4節)。新しい候補生成
   ロジック(新DB・新ヒューリスティック)が必要になった場合はSTOP。
2. DB Hybrid既存guidance「重要な単語・単語群候補区分から最低1件」
   (候補出自の区分)と、新設「important/topicロール」(選定後の役割区分)
   という**2つの異なる軸の並存**による選定LLMの混同リスク(B-3節)。
   文言整理方針の承認が必要。
3. 4+1構造不成立時の失敗経路をどこに接続するか(B-2節: DB Hybrid新
   reason_code `ROLE_STRUCTURE_INVALID`→Strategy Lへfallback、という
   設計素案はFable判断が必要な新しい分岐点)。
4. Strategy L側の「5枠外候補」取得には新しい出力契約(runner_up候補
   フィールド)の追加が必要(D節)。構造フィールド追加であり選定基準の
   追加ではないと考えるが、念のため確認を推奨。
5. 表示UI(5枠外候補・Topic Phrase区分の実際の画面配置・件数)は現時点で
   未決(D節)。
- 上記いずれも今回Phase Aでは**実装していない**(read-only、コード変更ゼロ)。

## G. 他Agentとの衝突・実装開始条件

- git status確認時点(本タスク開始時)で、`er030_*`(selector/core/
  source_reference_contract/test)・`er003_v1_n3_01_scaffold_generate.py`・
  `er003_v1_*`各種・`er021_*`・`er006_preprod_hardening_01_validation.py`・
  `er033_*`・`er019_family_x_audio_production_runner_01.py`・
  `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`が他Agentにより
  変更中(未commit)であることを確認した。
- Phase B(実装)着手条件:
  1. 上記ファイル群の他Agent作業が完了・commit済みであること。
  2. 本設計書の`key_phrase_role`命名・validator接続方針・prompt文言整理・
     STOP候補5件についてFable/ユーザーの承認を得ること。
  3. Phase Bは`er030_key_phrase_db_hybrid_source_reference_contract_01.py`
     (Family X)と`er003_key_words_min_unit.py`/`er003_key_words_
     production.py`/`er003_key_words_canonicalization.py`(共有Core)を
     触るため、**共有module変更に伴うMandatory Opus L2レビュー対象**に
     なる可能性が高い(直近のSource Reference Contract Production
     Wiringと同水準の変更範囲)。

## 参照ファイル一覧(Phase Aで読み取ったProduction module、いずれも無変更)

- `er003_v1_n3_01_scaffold_generate.py`(`run_key_phrase_selection`/
  `run_key_phrases`、記事単位のretry入口)
- `er019_family_x_audio_production_runner_01.py`(Family X runner、
  kp_backend既定値)
- `er026_family_z_fiction_production_runner_01.py`(Family Z runner)
- `er030_key_phrase_db_hybrid_selector_01.py`/`_core_01.py`/
  `_source_reference_contract_01.py`(DB Hybrid Primary)
- `er003_b1_p2_keywords.py`/`er003_key_words_production.py`/
  `er003_key_words_min_unit.py`(Strategy L共通schema/validator)
- `er003_key_words_canonicalization.py`(canonicalization+
  merge_canonicalization_result)
- `er011_key_phrase_set_redundancy_qa_01.py`(Redundancy QA)
- `er003_key_phrase_source_gate_01.py`(source consistency gate)
- `er003_b2_key_words.py`(`build_key_words_reading_copy`)
- `er003_v1_n3_01_tts_generate.py`(TTS呼び出し側、rankソートのみ)
- `er012_b_family_production_runner_01.py`(Family B legacy UI、OPEN-169)
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (Strategy L / DB Hybrid静的instructions共有元)
- `CURRENT_SPEC.md`(「Family体系」節、「Key Phrase」節)
- `DECISION_LOG.md`/`OPEN_ITEMS.md`(既存仕様・過去Trial確認、該当なし)
