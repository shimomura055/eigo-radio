# F1_EVALUATION_02(OPEN F-1: `thirty five`→`thirty 5` の部分数字化、委任_02 H、別commit)

## 問題
`er003_v1_n3_01_tts_generate.tts_safe_number_words_en` は `two..twelve` の語だけ数字化するため、`thirty five` が `thirty 5` になる(TTS入力=canon)。分類層(`er006 normalize_numeric`)は `30 5`、Tier1/最終ゲート(`er021 _tier1_atoms`)は number30+number5 と読み、ASR `35 people`(正しい読み)と値DIFFになる(`thirty 5 people`↔`35 people`は修正前DIFF。時刻 `At 10 thirty 5`↔`At 10:35`[TEST_MATRIX #72/73]も同じ原因で残存していた)。

## 修正(Opus推奨どおり、er006/er021の両方で『十の位の語+1桁数字』を合成数として読む)
- `er021_en_asr_semantic_equivalence_production_01.py::_consume_number_word_run` に1ブロック(+4行): 数詞語runの末尾が十の位の語で、直後トークンが `[1-9]` の1桁数字なら値に加算して消費。
- `er006_preprod_hardening_01_validation.py::_convert_cardinal_words` に1ブロック(+5行): 同じ条件で数字を数値語として `core` に追加して `j` を進める(後続の既存chunk分割[時刻]・単独合成の両方が効く)。
- er003側(TTS入力の数字化)は変更していない=Production TTS入力の挙動変更なし(Opus所見5)。

## 影響分析gate(DIFFサイズ: 各層1関数1ブロック・合計9行)
| gate | 結果 |
|---|---|
| replay PASS→NG(judge/分類層/value_guard) | 2,701対(`replay02_f1.json`[実装と同一内容のproto moduleで実行。proto dirは実装commitと同一のため削除] vs `replay02_after.json`)で全て **0**(変化自体が0件。saved dataに該当パターンが無い=F-1は本番データでは未観測の型) |
| 合成負例NG維持 | `thirty 5 people`↔`36 people` NG / `↔30 5 people` NG / `thirty 55 people`は合成しない / `thirty 0`・`ten 5`・`thirty and 5`は従来どおり / `At 10 thirty 5`↔`At 10:30 5`・`At 1035` NG |
| 合成正例 | `thirty 5 people`↔`35 people`/`thirty five people` EQ、`one hundred thirty 5 dollars`↔`$135` EQ、`thirty 5 percent`↔`35%` EQ、`At 10 thirty 5`↔`At 10:35`・`At 12 forty 5`↔`At 12:45` EQ(旧REF[NG]→EQ) |
| TEST_MATRIX_02 再実測 | 125件で期待不一致0(`matrix02_after_f1_02.txt`)。変化は旧REF 2行[#72/73]とF-1 PIN→EQの3行のみ |
| 固定test | `er006_f1_tens_digit_test_01.py`(4 test)、`er021_time_numeral_test_01.py` のF-1行をPIN→EQ更新 |
| 全回帰 | 別途(RESULT_PACKET_ATN2.md) |

## 開示(限界)
- 合成する対象は『十の位の語+1桁数字』のみ(`tts_safe_number_words_en`は `two..twelve` を数字化し、ハイフン複合 `thirty-five` は `(?<!-)` で保護される=部分数字化は空白区切りの `thirty five` 型)。同じ原因で `one hundred 5` / `one hundred and 5`(scale語+1桁数字)は残る(対象外・稀。新規OPENの残存欄に記録)。
- `thirty 5`が文字どおり『30と5』を意図する原稿は事実上存在しない(原稿は数字または語)ため、合成数読みによる誤PASSは生じない。
- 本修正は保存entryの再判定(rejudge/guard_entry)にも効く(同じ関数)。
