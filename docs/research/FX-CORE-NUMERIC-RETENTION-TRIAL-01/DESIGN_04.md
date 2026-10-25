# DESIGN_04 (R5: 既存B3に「読者が聞くべき重要数値」欄を追加。2026-10-25、委任_04。DEV/Trial専用・Production非接続・既定OFF)

根拠: ユーザー原文 `docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_02.md`(§2〜§6)、`OPUS_REVIEW_01.md` R5、`DESIGN_03.md`、`PHASE2_RESULT_01.md`(ig_nobel型でB3がStorylineに数値を入れずE=∅、4/4)。
Opus条件A: R5はOpusが提案し2回のレビューで言及済みの形(B3同一呼出のJSON欄・B3自身の判断・中核数値の表記から<=2)に沿うため再レビュー不要(Fable判断)。形から外れる変更(別LLM呼出・Writer Prompt構造変更)は行わない。

## 1. 既存B3との差分(Production B3 Prompt/schema定数/derive_ranks/規則5は不変)
| 項目 | 既存(Production・委任_03 v2) | R5(v3、DEV wrapperのみ) |
|---|---|---|
| B3 user message | USER_PROMPT_TEMPLATE | 末尾に追記: v2(Storylineの答えの数値)+ **追加の指示2**(`B3_ADDENDUM_V3_FIELD`) |
| B3 JSON出力 | selected_storyline / fact_tests / selected_fact_ids / selected_fact_brief / recheck_note | + `reader_must_hear_numbers`(文字列配列)。`with_field_schema()`が送信直前に`STORYLINE_B3_JSON_SCHEMA`の**deepcopy**へ追加(Production定数は不変・testで確認) |
| E(保持Gateの対象) | Storylineの数値 | **欄の数値**(従来と同じ写像規則: ニュース欄の中核数値のみ・_STORYのみ不可・同一概念1個・<=2)。Storyline数値は整合の記録のみ |
| 欄が空 | - | 数値不要の記事(E=∅許容。Gate無し) |
| Gate・O-2'・M2・J2 | 継続 | 継続(Eの出所が変わるだけ) |

追加指示2の骨子(ユーザー原文§3): 入れてよいのは「ないと中心的な発見・事実が伝わりにくい/驚き・面白さ・論旨・比較の説得力を支える/言葉で代替できない/流れを損なわない」を**すべて満たす**数値のみ。「重要なほど多く」ではなく絞る。日付・年・序数・背景/補足・内訳・比較の相手側の値は入れない(比較の結果の倍率/差そのものが中心的な発見ならそれは入れてよい)。最大2個。無ければ[]。採用Factの台帳numeric_value表記のまま。Storylineにも自然に入れられるなら入れてよい(任意)。例示は記事非依存(「12.5%」「約3万人」「4.5倍」)。

## 2. 欄とStorylineの不一致の事前登録
- **欄を優先**。Storyline数値が欄に無い場合は記録のみ(`storyline_consistency`: storyline_not_in_field)。欄の数値がStorylineに無い場合も記録のみ(field_not_in_storyline)。和集合にはしない(不要数値を増やさないため)。
- 欄の違反(ニュース欄の中核に写像できない/表記なし/<=2超/概念重複)は従来M1と同じく**B3を1回だけ再実行**(`M1_RETRY_NOTE_V3_TEMPLATE`)。なお違反ならM1_VIOLATION(chainへ進まない)。初回で3個以上を出した場合は「2個に収めるために不可欠な事実を落とす」可能性として`first_pass_field_items`を記録し報告する(独断で上限を変えない)。

## 3. Writerへの伝わり方(Prompt構造は変えない)
R0_PROMPT/R1/R2 Promptは不変。EはStoryline(『テーマ：』行)に入った場合のR0への自然な反映と、ニュース欄の【中核数値】印、そして保持Gate(R0/R1/R2直後の決定論検査→不足なら既存の再生成枠で1回だけ書き直し)で保護する。**R0の初稿で欄の数値が自然に入ったか**(Gate発火なし)をそのまま測る。R0への明示指示を足すには別途Writer契約(Prompt追記)が要り、その場合は本Trialの範囲外(Opus再レビュー・採用判断)として報告する。

## 4. 検証指標(PREREGISTERED_CRITERIA_03)
記事別に最終本文の数値を必須/任意/不要へ決定論で分類(`er115_fx_numeric_r5_score_01.py`、評価LLMなし)。Before/Afterの追加・削除、不要数の増減、ユニーク数値表記数。文章品質はFableが`COMPARISON_04.md`で読む。

## 5. Production不変・採用時の必要作業
- Production B3 Prompt・`STORYLINE_B3_JSON_SCHEMA`・`derive_ranks`・規則5・R0_PROMPT・閾値は不変。`grep`: er115_*以外に`er115_`・`B3_ADDENDUM`・`reader_must_hear_numbers`の参照0。DEVに環境変数読取なし。CLIの`--b3-addendum v3`を手動指定したときのみ有効(既定v1)。
- 採用時: B3 schemaに欄追加(Production変更)・Writer契約・Annotation producerとの整合・Opus条件C(`ADOPTION_NOTE_01.md`)。
- test: `er115_fx_numeric_r5_test_01.py`(11) + 既存`er115_fx_numeric_retention_trial_01_test_01.py`(46)全PASS。
