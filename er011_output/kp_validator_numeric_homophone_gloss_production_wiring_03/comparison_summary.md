# Runtime evidence 比較表(規約A・規約B、選定Prompt配線後)

対象: `er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/article.md`
(Trial-13 B1本文、原文無変更)。Production選定経路
(`er003_b1_p2_keywords.load_prompt_template/build_user_message/make_selector_fn`
+ `er003_key_words_production.run_production_selection_gate`)→canonicalization
(`er003_key_words_canonicalization`、規約B配線は-02で既に完了・変更なし)を
実データで2回実行した(attempt_1/attempt_2、いずれも初回でPASS、リトライなし)。

## 実行結果概要

| 項目 | Trial-13原本 | attempt_1(本タスク) | attempt_2(本タスク) |
|---|---|---|---|
| selection status | KEY_WORDS_STRUCTURE_PASS(1/1) | KEY_WORDS_STRUCTURE_PASS(1/1) | KEY_WORDS_STRUCTURE_PASS(1/1) |
| canonicalization status | (Trial-13時点は規約B未配線) | CANONICALIZATION_PASS、5件全qa_overall_status=PASS | CANONICALIZATION_PASS、5件全qa_overall_status=PASS |
| 選ばれたrank1〜5 | story with two different speeds / room for their own pace / median of about two nights / point to / emerging preference | emerging preference / median / self-directed travel / not fit all / point to | emerging preference / median / room for / too broad a label / self-directed travel |

選定される表現自体はLLMの非決定性により毎回変わり得る(これは本タスクで
変更した2文の追加とは無関係な、選定Prompt既存部分の性質)。5件が
Trial-13と一致することは要求されておらず、実際に一致していない。

## (a) glossに「～」「〜」「…」が含まれないか

attempt_1のrank5(`point to`)で直接確認できた: Trial-13原本のgloss
「～を示す、～を指し示す」(プレースホルダー使用)に対し、attempt_1では
**「示す、示唆する」**(プレースホルダーなし、プロンプトの例示
「～を示す」ではなく「示す、指し示す」と同型の書き換え)へ変わった。
attempt_1/attempt_2の他4項目、attempt_2の全5項目とも、gloss内に
「～」「〜」「…」はいずれも**含まれない**(目視・grep both確認済み、
`attempt_1/keywords_canonicalized.json`・`attempt_2/keywords_canonicalized.json`
参照)。

## (b) glossの数字が漢数字か

attempt_1・attempt_2とも、選ばれた5件の中に数字を含むgloss候補が
**含まれなかった**(Trial-13原本のrank3「median of about two nights」/
「中央値は約2泊」に相当する候補が、両attemptとも「median」単体
[数字を含まない]として選ばれ、"two nights"部分が採用されなかった)。
そのため、本タスクの2回の実プロダクション実行では規約Aを直接観測する
条件が偶然揃わなかった。

規約Aの実効性については、既存の`er011_output/open112_kp_validator_fix_
trial_17/track_c_raw_response.json`(同一の候補「median of about two
nights」/「中央値は約2泊」を含む入力に対し、本タスクと同一文言の
規約Aを指示したTrial)で、`"japanese_gloss": "中央値は約二泊"`
(漢数字への書き換え成功)という実LLM応答済みの証跡が既にある
(-02 Reportでも参照)。本タスクではこれを追加検証せず流用する
(同じ候補が今回選ばれなかったため、新規にこの一点だけを検証する
ための追加LLM呼び出しは行わなかった。過剰な追加コストを避ける判断)。

**遵守は確率的である**: (1)選定Prompt自体がLLMの選定判断であるため、
数字を含む候補が毎回top5に選ばれるとは限らない、(2)規約A/Bはいずれも
Prompt文言による指示であり、決定的Validatorによる強制ではないため、
モデルが指示に従わない場合でも構造上PASSしてしまう可能性が残る
(canonicalization側の`_JA_GLOSS_PARENTHETICAL_RE`のような決定的
gloss品質チェックは、プレースホルダー文字や数字表記には及んでいない)。

## (c) Key Phrase 5件の学習価値がTrial-13原本と比べて劣化していないか

- 決定的Validator(`validate_production_selection`、1〜5語・完全文/節
  排除・有限助動詞排除・本文対応・重複禁止等)は、attempt_1/attempt_2
  とも**初回(1/1)でPASS**——Trial-13原本と同じく、リトライなしで
  hard requirementを満たした。
- canonicalization側の12項目QA(`qa_standalone_natural_unit`等)は、
  attempt_1/attempt_2とも**5件×12項目すべてPASS**
  (`qa_overall_status: PASS`)——Trial-13原本の水準と同等。
- 選ばれた表現の性質(比喩・意味不透明な句動詞・統計用語・名詞句の
  抽象度)は、Trial-13原本(story with two different speeds/room for
  their own pace/median of about two nights/point to/emerging
  preference)と同種のカテゴリ(figurative・phrasal verb・domain
  term・compact pattern)に収まっており、質的な劣化の兆候は見られない。

以上より、規約A/Bの2文追加によって選定・canonicalizationの構造的品質
(Validator PASS率・QA PASS率)が悪化した形跡はない。

## 証跡パス

- `attempt_1/selector_prompt.txt`(規約A/B追加後の実際のuser_message)
- `attempt_1/keywords_runtime_metadata.json`(selection生応答)
- `attempt_1/canonicalization_prompt.txt`
- `attempt_1/canonicalization_runtime_metadata.json`(canonicalization生応答)
- `attempt_1/keywords_canonicalized.json`(最終マージ結果)
- `attempt_2/`配下、同様の構成

## Cost Trace(実費、概算)

selection・canonicalizationとも`gpt-5.6-sol`(reasoning effort=high)、
Trial-13 B1と同程度の入出力サイズ。Production関数(`make_selector_fn`/
`make_canonicalization_fn`)はusage(token数)を返さない設計のため、
Trial-17 Track C実績値(1回あたり約$0.12[約¥19])を参考値として、
本タスクでは選定2回+canonicalization2回の計4回の実LLM呼び出しを
行った(概算合計 約$0.5前後、小額の範囲)。
