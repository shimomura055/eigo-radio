# OPEN489_ROOT_CAUSE_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-489 `between nine and eleven` 誤NG)

## 結論(先に)
**既存承認仕様の不具合(局所的な解析不具合・構造変更なし)**。数詞語のrunを作る2つの層が、どちらも『`and`を数の一部として一括で解析する』前提で、接続詞の`and`をまたいでrun全体の解析に失敗していた。修正=各層1ブロック(er021 `_consume_number_word_run` +9行 / er006 `_convert_cardinal_words` +6行)。判定構造・閾値・受理面は無変更(Opusレビュー不要と判定=Fable方針どおり)。

## 再現(修正前HEAD、API 0。`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/test_matrix_02.py --modules base_HEAD03`)
```
canon 'between 9 and 11' || asr 'between nine and eleven'
  Tier1 atoms: canon [between, number 9, and, number 11] / asr [between, LITERAL nine, and, number 11]   <- nineが数値化されない
  value_guard: DIFF src_drop(b):'9'->None   classify: TRUE_CONTENT_MISMATCH  -> NG_PROTECTED/p1_value_diff   (誤NG)
同型: 'seven and eight children'||'7 and 8 children' / 'two and three'||'2 and 3' / 'between ten and eleven'(asr側が年ペア1011) / 'between twenty and thirty'(2030)
```
- 発生層(1) 検査層=Tier1/最終ゲートが使う`er021_en_asr_semantic_equivalence_production_01._consume_number_word_run`: `_NUMBER_VOCAB`に`and`を含めたまま語を貪欲に読み(`nine and eleven`を1 run)、`_parse_bare_number_run`が`and`を除去して`[nine, eleven]`として解析 → 『単独の一桁語の連続は合成しない』規則(`_split_into_two_digit_groups`:197)で失敗 → runごと破棄され`nine`はliteralに戻る。一桁語以外の組(`ten and eleven`=10,11、`twenty and thirty`)は**年ペア読み1011/2030という誤った1数**になる(さらに悪い側の失敗)。
- 発生層(2) 一次分類=`er006_preprod_hardening_01_validation._convert_cardinal_words`: 2026-10-23の是正(FAMILY-Z-VOICE-PRODUCTION-WIRING-01、`and`はscale語直後のみ)が『不正な`and`位置の数値語列は**列全体を変換しない**』としていたため、`nine and eleven`が`9 and 11`にならず、canon側(TTS入力の数字化後`9 and 11`)と語・token数が一致しない。
- 共通の欠陥: 不正な`and`位置を『列を分割する境界』ではなく『列全体の失敗』として扱っていた。

## 修正(各層1ブロック、新しい受理条件・閾値・辞書なし)
1. `er021._consume_number_word_run`: runの走査中、`and`は『直前語がscale語(hundred/thousand/million/billion/trillion)かつ直後が`and`以外の数詞語』の場合だけrunに含め、それ以外ではrunをその位置で終える(`and`は次の語としてliteral化)。`one hundred and ten`/`two thousand and five`/`two hundred and fifty and sixty`(2つ目のandは接続詞)は従来どおり/正しく処理。
2. `er006._convert_cardinal_words`: 不正な`and`位置では列全体を捨てず、その`and`の直前までを1つの列として変換し、`and`以降は次のloopで別の列として処理する(先頭`and`は既存の`lead`処理で語として残る)。`one hundred and two`型は従来どおり。

## 既存仕様・過去Trialとの整合(照合した箇所)
- `er006_preprod_hardening_01_validation.py:311-322`(2026-10-23の`and`是正コメント): 『andはhundred/thousand/million直後だけ』の方針はそのまま(本修正は『不正位置のandで列全体を捨てる』部分を『分割』に直しただけ)。`Her husband and two young brothers`型(and+数詞語)は従来どおりandを巻き込まない(TEST_MATRIX_03に回帰case)。
- OPEN-482(`_try_clock_pair`、`er021:374-`): `between nine and ten thirty`↔`between 9 and 10:30`、`between 9 and ten-thirty`、`and ten thirty`↔`and 1030`(NE)を TEST_MATRIX_03 で固定。`and`直前の判定(`_try_clock_pair`:`before in _SCALE_WORDS`)と本修正の`and`判定は同じ基準(scale語直後のみ数の一部)で一致。
- 年号読み(`nineteen ninety`=1990等)・`_parse_bare_number_run`・`_split_into_two_digit_groups`は無変更。
- OPUS_REVIEW_01(OF-TN-03)で『`between nine and ten-thirty`の`nine`側は別件X-3』と開示されていた不具合そのもの。PIN(NG)として固定されていた行(TEST_MATRIX_02 #93)をEQへ更新。

## 副所見(別管理)
- 保存corpus 5,330対で『数詞語 and 数詞語』(scale語なし)は0件、`hundred and`/`thousand and`型は9件(全て従来どおり)。実害の発生頻度は低い(Writerが数字表記を使うため)が、誤NGは再生成/HR Lockの原因になり得る性質のため通常手順で修正した。
- 新規候補 **OPEN-491 ASR-TTS-SCALE-WORD-DIGIT-COMPOSITE-01**: `tts_safe_number_words_en`が`one hundred and ten`を`one hundred and 10`、`two hundred and five`を`2 hundred and 5`にし、ASR=`110`/`205`との正式再判定が`p1_value_diff`(F-1[十の位+1桁]と同型の既存不具合。corpus 5,330対で該当0件、実害未観測)。分類=『不具合・是正待ち』(修正へ進む。次委任案=er021 `_consume_number_word_run`/er006 `_convert_cardinal_words`の2ブロック、同じ影響分析gate)。
