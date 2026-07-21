# ER-003-P2H Extraction Form QA FAIL 2件の詳細

P2Gの`88 PASS / 2 FAIL`のうち、FAILとなった2件を記録する。項目・score・P2G成果物は変更していない。

## FAIL 1: A01 / Set B (方式P) / Rank 2

- phrase: take off
- source_span: took off
- source_sentence: England took off players including Rice and strengthened their defense, hoping to protect their lead.
- 日本語グロス: 選手を交代で下げる
- Extraction Form QA notes: 競技上の他動詞義「選手を交代で下げる」には目的語枠が必要で、take offだけではこの学習単位として短くしすぎている。基本形化と出典上の句動詞の抽出自体は正しい。
- ユーザー評価: △(score=1)
- 方式比較への影響: 該当項目は他のQA PASS項目と同様に集計へ含めている(QA結果を理由とした除外・再生成は行っていない)。

## FAIL 2: ADD03 / Set C (方式U) / Rank 5

- phrase: be in place
- source_span: was still in place
- source_sentence: Because the toll was gone, but the blockade targeting ships linked to Iran was still in place.
- 日本語グロス: 依然として実施中である
- Extraction Form QA notes: display_phraseではstillを除いているため、グロスの「依然として」はbe in place自体には含まれない意味を加えている。
- ユーザー評価: △(score=1)
- 方式比較への影響: 該当項目は他のQA PASS項目と同様に集計へ含めている(QA結果を理由とした除外・再生成は行っていない)。
