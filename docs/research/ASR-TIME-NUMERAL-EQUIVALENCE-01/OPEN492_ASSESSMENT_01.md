# OPEN492_ASSESSMENT_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_06、API 0・LLM呼出0)

## 結論
OPEN-492 = **実害なし・対応不要(現状維持)**。分類=『実害なし』(11-8)。CLOSED(対応不要)。再オープン条件を末尾に記録。

## (a) 仕様確認(literal扱いは意図された仕様)
- er021_en_asr_semantic_equivalence_production_01.py:535-541 `_tier1_atoms`: 『7桁以上の生の数字列(電話番号・ID等) -> 値化せず桁完全一致のみ』(カンマ・小数点なしのとき)。コメントで目的が明記された設計(ID類を数値等価に巻き込まない保護)。
- test固定: er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py:179 NEGATIVE_NUMERIC `The reference number is 1234567.` ↔ `...one two three four five six seven.` は救済しない(Tier1が7桁以上を値として読まないことに依存)。trial側 er021_..._trial_01_test_01.py:120 も同じ。
- CURRENT_SPEC/DECISION_LOGに7桁literal規則の独立記載は無し(Grep 電話番号|7桁=0件)。承認済み仕様はTier1設計(EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01、commit 014bb9e52)の実装コメント。

## (b)(c) 修正の可否
`1,000,000 dollars`↔`1000000 dollars`の同値化は1ブロックでは済まない: literal atomは`_apply_suffixes`(通貨/percent/scale語の併合)を通らないため `1000000 dollars` は literal+literal(dollars)に分かれ、number(currency=dollar)と型が違う。同値化するには (1)7桁以上raw数字列もnumber化して接尾辞を併合する(=ID保護の設計を変更し、`1234567`≒`1,234,567`≒`one million two hundred…`の判定範囲拡張になる)、または (2)literalとnumberを桁文字列一致で橋渡しする新規比較規則、のいずれかが必要。いずれもID保護範囲の判断を伴い『自明な不具合修正』ではない。一方で下記のとおり実害の観測がないため、新規仕様判断を要求するほどの便益もない。

## (d) 実害の数値根拠(5,330対 replay corpus、`pairs_01.jsonl`、スクリプト出力)
- 7桁以上の生数字列を含む対: canon側 1件 / ASR側 1件。カンマ区切り7桁以上: canon側 1件 / ASR側 0件。
- 『同じ桁の生数字列とカンマ数が canon↔ASR で食い違う』対 = **0件**。
- 現在の挙動確認(runtime、`judge_primary`): `1,000,000 dollars`↔`1000000 dollars` および逆向き= NG_PROTECTED/final_gate_value_diff(誤NG)。`one million dollars`↔`1,000,000 dollars`/`1 million dollars`= PASS(通常のASR出力形では救済される)。`one million dollars`↔`1000000 dollars`= NG。
- 失敗の向きは安全側(誤PASSでなく誤NG)。誤NGはSecondary/Reviewへ回るだけで、誤PASSによる品質低下は生じない。ASR(gpt-4o-transcribe/Whisper系)は桁区切りカンマ付きで返す傾向で、7桁以上をカンマなしで返した実例は保存corpusに無い。

## 再オープン条件
(1) 保存corpusまたは新規runで ASR が7桁以上をカンマなしで返した誤NG(実対)が観測された場合、(2) canonに7桁以上の数が頻出する新Familyが追加された場合。その時はID保護範囲の仕様判断(判断候補)として扱う。
