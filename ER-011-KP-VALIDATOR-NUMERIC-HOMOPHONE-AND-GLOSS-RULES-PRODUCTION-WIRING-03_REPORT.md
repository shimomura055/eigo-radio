# ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-03

種別: **Production配線の残り(closeout)**。-02の未実装部分(規約A・規約Bの
gloss側を、canonicalization prompt側ではなく実際の生成元である選定
Prompt`b1_p2_keywords_l_prompt_template.txt`へ配線)+SSOT反映
(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)+Git commit/push。
前提となる-02の成果(`er003_audio_tts_asr_safety.py`のJA助数詞リスト縮小版、
`er006_preprod_hardening_01_validation.py`のEN厳密同音数字ゲート例外、
canonicalization promptへの規約B[key_phraseスコープ])は
`ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-
WIRING-02_REPORT.md`を参照。

## 1. 選定Promptの調査(A2側テンプレート特定)

`er003_v1_iran01_a2_generate.py`のKey Phrase選定コード
(`run_key_phrase_selection()`)が`er003_b1_p2_keywords.load_prompt_template()`
/`build_user_message()`/`make_selector_fn()`をB1と全く同じ関数として
再利用していることを確認した。すなわち`b1_p2_keywords_l_prompt_
template.txt`はA2・B1で**共有される単一のファイル**であり、A2専用の
別テンプレートは存在しない(B2レベルのみ別ファイル
`b2_key_words_production_l_prompt_template.txt`を使用しており、今回の
指示範囲外のため変更していない)。Trial-13 b1bの保存済み
`keywords_selector_prompt.txt`が、このテンプレートの`{approved_b1_article}`
置換結果と文字単位で一致することも確認した。

## 2. 変更内容

`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`の
既存のgloss指示行の直後へ、以下の2文を追加した(規約Cは追加していない、
既存の選定基準・3条件は無変更)。

```
日本語グロスには「～」「〜」「…」のようなプレースホルダー記号を一切
使わないでください。動詞句などで目的語を省略した言い方にしたい場合は、
日本語として自然な言い切りの形(例: 「～を示す」ではなく「示す、指し
示す」)へ書き換えてください。日本語グロスに数字を含める場合は、算用
数字(1、2、3…)ではなく漢数字(一、二、三…)で書いてください。
```

Trial-17 Track Cで実証済みの規約A/B文言(`er011_output/open112_kp_
validator_fix_trial_17/track_c_trial_prompt.txt`)を参考にしつつ、
選定Promptの既存トーンに合わせて最小限へ圧縮した。

## 3. 回帰結果

| スイート | 件数 | 結果 |
|---|---|---|
| `er003_test_b1_p2.py`(新規テスト3件含む) | 47 | 全PASS |
| `er003_test_p2i_production.py` | 63 | 全PASS |
| `er003_test_b2_key_words.py`/`er003_test_key_words_min_unit.py` | 309 | 全PASS |
| `er007_ja_asr_validator_01_test.py`/`er003_test_audio_tts_asr_safety.py`/`er006_preprod_hardening_01_validation_test.py`/`er008_asr_variant_hardening_15_homophone_en_test.py`/`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`(-02回帰の再確認) | 64+15項目 | 全PASS |
| **プロジェクト全体回帰**(`python run_project_regression.py`、canonical entry point) | collected=2084 | passed=2081、failed=3 |

3件のfailureはいずれも本タスク由来ではないことを、-02/-03で変更した
6ファイル(`er003_audio_tts_asr_safety.py`/`er003_test_b1_p2.py`/
`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_
template.txt`/`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_
template.txt`/`er006_preprod_hardening_01_validation.py`/
`er007_ja_asr_validator_01.py`)のみを`git stash`で一時的に除去した
baselineでも同一の3件(`er003_test_bad.FixtureTests.test_case_0`
[回帰harness自体の意図的self-check fixture]、
`er003_test_p2j_investigate`の`ReconciliationArithmeticTests`2件
[OPEN-77既知のmeta-test集計乖離、`AssertionError: 2084 != 1802`のような
桁違いの乖離であり本タスクの+3テストとは無関係])が再現することで
確認した。

### 新規テスト(規約A/B/C確認、`er003_test_b1_p2.py::KeywordsPromptTests`)

- `test_template_contains_gloss_rule_a_kanji_numeral`: 「漢数字」の
  文言が存在することを確認。
- `test_template_contains_gloss_rule_b_placeholder_prohibition`: 「～」
  「〜」「…」の3文字がいずれも存在することを確認。
- `test_template_does_not_contain_rule_c_short_function_word_wording`:
  規約C相当の文言(`track_c_short_function_word_ending_flagged`・
  「短い機能語終端」)が存在しないことを確認。

## 4. Runtime evidence(実LLM呼び出し、TTS/ASRなし)

保存先: `er011_output/kp_validator_numeric_homophone_gloss_production_
wiring_03/`(`attempt_1/`・`attempt_2/`・`comparison_summary.md`)。
Trial-13 B1の実記事(`article.md`、無変更)に対し、Production選定経路
(`er003_b1_p2_keywords`+`er003_key_words_production.
run_production_selection_gate()`)→canonicalization
(`er003_key_words_canonicalization.run_canonicalization_gate()`)を
実データで2回実行した(いずれも初回1/1でPASS、リトライなし)。
Trial-13保存資産(`open112_trend_theme2_b_full_audio_trial_13/`)は
上書きしていない。

- **(a) gloss placeholder不在**: attempt_1のrank5(`point to`)で直接
  確認: Trial-13原本のgloss「～を示す、～を指し示す」→本タスク実行後は
  「示す、示唆する」(placeholderなし、プロンプトの例示と同型の書き換え)。
  attempt_1/attempt_2の他全項目も「～」「〜」「…」を含まない。
- **(b) gloss数字の漢数字化**: attempt_1・attempt_2とも、選ばれた5件の
  中に数字を含むgloss候補が偶然選ばれなかった(選定はLLMの非決定的
  判断であり、Trial-13原本の数値候補「median of about two nights」に
  相当する候補は両attemptとも数字を含まない「median」単体として選ばれた)
  ため、本タスクの実行では直接観測できなかった。同一文言による漢数字化
  は、既存の`er011_output/open112_kp_validator_fix_trial_17/track_c_
  raw_response.json`(同じ「median of about two nights」候補を含む入力)
  で実証済み(「中央値は約2泊」→「中央値は約二泊」)であり、この既存
  証跡を援用する。**規約は決定的Validatorではなく、Prompt文言による
  指示であるため、遵守は確率的である**ことを明記する。
- **(c) 学習価値の劣化なし**: 決定的Validator(`validate_production_
  selection`)は両attemptとも初回でPASS(Trial-13原本と同水準)。
  canonicalization側12項目QAは両attemptとも5件×12項目全てPASS
  (`qa_overall_status: PASS`)。選ばれた表現のカテゴリ(比喩・句動詞・
  統計用語・抽象名詞句)もTrial-13原本と同種であり、質的劣化の兆候は
  見られない。詳細比較表は`comparison_summary.md`参照。

Cost: `gpt-5.6-sol`(reasoning effort=high)による選定2回+canonicalization
2回=計4回の実LLM呼び出し。Production関数はusageを返さない設計のため、
Trial-17 Track C実績値(1回あたり約$0.12)を参考値として、概算合計
約$0.5前後(小額の範囲)。

## 5. SSOT反映

- `CURRENT_SPEC.md`: 「Audio Production Pipeline」内の既存2行
  (「Validator(数値正規化含む一般化仕様)」「Validator(日本語)」)へ
  それぞれTrack B/Track Aの内容を追記し`PRODUCTION_WIRED`を明記。
  「Key Phrase」節へ新規行「日本語グロス(`ja_gloss`)のPrompt規約A/B」
  を追加(規約Cは`REJECTED`と明記)。
- `DECISION_LOG.md`: 新規エントリ「ER-011-KP-VALIDATOR-NUMERIC-
  HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03」を追加
  (-02/-03の実装・回帰・Runtime evidence・アーキテクチャ上の発見を
  1エントリへ集約)。
- `OPEN_ITEMS.md`: OPEN-116を`RESOLVED / PRODUCTION_WIRED`へ更新
  (Track A/B/規約A・Bは`PRODUCTION_WIRED`、規約Cは`REJECTED`と明記)。
  OPEN-40へ「助数詞リストの共通モジュール統合により部分的に解消
  (本体は引き続き未解消)」を追記。
- `HISTORY_INDEX.md`は指示通り触っていない。

## 6. Gate 3チェックリスト充足状況

- [x] Production正式初回経路への配線(A2・B1が共有する選定Prompt本体
  へ配線、呼び出し側コード変更不要で両レベルへ自動反映)。
- [x] 既存回帰(§3、判定変化ゼロ)。
- [x] 新規回帰テスト(§3、規約A/B存在・規約C不在の3件)。
- [x] Runtime evidence(§4、規約Bは直接確認、規約Aは同一文言の既存
  Trial-17証跡を援用、確率的遵守である旨を明記)。
- [x] approved specとProduction挙動の一致確認: 規約Cを追加していない
  ことをテストで固定。
- [x] Report作成(本ファイル)。
- [x] SSOT反映(§5)。
- [x] Git commit・push(§7)。

## 7. STOP条件該当有無

該当なし。規約Cの追加・「日」「人」のリスト追加・近似音PASS・
retry/fallback変更・TTS/ASR再生成・`git add -A`・他Agent起動・
バックグラウンド待機のいずれも行っていない。

## 8. 変更ファイル一覧

-02由来(未commitのまま引き継ぎ):
- `er003_audio_tts_asr_safety.py`
- `er007_ja_asr_validator_01.py`
- `er006_preprod_hardening_01_validation.py`
- `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`
- `ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02_REPORT.md`(新規)
- `er011_output/kp_validator_numeric_homophone_gloss_production_wiring_02/`(新規)

-03(本タスク)で追加:
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(規約A/B追加)
- `er003_test_b1_p2.py`(新規テスト3件)
- `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`
- `er011_output/kp_validator_numeric_homophone_gloss_production_wiring_03/`(新規)
- 本Reportファイル(新規)
